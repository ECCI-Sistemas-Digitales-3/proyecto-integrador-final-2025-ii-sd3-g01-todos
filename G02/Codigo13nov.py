from machine import Pin, PWM
import time
import network
from umqtt.simple import MQTTClient

EJECUTAR_CICLO_AL_INICIO = False   # Normal: solo se inicia desde Node-RED

# --- PWM (0–100%) por defecto ---
PWM_AGITADOR_POR_DEFECTO = 70       # Velocidad agitador
PWM_ELEVADOR_POR_DEFECTO = 60       # Velocidad elevador

# --- TIEMPOS DE MOVIMIENTO (segundos) ---
TIEMPO_BAJAR_ASPA  = 5              # Tiempo para bajar la aspa
TIEMPO_AGITAR      = 10             # Tiempo del ciclo de agitación
TIEMPO_SUBIR_ASPA  = 5              # Tiempo para subir la aspa

# --- TIEMPOS DE ESPERA ENTRE MOTORES (segundos) ---
ESPERA_ENTRE_ELEVADOR_Y_AGITADOR = 5
ESPERA_ENTRE_AGITADOR_Y_ELEVADOR = 5

SSID = "Familia puentes"
PASSWORD = "Matteo2023"

MQTT_BROKER = "192.168.1.9"
MQTT_CLIENT_ID = "ESP32_Agitador"

TOPIC_ESTADO          = b"agitador/estado"
TOPIC_CONTROL         = b"agitador/control"

TOPIC_PWM_AGITADOR    = b"agitador/pwm"
TOPIC_ELEVADOR_ESTADO = b"elevador/estado"
TOPIC_ELEVADOR_PWM    = b"elevador/pwm"
TOPIC_ELEVADOR_POS    = b"elevador/posicion"
TOPIC_LOG             = b"sistema/log"

# Pines motor agitador
PIN_PWM_AGITADOR = 15
PIN_IN1_AGITADOR = 4
PIN_IN2_AGITADOR = 2

# Pines motor elevador
PIN_ENA_ELEVADOR = 25
PIN_IN1_ELEVADOR = 26
PIN_IN2_ELEVADOR = 27

# LED indicador
PIN_LED = 14
led = Pin(PIN_LED, Pin.OUT, value=0)

# PWM
FREQ = 1000
pwm_agitador = PWM(Pin(PIN_PWM_AGITADOR), freq=FREQ, duty=0)
in1_agitador = Pin(PIN_IN1_AGITADOR, Pin.OUT, value=0)
in2_agitador = Pin(PIN_IN2_AGITADOR, Pin.OUT, value=0)

IN1_ELEVADOR = Pin(PIN_IN1_ELEVADOR, Pin.OUT, value=0)
IN2_ELEVADOR = Pin(PIN_IN2_ELEVADOR, Pin.OUT, value=0)
ENA_ELEVADOR = PWM(Pin(PIN_ENA_ELEVADOR), freq=1000, duty=0)

client = None

# ------------------ FUNCIONES MQTT / PUBLICACIÓN ---------------------

def publicar(topic, msg):
    if isinstance(msg, str):
        msg = msg.encode()
    if client is not None:
        try:
            client.publish(topic, msg)
            print("MQTT PUBLISH ->", topic, msg)
        except Exception as e:
            print("Error al publicar MQTT:", e)

def publicar_posicion_elevador(porc_real):
    """
    porc_real: 0 = abajo, 100 = arriba (lógica interna)
    Queremos que en el dashboard se vea al revés:
    100 = abajo, 0 = arriba
    """
    valor_invertido = 100 - int(porc_real)
    publicar(TOPIC_ELEVADOR_POS, str(valor_invertido))

# ------------------ MOTOR AGITADOR ------------------------

def motor_forward_agitador(pwm_porcentaje):
    """Enciende el agitador al % indicado y prende el LED."""
    pwm = int((pwm_porcentaje/100)*1023)
    in1_agitador.on()
    in2_agitador.off()
    pwm_agitador.duty(pwm)
    led.on()   # LED SOLO encendido mientras el motor agitador está activo

    # Publicaciones para Node-RED
    publicar(TOPIC_PWM_AGITADOR, str(pwm_porcentaje))   # p.ej. "70"
    publicar(TOPIC_ESTADO, "agitador_on")               # estado lógico ON

    print("Agitador ENCENDIDO al {}%".format(pwm_porcentaje))


def motor_brake_agitador():
    """Frena el agitador (ambos transistores activos) y apaga LED."""
    in1_agitador.on()
    in2_agitador.on()
    pwm_agitador.duty(0)
    led.off()

    # Avisar a Node-RED que se apagó
    publicar(TOPIC_PWM_AGITADOR, "0")
    publicar(TOPIC_ESTADO, "agitador_off")

    print("Agitador FRENADO")


def motor_coast_agitador():
    """Apaga el agitador en rueda libre y apaga LED."""
    in1_agitador.off()
    in2_agitador.off()
    pwm_agitador.duty(0)
    led.off()

    # Avisar a Node-RED que se apagó
    publicar(TOPIC_PWM_AGITADOR, "0")
    publicar(TOPIC_ESTADO, "agitador_off")

    print("Agitador APAGADO")

# ------------------ MOTOR ELEVADOR ------------------------

def detener_motor_elevador():
    IN1_ELEVADOR.off()
    IN2_ELEVADOR.off()
    ENA_ELEVADOR.duty(0)
    publicar(TOPIC_ELEVADOR_ESTADO, "reposo")
    publicar(TOPIC_ELEVADOR_PWM, "0")
    print("Elevador DETENIDO")

def mover_abajo(pwm_percent):
    pwm = int((pwm_percent/100)*1023)
    IN1_ELEVADOR.off()
    IN2_ELEVADOR.on()
    ENA_ELEVADOR.duty(pwm)
    publicar(TOPIC_ELEVADOR_ESTADO, "bajando")
    publicar(TOPIC_ELEVADOR_PWM, str(pwm_percent))
    print("Elevador BAJANDO al {}%".format(pwm_percent))

def mover_arriba(pwm_percent):
    pwm = int((pwm_percent/100)*1023)
    IN1_ELEVADOR.on()
    IN2_ELEVADOR.off()
    ENA_ELEVADOR.duty(pwm)
    publicar(TOPIC_ELEVADOR_ESTADO, "subiendo")
    publicar(TOPIC_ELEVADOR_PWM, str(pwm_percent))
    print("Elevador SUBIENDO al {}%".format(pwm_percent))

# ------------------ WIFI ---------------------

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a WiFi...")
        wlan.connect(SSID, PASSWORD)
        intento = 1
        while not wlan.isconnected() and intento <= 10:
            print(" Intento {}/10...".format(intento))
            time.sleep(2)
            intento += 1
    if wlan.isconnected():
        print("WiFi CONECTADO:", wlan.ifconfig())
    else:
        print("ERROR: No se pudo conectar a WiFi")
    return wlan

# ------------------ MQTT ---------------------

def conectar_mqtt():
    global client
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
    try:
        client.connect()
        print("MQTT CONECTADO a", MQTT_BROKER)
        return client
    except Exception as e:
        print("ERROR al conectar MQTT:", e)
        return None

# ------------------ CICLO COMPLETO ---------------------

def ciclo_agitacion_completo(porc_agitador=None, porc_elevador=None):
    """
    Si porc_agitador o porc_elevador son None, usa los valores
    por defecto definidos arriba.
    Si vienen valores desde Node-RED (iniciar 40 60), se usan esos.
    """
    if porc_agitador is None:
        porc_agitador = PWM_AGITADOR_POR_DEFECTO
    if porc_elevador is None:
        porc_elevador = PWM_ELEVADOR_POR_DEFECTO

    print("=== INICIO CICLO COMPLETO ===")
    print("   Agitador: {}%  Elevador: {}%".format(porc_agitador, porc_elevador))

    publicar(TOPIC_ESTADO, "Ciclo iniciado")

    # Asumimos inicio ARRIBA → 100% real → en dashboard se verá 0%
    publicar_posicion_elevador(100)

    # --- 1. BAJAR ASPA ---
    print("Paso 1: Bajar aspa")
    mover_abajo(porc_elevador)
    time.sleep(TIEMPO_BAJAR_ASPA)
    detener_motor_elevador()
    publicar_posicion_elevador(0)   # 0 real (abajo) → dashboard 100%

    # --- ESPERA ENTRE ELEVADOR Y AGITADOR ---
    print("Esperando {} s antes de iniciar agitador...".format(
        ESPERA_ENTRE_ELEVADOR_Y_AGITADOR))
    time.sleep(ESPERA_ENTRE_ELEVADOR_Y_AGITADOR)

    # --- 2. AGITAR ---
    print("Paso 2: Agitar mezcla")
    motor_forward_agitador(porc_agitador)
    time.sleep(TIEMPO_AGITAR)
    motor_brake_agitador()
    publicar(TOPIC_ESTADO, "Agitación finalizada")

    # --- ESPERA ENTRE AGITADOR Y ELEVADOR ---
    print("Esperando {} s antes de subir aspa...".format(
        ESPERA_ENTRE_AGITADOR_Y_ELEVADOR))
    time.sleep(ESPERA_ENTRE_AGITADOR_Y_ELEVADOR)

    # --- 3. SUBIR ASPA ---
    print("Paso 3: Subir aspa")
    mover_arriba(porc_elevador)
    time.sleep(TIEMPO_SUBIR_ASPA)
    detener_motor_elevador()
    publicar_posicion_elevador(100)  # 100 real (arriba) → dashboard 0%

    publicar(TOPIC_ESTADO, "Ciclo finalizado")
    print("=== CICLO COMPLETO FINALIZADO ===")

# ------------------ CALLBACK MQTT ---------------------

def sub_cb(topic, msg):
    msg = msg.decode().strip()
    print("MQTT MSG:", topic, "->", msg)

    partes = msg.split()

    if len(partes) >= 1 and partes[0] == "iniciar":
        # Por defecto, None → usa PWM_AGITADOR_POR_DEFECTO y PWM_ELEVADOR_POR_DEFECTO
        porc_agitador = None
        porc_elevador = None

        # Si viene: iniciar 40 60
        if len(partes) >= 2:
            porc_agitador = int(partes[1])
        if len(partes) >= 3:
            porc_elevador = int(partes[2])

        ciclo_agitacion_completo(porc_agitador, porc_elevador)

# ------------------ MAIN ---------------------

print("==== INICIANDO PROGRAMA ESP32 ====")

wlan = conectar_wifi()

client = conectar_mqtt()
if client is not None:
    client.set_callback(sub_cb)
    client.subscribe(TOPIC_CONTROL)
    print("Suscrito a:", TOPIC_CONTROL)
else:
    print("No hay cliente MQTT, revisa el broker.")

motor_coast_agitador()
detener_motor_elevador()
led.off()

# estado inicial: aspa arriba (100 real → dashboard 0)
publicar_posicion_elevador(100)
publicar(TOPIC_ESTADO, "Sistema listo")

# Solo ejecuta automático si lo activas arriba
if EJECUTAR_CICLO_AL_INICIO:
    ciclo_agitacion_completo()

print("Esperando mensajes MQTT en bucle... (envía 'iniciar' o 'iniciar 40 60' en agitador/control)")

while True:
    try:
        if client is not None:
            client.check_msg()
        time.sleep(0.1)
    except OSError as e:
        print("Error en bucle principal:", e)
        time.sleep(2)
