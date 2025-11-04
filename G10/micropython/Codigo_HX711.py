# ===== Librerías =====
import network
import time
from machine import Pin
from umqtt.simple import MQTTClient
from HX711 import HX711

# ===== CONFIGURACIÓN WiFi =====
SSID = "Camilo Correa"
PASSWORD = "1234567890"

# ===== CONFIGURACIÓN MQTT =====
MQTT_BROKER = "172.20.10.3"   # IP del broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC = b"sensor/peso"

# ===== CONFIGURACIÓN HX711 =====
DT_PIN = 4    # Pin de datos DT del HX711
SCK_PIN = 16   # Pin de reloj SCK del HX711

# ===== Conectar WiFi =====
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a WiFi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
            print(".", end="")
    print("\Conectado a WiFi:", wlan.ifconfig())

# ===== Inicializar MQTT =====
def conectar_mqtt():
    client = MQTTClient("ESP32_HX711", MQTT_BROKER, port=MQTT_PORT)
    client.connect()
    print("Conectado al broker MQTT")
    return client

# ===== Inicializar HX711 =====
def inicializar_hx711():
    hx = HX711(dout_pin=DT_PIN, pd_sck_pin=SCK_PIN)
    hx.tare()  # calibrar a cero
    print("HX711 listo (calibrado a 0)")
    return hx

# ===== PROGRAMA PRINCIPAL =====
def main():
    conectar_wifi()
    client = conectar_mqtt()
    hx = inicializar_hx711()

    FACTOR_CALIBRACION = 6000  # Ajustar este valor según tu celda

    while True:
        try:
            peso = hx.get_data_mean(10)  # Promedio de 10 lecturas
            if peso is not None:
                peso_kg = peso / FACTOR_CALIBRACION
                print("Peso:", round(peso_kg, 2), "kg")
                client.publish(MQTT_TOPIC, str(round(peso_kg, 2)))
            else:
                print("Lectura inválida")
            time.sleep(2)

        except Exception as e:
            print("Error:", e)
            time.sleep(3)

# ===== Ejecutar =====
main()
