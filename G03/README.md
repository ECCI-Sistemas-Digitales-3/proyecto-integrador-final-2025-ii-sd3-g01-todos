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
 
# Explicación del código del sistema de reconocimiento de color

Este programa permite que el **ESP32** lea los valores de color detectados por el **sensor TCS34725**, los convierta a una escala RGB de 0 a 255 y los envíe mediante **MQTT** hacia una **Raspberry Pi** para su visualización en **Node-RED**.  
A continuación se explica paso a paso cómo funciona.

---

## 1. Conexión WiFi

**WIFI_SSID = "TU_SSID"**
**WIFI_PASS = "TU_PASSWORD"**

El ESP32 se conecta a una red WiFi usando el nombre y la contraseña definidos aquí.  
Esto permite que más adelante pueda enviar los datos del sensor a través del protocolo MQTT hacia la Raspberry Pi.

---

## 2. Configuración MQTT

**BROKER = "192.168.153.216"**
**PORT = 1883**
**TOPIC = b"in/micro/sensor/color"**

- **BROKER:** es la dirección IP de la Raspberry Pi, donde está instalado Node-RED y el servidor MQTT.  
- **PORT:** es el puerto de comunicación (1883 es el estándar de MQTT).  
- **TOPIC:** es el canal por el cual el ESP32 envía los valores RGB que detecta el sensor.

En resumen, esta parte configura el medio de comunicación entre el ESP32 y Node-RED.

---

## 3. Configuración del sensor TCS34725

**i2c = I2C(1, scl=Pin(22), sda=Pin(21))**
**ADDR = 0x29**

El sensor TCS34725 se comunica mediante el bus **I2C**, usando los pines GPIO 21 (SDA) y GPIO 22 (SCL) del ESP32.  
La dirección **0x29** identifica al sensor dentro del bus I2C.

### Funciones principales:
- **write_reg():** escribe datos en un registro del sensor.  
- **read_reg16():** lee un valor de 16 bits desde un registro.  
- **init_tcs34725():** inicializa el sensor, lo enciende y configura el tiempo de integración y la ganancia.  
- **leer_rgbc():** obtiene los valores crudos de los cuatro canales del sensor: rojo, verde, azul y claro (intensidad de luz).

Esta parte prepara al sensor para empezar a tomar lecturas precisas de color.

---

## 4. Conversión a escala RGB (0–255)

**def convertir_255(r, g, b, coef):**

El sensor entrega valores altos (por ejemplo, entre 0 y 30000).  
Esta función los convierte al formato RGB estándar (de 0 a 255), usando los **valores máximos y mínimos obtenidos durante la calibración**.  
Así, el color detectado es más real y proporcional a la luz del entorno.

---

## 5. Conexión a WiFi

**def conectar_wifi():**

Activa el WiFi del ESP32 y lo conecta a la red configurada.  
Muestra por consola el proceso de conexión y la dirección IP obtenida.  
Esto es esencial para que luego el ESP32 pueda comunicarse con el broker MQTT.

---

## 6. Calibración del sensor

**def calibrar():**

Este proceso se hace una vez para obtener los límites de color:

1. Se coloca una superficie **blanca**, se leen los valores RGB y se guardan como máximos.  
2. Luego una superficie **negra**, para registrar los valores mínimos.  
3. Con estos datos se crea un archivo llamado **calib_rgb.json**, que guarda los coeficientes de calibración.

Gracias a esto, el sensor puede dar lecturas más precisas sin depender de la luz ambiente.

---

## 7. Programa principal

El flujo principal del programa hace lo siguiente:

1. Inicializa el sensor con init_tcs34725().  
2. Conecta el ESP32 al WiFi con conectar_wifi().  
3. Carga la calibración guardada (o realiza una nueva si no existe).  
4. Se conecta al **broker MQTT**.  
5. Entra en un bucle infinito donde:
   - Lee los valores de color del sensor.  
   - Los convierte a escala 0–255.  
   - Crea un mensaje en formato JSON, por ejemplo:
     {"R": 120, "G": 85, "B": 60}
   - Envía ese mensaje al **topic MQTT** para que Node-RED lo reciba y visualice.

El envío se realiza cada medio segundo.

---

## 8. Flujo completo del sistema

Sensor TCS34725 → ESP32 (lectura I2C)
→ WiFi → MQTT (broker en Raspberry Pi)
→ Node-RED → Visualización de color en tiempo real

---

## Avances  

### 1. [Flujos](/G03/flujos/flows.json)  

### 2. [Programación Micropython](/G03/micropython/test.py)  
</div>