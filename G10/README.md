[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=21147975&assignment_repo_type=AssignmentRepo)
# Proyecto integrador avance 1/11/2025

## Integrantes

[Karen Lizeth Sosa](https://github.com/karenlsosam-hub)

[Michael Mendez](https://github.com/michaelsmendezm-collab)

[Juan Acosta](https://github.com/juanfacostap-wq)

## Objetivo

Implementar un sistema de lectura de peso mediante galgas extensiométricas conectadas a sus respectivos módulos HX711, los cuales entregan los valores digitales a una ESP32. De esta manera, se integra un sistema que combina la información obtenida por la cámara —encargada de sensar el color inicial— con los valores digitales de peso, con el fin de codificar dichos valores en el modelo de color CMYK y obtener así el color deseado en el recipiente final de pintura.



## Arquitectura propuesta

En el caso del Grupo 10, corresponde el desarrollo e implementación de los periféricos asociados a los sensores de peso para cada tanque de pintura, utilizando para este propósito el módulo HX711 en conjunto con una galga extensiométrica.

El sistema permite realizar la medición de peso mediante celdas de carga, empleando el HX711 como amplificador y convertidor analógico-digital (ADC), el cual entrega la señal procesada hacia el microcontrolador ESP32 para su posterior lectura y transmisión de datos.

Se adjunta el documento en formato PDF, donde se presenta el diseño del sistema, el esquema de conexiones eléctricas y la configuración de los periféricos utilizados para la correcta integración del sensor de peso con el entorno de control.

ver pfd (PLANO_GALGA_ACTUALIZADO)


Se implementaron los programas destinados a la adquisición y visualización de los datos generados por la galga extensiométrica, empleando el entorno de desarrollo Thonny,  el lenguaje MicroPython para la programación del microcontrolador.

![alt text](image.png)


A continuación, se diseñaron los esquemas de comunicación en Node-RED y se realizó la configuración del tópico MQTT, permitiendo la visualización en tiempo real de las lecturas de la galga extensiométrica dentro del entorno de monitoreo de Node-RED.


![alt text](image-1.png)


![alt text](image-2.png)



## Periférico a trabajar



# ===== CONFIGURACIÓN HX711 =====


Pines de conexion HX711 y la esp32

VCC= FUENTE +5V

GND=GND DE LA FUENTE

GALGA 1

DT_PIN = 13    # Pin de datos DT del HX711 pin GPIO 13 de la esp32

SCK_PIN = 12   # Pin de reloj SCK del HX711 pin GPIO 12 de la esp32

GALGA 2

DT_PIN = 16   # Pin de datos DT del HX711 pin GPIO 16 de la esp32

SCK_PIN = 17   # Pin de reloj SCK del HX711 pin GPIO 17 de la esp32

GALGA 3

DT_PIN = 5   # Pin de datos DT del HX711 pin GPIO 5 de la esp32

SCK_PIN = 18   # Pin de reloj SCK del HX711 pin GPIO 18 de la esp32

GALGA 4

DT_PIN = 19   # Pin de datos DT del HX711 pin GPIO 19 de la esp32

SCK_PIN = 3   # Pin de reloj SCK del HX711 pin GPIO 3 de la esp32

GALGA 5

DT_PIN = 1   # Pin de datos DT del HX711 pin GPIO 1 de la esp32

SCK_PIN = 23   # Pin de reloj SCK del HX711 pin GPIO 23 de la esp32



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


A continuación, se presenta el diseño preliminar propuesto para las bases de las galgas extensiométricas y sus respectivos recipientes, donde se alojará la pintura destinada al proceso de mezclado previo a la entrega final.

![alt text](DISEÑOS_1.png)

![alt text](DISEÑOS_2.png)


Se elabora el diagrama de flujo del sistema utilizando pseudocódigo, en el cual se indica la lógica prevista para la integración completa del sistema. Este diagrama representa la secuencia de operaciones que se ejecutarán durante el proceso de adquisición de datos de las galgas extensiométricas (por medio de los módulos HX711), la lectura de color mediante la cámara y la posterior codificación de los valores en el modelo CMYK, con el fin de obtener el color final en el recipiente de pintura.
![alt text](Flujo_mezclador-Galga.drawio.png)


## AVANCE 07-11-2025

Durante la semana se realizó la integración de las cinco galgas extensiométricas con el módulo ESP32, dejando cada una debidamente calibrada para que puedan ser dispuestas en las pruebas finales.

![alt text](medida.png)


Igualmente, se realizaron los esquemas de conexión y visualización mediante Node-RED y su Dashboard. En este caso, se dejaron configurados los bloques de medida y el histograma obtenido durante las pruebas, permitiendo una representación gráfica del comportamiento de las señales provenientes de las galgas.





### 1. [Flujos](/G10/flujos/flows.json)



### 2. [Programación micropython](/G10/micropython/test.py)

