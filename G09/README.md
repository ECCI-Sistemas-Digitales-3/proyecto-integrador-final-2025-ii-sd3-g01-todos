# Nombre de la etapa:

## Integrantes
Maria Paula Fierro Barrios (https://github.com/fierrobarriosmariapaula-blip)

Astrid Catalina Ortiz Lopez (https://github.com/astridcortizl-del)

Camilo Suarez Camacho (https://github.com/Camilosc13)

## Documentación

## Objetivo General

Diseñar e implementar un sistema distribuido de monitoreo y control de temperatura basado en ESP32, con comunicación MQTT y visualización en Node-RED que permita activar válvulas y resistencias automáticamente al superar un umbral térmico definido.


### Funcionamiento del Sistema

**Capa 1: Lectura de Sensores (ESP32)**

El ESP32 recibe señales de cinco sensores DS18B20 conectados en diferentes pines (33, 25, 26, 27, 14).
Cada sensor mide la temperatura y publica los valores por MQTT en los siguientes tópic:

- micro/temperatura/sensor1
- micro/temperatura/sensor2
- micro/temperatura/sensor3
- micro/temperatura/sensor4
- micro/temperatura/sensor5

**Capa 2: Control Local**

El ESP32 compara cada lectura con un umbral de 30°C (TEMP_UMBRAL).

- Si la temperatura ≥ 30°C → activa la válvula correspondiente enviando ON al tópico MQTT.
- Si la temperatura < 30°C → envía OFF para desactivar la válvula.

Tópic de control:

- micro/pintura/valvula1
- micro/pintura/valvula2
- micro/pintura/valvula3
- micro/pintura/valvula4
- micro/pintura/valvula5

<p align="center">
  <img src="flujos/NodeRed_SensorTemperatura.png" alt="Flujo en Node-RED" width="500">
  <br>
  <b>Figura 1.</b> Flujo de monitoreo de temperatura en Node-RED.
</p>


**Capa 3: Visualización en Node-RED**

En Node-RED se visualizan las temperaturas y estados:

- Indicadores tipo termómetro muestran la temperatura en tiempo real.
- LEDs representan el estado de cada válvula (encendida o apagada).

El flujo incluye:

- Nodos MQTT IN para recibir datos de temperatura.
- Nodos Function que procesan las condiciones de temperatura.
- Nodos MQTT OUT para enviar comandos de activación/desactivación.
- Dashboard con widgets de temperatura y estado de válvulas.

<p align="center">
  <img src="flujos/Dashboard.png" alt="Dashboard Node-RED" width="500">
  <br>
  <b>Figura 2.</b> Panel de control (Dashboard) en Node-RED para visualizar las temperaturas y estados de válvulas.
</p>


## Variables y Parámetros Principales

| **Variable**          | **Descripción**                                   | **Tipo**          |
|------------------------|--------------------------------------------------|-------------------|
| **TEMP_UMBRAL**        | Umbral de activación de válvulas (30°C)          | Float             |
| **datos**              | Diccionario con las lecturas actuales            | Dict              |
| **estado_valvulas**    | Lista con el estado ON/OFF de cada válvula       | Boolean list      |
| **json_filename**      | Archivo donde se guardan los registros           | String            |
| **MQTT_TOPICS_TEMP**   | Lista de tópicos de publicación de temperatura   | List              |
| **MQTT_TOPICS_VALVULAS** | Lista de tópicos de control de válvulas        | List              |


**Registro de Datos**

Cada ciclo de lectura guarda las temperaturas en un archivo local temperaturasSensores.json, que actúa como un histórico de las mediciones.

El formato JSON permite analizar tendencias o generar reportes posteriores.

## Pruebas ESP32 y Node Red



 ## [Funciones Especiales del Código SensoresValvulas.py](/G09/micropython/SensoresValvulas.py)

- **KeyboardInterrupt:**
Permite detener manualmente el programa (con Ctrl + C) sin perder control.
Cuando se interrumpe, el script automáticamente ejecuta otro archivo (MqttValvula.py), garantizando que el sistema no quede inactivo.

- **try/except:**
Evita que errores en sensores o la conexión WiFi detengan el sistema.
En caso de falla, reinicia o ejecuta un script alterno.

- **os.system("MqttValvula.py"):**
Sirve para lanzar otro proceso cuando ocurre una interrupción o error, útil como mecanismo de respaldo o failover.



 ## [Funcionamiento y funciones Especiales del Código MqttValvula.py](/G09/micropython/MqttValvula.py)




![alt text](flujos/NodeRed_Valvula.png)


 ## Funcionamiento y funciones Especiales del Código FuncionSensores








## Retos Encontrados

1.	Sincronización de sensores:
Los DS18B20 requieren un tiempo de conversión (750 ms); si no se respeta, las lecturas pueden ser erróneas.
2.	Gestión de tópicos MQTT:
Mantener nombres consistentes en Node-RED y el código es vital para evitar desconexiones o mensajes perdidos.
3.	Actualización visual en Node-RED:
Requiere configurar correctamente los widgets y funciones para reflejar el estado real en tiempo real.


