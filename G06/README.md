# Nombre de la etapa:

Control de Bombas con MQTT (ESP32)
.
## Integrantes
Steven Herrera 
Carlos Medina
Daniel Camacho

## Documentación

# ===========================================================
#     CONTROL DE BOMBAS MEDIANTE MQTT CON ESP32
# ===========================================================
# Descripción: Control de bombas por MQTT, con 5 canales (colores).
# ===========================================================

import network            # Manejo de conexión WiFi
import time               # Control de tiempos
from machine import Pin   # Control de pines GPIO
from umqtt.robust import MQTTClient  # Cliente MQTT robusto
import ujson              # Manejo de formato JSON (no usado aquí)
import wify               # Módulo personalizado para conexión WiFi

# --- Configuración del Broker MQTT ---
BROKER = "6.tcp.ngrok.io"   # Dirección del broker MQTT remoto
PORT = 18263                # Puerto MQTT asignado por ngrok

# --- Topics MQTT (uno por color) ---
TOPICS = {
    "CYAN": b"bombas/CYAN",
    "MAGENTA": b"bombas/MAGENTA",
    "YELLOW": b"bombas/YELLOW",
    "BLACK": b"bombas/BLACK",
    "WHITE": b"bombas/WHITE"
}

# === Conexión WiFi ===
if not wify.conectar():                       # Intentar conexión
    print("Error: no se puede continuar sin conexión WiFi")
    while True:
        time.sleep(1)

# --- Configuración de los pines de salida ---
bombas = [
    Pin(14, Pin.OUT),  # CYAN
    Pin(12, Pin.OUT),  # MAGENTA
    Pin(13, Pin.OUT),  # YELLOW
    Pin(27, Pin.OUT),  # BLACK
    Pin(26, Pin.OUT)   # WHITE
]

# --- Flags lógicas para control interno ---
flag_CYAN_galga = True
flag_MAGENTA_galga = True
flag_YELLOW_galga = True
flag_BLACK_galga = True
flag_WHITE_galga = True

# --- Callback MQTT ---
def mensaje(topic, msg):
    """Función que procesa los mensajes recibidos desde el broker."""
    topic = topic.decode()
    msg = msg.decode().strip()
    print(f"Mensaje recibido en {topic}: {msg}")

    # === CYAN ===
    if topic == "bombas/CYAN":
        if msg == "ON" and flag_CYAN_galga:
            bombas[0].value(1)
        elif msg == "OFF" or not flag_CYAN_galga:
            bombas[0].value(0)

    # === MAGENTA ===
    elif topic == "bombas/MAGENTA":
        if msg == "ON" and flag_MAGENTA_galga:
            bombas[1].value(1)
        elif msg == "OFF" or not flag_MAGENTA_galga:
            bombas[1].value(0)

    # === YELLOW ===
    elif topic == "bombas/YELLOW":
        if msg == "ON" and flag_YELLOW_galga:
            bombas[2].value(1)
        elif msg == "OFF" or not flag_YELLOW_galga:
            bombas[2].value(0)

    # === BLACK ===
    elif topic == "bombas/BLACK":
        if msg == "ON" and flag_BLACK_galga:
            bombas[3].value(1)
        elif msg == "OFF" or not flag_BLACK_galga:
            bombas[3].value(0)

    # === WHITE ===
    elif topic == "bombas/WHITE":
        if msg == "ON" and flag_WHITE_galga:
            bombas[4].value(1)
        elif msg == "OFF" or not flag_WHITE_galga:
            bombas[4].value(0)

    else:
        print("Topic desconocido:", topic)

# --- Conexión al broker MQTT ---
def conectar_mqtt():
    """Crea y configura el cliente MQTT, suscribiéndose a los topics."""
    client = MQTTClient("ESP32_Bombas", BROKER, PORT)
    client.set_callback(mensaje)
    client.connect()

    for color, t in TOPICS.items():
        client.subscribe(t)
        print(f"Suscrito al topic: {t.decode()}")

    print("Conectado al broker MQTT")
    return client

# --- Bucle principal ---
cliente = conectar_mqtt()

try:
    while True:
        cliente.check_msg()   # Verifica si hay nuevos mensajes MQTT
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Desconectando...")
    cliente.disconnect()


### 1. [Flujos](/G06/flujos/flows.json)

### 2. [Programación micropython](/G06/micropython/test.py)

import network
import time
from machine import Pin
from umqtt.robust import MQTTClient
import ujson
import wify  # Tu módulo personalizado de conexión WiFi

# --- CONFIGURACIÓN DEL BROKER MQTT ---
BROKER = "6.tcp.ngrok.io"
PORT = 18263

# Topics individuales por color
TOPICS = {
    "CYAN": b"bombas/CYAN",
    "MAGENTA": b"bombas/MAGENTA",
    "YELLOW": b"bombas/YELLOW",
    "BLACK": b"bombas/BLACK",
    "WHITE": b"bombas/WHITE"
}

# === Conexión WiFi ===
if not wify.conectar():
    print(" Error: no se puede continuar sin conexión WiFi")
    while True:
        time.sleep(1)

# --- Pines de bombas ---
bombas = [
    Pin(14, Pin.OUT),  # CYAN
    Pin(12, Pin.OUT),  # MAGENTA
    Pin(13, Pin.OUT),  # YELLOW
    Pin(27, Pin.OUT),  # BLACK
    Pin(26, Pin.OUT)   # WHITE
]

# --- Flags lógicas (booleanas) ---
flag_CYAN_galga = True
flag_MAGENTA_galga = True
flag_YELLOW_galga = True
flag_BLACK_galga = True
flag_WHITE_galga = True

# --- Callback MQTT ---
def mensaje(topic, msg):
    topic = topic.decode()
    msg = msg.decode().strip()
    print(f"📩 Mensaje recibido en {topic}: {msg}")

    # === CYAN ===
    if topic == "bombas/CYAN":
        if msg == "ON" and flag_CYAN_galga:
            bombas[0].value(1)
        elif msg == "OFF" or not flag_CYAN_galga:
            bombas[0].value(0)

    # === MAGENTA ===
    elif topic == "bombas/MAGENTA":
        if msg == "ON" and flag_MAGENTA_galga:
            bombas[1].value(1)
        elif msg == "OFF" or not flag_MAGENTA_galga:
            bombas[1].value(0)

    # === YELLOW ===
    elif topic == "bombas/YELLOW":
        if msg == "ON" and flag_YELLOW_galga:
            bombas[2].value(1)
        elif msg == "OFF" or not flag_YELLOW_galga:
            bombas[2].value(0)

    # === BLACK ===
    elif topic == "bombas/BLACK":
        if msg == "ON" and flag_BLACK_galga:
            bombas[3].value(1)
        elif msg == "OFF" or not flag_BLACK_galga:
            bombas[3].value(0)

    # === WHITE ===
    elif topic == "bombas/WHITE":
        if msg == "ON" and flag_WHITE_galga:
            bombas[4].value(1)
        elif msg == "OFF" or not flag_WHITE_galga:
            bombas[4].value(0)

    else:
        print(" Topic desconocido:", topic)


# --- Conexión MQTT ---
def conectar_mqtt():
    client = MQTTClient("ESP32_Bombas", BROKER, PORT)
    client.set_callback(mensaje)
    client.connect()

    # Suscribirse a todos los topics definidos
    for color, t in TOPICS.items():
        client.subscribe(t)
        print(f" Suscrito al topic: {t.decode()}")

    print(" Conectado al broker MQTT")
    return client


# --- Programa principal ---
cliente = conectar_mqtt()

try:
    while True:
        cliente.check_msg()
        time.sleep(0.1)

except KeyboardInterrupt:
    print(" Desconectando...")
    cliente.disconnect()

