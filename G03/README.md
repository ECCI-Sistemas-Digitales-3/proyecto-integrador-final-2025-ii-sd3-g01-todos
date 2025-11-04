# Nombre de la etapa
<div align="justify">
## Integrantes  
- Heidy Nicol Sánchez Peña  
- David Mora  
- Federico Díaz Novoa  

---

## Documentación  

El objetivo de este avance es implementar un sistema de reconocimiento de colores usando el sensor TCS34725 y el módulo ESP32. El sistema detecta los colores dentro de la cabina de pintura y envía los valores RGB a la Raspberry Pi mediante comunicación MQTT.  
Toda la información se procesa y se muestra en Node-RED, lo que permite ver en tiempo real los colores captados por el sensor.  

Este avance busca lograr una lectura rápida y precisa de los colores, garantizando que la integración con el resto del sistema funcione correctamente y cumpla con el propósito general del proyecto.  

---

## Herramientas utilizadas  

- **Sensor TCS34725:** detecta los componentes de color rojo, verde y azul (RGB) con alta precisión usando comunicación I2C.  
- **ESP32:** se encarga de leer los datos del sensor y enviarlos por WiFi.  
- **Raspberry Pi:** recibe los datos enviados por el ESP32 a través de MQTT y los muestra en Node-RED.  
- **Node-RED:** permite visualizar los valores RGB de forma ordenada y monitorear los resultados en tiempo real.  

---

## Configuración del sensor TCS34725  

Antes de usarlo, fue necesario entender cómo trabaja este sensor y cómo se comunica con el ESP32.  

### Funcionamiento del sensor TCS34725  

El TCS34725 detecta el color de la luz que refleja un objeto. Mide la intensidad del rojo, verde y azul (RGB) y también calcula un valor adicional llamado Clear, que representa la cantidad total de luz.  
Tiene un filtro infrarrojo que bloquea la luz no visible para hacer las mediciones más precisas, y un conversor interno que convierte esas señales de luz en datos digitales que el ESP32 puede leer fácilmente mediante I2C, usando los pines SDA y SCL.  

Cuenta con cuatro LEDs blancos que iluminan el objeto mientras se mide, lo que evita depender de la luz ambiental y mejora la estabilidad de las lecturas.  
Además, permite ajustar la ganancia y el tiempo de integración desde el software, lo que ayuda a adaptarse a diferentes niveles de iluminación.  

También dispone de un pin de interrupción que puede configurarse para ejecutar acciones automáticas si se detecta un color fuera de un rango específico.  
En general, es un sensor muy versátil y confiable, ampliamente usado en robótica, control de iluminación y sistemas IoT que requieren un reconocimiento de color rápido y preciso.  

El sensor se conectó al ESP32 mediante el protocolo I2C con la siguiente distribución de pines:

- **VDD → 3.3V:** alimentación del sensor  
- **SCL → GPIO 22:** línea de reloj  
- **GND → GND:** referencia de tierra  
- **NC:** sin conexión  
- **INT:** no se utilizó  
- **SDA → GPIO 21:** línea de datos  

---

### ⚙️ Proceso de calibración del sensor  

Para calibrar el sensor se realizaron tres pasos sencillos:  

1. Se colocó una superficie **blanca** frente al sensor para registrar los valores RGB más altos.  
2. Luego, se midió una superficie **negra** para obtener los valores más bajos.  
3. Con esos límites, se ajustaron las lecturas para lograr una medición más precisa de cualquier color intermedio.  

---

### 🔧 Características técnicas  

- Voltaje de entrada: 3.0 V a 5.0 V  
- Corriente de entrada: hasta 20 mA  
- Chip base: TCS3472  
- Interfaz de comunicación: I2C (SDA y SCL)  
- Filtro IR integrado para mejorar la precisión  

---

### 📷 Aplicaciones  

- Detección y reconocimiento de color  
- Control automático de iluminación RGB  
- Clasificación de objetos por color  
- Sensado ambiental o ajuste de balance de blancos en cámaras  

---

#### Figura 1. Distribución de pines del sensor TCS34725  

<img width="600" alt="Distribución de pines del sensor TCS34725" src="https://github.com/user-attachments/assets/99e27d8b-741d-4262-a29c-fb898426a1cf" />  

**Fuente:** [TCS34725 Datasheet – ams OSRAM](https://electronilab.co/wp-content/uploads/2021/06/TCS34725.pdf)  

---

## Avances  

### 1. [Flujos](/G03/flujos/flows.json)  

### 2. [Programación Micropython](/G03/micropython/test.py)  
</div>