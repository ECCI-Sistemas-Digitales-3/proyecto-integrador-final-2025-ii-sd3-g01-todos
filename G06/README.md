# Nombre de la etapa:
Control de Bombas con MQTT (ESP32)
## Integrantes
Steven Herrera 
Carlos Medina
Daniel Camacho

## Documentación


# Control de Bombas CMYKW mediante MQTT y Galgas

## Resumen General

Este proyecto implementa un **sistema de control remoto para cinco bombas peristálticas** correspondientes a los colores del modelo **CMYKW (Cyan, Magenta, Yellow, Black y White)**.  
El control se realiza mediante el **protocolo MQTT**, utilizando un **ESP32 programado en MicroPython**, el cual recibe comandos remotos, **verifica el estado físico mediante galgas** y activa las bombas de forma segura.

Cada bomba está asociada a un **topic MQTT individual**, y su funcionamiento depende tanto del **comando remoto ("ON"/"OFF")** como del **estado lógico de la galga correspondiente**, que actúa como un permiso físico de habilitación.



## Objetivos del Sistema

  -Permitir el **control remoto e independiente** de las cinco bombas CMYKW mediante MQTT.  
  -Implementar una **seguridad lógica y física** con galgas que habilitan o bloquean cada bomba.  
  -Facilitar la **integración con plataformas IoT** (Node-RED, Raspberry Pi, SCADA educativos, etc.).  
  -Servir como **base didáctica** para prácticas de control y comunicaciones con MicroPython y ESP32.  

## Arquitectura del Sistema

### ESP32 con MicroPython
- Conectado por Wi-Fi mediante el módulo personalizado `wify.py`.  
- Suscrito a **cinco topics MQTT**, uno por cada bomba.  
- Controla directamente las **salidas digitales** que alimentan las bombas.  
- Lee las **entradas digitales** de las galgas (una por cada color).  

### Broker MQTT (Ngrok)
- Servidor remoto que **intermedia la comunicación** entre el cliente y el ESP32.  

###  Cliente Remoto (Node-RED / PC)
- Envía comandos `"ON"` o `"OFF"` a los topics específicos de cada color.  

## Funcionamiento Lógico

1. Al iniciar, el ESP32 se **conecta a la red Wi-Fi**.  
2. Luego se **conecta al broker MQTT** y se **suscribe a los cinco topics**:

-bombas/CYAN
-bombas/MAGENTA
-bombas/YELLOW
-bombas/BLACK
-bombas/WHITE


3. En el ciclo principal, el programa **escucha los mensajes MQTT**:

- Si el mensaje es `"ON"` **y la galga está activa (True)** → la bomba se energiza.  
- Si el mensaje es `"OFF"` **o la galga está inactiva (False)** → la bomba se apaga.  

4. Las **galgas actúan como interruptores de seguridad**, evitando la activación de una bomba sin permiso físico.  

## Variables y Componentes Principales

| Elemento | Descripción |
|-----------|-------------|
| **bombas[]** | Lista de objetos `Pin` configurados como **salidas digitales** conectadas a las bombas CMYKW. |
| **flag_*_galga** | Variables booleanas (`True/False`) que representan el **estado de cada galga**. |
| **TOPICS** | Diccionario con los **topics MQTT** para cada color. |
| **mensaje()** | Función *callback* ejecutada al recibir un mensaje MQTT. Controla las bombas según el topic, comando y galga. |
| **conectar_mqtt()** | Función que **establece la conexión** con el broker y realiza la **suscripción a los topics**. |

## Mensajes MQTT Admitidos

| Topic | Mensaje | Acción |
|-------|----------|--------|
| `bombas/CYAN` | `"ON"` / `"OFF"` | Controla la bomba **Cyan** |
| `bombas/MAGENTA` | `"ON"` / `"OFF"` | Controla la bomba **Magenta** |
| `bombas/YELLOW` | `"ON"` / `"OFF"` | Controla la bomba **Amarilla** |
| `bombas/BLACK` | `"ON"` / `"OFF"` | Controla la bomba **Negra** |
| `bombas/WHITE` | `"ON"` / `"OFF"` | Controla la bomba **Blanca** |

## Lógica de Seguridad

Cada **galga actúa como un permiso físico**.  
Si una galga está desactivada (`False`), **la bomba no podrá encenderse**, incluso si se recibe el comando `"ON"`.  
Esto evita fallos eléctricos o activaciones indebidas, garantizando **un control seguro y estable**.

## Ventajas del Diseño

-  **Control remoto seguro** con validación física mediante galgas.  
-  **Separación clara** entre control lógico (galgas) y control remoto (MQTT).  
-  **Sistema modular y escalable**, fácil de ampliar a más bombas o sensores.  
-  **Compatible** con plataformas IoT educativas o industriales.  
- **Ejecución estable** y bajo consumo en ESP32.  

## Tecnologías Utilizadas

- **MicroPython**  
- **ESP32**  
- **MQTT (umqtt.robust)**  
- **Ngrok (Broker remoto)**  
- **Wi-Fi (módulo personalizado `wify.py`)**

## Estructura del Proyecto

Control_Bombas_CMYKW_MQTT

─ main.py # Código principal de control de bombas
─ wify.py # Módulo de conexión Wi-Fi
─ README.md # Documentación del proyecto
─ requirements.txt # Dependencias (opcional)

## 🧪 Ejemplo de Uso

1. Iniciar el ESP32 con los archivos cargados (`main.py`, `wify.py`).  
2. Conectarse al Wi-Fi automáticamente.  
3. Conectarse al broker MQTT mediante Ngrok.  
4. Enviar comandos desde Node-RED o un cliente MQTT:

Topic: bombas/CYAN
Mensaje: ON 

Si la galga CYAN está activa, la bomba se encenderá.  
Enviar `"OFF"` para apagarla.


### 1. [Flujos](/G06/flujos/flows.json)

### 2. [Programación micropython](/G06/micropython/test.py)
