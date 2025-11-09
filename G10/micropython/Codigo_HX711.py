import network, time
from machine import Pin
from umqtt.simple import MQTTClient

# ===== CONFIG WiFi y MQTT =====
SSID = "Galaxy A127CAB"
PASSWORD = "sebasniko"
MQTT_BROKER = "4.tcp.ngrok.io"
MQTT_PORT = 12210
TOPICS = [b"sensor/peso1", b"sensor/peso2", b"sensor/peso3", b"sensor/peso4", b"sensor/peso5"]

# ===== PINES DE GALGAS (DT, SCK) =====
PINES_GALGAS = [(12, 13), (2, 4), (5, 18), (19, 3), (1, 23)]

# ===== CLASE HX711 LIGERA =====
class HX711:
    def __init__(self, dout, sck, gain=128):
        self.PD_SCK = Pin(sck, Pin.OUT, value=0)
        self.DOUT = Pin(dout, Pin.IN)
        self.GAIN = 1 if gain == 128 else (3 if gain == 64 else 2)
        self.OFFSET = 0
        self.SCALE = 1.0

    def ready(self):
        return self.DOUT.value() == 0

    def read_raw(self):
        if not self.ready():
            return None
        count = 0
        pd_sck = self.PD_SCK
        dout = self.DOUT
        for _ in range(24):
            pd_sck(1)
            count = (count << 1) | dout()
            pd_sck(0)
        for _ in range(self.GAIN):
            pd_sck(1)
            pd_sck(0)
        if count & 0x800000:
            count -= 0x1000000
        return count

    def tare(self, muestras=8):
        suma = 0
        valid = 0
        for _ in range(muestras):
            val = self.read_raw()
            if val:
                suma += val
                valid += 1
            time.sleep_ms(2)
        if valid:
            self.OFFSET = suma // valid

    def set_scale(self, scale):
        self.SCALE = scale or 1.0

    def get_weight(self):
        val = self.read_raw()
        if val is None:
            return 0.0
        return (val - self.OFFSET) / self.SCALE * 1000

# ===== CONEXIONES =====
def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(SSID, PASSWORD)
        print("Conectando WiFi...", end="")
        for _ in range(30):
            if wlan.isconnected():
                break
            print(".", end="")
            time.sleep(0.5)
    print("\n✅ WiFi:", wlan.ifconfig())
    return wlan

def mqtt_connect():
    client = MQTTClient("ESP32_HX711", MQTT_BROKER, port=MQTT_PORT)
    client.connect()
    print("✅ MQTT conectado")
    return client

# ===== PROGRAMA PRINCIPAL =====
def main():
    wifi_connect()
    client = mqtt_connect()

    galgas = [HX711(dt, sck) for dt, sck in PINES_GALGAS]
    factores = [-682000.0, -692007.0, -701230.0, -698540.0, -705000.0]

    print("\nTara en curso...")
    for i, hx in enumerate(galgas):
        hx.tare()
        hx.set_scale(factores[i])
        print(f"→ Galga {i+1} lista")

    print("\nLeyendo galgas...")

    ventanas = [[0.0]*4 for _ in range(5)]  # buffer pequeño
    idx = 0

    while True:
        try:
            for i, hx in enumerate(galgas):
                peso = hx.get_weight()
                ventanas[i][idx % 4] = peso
                prom = sum(ventanas[i]) / 4
                client.publish(TOPICS[i], str(round(prom, 2)))
            idx += 1
            time.sleep(0.2)  # lectura más rápida
        except OSError:
            print("⚠️ Reconectando MQTT...")
            client = mqtt_connect()
        except KeyboardInterrupt:
            print("\n🛑 Detenido por usuario")
            break

if __name__ == "__main__":
    main()
