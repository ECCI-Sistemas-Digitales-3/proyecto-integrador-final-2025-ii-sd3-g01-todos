[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=21147975&assignment_repo_type=AssignmentRepo)
# Proyecto integrador 1ra Entrega

## Integrantes

[Karen Lizeth Sosa](https://github.com/karenlsosam-hub)

[Michael Mendez](https://github.com/michaelsmendezm-collab)

[Juan Acosta](https://github.com/juanfacostap-wq)


## Arquitectura propuesta

En el caso del Grupo 10, corresponde el desarrollo e implementación de los periféricos asociados a los sensores de peso para cada tanque de pintura, utilizando para este propósito el módulo HX711 en conjunto con una galga extensiométrica.

El sistema permite realizar la medición de peso mediante celdas de carga, empleando el HX711 como amplificador y convertidor analógico-digital (ADC), el cual entrega la señal procesada hacia el microcontrolador ESP32 para su posterior lectura y transmisión de datos.

Se adjunta el documento en formato PDF, donde se presenta el diseño del sistema, el esquema de conexiones eléctricas y la configuración de los periféricos utilizados para la correcta integración del sensor de peso con el entorno de control.

ver pfd (PLANO_GALGA _GRUPO_10)


Se implementaron los programas destinados a la adquisición y visualización de los datos generados por la galga extensiométrica, empleando el entorno de desarrollo Thonny,  el lenguaje MicroPython para la programación del microcontrolador.

![alt text](image.png)


A continuación, se diseñaron los esquemas de comunicación en Node-RED y se realizó la configuración del tópico MQTT, permitiendo la visualización en tiempo real de las lecturas de la galga extensiométrica dentro del entorno de monitoreo de Node-RED.


![alt text](image-1.png)


![alt text](image-2.png)



## Periférico a trabajar



# ===== CONFIGURACIÓN HX711 =====


Pines de conexion HX711 y la esp32

VCC

GND

DT_PIN = 4    # Pin de datos DT del HX711 pin 4 de la esp32

SCK_PIN = 16   # Pin de reloj SCK del HX711 pin 16 de la esp32

![alt text](image-4.png)







GALGA:

VCC:E+

GND:E-

SEÑAL+:A+

SEÑAL-: A-

![alt text](image-3.png)

## Avances

En este apartado se presenta la evidencia fotográfica del montaje realizado por parte de nuestro equipo, correspondiente al sistema instalado.

![alt text](image-5.png)

![alt text](image-6.png)

![alt text](image-7.png)

### 1. [Flujos](/G10/flujos/flows.json)

### 2. [Programación micropython](/G10/micropython/test.py)

