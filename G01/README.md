# AVANCES PROYECTO INTEGRADOR

## Integrantes

- [Michael Handrety Fonseca Arana](https://github.com/MichaelJF50)
- [Laura Daniela Rincón Pinilla](https://github.com/Laura03rincon)

## Documentación

En este proyecto se desarrolló un sistema de control automático para bombas peristálticas, utilizando un ESP32 y el protocolo MQTT.

El sistema permite dosificar con precisión las pinturas base: Cian (C), Magenta (M), Amarillo (Y), Negro (K) y Blanco (W), necesarias para obtener el color final deseado en el proceso de mezcla automatizada.

Por medio de la comunicación MQTT, las bombas pueden encenderse y apagarse desde una interfaz en Node-RED, mientras que el ESP32 recibe las proporciones de cada color y controla el tiempo de activación según la cantidad que se necesita dosificar.

Además, el sistema cuenta con una galga de carga que mide el peso del recipiente y detiene automáticamente las bombas cuando se alcanza el valor esperado.

### Objetivo

Diseñar e implementar un sistema de control para las bombas peristálticas encargadas de transferir las pinturas base (C, M, Y, K, W), utilizando un ESP32 conectado a un servidor MQTT, para lograr una dosificación automática, precisa y monitoreada en tiempo real.

# ⚙️ Funcionamiento General

## 🟢 Inicio del proceso
- El usuario selecciona el color que desea dosificar.  
- Se envía un mensaje MQTT con el tema `bomba/inicio` y el valor `ON`.  
- El ESP32 enciende la bomba (salida en el pin configurado para el actuador).  
- El líquido fluye por el sistema hasta alcanzar el sensor correspondiente al color seleccionado.  

## 🔵 Lectura de sensores
- Los sensores detectan la presencia del color mediante cambios en el valor de salida (S, M, Y, K, W).  
- Cada sensor envía su señal al ESP32, donde se procesa para determinar el momento exacto en el que debe detenerse la bomba.  
- Los valores se leen constantemente para garantizar precisión en la dosificación.

## 🟡 Control del sistema
- El sistema trabaja con los parámetros S, M, Y, K y W, que representan los diferentes canales de color:  
  - **S:** Sensor de inicio o sincronización.  
  - **M:** Magenta.  
  - **Y:** Amarillo.  
  - **K:** Negro.  
  - **W:** Blanco o referencia.  
- El controlador evalúa las señales recibidas y ajusta el tiempo de activación de la bomba.  
- En caso de error o lectura fuera del rango esperado, se detiene el proceso automáticamente.

## 🔴 Comunicación MQTT
- El ESP32 se comunica con un servidor MQTT que recibe y envía los datos en tiempo real.  
- Los tópicos principales utilizados son:  
  - `bomba/inicio`: activa o detiene la bomba.  
  - `sensor/S`, `sensor/M`, `sensor/Y`, `sensor/K`, `sensor/W`: envían los valores de los sensores.  
  - `estado/sistema`: reporta el estado general (activo, detenido, error).  
- Esta comunicación permite visualizar el estado del proceso desde cualquier dispositivo conectado a la red.

## ⚪ Visualización y monitoreo
- Los datos se pueden observar desde un panel MQTT o una interfaz desarrollada en Node-RED.  
- El sistema muestra el estado de los sensores y la bomba en tiempo real.  
- Esto permite verificar si la mezcla de colores y la cantidad dosificada son correctas.

## 🔩 Variables Principales

| Variable        | Descripción                                       |
|-----------------|---------------------------------------------------|
| `sensor1`, `sensor2` | Entradas digitales conectadas al nivel del tanque |
| `bomba`         | Salida digital para el control de la bomba        |
| `led`           | LED indicador de estado de la bomba               |
| `modo_manual`   | Indica si el control es manual o automático       |
| `bomba_estado`  | Estado actual de la bomba (ON / OFF)              |

## 📸 Evidencias del Montaje

<p align="center">
  <img src="./Thonny.jpeg" alt="Logo" width="800"/>
</p>

<p align="center">
  <img src="./Node Red.jpeg" alt="Logo" width="800"/>
</p>

<p align="center">
  <img src="./Control bomba.jpeg" alt="Logo" width="800"/>
</p>
