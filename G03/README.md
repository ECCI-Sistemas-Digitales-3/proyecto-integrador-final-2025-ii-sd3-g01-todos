# Nombre de la etapa:

## Integrantes
- Heidy Nicol Sánchez Peña
- David Mora
- Federico Díaz Novoa

## Documentación

### Objetivo  
El objetivo del avance del proyecto es implementar un sistema de **reconocimiento de colores** mediante el **sensor TCS34725** y un **módulo ESP32**, capaz de detectar automáticamente los colores dentro de una **cabina de pintura** y enviar los valores RGB a una **Raspberry Pi** mediante comunicación **MQTT**.  
Esta información será procesada y visualizada en **Node-RED**, permitiendo monitorear los colores captados por el sensor en tiempo real.  

Este avance busca fortalecer los conocimientos en el uso de **sensores ópticos**, **microcontroladores** y **comunicación IoT (Internet de las Cosas)** aplicados a procesos de **automatización y control**.  

---

### Herramientas  

| Elemento | Descripción |
|-----------|-------------|
| **Sensor TCS34725** | Sensor óptico RGB + Clear con comunicación I2C. |
| **ESP32** | Microcontrolador encargado de la lectura del sensor y envío de datos por WiFi. |
| **Raspberry Pi** | Nodo receptor MQTT que recibe y visualiza los datos. |
| **Fuente 5V** | Alimentación del ESP32 y el sensor. |
| **Cables Dupont** | Conexión entre el ESP32 y el sensor TCS34725. |
| **Node-RED** | Interfaz de visualización y procesamiento de los datos recibidos. |
| **Software** | Python, Thonny IDE, MQTT Broker (Mosquitto). |

---

### Configuración inicial del sensor TCS34725  

El sensor **TCS34725** se conecta al **ESP32** utilizando el protocolo de comunicación **I2C**, empleando los siguientes pines:  

| Pin Sensor | Nombre | Conexión ESP32 |
|-------------|---------|----------------|
| 1 | VDD | 3.3 V |
| 2 | SCL | GPIO 22 |
| 3 | GND | GND |
| 4 | NC | No conectado |
| 5 | INT | No conectado |
| 6 | SDA | GPIO 21 |

### 1. [Flujos](/G03/flujos/flows.json)

### 2. [Programación micropython](/G03/micropython/test.py)


