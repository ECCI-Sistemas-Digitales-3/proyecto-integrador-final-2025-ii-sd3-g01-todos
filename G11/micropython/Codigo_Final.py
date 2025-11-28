from machine import Pin, PWM
from time import sleep, time
from umqtt.robust import MQTTClient
import Wifi

# 1. CONSTANTES DE CONTROL Y RED
# Tiempo total de succión para el 100% de la mezcla (en segundos)
TIEMPO_100_PORCIENTO = 25
MOTOR_PWM_FREQ = 1000
SEGUNDOS_ENTRE_MOTORES = 2

# Variables del tanque final
TIEMPO_FINAL_MOTOR = 3 # 3 segundos para bajar, agitar y subir
PAUSA_FINAL = 2 # Segundos entre acciones finales

# CONFIG MQTT
MQTT_BROKER = "192.168.59.216"
MQTT_PORT = 1883
MQTT_CLIENT_ID = b"ESP32_BOMBAS"
MQTT_TOPIC_IN = b"esp/out" # Topic para recibir el setpoint de mezcla

# Topics para notificar el estado de las bombas al dashboard
TOPIC_ESTADO_BOMBAS = b"in/esp2/bombas/estado"
# Topics para motores del tanque final
TOPIC_AGITADOR = b"agitador/estado"
TOPIC_ELEVADOR = b"elevador/estado"

# 2. DEFINICIÓN DE PINES Y MOTORES

# Los colores base y sus respectivos pines (usando los pines seguros)
COLORES_MOTORES = [
    # (Color, Pin_IN1, Pin_IN2, Pin_ENA, Clave_Corta)
    ("CIAN",    26, 27, 25, 'C'), # Motor 1
    ("MAGENTA", 32, 33, 23, 'M'), # Motor 2
    ("YELLOW",  13, 19, 14, 'Y'), # Motor 3 (IN2: 19)
    ("BLACK",   21, 4, 5, 'K'),   # Motor 4 (IN1: 21)
    ("WHITE",   12, 22, 2, 'W'), # Motor 5
]

MOTORES = [] # Lista para almacenar los objetos Pin y PWM

# Pines para motores de tanque final
ELEVADOR_IN1_PIN = 15 # Dirección 1 (Ej. Bajar)
ELEVADOR_IN2_PIN = 16 # Dirección 2 (Ej. Subir)
AGITADOR_IN1_PIN = 17 # Dirección 1 (Agitar)
AGITADOR_IN2_PIN = 18 # Dirección 2 (Agitar Inverso o Apagado)

# Almacenamiento de los motores finales 
MOTOR_ELEVADOR = {}
MOTOR_AGITADOR = {}

def inicializar_motores():
    """Inicializa todos los pines de control de motor."""
    print("Inicializando 5 motores...")
    for color, pin_in1, pin_in2, pin_ena, clave in COLORES_MOTORES:
        try:
            IN1 = Pin(pin_in1, Pin.OUT)
            IN2 = Pin(pin_in2, Pin.OUT)
            ENA_PWM = PWM(Pin(pin_ena), freq=MOTOR_PWM_FREQ)
            
            IN1.value(0)
            IN2.value(0)
            ENA_PWM.duty(0)
            
            MOTORES.append({
                'color': color,
                'clave': clave, # Clave corta (C, M, Y, K, W)
                'in1': IN1,
                'in2': IN2,
                'ena': ENA_PWM
            })
            print(f"Motor {color} OK.")
        except Exception as e:
            print(f"Error al inicializar Motor {color} en GPIOs {pin_in1}, {pin_in2}, {pin_ena}: {e}")
            pass
    
    print(f"Total de motores listos: {len(MOTORES)}")
    
    # Inicializar motores del tanque final
    global MOTOR_ELEVADOR, MOTOR_AGITADOR
    try:
        # Elevador
        MOTOR_ELEVADOR['in1']= Pin(ELEVADOR_IN1_PIN,Pin.OUT)
        MOTOR_ELEVADOR['in2']= Pin(ELEVADOR_IN2_PIN,Pin.OUT)
        MOTOR_ELEVADOR['in1'].value(0)
        MOTOR_ELEVADOR['in2'].value(0)
        # Agitador
        MOTOR_AGITADOR['in1']= Pin(AGITADOR_IN1_PIN,Pin.OUT)
        MOTOR_AGITADOR['in2']= Pin(AGITADOR_IN2_PIN,Pin.OUT) # CORREGIDO: Usar AGITADOR_IN2_PIN
        MOTOR_AGITADOR['in1'].value(0)
        MOTOR_AGITADOR['in2'].value(0)
        print(f"Motores de tanque final Agitador, Elevador:")
    except Exception as e:
        print(f"Error al inicializar motores {e}") # Usar f-string para mostrar la excepción
        pass

# 3. FUNCIONES DE CONTROL DE MOTOR

def motor_apagar_total(motor):
    """Apaga el motor (coast mode) para bombas y motores finales."""
    # Apaga la habilitación si existe (solo para las bombas de dosificación)
    if 'ena' in motor:
        motor['ena'].duty(0)
    # Pone ambas entradas de dirección a LOW (aplica a todos los motores)
    motor['in1'].value(0)
    motor['in2'].value(0)

def motor_succionar(motor, tiempo_segundos):
    """Activa el motor para la succión por un tiempo dado."""
    color = motor['color']
    
    try:
        # 1. Notificar al dashboard: Motor ON (Usando f-string con string)
        # Nota: Los mensajes MQTT deben ser bytes, la conversión se hace implícitamente en el publish.
        msg_on = '{"bomba":"%s", "estado":"ON", "tiempo":%.2f}' % (color, tiempo_segundos)
        client.publish(TOPIC_ESTADO_BOMBAS, msg_on)
        print(f"→ MQTT ON: {color} por {tiempo_segundos:.2f}s")
        
        # 2. Activar el motor 
        motor['in1'].value(1)
        motor['in2'].value(0)
        motor['ena'].duty(800) 
        
        # 3. Esperar el tiempo de dosificación
        sleep(tiempo_segundos)
        
        # 4. Apagar 
        motor_apagar_total(motor)
        
        # 5. Notificar al dashboard: Motor OFF
        msg_off = '{"bomba":"%s", "estado":"OFF"}' % color
        client.publish(TOPIC_ESTADO_BOMBAS, msg_off)
        print(f"← MQTT OFF: {color}")
        
    except Exception as e:
        print(f"ERROR durante la succión del motor {color}: {e}")
        motor_apagar_total(motor) # Apagado de emergencia
        
        
# Función: Secuencia de motores del tanque final
def Elevador_agitador():
    """
    Ejecuta la secuencia de Bajada, Agitación y Subida del elevador.
    Publica el estado de cada acción por MQTT.
    """
    
    print("\n Iniciando secuencia final (Elevador y Agitador) ")
    
    # 1. Elevador: BAJAR
    try:
        print(f"1. Elevador BAJANDO ({TIEMPO_FINAL_MOTOR}s)...")
        client.publish(TOPIC_ELEVADOR, b"DOWN")
        
        # Activar Bajar (Ej. IN1=1, IN2=0)
        MOTOR_ELEVADOR['in1'].value(1)
        MOTOR_ELEVADOR['in2'].value(0)
        
        sleep(TIEMPO_FINAL_MOTOR)
        
        # Parar
        motor_apagar_total(MOTOR_ELEVADOR)
        client.publish(TOPIC_ELEVADOR, b"STOP")
        print("Elevador Parado.")
    except Exception as e:
        print(f"ERROR en Elevador (Bajada): {e}")
        motor_apagar_total(MOTOR_ELEVADOR)
    
    # Esperar 2 segundos
    sleep(PAUSA_FINAL)

    # 2. Agitador: REVOLVER
    try:
        print(f"2. Agitador REVOLVIENDO ({TIEMPO_FINAL_MOTOR}s)...")
        client.publish(TOPIC_AGITADOR, b"ON")
        
        # Activar Agitar (Ej. IN1=1, IN2=0)
        MOTOR_AGITADOR['in1'].value(1)
        MOTOR_AGITADOR['in2'].value(0)
        
        sleep(TIEMPO_FINAL_MOTOR)
        
        # Parar
        motor_apagar_total(MOTOR_AGITADOR)
        client.publish(TOPIC_AGITADOR, b"OFF")
        print("Agitador Parado.")
    except Exception as e:
        print(f"ERROR en Agitador: {e}")
        motor_apagar_total(MOTOR_AGITADOR)

    # Esperar 2 segundos
    sleep(PAUSA_FINAL)
    
    # 3. Elevador: SUBIR 
    try:
        print(f"3. Elevador SUBIENDO ({TIEMPO_FINAL_MOTOR}s)...")
        client.publish(TOPIC_ELEVADOR, b"UP")
        
        # Activar Subir (Ej. IN1=0, IN2=1)
        MOTOR_AGITADOR['in1'].value(0)
        MOTOR_AGITADOR['in2'].value(1)
        
        sleep(TIEMPO_FINAL_MOTOR)
        
        # Parar
        motor_apagar_total(MOTOR_ELEVADOR)
        client.publish(TOPIC_ELEVADOR, b"STOP")
        print("Elevador Parado.")
    except Exception as e:
        print(f"ERROR en Elevador (Subida): {e}")
        motor_apagar_total(MOTOR_ELEVADOR)

    print("Secuencia final completada")

# 4. PARSEO DE MENSAJE Y LÓGICA DE MEZCLA

def parse_mqtt_message(msg):
    """
    Parsea el string de MQTT (ej: 'C:0 M:10 Y:20 K:60 W:10') a un diccionario
    de tiempos de succión, y valida que la suma de porcentajes sea 100.
    """
    tiempos = {}
    msg_str = msg.decode().strip()
    suma_total = 0
    
    try:
        # 1. Separar por componentes (ej: ['C:0', 'M:10', ...])
        componentes = msg_str.split() 
        
        for item in componentes:
            # 2. Separar clave y valor (ej: 'C', '0')
            if ':' not in item: continue # Ignorar formato incorrecto
            key, value = item.split(':', 1)
            
            # 3. Intentar convertir a entero
            try:
                porcentaje = int(value)
            except ValueError:
                print(f"ERROR: Valor '{value}' no es un número para la clave {key}.")
                return None
            
            # 4. Acumular y calcular tiempo
            if 0 <= porcentaje <= 100:
                suma_total += porcentaje
                # Calcular el tiempo de succión: (Porcentaje / 100) * Tiempo_Total
                tiempo = (porcentaje / 100) * TIEMPO_100_PORCIENTO 
                tiempos[key.upper()] = tiempo
            else:
                print(f"ERROR: Porcentaje {porcentaje} fuera de rango (0-100) para {key}.")
                return None

        # 5. Validación final
        if suma_total != 100:
            print(f"ERROR: La suma de porcentajes es {suma_total}%, debe ser 100%.")
            return None
            
        return tiempos # Devuelve el diccionario de tiempos (ej: {'C': 0.0, 'M': 1.0, ...})
        
    except Exception as e:
        print(f"ERROR de procesamiento del mensaje: {e} en mensaje: {msg_str}")
        return None

def on_message(topic, msg):
    """Callback que se ejecuta al recibir un mensaje MQTT."""
    print("\n--- Mensaje de Setpoint Recibido ---")
    
    if topic != MQTT_TOPIC_IN:
        return

    # 1. Parsear y validar el mensaje, obteniendo el tiempo de succión
    tiempos_succion = parse_mqtt_message(msg)
    if tiempos_succion is None:
        return

    # 2. Ejecutar la secuencia de dosificación
    print(f"\n--- Iniciando Secuencia de Mezcla ({TIEMPO_100_PORCIENTO}s total) ---")
    
    try:
        for i, motor in enumerate(MOTORES):
            clave = motor['clave']
            
            # 3. Buscar el tiempo calculado para este motor
            tiempo_succion = tiempos_succion.get(clave, 0) # Usa 0 si la clave no se encuentra
            
            if tiempo_succion > 0:
                # 4. Activar y succionar
                motor_succionar(motor, tiempo_succion)
                
                # 5. Pausa de seguridad entre bombas 
                if i < len(MOTORES) - 1:
                    sleep(SEGUNDOS_ENTRE_MOTORES)
            else:
                print(f"Motor {motor['color']} {tiempo_succion:.2f}s → Omitiendo.")

    except Exception as e:
        print(f"ERROR FATAL en la secuencia de mezcla: {e}")
        # Asegurar el apagado de todas las bombas en caso de error
        for motor in MOTORES:
            motor_apagar_total(motor)
    
    print("\n--- Secuencia de Mezcla Finalizada ---")
    
    # Ejecutar la secuencia de motores del tanque final
    Elevador_agitador()

# 5. INICIALIZACIÓN PRINCIPAL

# Inicializar y conectar WiFi
try:
    if not Wifi.conectar():
        print("ERROR: Fallo al conectar WiFi.")
        while True:
            sleep(1)
except Exception as e:
    print(f"ERROR: No se pudo importar/ejecutar el módulo Wifi: {e}")
    while True:
        sleep(1)

# Inicializar los motores
inicializar_motores()

# Inicializar y conectar MQTT
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
client.set_callback(on_message)

try:
    client.connect()
    client.subscribe(MQTT_TOPIC_IN)
    print(f"\nMQTT conectado y escuchando en el tópico: {MQTT_TOPIC_IN.decode()}")
except Exception as e:
    print(f"ERROR al conectar MQTT: {e}")
    
print("\nESP32 #2 listo y en modo escucha.")

# 6. BUCLE PRINCIPAL (Modo Escucha No Bloqueante)

while True:
    try:
        client.check_msg() 
    except OSError as e:
        print(f"Error de conexión MQTT: {e}. Reintentando...")
        sleep(5)
        try:
            client.connect()
            client.subscribe(MQTT_TOPIC_IN)
        except:
            pass
            
    sleep(0.1)
