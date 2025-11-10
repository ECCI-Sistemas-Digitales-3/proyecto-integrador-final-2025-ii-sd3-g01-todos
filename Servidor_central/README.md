## Servidor Central - Sistema de Captura y Comunicación MQTT con Raspberry Pi


### 1. RESUMEN

Este documento detalla la implementación del servidor central del proyecto de captura de imágenes y comunicación IoT basado en Raspberry Pi, Node-RED y MQTT. El servidor actúa como nodo principal encargado de la gestión de datos, publicación de imágenes, y coordinación con dispositivos clientes (ESP32, otros nodos MQTT, etc.).
Se describe detalladamente la instalación de servicios, configuración de Ngrok para accesos externos, resolución de errores, y pruebas de funcionamiento.

### 2. INTRODUCCIÓN
El servidor central se diseñó para concentrar la comunicación entre los diferentes dispositivos del sistema de monitoreo. Opera bajo una arquitectura cliente-servidor, donde la Raspberry Pi ejecuta los servicios MQTT y Node-RED, además de servir como pasarela a Internet mediante Ngrok.

El objetivo principal es establecer un entorno robusto, accesible desde redes externas, y compatible con dispositivos que envíen o reciban información mediante tópicos MQTT.
### Componentes utilizados
•	Hardware: Raspberry Pi 3 B+ (o superior), microSD ≥ 16GB, cámara CSI.

•	Software: Raspberry Pi OS (Bookworm), Node-RED, Mosquitto, Python3, Ngrok.

•	Protocolos: MQTT para mensajería ligera, HTTP/HTTPS para acceso remoto a Node-RED.

### 3. METODOLOGÍA
### 3.1 Preparación del entorno
1.	Actualizar el sistema operativo:

 	```sudo apt update && sudo apt upgrade -y```
2.	Instalar Mosquitto y sus clientes:

 	    sudo apt install mosquitto mosquitto-clients -y
        sudo systemctl enable mosquitto
        sudo systemctl start mosquitto

 	Verificación:

 	```sudo systemctl status mosquitto```
 	El servicio debe mostrarse como active (running).
3.	Instalar Node-RED: 

 	```<(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)```

 	Luego:

 	```node-red-start```

 	Acceso desde navegador local:

 	```http://localhost:1880```

 	Para que Node-RED arranque automáticamente con el sistema:
 	```sudo systemctl enable nodered.service```

4.	Instalar Python y dependencias:

 	```sudo apt install python3-pip imagemagick -y```

    ```pip install paho-mqtt --break-system-packages```

5.	Verificar la cámara (opcional):

 	libcamera-hello
 	Si no responde, usar Raspberry Pi OS Bookworm o superior, donde la cámara ya está habilitada por defecto.

### 3.2 Configuración del broker MQTT

El broker Mosquitto es el núcleo de la comunicación MQTT.

1.	Probar la comunicación local:

 	```mosquitto_sub -t prueba & mosquitto_pub -t prueba -m "Hola MQTT"```

 	Si el mensaje aparece en la terminal del mosquitto_sub, la comunicación está operativa.

2.	Permitir conexiones externas:

    Editar el archivo de configuración: ```sudo nano /etc/mosquitto/mosquitto.conf```

    Agregar al final:

    listener 1883
    allow_anonymous true

    Reiniciar el servicio: ```sudo systemctl restart mosquitto```

3.	Errores frecuentes:

* Conexión rechazada: verificar que el puerto 1883 esté libre (sudo netstat -tulnp | grep 1883).
* Sin respuesta MQTT: revisar firewall o router local.

### 3.3 Instalación y configuración de Ngrok
Ngrok se utiliza para exponer servicios locales (Node-RED y MQTT) a Internet de forma segura.
1.	Descargar e instalar Ngrok:
 	