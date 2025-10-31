import network
import time
from machine import Pin, I2C
from umqtt.robust import MQTTClient

# =======================
# CONFIGURACIONES
# =======================
WIFI_SSID = "vivo V23 5G"
WIFI_PASS = "yeison123"
MQTT_BROKER = "10.27.57.138"

# Topics MQTT
MQTT_TOPIC_TEMP = b"in/micro/sensor/temperatura"
MQTT_TOPIC_LED_CMD = b"in/micro/led/control"
MQTT_TOPIC_LED_STATUS = b"out/micro/led/estado"

# Pines I2C ESP32
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

# LED/RELE en pin 13 (para controlar ventilador/calentador)
rele = Pin(13, Pin.OUT)
rele.off()  # Comenzar apagado

# Variables de control
dispositivo_encendido = False
modo_automatico = True

# Umbrales de temperatura CORREGIDOS
TEMPERATURA_ENCENDER = 27.0   # Encender dispositivo cuando temperatura > 45°C
TEMPERATURA_APAGAR = 22.0     # Apagar dispositivo cuando temperatura < 20°C

# =======================
# FUNCIONES MQTT
# =======================

def mqtt_callback(topic, msg):
    global dispositivo_encendido, modo_automatico
    
    print(f"Mensaje recibido - Topic: {topic}, Mensaje: {msg}")
    
    if topic == MQTT_TOPIC_LED_CMD:
        comando = msg.decode().lower().strip()
        
        if comando in ["on", "1", "encender"]:
            modo_automatico = False
            rele.value(1)
            dispositivo_encendido = True
            print("DISPOSITIVO encendido por comando MQTT")
            client.publish(MQTT_TOPIC_LED_STATUS, b"ON")
            
        elif comando in ["off", "0", "apagar"]:
            modo_automatico = False
            rele.value(0)
            dispositivo_encendido = False
            print("DISPOSITIVO apagado por comando MQTT")
            client.publish(MQTT_TOPIC_LED_STATUS, b"OFF")
            
        elif comando in ["auto", "automatico"]:
            modo_automatico = True
            print("Modo automático activado")
            client.publish(MQTT_TOPIC_LED_STATUS, b"AUTO")
            
        elif comando in ["toggle", "alternar"]:
            modo_automatico = False
            nuevo_estado = not rele.value()
            rele.value(nuevo_estado)
            dispositivo_encendido = nuevo_estado
            estado = "ON" if nuevo_estado else "OFF"
            print(f"DISPOSITIVO alternado a: {estado}")
            client.publish(MQTT_TOPIC_LED_STATUS, estado.encode())
            
        elif comando in ["status", "estado"]:
            estado = "AUTO" if modo_automatico else ("ON" if rele.value() else "OFF")
            client.publish(MQTT_TOPIC_LED_STATUS, estado.encode())
            print(f"Estado reportado: {estado}")

def conectar_mqtt():
    client = MQTTClient("ESP32_LM75", MQTT_BROKER)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(MQTT_TOPIC_LED_CMD)
    print("Conectado al broker MQTT y suscrito a temas")
    return client

# =======================
# FUNCIONES WIFI Y SENSOR
# =======================

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    print("Conectando a WiFi...", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\nConectado a WiFi:", wlan.ifconfig())

def buscar_dispositivos_i2c():
    print("Buscando dispositivos I2C...")
    dispositivos = i2c.scan()
    if len(dispositivos) == 0:
        print("No se encontraron dispositivos I2C!")
    else:
        print("Dispositivos I2C encontrados en las direcciones:")
        for addr in dispositivos:
            print("   - 0x{:02X}".format(addr))
    return dispositivos

def leer_lm75(lm75_addr=0x48):
    try:
        data = i2c.readfrom_mem(lm75_addr, 0x00, 2)
        temp = (data[0] << 8 | data[1]) >> 7
        if temp > 1023:
            temp -= 2048
        return temp * 0.5
    except OSError as e:
        print(f"Error leyendo LM75 en 0x{lm75_addr:02X}: {e}")
        return None

def control_dispositivo_automatico(temperatura):
    global dispositivo_encendido
    
    if not modo_automatico:
        return
    
    # DEBUG: Mostrar información de diagnóstico
    print(f"DEBUG - Temp: {temperatura}°C, Encender: >{TEMPERATURA_ENCENDER}°C, Apagar: <{TEMPERATURA_APAGAR}°C, Estado actual: {'ON' if dispositivo_encendido else 'OFF'}")
    
    # LÓGICA CORREGIDA PARA CONTROL DE TEMPERATURA
    if temperatura > TEMPERATURA_ENCENDER:
        # ENCENDER dispositivo si temperatura > 45°C
        if rele.value() == 0:  # Si el dispositivo está apagado
            rele.on()
            dispositivo_encendido = True
            print(f"🔥🔥🔥 ALTA TEMPERATURA {temperatura}°C > {TEMPERATURA_ENCENDER}°C - ENCENDIENDO DISPOSITIVO")
            client.publish(MQTT_TOPIC_LED_STATUS, b"ON_AUTO")
        else:
            print(f"🔥 Temperatura ALTA {temperatura}°C > {TEMPERATURA_ENCENDER}°C - DISPOSITIVO ya está ENCENDIDO")
            
    elif temperatura < TEMPERATURA_APAGAR:
        # APAGAR dispositivo si temperatura < 20°C
        if rele.value() == 1:  # Si el dispositivo está encendido
            rele.off()
            dispositivo_encendido = False
            print(f"❄❄❄ BAJA TEMPERATURA {temperatura}°C < {TEMPERATURA_APAGAR}°C - APAGANDO DISPOSITIVO")
            client.publish(MQTT_TOPIC_LED_STATUS, b"OFF_AUTO")
        else:
            print(f"❄ Temperatura BAJA {temperatura}°C < {TEMPERATURA_APAGAR}°C - DISPOSITIVO ya está APAGADO")
    
    else:
        # Temperatura entre 20°C y 45°C - mantener estado actual
        print(f"✅ Temperatura NORMAL {temperatura}°C - Manteniendo estado: {'ON' if dispositivo_encendido else 'OFF'}")

# =======================
# PROGRAMA PRINCIPAL
# =======================

# Conectar a WiFi
conectar_wifi()

# Buscar dispositivos I2C
dispositivos = buscar_dispositivos_i2c()

if not dispositivos:
    print("ERROR: No hay dispositivos I2C conectados.")
    client = conectar_mqtt()
    lm75_addr = None
else:
    lm75_addr = dispositivos[0]
    print(f"Usando dispositivo I2C en 0x{lm75_addr:02X}")
    client = conectar_mqtt()

# Publicar estado inicial
client.publish(MQTT_TOPIC_LED_STATUS, b"AUTO" if modo_automatico else ("ON" if rele.value() else "OFF"))

print("\n" + "="*60)
print("CONTROLADOR DE TEMPERATURA - SISTEMA INICIADO")
print("="*60)
print(f"UMBRALES DE TEMPERATURA:")
print(f"  - ENCENDER dispositivo cuando temperatura > {TEMPERATURA_ENCENDER}°C")
print(f"  - APAGAR dispositivo cuando temperatura < {TEMPERATURA_APAGAR}°C")
print(f"Estado inicial: Modo {'AUTO' if modo_automatico else 'MANUAL'}")
print(f"DISPOSITIVO: {'ENCENDIDO' if rele.value() else 'APAGADO'}")
print("="*60)

# Bucle principal
while True:
    try:
        # Verificar mensajes MQTT
        client.check_msg()
        
        # Leer temperatura si hay sensor
        if lm75_addr is not None:
            temperatura = leer_lm75(lm75_addr)
            if temperatura is not None:
                # Control automático del dispositivo
                control_dispositivo_automatico(temperatura)
                
                # Publicar temperatura
                client.publish(MQTT_TOPIC_TEMP, str(temperatura))
            else:
                print("❌ Error al leer temperatura del sensor")
        
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ Error en loop principal: {e}")
        time.sleep(5)
        try:
            client.connect()
        except:
            print("❌ Error reconectando MQTT")