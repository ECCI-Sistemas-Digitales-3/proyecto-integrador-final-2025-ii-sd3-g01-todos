import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

SSID = "motorola2822"
PASSWORD = "hellomoto"
MQTT_BROKER = "4.tcp.ngrok.io"
MQTT_PORT = 12210

# Pines válidos ya corregidos (ninguno es 34-39)
GALGAS = [
    {"dt": 12, "sck": 13, "topic": b"sensor/peso1", "scale": 350.0},
    {"dt": 14, "sck": 27, "topic": b"sensor/peso2", "scale": 369.0},
    {"dt": 25, "sck": 26, "topic": b"sensor/peso3", "scale": 360.0},
    {"dt": 32, "sck": 33, "topic": b"sensor/peso4", "scale": 380.0},
    {"dt": 4,  "sck": 16, "topic": b"sensor/peso5", "scale": 370.0}
]

class HX711:
    def __init__(self, dout_pin, pd_sck_pin, gain=128):
        self.PD_SCK = Pin(pd_sck_pin, Pin.OUT)
        self.DOUT = Pin(dout_pin, Pin.IN, Pin.PULL_UP)

        self.GAIN = 1 if gain == 128 else (3 if gain == 64 else 2)
        self.OFFSET = 0
        self.SCALE = 1.0
        self.PD_SCK.value(0)
        time.sleep_ms(5)

    def is_ready(self, timeout_ms=500):
        start = time.ticks_ms()
        while self.DOUT.value() == 1:
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                return False
            time.sleep_us(200)
        return True

    def read_raw(self):
        if not self.is_ready():
            return None

        count = 0
        for _ in range(24):
            self.PD_SCK.value(1)
            count = (count << 1) | self.DOUT.value()
            self.PD_SCK.value(0)

        for _ in range(self.GAIN):
            self.PD_SCK.value(1)
            self.PD_SCK.value(0)

        if count & 0x800000:
            count -= 0x1000000

        return count

    def get_mean_raw(self, times=4):
        readings = []
        for _ in range(times):
            r = self.read_raw()
            if r is not None:
                readings.append(r)
            time.sleep_ms(3)

        if not readings:
            return None

        readings.sort()
        if len(readings) > 2:
            readings = readings[1:-1]

        return sum(readings) // len(readings)

    def tare(self, times=10):
        vals = []
        for _ in range(times):
            r = self.read_raw()
            if r is not None:
                vals.append(r)
            time.sleep_ms(5)

        if not vals:
            return False

        vals.sort()
        if len(vals) > 2:
            vals = vals[1:-1]

        self.OFFSET = sum(vals) // len(vals)
        return True

    def set_scale(self, scale):
        self.SCALE = scale if scale != 0 else 1.0

    def get_weight(self, times=4):
        raw = self.get_mean_raw(times)
        if raw is None:
            return None
        return (raw - self.OFFSET) / self.SCALE


def conectar_wifi():
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)

        if not wlan.isconnected():
            wlan.connect(SSID, PASSWORD)
            timeout = 15
            while not wlan.isconnected() and timeout > 0:
                time.sleep(1)
                timeout -= 1

        if wlan.isconnected():
            print("WiFi OK:", wlan.ifconfig()[0])
            return wlan
        return None
    except:
        return None


def mqtt_connect():
    try:
        client = MQTTClient("ESP32_5GALGAS", MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print("MQTT conectado")
        return client
    except:
        print("MQTT ERROR")
        return None


def main():
    print("Iniciando...")

    wlan = conectar_wifi()
    mqtt = mqtt_connect() if wlan else None

    galgas = []
    for cfg in GALGAS:
        try:
            hx = HX711(cfg["dt"], cfg["sck"])
            if hx.tare():
                hx.set_scale(cfg["scale"])
                galgas.append(hx)
            else:
                galgas.append(None)
        except:
            galgas.append(None)

    ventanas = [[] for _ in range(5)]

    while True:
        pesos = [0.0] * 5
        valid = [False] * 5

        for i, hx in enumerate(galgas):
            if hx is not None:
                p = hx.get_weight()
                if p is not None:
                    ventanas[i].append(p)
                    if len(ventanas[i]) > 5:
                        ventanas[i].pop(0)
                    pesos[i] = sum(ventanas[i]) / len(ventanas[i])
                    valid[i] = True

        linea = " | ".join(
            f"G{i+1}:{pesos[i]:.2f}" if valid[i] else f"G{i+1}:--"
            for i in range(5)
        )
        print(linea)

        if mqtt:
            try:
                for i in range(5):
                    if valid[i]:
                        mqtt.publish(GALGAS[i]["topic"], f"{pesos[i]:.2f}")
            except:
                mqtt = None

        time.sleep(0.15)


main()


