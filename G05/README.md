# Nombre de la etapa: Resistencias

## Integrantes
Michael Yesid Velasquez V.- Cod: 94882 Yeison Gabriel Niño J. - Cod: 61096 Carlos Eduardo Puentes L. - Cod: 89466

## Arquitectura propuesta
<img width="724" height="485" alt="image" src="https://github.com/user-attachments/assets/f6a70a1b-818a-462a-9783-3bb44cf8ccfe" />

## Periférico a trabajar
Resistencia, Para calentar pintura.
## Importar configuración desde config.py
try: from config import WIFI_SSID, WIFI_PASS, MQTT_BROKER, MQTT_TOPIC except ImportError: raise Exception("⚠️ Debes crear un archivo config.py con tus credenciales (ver config.py.sample)")

## Configuración I2C y LED
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000) led = Pin(13, Pin.OUT) led.off()

## Umbrales de temperatura
TEMPERATURA_ENCENDER = 20.0 # Encender LED cuando supere 20°C TEMPERATURA_APAGAR = 25.0 # Apagar LED cuando baje de 25°C

## Conectar WiFi
def conectar_wifi(): wlan = network.WLAN(network.STA_IF) wlan.active(True) wlan.connect(WIFI_SSID, WIFI_PASS) print("Conectando a WiFi...", end="") while not wlan.isconnected(): print(".", end="") time.sleep(1) print("\n✅ WiFi conectado:", wlan.ifconfig())

## Conectar MQTT
def conectar_mqtt(): client = MQTTClient("esp32", MQTT_BROKER) client.connect() print("✅ Conectado a broker MQTT:", MQTT_BROKER) return client

## Simulación lectura temperatura
(En práctica puedes leer desde un sensor real como LM75, DHT, etc.)

def leer_temperatura(): # Aquí puedes poner lectura real del sensor return 25 + (time.time() % 10) # Simulación 25°C a 35°C

## Programa principal
def main(): conectar_wifi() client = conectar_mqtt()

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
### 1. [Flujos](/G05/flujos/flows.json)

### 2. [Programación micropython](/G05/micropython/test.py)


