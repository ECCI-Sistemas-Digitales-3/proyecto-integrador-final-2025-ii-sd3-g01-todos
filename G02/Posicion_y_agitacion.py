from machine import Pin, PWM
import time
import network
from umqtt.simple import MQTTClient

# === CONFIGURACIÓN DE RED ===
SSID = "S22 Ultra de Nicolas"
PASSWORD = "12345678"

# === CONFIGURACIÓN MQTT ===
MQTT_BROKER = "10.152.59.190"
MQTT_CLIENT_ID = "ESP32_Agitador"
TOPIC_ESTADO = b"agitador/estado"
TOPIC_PWM = b"agitador/pwm"
TOPIC_CONTROL = b"agitador/control"

# === PINES (L298N canal A - Motor Agitador) ===
PIN_PWM = 4
PIN_IN1 = 18
PIN_IN2 = 5

# === NUEVO MOTOR (Motor de elevación del aspa - Motor 1) ===
PIN_PWM2 = 2     # PWM del motor de elevación
PIN_IN3 = 26     # Dirección 1 (subir/bajar)
PIN_IN4 = 27     # Dirección 2 (subir/bajar)

# === OTROS PINES ===
PIN_LED = 12     # LED indicador
PIN_BOTON = 15   # Botón de inicio

# === CONFIGURACIÓN PWM/DIGITAL ===
FREQ = 1000
# Motor agitador (motor 2)
pwm_motor = PWM(Pin(PIN_PWM), freq=FREQ, duty=0)
in1 = Pin(PIN_IN1, Pin.OUT, value=0)
in2 = Pin(PIN_IN2, Pin.OUT, value=0)
# Motor de elevación (motor 1)
pwm_motor2 = PWM(Pin(PIN_PWM2), freq=FREQ, duty=0)
in3 = Pin(PIN_IN3, Pin.OUT, value=0)
in4 = Pin(PIN_IN4, Pin.OUT, value=0)
# LED y botón
led = Pin(PIN_LED, Pin.OUT)
boton = Pin(PIN_BOTON, Pin.IN, Pin.PULL_UP)

# === FUNCIONES MOTOR 2 (Agitador) ===
def motor2_forward():
    in1.on(); in2.off()

def motor2_reverse():
    in1.off(); in2.on()

def motor2_brake():
    in1.on(); in2.on()

def motor2_coast():
    in1.off(); in2.off()

# === FUNCIONES MOTOR 1 (Elevación) ===
def motor1_bajar():
    in3.on(); in4.off()

def motor1_subir():
    in3.off(); in4.on()

def motor1_parar():
    in3.off(); in4.off()
    pwm_motor2.duty(0)

# === CONFIGURACIÓN WIFI ===
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("📡 Conectando a WiFi...")
        wlan.connect(SSID, PASSWORD)
        intento = 1
        while not wlan.isconnected() and intento <= 10:
            print(f"⏳ Intento {intento}/10")
            time.sleep(2)
            intento += 1
    if wlan.isconnected():
        print("✅ WiFi conectado:", wlan.ifconfig())
    else:
        print("❌ No se pudo conectar a WiFi")
    return wlan

# === MQTT ===
def conectar_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
    try:
        client.connect()
        print("🔗 Conectado al broker MQTT")
        return client
    except Exception as e:
        print("❌ Error al conectar MQTT:", e)
        return None

# === FUNCIONES DE PUBLICACIÓN ===
def publicar_estado(msg):
    print("📤 Estado:", msg)
    client.publish(TOPIC_ESTADO, msg)

# === RAMPAS PWM MOTOR AGITADOR ===
def ramp_up(pwm, step=5, delay=0.2):
    for duty in range(0, 1024, step):
        pwm.duty(duty)
        client.publish(TOPIC_PWM, str(int(duty / 4)))
        time.sleep(delay)

def ramp_down(pwm, step=5, delay=0.2):
    for duty in range(1023, -1, -step):
        pwm.duty(duty)
        client.publish(TOPIC_PWM, str(int(duty / 4)))
        time.sleep(delay)

# === FUNCIONES MOTOR 1: SUBIR Y BAJAR ===
def motor1_bajar_ciclo():
    publicar_estado(b"Motor1: Bajando aspa (30s)")
    motor1_bajar()
    pwm_motor2.duty(800)  # velocidad media-alta
    time.sleep(30)
    motor1_parar()
    publicar_estado(b"Motor1: Aspa abajo (listo)")

def motor1_subir_ciclo():
    publicar_estado(b"Motor1: Subiendo aspa (30s)")
    motor1_subir()
    pwm_motor2.duty(800)
    time.sleep(30)
    motor1_parar()
    publicar_estado(b"Motor1: Aspa arriba (finalizado)")

# === CICLO COMPLETO DE AGITACIÓN CON MOTOR 1 + MOTOR 2 ===
def ciclo_agitacion_total():
    led.on()
    publicar_estado(b"Iniciando secuencia completa")

    # 1️⃣ BAJA EL ASPA
    motor1_bajar_ciclo()

    # 2️⃣ ESPERA 10s
    publicar_estado(b"Esperando 10s antes de agitar")
    time.sleep(10)

    # 3️⃣ MOTOR AGITADOR (motor2)
    publicar_estado(b"Iniciando agitación (rampa subida)")
    motor2_forward()
    ramp_up(pwm_motor, step=4, delay=0.15)

    publicar_estado(b"Agitador a máxima velocidad")
    print("⚙  Agitación en curso (5s)")
    start_time = time.time()
    while (time.time() - start_time) < 5:
        elapsed = int(time.time() - start_time)
        current_duty = int(pwm_motor.duty() / 4)
        client.publish(TOPIC_PWM, str(current_duty))
        print(f"⏱ {elapsed:02d}s | PWM: {current_duty}/255")
        time.sleep(1)

    publicar_estado(b"Finalizando agitación (rampa bajada)")
    ramp_down(pwm_motor, step=4, delay=0.15)
    pwm_motor.duty(0)
    motor2_brake()
    client.publish(TOPIC_PWM, "0")
    publicar_estado(b"Agitador apagado")

    # 4️⃣ ESPERA 10s
    publicar_estado(b"Esperando 10s antes de subir aspa")
    time.sleep(10)

    # 5️⃣ SUBE EL ASPA
    motor1_subir_ciclo()

    led.off()
    publicar_estado(b"✅ Secuencia completa finalizada\n")

# === CALLBACK MQTT (control remoto desde Node-RED) ===
def sub_cb(topic, msg):
    msg = msg.decode()
    print(f"📩 Mensaje recibido en {topic}: {msg}")
    if msg == "iniciar":
        ciclo_agitacion_total()
    elif msg == "detener":
        pwm_motor.duty(0)
        pwm_motor2.duty(0)
        motor2_brake()
        motor1_parar()
        led.off()
        publicar_estado(b"Proceso detenido manualmente")
    elif msg == "bajar":
        motor1_bajar_ciclo()
    elif msg == "subir":
        motor1_subir_ciclo()

# === PROGRAMA PRINCIPAL ===
wlan = conectar_wifi()
client = conectar_mqtt()
if client:
    client.set_callback(sub_cb)
    client.subscribe(TOPIC_CONTROL)

publicar_estado(b"ESP32 listo. Esperando orden o boton...")

while True:
    client.check_msg()
    if boton.value() == 0:
        publicar_estado(b"Boton presionado: iniciando ciclo total")
        ciclo_agitacion_total()
        time.sleep(1)