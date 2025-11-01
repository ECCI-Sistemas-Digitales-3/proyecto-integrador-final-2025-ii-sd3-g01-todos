

# DOCUMENTACIÓN DEL AVANCE DEL PROYECTO INTEGRADOR
## Integrantes


## Objetivo
El objetivo del avance del proyecto es configurar una Raspberry Pi como nodo publicador MQTT, capaz de capturar imágenes en tiempo real mediante una cámara (CSI o USB) y transmitirlas mediante el protocolo MQTT hacia un cliente Node-RED, donde se visualizarán y podrán procesarse para tareas de monitoreo, análisis o automatización.

Esta integración combina tecnologías de IoT (Internet of Things), procesamiento de imágenes y mensajería ligera, fortaleciendo la comprensión práctica de los conceptos de comunicación entre dispositivos inteligentes.

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
1. Conectar la Raspberry Pi a la fuente de alimentación y a la red (WiFi o cable Ethernet).

2. Acceder al sistema operativo desde un terminal local o mediante SSH desde otro equipo:
```
ssh pi@192.168.7.217 (Esta direccion IP varia)
```
Ingresar la contraseña correspondiente al usuario pi o la establecida previamente.


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

1. Abrir el panel de configuración de la Raspberry Pi:
```
sudo raspi-config
```
2. Habilitar también el acceso remoto SSH (si aún no está activo):
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

Una vez actualizado el sistema, se procede a instalar las herramientas básicas, las utilidades para la cámara.
Los siguientes comandos deben ejecutarse en orden:
```
sudo apt update
sudo apt install imagemagick -y
sudo apt install python3-pip -y
```
**Descripción de cada instalación:**

imagemagick: Permite manipular imágenes (redimensionar, convertir formato, etc.).

python3-pip: Instala el gestor de paquetes Python, necesario para las siguientes librerías.

## Verificación del broker MQTT
Nos conectamos al laboratorio de mosquito, 
enlace:

[Instalación Mosquitto](https://github.com/ECCI-Sistemas-Digitales-3/lab05-mqtt-2025-ii-sd3-g04)


## Flujo práctico de comunicacion 
En la siguiente imagen se observan los principales componentes del montaje: la cámara, la Raspberry Pi 3, el entorno Node-RED y el módulo ESP32.

![Texto alternativo](./Img/1.png)

## Conclusiones
Este documento presenta un adelanto del proyecto de integración de cámara y Raspberry Pi mediante Node-RED, donde se comprobó la comunicación entre el hardware y la plataforma de automatización. Se logró habilitar la cámara y ejecutar el comando rpicam-vid -t 0 -o video.h264 desde un fluj, demostrando la capacidad del sistema para capturar video de forma remota. Este avance sienta las bases para futuras etapas orientadas a la transmisión y procesamiento de imágenes en proyectos de monitoreo y análisis para captar colores en la mezcladora.