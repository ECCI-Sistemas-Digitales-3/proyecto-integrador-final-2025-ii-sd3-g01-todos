import time
import machine
import onewire
import ds18x20
from umqtt.robust import MQTTClient
import Wifi 

#  CONFIGURACIÓN WIFI
if not Wifi.conectar():
    print("Error: No hay conexión WiFi")
    while True:
        time.sleep(1)

print("WiFi conectado")

#  CONFIGURACIÓN MQTT
MQTT_BROKER = "192.168.2.216"
MQTT_PORT   = 1883
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

#  PINES Y HARDWARE
PINES_SENSORES = [15, 2, 4, 5, 32]    
PINES_RESISTENCIAS = [33, 25, 26, 27, 14]

#  CONFIGURACIÓN SENSORES
sensores = []
estado_sensores = []   # registros: {roms, fallos, estado}

for pin in PINES_SENSORES:
    ow = onewire.OneWire(machine.Pin(pin))
    ds = ds18x20.DS18X20(ow)
    roms = ds.scan()

    sensores.append(ds)
    estado_sensores.append({
        "roms": roms,
        "fallos": 0,
        "estado": "OK" if roms else "SIN_ROM"
    })

    print(f"Sensor en pin {pin}: {roms}")

#  CONFIGURACIÓN RESISTENCIAS
resistencias = []
for pin in PINES_RESISTENCIAS:
    r = machine.Pin(pin, machine.Pin.OUT)
    r.value(0)
    resistencias.append(r)

#  PARÁMETROS DE CONTROL
TEMP_MIN = 22.0
TEMP_MAX = 27.0

TIEMPO_MAX_RESISTENCIA = 60
INTERVALO_LECTURA = 5

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

#  BUCLE PRINCIPAL
print("\nESP1 listo: Temperaturas + Control de resistencias\n")

while True:

    temperaturas = []
    #  1. LECTURA SEGURA DE SENSORES — con try/except
    for i, ds in enumerate(sensores):

        registro = estado_sensores[i]
        roms = registro["roms"]

        # Si no hay ROM → no intentamos leer
        if not roms:
            registro["fallos"] += 1
            registro["estado"] = "SIN_ROM"
            temperaturas.append(None)
            print(f"Sensor {i+1}: SIN_ROM")
            continue

        try:
            ds.convert_temp()
            time.sleep_ms(750)

            temp = ds.read_temp(roms[0])

            # Lectura correcta
            registro["fallos"] = 0
            registro["estado"] = "OK"
            temperaturas.append(temp)

            print(f"Sensor {i+1}: {temp} °C")

            client.publish(TOPICS_TEMP[i], str(temp))

        except Exception as e:
            registro["fallos"] += 1
            temperaturas.append(None)

            if registro["fallos"] >= 5:
                registro["estado"] = "DAÑADO"
            else:
                registro["estado"] = "ERROR"

            print(f"Sensor {i+1}: ERROR ({registro['estado']}) (fallos {registro['fallos']})")


    #  2. LÓGICA DE CONTROL DE RESISTENCIAS (sin cambios)
    for i, temp in enumerate(temperaturas):

        if temp is None:
            continue

        if temp < TEMP_MIN:

            if resistencia_activa is not None and resistencia_activa != i:
                continue

            if resistencia_activa is None:
                print(f"> Encendiendo RESISTENCIA {i+1}")
                resistencias[i].value(1)
                resistencia_activa = i
                tiempo_inicio_resistencia = time.time()

        elif temp > TEMP_MAX:

            if resistencia_activa == i:
                print(f"> Apagando RESISTENCIA {i+1} por temperatura alta")
                resistencias[i].value(0)
                resistencia_activa = None
                tiempo_inicio_resistencia = None

    #  3. CONTROL DE TIEMPO MÁXIMO
    if resistencia_activa is not None:
        if time.time() - tiempo_inicio_resistencia > TIEMPO_MAX_RESISTENCIA:
            print("Tiempo máximo excedido → apagando resistencias")
            apagar_todas()

    print("-----------------------------------\n")
    time.sleep(INTERVALO_LECTURA)
