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

Control_Bombas_CMYKW_MQTT

─ main.py # Código principal de control de bombas
─ wify.py # Módulo de conexión Wi-Fi
─ README.md # Documentación del proyecto
─ requirements.txt # Dependencias (opcional)

## Ejemplo de Uso

1. Iniciar el ESP32 con los archivos cargados (`main.py`, `wify.py`).  
2. Conectarse al Wi-Fi automáticamente.  
3. Conectarse al broker MQTT mediante Ngrok.  
4. Enviar comandos desde Node-RED o un cliente MQTT:

Topic: bombas/CYAN
Mensaje: ON 

Si la galga CYAN está activa, la bomba se encenderá.  
Enviar `"OFF"` para apagarla.


### 1. [Flujos](/G06/flujos/flows.json)

### 2. [Programación micropython](/G06/micropython/test.py)

# ============================================================
#  Proyecto: Control de Bombas CMYKW mediante MQTT y Galgas
#  Plataforma: ESP32 con MicroPython
#  Descripción: Este programa permite controlar cinco bombas peristálticas correspondientes a los colores CMYKW (Cyan, Magenta, Yellow, Black y White) mediante el protocolo MQTT. Cada bomba cuenta con una galga que actúa como interruptor de seguridad, habilitando o bloqueando su funcionamiento según condiciones físicas.
# ============================================================

# -------------------- IMPORTACIÓN DE LIBRERÍAS --------------------

import network            # Módulo para conexión Wi-Fi
import time               # Permite pausas o temporización
from machine import Pin   # Control de pines digitales del ESP32
from umqtt.robust import MQTTClient  # Cliente MQTT robusto
import ujson              # Para manejo de datos en formato JSON
import wify               # Módulo personalizado para conexión Wi-Fi

# -------------------- CONFIGURACIÓN DEL BROKER MQTT --------------------

BROKER = "6.tcp.ngrok.io"   # Dirección del broker MQTT (ngrok en este caso)
PORT = 18263                # Puerto TCP asignado al túnel MQTT

# -------------------- DEFINICIÓN DE TOPICS MQTT --------------------
# Cada bomba tiene su propio canal MQTT para recibir órdenes ON/OFF

TOPICS = {
    "CYAN": b"bombas/CYAN",
    "MAGENTA": b"bombas/MAGENTA",
    "YELLOW": b"bombas/YELLOW",
    "BLACK": b"bombas/BLACK",
    "WHITE": b"bombas/WHITE"
}

# -------------------- CONFIGURACIÓN DE PINES --------------------
# Cada bomba está conectada a un pin de salida del ESP32
# Cada galga (sensor o interruptor) está en un pin de entrada

bombas = {
    "CYAN": Pin(12, Pin.OUT),
    "MAGENTA": Pin(13, Pin.OUT),
    "YELLOW": Pin(14, Pin.OUT),
    "BLACK": Pin(27, Pin.OUT),
    "WHITE": Pin(26, Pin.OUT)
}

galgas = {
    "CYAN": Pin(32, Pin.IN),
    "MAGENTA": Pin(33, Pin.IN),
    "YELLOW": Pin(25, Pin.IN),
    "BLACK": Pin(15, Pin.IN),
    "WHITE": Pin(4, Pin.IN)
}

# -------------------- CONEXIÓN A LA RED WI-FI --------------------
# Se usa el módulo personalizado wify.py que contiene una función
# de conexión automática. Esta función se encarga de conectar el
# ESP32 a la red Wi-Fi configurada en ese archivo.

print("Conectando a Wi-Fi...")
wify.connect()             # Llama a la función de conexión del módulo externo
print("Wi-Fi conectada correctamente\n")

# -------------------- FUNCIÓN CALLBACK DE MENSAJES MQTT --------------------
# Esta función se ejecuta automáticamente cada vez que llega un mensaje MQTT.
# Recibe como parámetros el topic (canal) y el mensaje (ON/OFF).
# Su función es determinar qué bomba debe encenderse o apagarse según:
#  1. El topic del mensaje.
#  2. El estado lógico de la galga asociada.

def mensaje(topic, msg):
    try:
        # Decodifica los valores recibidos de bytes a texto
        topic_str = topic.decode()
        msg_str = msg.decode()
        print(f"Mensaje recibido -> Topic: {topic_str} | Mensaje: {msg_str}")

        # Recorre todos los colores definidos en el diccionario de TOPICS
        for color, topico in TOPICS.items():
            # Si el topic recibido corresponde a uno de los definidos
            if topic == topico:
                estado_galga = galgas[color].value()  # Lee el estado de la galga (1 o 0)
                
                # Condición lógica de seguridad:
                # Solo enciende la bomba si el comando es "ON" y la galga está activa (1)
                if msg_str == "ON" and estado_galga == 1:
                    bombas[color].on()   # Activa la bomba
                    print(f"Bomba {color} ENCENDIDA (galga activa)")
                else:
                    bombas[color].off()  # Apaga la bomba
                    print(f"Bomba {color} APAGADA (comando OFF o galga inactiva)")
                    
    except Exception as e:
        # Si ocurre un error (por ejemplo, topic no válido), se muestra en consola
        print(f"Error procesando mensaje MQTT: {e}")

# -------------------- FUNCIÓN PARA CONECTAR AL BROKER MQTT --------------------
# Esta función establece la conexión con el broker MQTT y realiza la suscripción
# a los topics definidos en el diccionario TOPICS.

def conectar_mqtt():
    try:
        print("Conectando al broker MQTT...")
        # Se crea un objeto cliente MQTT con un ID de cliente único
        cliente = MQTTClient("ESP32_CMKW", BROKER, PORT)
        cliente.set_callback(mensaje)  # Asigna la función callback a los mensajes entrantes
        cliente.connect()              # Intenta establecer conexión con el broker
        print("Conexión MQTT establecida correctamente.\n")

        # Se suscribe a todos los topics definidos
        for color, topic in TOPICS.items():
            cliente.subscribe(topic)
            print(f"Suscrito al topic: {topic.decode()}")
        
        return cliente  # Devuelve el objeto cliente para usarlo en el bucle principal

    except Exception as e:
        print(f"Error conectando al broker MQTT: {e}")
        return None  # En caso de fallo, retorna None

# -------------------- PROGRAMA PRINCIPAL --------------------

cliente = conectar_mqtt()  # Llama a la función de conexión

if cliente:
    print("Esperando mensajes MQTT...\n")
    while True:
        try:
            # Verifica si hay nuevos mensajes MQTT disponibles
            cliente.check_msg()
            # Pequeña pausa para evitar saturar el CPU
            time.sleep(0.1)

        except Exception as e:
            # Si se pierde la conexión, intenta reconectarse automáticamente
            print(f"Error en la conexión MQTT: {e}")
            time.sleep(3)
            cliente = conectar_mqtt()
else:
    print("No fue posible establecer conexión MQTT. Reinicie el dispositivo.")
