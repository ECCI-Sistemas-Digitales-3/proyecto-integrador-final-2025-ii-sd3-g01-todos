# Nombre de la etapa:

## Integrantes
- Heidy Nicol Sánchez Peña
- David Mora
- Federico Díaz Novoa

## Documentación

El objetivo del avance del proyecto es implementar un sistema de reconocimiento de colores mediante el sensor TCS34725 y el módulo ESP32, capaz de detectar automáticamente los colores dentro de la cabina de pintura y enviar los valores RGB a Raspberry Pi mediante comunicación MQTT.
La información es procesada y visualizada en Node-RED, permitiendo monitorear los colores captados por el sensor en tiempo real.

Este avance busca establecer un reconocimiento de colores preciso y rápido, garantizando una integración adecuada dentro del sistema general del proyecto y contribuyendo al cumplimiento del objetivo final.
---

## Herramientas utilizadas  

- **Sensor TCS34725:** sensor óptico RGB + Clear con comunicación I2C, utilizado para la detección precisa de colores.  
- **ESP32:** microcontrolador encargado de realizar la lectura de los valores RGB del sensor y enviar los datos por WiFi.  
- **Raspberry Pi:** dispositivo que actúa como nodo receptor MQTT para recibir y visualizar los datos enviados por el ESP32.  
- **Node-RED:** entorno para la visualización y procesamiento de los valores captados por el sensor.  

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
### 🔧 Características técnicas
- **Voltaje de entrada:** 3.0 V a 5.0 V  
- **Corriente de entrada:** hasta 20 mA  
- **Chip base:** TCS3472   
- **Interfaz de comunicación:** I2C (SDA y SCL)  
- **Filtro IR:** integrado, mejora la precisión del color  

---

### 📷 Aplicaciones
- Detección y reconocimiento de color  
- Control automático de iluminación RGB  
- Clasificación de objetos por color  
- Sensado ambiental o corrección de balance de blancos en cámaras  


#### Figura 1. Distribución de pines del sensor TCS34725

<img width="600" alt="Distribución de pines del sensor TCS34725" src="https://github.com/user-attachments/assets/99e27d8b-741d-4262-a29c-fb898426a1cf" />

**Fuente:** [TCS34725 Datasheet – ams OSRAM](https://electronilab.co/wp-content/uploads/2021/06/TCS34725.pdf)

### Funcionamiento del Sensor TCS34725  

El sensor **TCS34725** es un dispositivo digital de detección de color que permite identificar la intensidad de los componentes rojo, verde y azul (RGB) presentes en la luz reflejada por un objeto. Integra un **filtro infrarrojo (IR)** que elimina interferencias no visibles, garantizando mediciones más precisas.  

El módulo incorpora un **convertidor analógico-digital (ADC)** que transforma las señales ópticas en valores digitales, los cuales se comunican con el microcontrolador mediante el protocolo **I2C**, utilizando solo las líneas SDA y SCL.  

Para mejorar la detección, dispone de **cuatro LEDs blancos** que proporcionan iluminación constante sobre la superficie medida, lo que permite trabajar sin depender de fuentes de luz externas.  

El sensor mide simultáneamente los valores de los tres colores primarios (**R**, **G** y **B**) y un canal adicional denominado **Clear**, que representa la intensidad total de luz. Con estos datos, el sistema puede determinar el color predominante en tiempo real.  

Su funcionamiento es estable tanto con **3.3 V** como con **5 V**, gracias a su regulador de voltaje integrado. Además, permite ajustar la **ganancia y el tiempo de integración** por software, adaptándose a diferentes niveles de iluminación.  

El **TCS34725** también incluye un **pin de interrupción configurable**, útil para activar acciones automáticas cuando los valores de color superan un umbral determinado.  

Este sensor es ampliamente utilizado en **sistemas de clasificación, control de iluminación, robótica e IoT**, donde se requiere un reconocimiento de color confiable y rápido.  

## Avances
### 1. [Flujos](/G03/flujos/flows.json)

### 2. [Programación micropython](/G03/micropython/test.py)


