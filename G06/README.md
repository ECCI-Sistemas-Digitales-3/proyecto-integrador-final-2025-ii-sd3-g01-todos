# Nombre de la etapa:
Control de Bombas con MQTT (ESP32)
## Integrantes
Steven Herrera 
Carlos Medina
Daniel Camacho

## Documentación


# Control de Bombas CMYKW mediante MQTT y Galgas

## Resumen General

Este proyecto implementa un **sistema de control remoto para cinco bombas peristálticas** correspondientes a los colores del modelo **CMYKW (Cyan, Magenta, Yellow, Black y White)**.  
El control se realiza mediante el **protocolo MQTT**, utilizando un **ESP32 programado en MicroPython**, el cual recibe comandos remotos, **verifica el estado físico mediante galgas** y activa las bombas de forma segura.

Cada bomba está asociada a un **topic MQTT individual**, y su funcionamiento depende tanto del **comando remoto ("ON"/"OFF")** como del **estado lógico de la galga correspondiente**, que actúa como un permiso físico de habilitación.



## Objetivos del Sistema

  -Permitir el **control remoto e independiente** de las cinco bombas CMYKW mediante MQTT.  
  -Implementar una **seguridad lógica y física** con galgas que habilitan o bloquean cada bomba.  
  -Facilitar la **integración con plataformas IoT** (Node-RED, Raspberry Pi, SCADA educativos, etc.).  
  -Servir como **base didáctica** para prácticas de control y comunicaciones con MicroPython y ESP32.  

## Arquitectura del Sistema

### ESP32 con MicroPython
- Conectado por Wi-Fi mediante el módulo personalizado `wify.py`.  
- Suscrito a **cinco topics MQTT**, uno por cada bomba.  
- Controla directamente las **salidas digitales** que alimentan las bombas.  
- Lee las **entradas digitales** de las galgas (una por cada color).  

### Broker MQTT (Ngrok)
- Servidor remoto que **intermedia la comunicación** entre el cliente y el ESP32.  

###  Cliente Remoto (Node-RED / PC)
- Envía comandos `"ON"` o `"OFF"` a los topics específicos de cada color.  

## Funcionamiento Lógico

1. Al iniciar, el ESP32 se **conecta a la red Wi-Fi**.  
2. Luego se **conecta al broker MQTT** y se **suscribe a los cinco topics**:

-bombas/CYAN
-bombas/MAGENTA
-bombas/YELLOW
-bombas/BLACK
-bombas/WHITE


3. En el ciclo principal, el programa **escucha los mensajes MQTT**:

- Si el mensaje es `"ON"` **y la galga está activa (True)** → la bomba se energiza.  
- Si el mensaje es `"OFF"` **o la galga está inactiva (False)** → la bomba se apaga.  

4. Las **galgas actúan como interruptores de seguridad**, evitando la activación de una bomba sin permiso físico.  

## Variables y Componentes Principales

| Elemento | Descripción |
|-----------|-------------|
| **bombas[]** | Lista de objetos `Pin` configurados como **salidas digitales** conectadas a las bombas CMYKW. |
| **flag_*_galga** | Variables booleanas (`True/False`) que representan el **estado de cada galga**. |
| **TOPICS** | Diccionario con los **topics MQTT** para cada color. |
| **mensaje()** | Función *callback* ejecutada al recibir un mensaje MQTT. Controla las bombas según el topic, comando y galga. |
| **conectar_mqtt()** | Función que **establece la conexión** con el broker y realiza la **suscripción a los topics**. |

## Mensajes MQTT Admitidos

| Topic | Mensaje | Acción |
|-------|----------|--------|
| `bombas/CYAN` | `"ON"` / `"OFF"` | Controla la bomba **Cyan** |
| `bombas/MAGENTA` | `"ON"` / `"OFF"` | Controla la bomba **Magenta** |
| `bombas/YELLOW` | `"ON"` / `"OFF"` | Controla la bomba **Amarilla** |
| `bombas/BLACK` | `"ON"` / `"OFF"` | Controla la bomba **Negra** |
| `bombas/WHITE` | `"ON"` / `"OFF"` | Controla la bomba **Blanca** |

## Lógica de Seguridad

Cada **galga actúa como un permiso físico**.  
Si una galga está desactivada (`False`), **la bomba no podrá encenderse**, incluso si se recibe el comando `"ON"`.  
Esto evita fallos eléctricos o activaciones indebidas, garantizando **un control seguro y estable**.

## Ventajas del Diseño

-  **Control remoto seguro** con validación física mediante galgas.  
-  **Separación clara** entre control lógico (galgas) y control remoto (MQTT).  
-  **Sistema modular y escalable**, fácil de ampliar a más bombas o sensores.  
-  **Compatible** con plataformas IoT educativas o industriales.  
- **Ejecución estable** y bajo consumo en ESP32.  

## Tecnologías Utilizadas

- **MicroPython**  
- **ESP32**  
- **MQTT (umqtt.robust)**  
- **Ngrok (Broker remoto)**  
- **Wi-Fi (módulo personalizado `wify.py`)**

## Estructura del Proyecto

Control_Bombas_CMYKW_MQTT/
│
├── main.py # Código principal de control de bombas
├── wify.py # Módulo de conexión Wi-Fi
├── README.md # Documentación del proyecto
└── requirements.txt # Dependencias (opcional)

## 🧪 Ejemplo de Uso

1. Iniciar el ESP32 con los archivos cargados (`main.py`, `wify.py`).  
2. Conectarse al Wi-Fi automáticamente.  
3. Conectarse al broker MQTT mediante Ngrok.  
4. Enviar comandos desde Node-RED o un cliente MQTT:

Topic: bombas/CYAN
Mensaje: ON 

Si la galga CYAN está activa, la bomba se encenderá.  
Enviar `"OFF"` para apagarla.


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

### 1. [Flujos](/G06/flujos/flows.json)

### 2. [Programación micropython](/G06/micropython/test.py)
