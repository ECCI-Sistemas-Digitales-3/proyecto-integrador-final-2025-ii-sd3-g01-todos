import time
import machine
import onewire
import ds18x20
from umqtt.robust import MQTTClient
import wifi  

#  CONFIGURACIÓN WIFI
if not wifi.conectar():
    print("Error: No hay conexión WiFi")
    while True:
        time.sleep(1)

print("WiFi conectado")

#  CONFIGURACIÓN MQTT
MQTT_BROKER = "8.tcp.ngrok.io"
MQTT_PORT   = 12777
MQTT_ID     = "esp1_temperaturas"

TOPICS_TEMP = [
    b"in/esp1/temperatura/azul",
    b"in/esp1/temperatura/rojo",
    b"in/esp1/temperatura/amarillo",
    b"in/esp1/temperatura/negro",
    b"in/esp1/temperatura/blanco"
]

client = MQTTClient(MQTT_ID, MQTT_BROKER, port=MQTT_PORT)
client.connect()
print("MQTT conectado\n")

PINES_SENSORES = [33, 25, 26, 27, 14]  # 5 sensores DS18B20
PINES_RESISTENCIAS = [15, 2, 4, 5, 32]  # 5 resistencias

#  CONFIGURACIÓN SENSORES 
sensores = []
for pin in PINES_SENSORES:
    ow = onewire.OneWire(machine.Pin(pin))
    ds = ds18x20.DS18X20(ow)
    roms = ds.scan()
    sensores.append((ds, roms))
    print(f"Sensor en pin {pin}: {roms}")

#  CONFIGURACIÓN RESISTENCIAS
resistencias = []
for pin in PINES_RESISTENCIAS:
    r = machine.Pin(pin, machine.Pin.OUT)
    r.value(0)
    resistencias.append(r)

#  PARÁMETROS CONTROL
TEMP_MIN = 22.0   # Bajo este valor encender resistencia
TEMP_MAX = 27.0   # Sobre este valor apagar resistencia

TIEMPO_MAX_RESISTENCIA = 60  # 1 minuto máximo
INTERVALO_LECTURA = 5  # Tiempo entre lecturas

#  VARIABLES DE CONTROL
resistencia_activa = None
tiempo_inicio_resistencia = None

def apagar_todas():
    global resistencia_activa, tiempo_inicio_resistencia
    for r in resistencias:
        r.value(0)
    resistencia_activa = None
    tiempo_inicio_resistencia = None
    print("Todas las resistencias APAGADAS\n")

# ==========================
#  NOTA: Pines I2C libres
#  SDA = 21
#  SCL = 22
#  (NO usados por ahora)
# ==========================

#  BUCLE PRINCIPAL
print("\nESP1 listo: Temperaturas + Control de resistencias\n")
while True:

    temperaturas = []

    # 1. LEER TEMPERATURAS 
    for i, (sensor, roms) in enumerate(sensores):

        sensor.convert_temp()
        time.sleep_ms(750)

        if roms:
            temp = sensor.read_temp(roms[0])
        else:
            temp = None

        temperaturas.append(temp)
        print(f"Sensor {i+1}: {temp} °C")

        # Publicar temperatura
        if temp is not None:
            client.publish(TOPICS_TEMP[i], str(temp))

    # 2. CONTROL DE RESISTENCIAS 
    for i, temp in enumerate(temperaturas):

        if temp is None:
            continue

        # ENCENDER resistencia (solo a la ves)
        if temp < TEMP_MIN:

            # Si ya hay otra encendida, ignorar
            if resistencia_activa is not None and resistencia_activa != i:
                continue

            if resistencia_activa is None:
                print(f"> Encendiendo RESISTENCIA {i+1}")
                resistencias[i].value(1)
                resistencia_activa = i
                tiempo_inicio_resistencia = time.time()

        # APAGAR si pasó del máximo
        elif temp > TEMP_MAX:

            if resistencia_activa == i:
                print(f"> Apagando RESISTENCIA {i+1} por temperatura alta")
                resistencias[i].value(0)
                resistencia_activa = None
                tiempo_inicio_resistencia = None

    # 3. CONTROL DE TIEMPO MÁXIMO 
    if resistencia_activa is not None:
        if time.time() - tiempo_inicio_resistencia > TIEMPO_MAX_RESISTENCIA:
            print("Tiempo máximo excedido → apagando resistencias")
            apagar_todas()

    print("-----------------------------------\n")
    time.sleep(INTERVALO_LECTURA)
