# Nombre de la etapa:

## Integrantes

Giselle Puentes Piñeros 31594  
Juan Pablo Ramirez 103681  
Nicolas Quiroga 109393  

## Documentación

El objetivo de este avance del proyecto es implementar un sistema de control automático para un motor agitador mediante el uso de dos motores eléctricos, una Raspberry Pi Pico 2 y una ESP32.
El primer motor se encarga de bajar y subir el aspa mezcladora, mientras que el segundo motor realiza la agitación de la pintura dentro de la cabina.
La coordinación de ambos motores se realiza de forma secuencial según el flujo de operación establecido, garantizando un proceso automatizado, preciso y eficiente.
Los motores son controlados a través de los pines GPIO2 y GPIO4 de la ESP32, con el apoyo de módulos puente H que permiten invertir el sentido de giro, y convertidores DC-DC Step-Down (Buck Converter) ajustables que regulan el voltaje de alimentación de cada motor.

![Periféricos del sistema](ESP1.jpg)

Herramientas utilizadas

Raspberry Pi Pico 2: microcontrolador principal encargado de gestionar la lógica de control y los tiempos de activación de los motores.

ESP32: microcontrolador auxiliar encargado de recibir y enviar señales de control mediante comunicación con la Pico 2; utiliza los pines GPIO2 y GPIO4 para activar los módulos puente H.

Motores DC (2 unidades):
Motor 1: encargado del movimiento vertical del aspa (bajar/subir).  
Motor 2: encargado de realizar la mezcla de pintura.  

Módulos Puente H: permiten controlar el sentido de giro y la activación de los motores mediante las señales de la ESP32.
Convertidores DC-DC Step-Down (Buck Converter): utilizados para ajustar el voltaje de alimentación de los motores, garantizando estabilidad y protección del sistema.

Software: Thonny IDE (para programación de la Pico y ESP32) y Node-RED o MQTT Broker (para monitoreo y control remoto del sistema).

### 1. [Flujos](/G02/flujos/flows.json)

![Periféricos del sistema](Flujo_motoagitador.jpg)

### 2. [Programación micropython](/G02/micropython/test.py)


