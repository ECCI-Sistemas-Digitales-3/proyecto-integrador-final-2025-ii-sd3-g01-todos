# Nombre de la etapa:

## Integrantes
- Heidy Nicol Sánchez Peña
- David Mora
- Federico Díaz Novoa

## Documentación

El objetivo del avance del proyecto es implementar un sistema de reconocimiento de colores mediante el sensor TCS34725 y el módulo ESP32, capaz de detectar automáticamente los colores dentro de la cabina de pintura y enviar los valores RGB a Raspberry Pi mediante comunicación MQTT.
La información es procesada y visualizada en Node-RED, permitiendo monitorear los colores captados por el sensor en tiempo real.

El avance busca fortalecer los conocimientos relacionados con el uso de sensores ópticos, microcontroladores y comunicación IoT (Internet de las Cosas) aplicados a procesos de automatización y control.
---

## Herramientas utilizadas  

- **Sensor TCS34725:** sensor óptico RGB + Clear con comunicación I2C, utilizado para la detección precisa de colores.  
- **ESP32:** microcontrolador encargado de realizar la lectura de los valores RGB del sensor y enviar los datos por WiFi.  
- **Raspberry Pi:** dispositivo que actúa como nodo receptor MQTT para recibir y visualizar los datos enviados por el ESP32.  
- **Node-RED:** entorno para la visualización y procesamiento de los valores captados por el sensor.  
- **Software:** uso de Python, Thonny IDE y MQTT Broker (Mosquitto) para la ejecución, conexión y transferencia de datos.  

---

## Configuración inicial del sensor TCS34725  

El sensor **TCS34725** se conecta al ESP32 mediante el protocolo de comunicación I2C, siguiendo la siguiente distribución de conexiones:  

- **VDD → 3.3V:** alimentación del sensor.  
- **SCL → GPIO 22:** línea de reloj del bus I2C.  
- **GND → GND:** referencia de tierra.  
- **NC:** pin sin conexión.  
- **INT:** pin de interrupción no utilizado.  
- **SDA → GPIO 21:** línea de datos del bus I2C.  

---

### ⚙️ Proceso de calibración del sensor

Para poder realizar la calibración del sensor:

1. Se colocó una superficie **blanca** frente al sensor, registrando los valores RGB como referencia máxima.  
2. Luego se colocó una superficie **negra**, registrando los valores mínimos.  
3. Finalmente, se usaron esos valores como límites para ajustar las lecturas y obtener una medición más precisa de cualquier color intermedio.

---

#### Figura 1. Distribución de pines del sensor TCS34725

<img width="600" alt="Distribución de pines del sensor TCS34725" src="https://github.com/user-attachments/assets/99e27d8b-741d-4262-a29c-fb898426a1cf" />

**Fuente:** [TCS34725 Datasheet – ams OSRAM](https://electronilab.co/wp-content/uploads/2021/06/TCS34725.pdf)

## Avances
### 1. [Flujos](/G03/flujos/flows.json)

### 2. [Programación micropython](/G03/micropython/test.py)


