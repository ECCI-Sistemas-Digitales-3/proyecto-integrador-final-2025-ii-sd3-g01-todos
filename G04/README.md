
# DOCUMENTACIÓN DEL AVANCE DEL PROYECTO INTEGRADOR
## Integrantes

[Jesus Zuluaga]()
[Kevin Vivas]()
[Sebastian Bonza]()

## Objetivo
El objetivo de este avance del proyecto es configurar una Raspberry Pi como nodo publicador MQTT, capaz de capturar imágenes en tiempo real mediante una cámara (CSI o USB) para realizar la lectura y análisis de los colores generados por una mezcladora de pinturas.

Las imágenes capturadas se transmitirán mediante el protocolo MQTT hacia un cliente Node-RED, donde serán visualizadas y procesadas para identificar tonalidades, realizar comparaciones y facilitar tareas de monitoreo y control automatizado del proceso de mezcla.

Este desarrollo integra tecnologías de IoT (Internet of Things), procesamiento de imágenes y mensajería ligera, fortaleciendo la comprensión práctica de la comunicación entre dispositivos inteligentes y su aplicación en sistemas de control y análisis de color.


## Herramientas

| Elemento                        | Descripción                                           |
|----------------------------------|-------------------------------------------------------|
| Raspberry Pi 3                       | Nodo principal y publicador MQTT.                    |
| Cámara REv 1.3                   | Captura de imágenes.                                 |
| Fuente 5V / 3A                   | Alimentación estable de la Raspberry Pi 3.             |
| MicroSD                         | Almacenamiento del sistema operativo.                |
| Conexión WiFi o Ethernet         | Comunicación con el servidor MQTT y Node-RED.        |
| PC con Node-RED                  | Cliente suscriptor y visualizador de datos.          |
| Software                       | Raspbian OS, Mosquitto, Python3 y Node-RED.          |


## Configuración inicial de la Raspberry Pi
1. Conectar la Raspberry Pi 3 a la fuente de alimentación y establecer la conexión a la red, ya sea mediante WiFi o cable Ethernet.

2. Acceder al sistema operativo desde un terminal local o de forma remota mediante SSH desde otro equipo utilizando el siguiente comando:
```
ssh pi@192.168.7.217 (Esta direccion IP varia)
```
Ingresar la contraseña del usuario “pi” o la que se haya configurado previamente.


## Actualización del sistema
Antes de comenzar la instalación, es recomendable realizar una limpieza y actualización completa del sistema operativo para garantizar estabilidad y evitar conflictos de dependencias:
```
sudo apt clean
sudo apt autoremove -y
sudo apt update -y
sudo apt upgrade -y
```
Este procedimiento mantiene los repositorios actualizados, elimina paquetes innecesarios y prepara el sistema para las siguientes instalaciones.

## Habilitación de la cámara

1. Abrir el panel de configuración de la Raspberry Pi ejecutando el siguiente comando:
```
sudo raspi-config
```
2. En el menú de configuración, dirigirse a Interface Options → Camera → Enable para habilitar la cámara integrada.

**Interface Options → SSH → Enable**

3. Guardar los cambios y reiniciar la Raspberry Pi para aplicar la configuración:
```
sudo reboot
```
4. Verificar funcionamiento de la cámara:
```
mkdir -p ~/camara
libcamera-hello
libcamera-jpeg -o ~/camara/test.jpg
ls -l ~/camara/test.jpg
```
Si se genera el archivo test.jpg, la cámara está operativa.

![Texto alternativo](./Img/3.png)

La imagen presenta un flujo en Node-RED donde el nodo de cámara Raspberry Pi envía los datos capturados hacia una plantilla HTML, la cual los transmite a una función denominada Procesar_color. Esta función analiza la información y envía los resultados a diversos nodos de salida, incluyendo nodos de depuración, un módulo ESP32 conectado al microcontrolador y un selector de color (colour picker). El flujo evidencia la integración entre la captura de imágenes, el procesamiento de datos y la comunicación con dispositivos IoT dentro del entorno Node-RED.

![Texto alternativo](./Img/2.png)


## Instalación de dependencias necesarias

Una vez actualizado el sistema, se procede a instalar las dependencias esenciales para garantizar el correcto funcionamiento de la cámara y las herramientas de procesamiento de imágenes.
Ejecutar los siguientes comandos en el orden indicado:
```
sudo apt update
sudo apt install imagemagick -y
sudo apt install python3-pip -y
```
**Descripción de cada instalación:**

**ImageMagick:** Utilidad de línea de comandos que permite manipular y procesar imágenes (por ejemplo, redimensionar, recortar, convertir formatos o ajustar parámetros visuales).

**Python3-pip:** Gestor de paquetes de Python que facilita la instalación de librerías adicionales, necesarias para el desarrollo y comunicación entre la Raspberry Pi y el entorno Node-RED.

Estas herramientas son fundamentales para habilitar el procesamiento local de imágenes capturadas y permitir la integración fluida con los módulos de análisis y envío de datos mediante el protocolo MQTT.

## Verificación del broker MQTT
Para comprobar la correcta comunicación entre la Raspberry Pi (publicador) y el cliente Node-RED (suscriptor), se realizó una prueba de conexión al broker MQTT.
Esta verificación permite confirmar que los mensajes pueden transmitirse y recibirse correctamente a través del protocolo MQTT, garantizando la funcionalidad del sistema IoT, disponible en el siguiente enlace:

[Instalación Mosquitto](https://github.com/ECCI-Sistemas-Digitales-3/lab05-mqtt-2025-ii-sd3-g04)


## Flujo práctico de comunicacion 
En la siguiente imagen se muestran los componentes principales del montaje experimental, conformado por la cámara, la Raspberry Pi 3, el entorno de desarrollo Node-RED y el módulo ESP32.
Este conjunto representa la arquitectura funcional del sistema IoT, donde la Raspberry Pi desempeña el rol de nodo publicador, encargado de capturar y enviar los datos obtenidos por la cámara, mientras que el ESP32 y Node-RED se encargan del procesamiento, visualización y control de la información transmitida a través del protocolo MQTT.

![Texto alternativo](./Img/1.png)

## Flujo de operación del sistema de mezcla automatizada de pintura

El diagrama representa la secuencia de operaciones del sistema desarrollado para la detección y mezcla automática de colores. El proceso inicia con la captura de una imagen mediante la Raspberry Pi y su cámara, a partir de la cual el usuario selecciona un punto para obtener el valor RGB del color objetivo. Con esta información, el sistema calcula las proporciones necesarias de cada color base (C, M, Y, K, W).

A continuación, se verifican las condiciones de operación: la disponibilidad de pintura en los recipientes y la temperatura adecuada (entre 25 °C y 27 °C). Si ambas son correctas, el sistema activa las bombas para dosificar las pinturas según las proporciones calculadas y enciende el rodillo mezclador para lograr una mezcla homogénea. Finalmente, el color resultante se compara con el color objetivo; si coincide, el proceso finaliza, y si no, se calcula el error para ajustar la mezcla.

![Texto alternativo](./Img/Diagrama_flujo.png)

## Conclusiones
Durante esta etapa se logró la integración funcional entre la cámara y la Raspberry Pi a través de Node-RED, verificando la comunicación entre el hardware y la plataforma de automatización. Se consiguió habilitar la cámara y ejecutar el comando rpicam-vid -t 0 -o video.h264 desde un flujo, confirmando la capacidad del sistema para capturar video de manera remota. Estos resultados representan un avance importante dentro del proyecto, que permitirá en futuras fases implementar la transmisión en tiempo real y el procesamiento de imágenes para la detección de colores en la mezcladora