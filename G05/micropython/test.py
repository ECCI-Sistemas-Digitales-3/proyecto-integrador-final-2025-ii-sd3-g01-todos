import network
import time
from machine import Pin, I2C
from umqtt.robust import MQTTClient

# =======================
# CONFIGURACIONES
# =======================
WIFI_SSID = "vivo V23 5G"   # Cambia por tu red WiFi
WIFI_PASS = "yeison123"     # Contraseña de tu WiFi
MQTT_BROKER = "10.27.57.138" # IP de la Raspberry Pi (Broker MQTT)

# Topics MQTT
MQTT_TOPIC_TEMP = b"in/micro/sensor/temperatura"   # Publicar temperatura
MQTT_TOPIC_LED_CMD = b"in/micro/led/control"       # Recibir comandos LED
MQTT_TOPIC_LED_STATUS = b"out/micro/led/estado"    # Publicar estado LED

# Pines I2C ESP32
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

# LED en pin 13
led = Pin(13, Pin.OUT)
led.off()  # Asegurar que el LED empiece apagado

# Variables de control
led_encendido = False
modo_automatico = True  # True = control por temperatura, False = control manual

# Umbrales de temperatura
TEMPERATURA_ENCENDER = 20.0
TEMPERATURA_APAGAR = 25.0

# =======================
# FUNCIONES MQTT
# =======================

def mqtt_callback(topic, msg):
    """Función que se ejecuta cuando llega un mensaje MQTT"""
    global led_encendido, modo_automatico
    
    print(f"Mensaje recibido - Topic: {topic}, Mensaje: {msg}")
    
    if topic == MQTT_TOPIC_LED_CMD:
        comando = msg.decode().lower().strip()
        
        if comando == "on" or comando == "1" or comando == "encender":
            # Encender LED manualmente
            modo_automatico = False
            led.on()
            led_encendido = True
            print("LED encendido por comando MQTT")
            client.publish(MQTT_TOPIC_LED_STATUS, b"ON")
            
        elif comando == "off" or comando == "0" or comando == "apagar":
            # Apagar LED manualmente
            modo_automatico = False
            led.off()
            led_encendido = False
            print("LED apagado por comando MQTT")
            client.publish(MQTT_TOPIC_LED_STATUS, b"OFF")
            
        elif comando == "auto" or comando == "automatico":
            # Volver al modo automático (temperatura)
            modo_automatico = True
            print("Modo automático activado")
            client.publish(MQTT_TOPIC_LED_STATUS, b"AUTO")
            
        elif comando == "toggle" or comando == "alternar":
            # Alternar estado del LED
            modo_automatico = False
            led_encendido = not led_encendido
            led.value(led_encendido)
            estado = "ON" if led_encendido else "OFF"
            print(f"LED alternado a: {estado}")
            client.publish(MQTT_TOPIC_LED_STATUS, estado.encode())
            
        elif comando == "status" or comando == "estado":
            # Reportar estado actual
            estado = "AUTO" if modo_automatico else ("ON" if led_encendido else "OFF")
            client.publish(MQTT_TOPIC_LED_STATUS, estado.encode())
            print(f"Estado reportado: {estado}")

def conectar_mqtt():
    """Conectar al broker MQTT y configurar callbacks"""
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
    """Busca y muestra todos los dispositivos I2C conectados"""
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
        # Leer 2 bytes de temperatura
        data = i2c.readfrom_mem(lm75_addr, 0x00, 2)
        temp = (data[0] << 8 | data[1]) >> 7   # Quitar bits no usados
        if temp > 1023:  # Ajustar si es negativo
            temp -= 2048
        return temp * 0.5   # Cada bit equivale a 0.5 °C
    except OSError as e:
        print(f"Error leyendo LM75 en 0x{lm75_addr:02X}: {e}")
        return None

def controlar_led_automatico(temperatura):
    """Controla el LED según la temperatura (solo en modo automático)"""
    global led_encendido
    
    if not modo_automatico:
        return  # No hacer nada si estamos en modo manual
    
<<<<<<< HEAD
    if temperatura > TEMPERATURA_APAGAR:
        # Apagar LED si temperatura supera 25°C
        led.off()
        led_encendido = False
        print(f"¡ALERTA! Temperatura {temperatura}°C > {TEMPERATURA_APAGAR}°C - LED APAGADO")
        client.publish(MQTT_TOPIC_LED_STATUS, b"OFF_AUTO")
    elif temperatura > TEMPERATURA_ENCENDER and not led_encendido:
        # Encender LED si temperatura es mayor a 20°C y el LED está apagado
        led.on()
        led_encendido = True
        print(f"Temperatura {temperatura}°C > {TEMPERATURA_ENCENDER}°C - LED ENCENDIDO")
        client.publish(MQTT_TOPIC_LED_STATUS, b"ON_AUTO")
    elif temperatura <= TEMPERATURA_ENCENDER and led_encendido:
        # Apagar LED si temperatura baja a 20°C o menos y el LED está encendido
        led.off()
        led_encendido = False
        print(f"Temperatura {temperatura}°C <= {TEMPERATURA_ENCENDER}°C - LED APAGADO")
        client.publish(MQTT_TOPIC_LED_STATUS, b"OFF_AUTO")
=======
    # DEBUG: Mostrar información de diagnóstico
    print(f"DEBUG - Temp: {temperatura}°C, Encender: >{TEMPERATURA_ENCENDER}°C, Apagar: <{TEMPERATURA_APAGAR}°C, Estado actual: {'ON' if dispositivo_encendido else 'OFF'}")
    
    # LÓGICA CORREGIDA PARA CONTROL DE TEMPERATURA
    if temperatura > TEMPERATURA_ENCENDER:
        # ENCENDER dispositivo si temperatura > 45°C
        if rele.value() == 0:  # Si el dispositivo está apagado
            rele.on()
            dispositivo_encendido = True
            print(f"ALTA TEMPERATURA {temperatura}°C > {TEMPERATURA_ENCENDER}°C - ENCENDIENDO DISPOSITIVO")
            client.publish(MQTT_TOPIC_LED_STATUS, b"ON_AUTO")
        else:
            print(f"Temperatura ALTA {temperatura}°C > {TEMPERATURA_ENCENDER}°C - DISPOSITIVO ya está ENCENDIDO")
            
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
        print(f"Temperatura NORMAL {temperatura}°C - Manteniendo estado: {'ON' if dispositivo_encendido else 'OFF'}")
>>>>>>> 61f4a8b (Doc_inicial_servidor)

# =======================
# PROGRAMA PRINCIPAL
# =======================

# Conectar a WiFi
conectar_wifi()

# Buscar dispositivos I2C
dispositivos = buscar_dispositivos_i2c()

if not dispositivos:
    print("ERROR: No hay dispositivos I2C conectados.")
    # Aún así conectar MQTT para control manual del LED
    client = conectar_mqtt()
    lm75_addr = None
else:
    lm75_addr = dispositivos[0]
    print(f"Usando dispositivo I2C en 0x{lm75_addr:02X}")
    client = conectar_mqtt()

# Publicar estado inicial
client.publish(MQTT_TOPIC_LED_STATUS, b"AUTO" if modo_automatico else ("ON" if led_encendido else "OFF"))

print("\nSistema iniciado. Comandos disponibles via MQTT:")
print("  - 'on' / '1' / 'encender': Encender LED manual")
print("  - 'off' / '0' / 'apagar': Apagar LED manual")
print("  - 'auto' / 'automatico': Volver a modo automático")
print("  - 'toggle' / 'alternar': Alternar estado LED")
print("  - 'status' / 'estado': Consultar estado actual")

while True:
    try:
        # Verificar mensajes MQTT (non-blocking)
        client.check_msg()
        
        # Leer y publicar temperatura si hay sensor
        if lm75_addr is not None:
            temperatura = leer_lm75(lm75_addr)
            if temperatura is not None:
                print(f"Temperatura: {temperatura}°C - Modo: {'AUTO' if modo_automatico else 'MANUAL'} - LED: {'ON' if led_encendido else 'OFF'}")
                
                # Control automático del LED (solo si está en modo automático)
                controlar_led_automatico(temperatura)
                
                # Publicar temperatura
                client.publish(MQTT_TOPIC_TEMP, str(temperatura))
            else:
                print("Error al leer temperatura")
        else:
            # Sin sensor, solo reportar estado
            print(f"Modo: {'AUTO' if modo_automatico else 'MANUAL'} - LED: {'ON' if led_encendido else 'OFF'}")
        
        time.sleep(2)  # Esperar 2 segundos entre lecturas
        
    except Exception as e:
        print(f"Error en loop principal: {e}")
        time.sleep(5)
        # Intentar reconectar si hay error
        try:
            client.connect()
        except:
            pass
