import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# ===== CONFIGURACIÓN WiFi y MQTT =====
SSID = "Galaxy A127CAB"
PASSWORD = "sebasniko"
MQTT_BROKER = "4.tcp.ngrok.io"
MQTT_PORT = 12210

# ===== CONFIGURACIÓN CORREGIDA DE LAS 5 GALGAS =====
GALGAS = [
    {"dt": 12, "sck": 13, "topic": b"sensor/peso1", "scale": -682000.0},
    {"dt": 14, "sck": 27, "topic": b"sensor/peso2", "scale": -692007.0},
    {"dt": 25, "sck": 26, "topic": b"sensor/peso3", "scale": -682000.0},
    {"dt": 32, "sck": 33, "topic": b"sensor/peso4", "scale": -682000.0},
    {"dt": 34, "sck": 35, "topic": b"sensor/peso5", "scale": -682000.0}  # Cambiado SCK a pin 15
]

# ===== CLASE HX711 CORREGIDA =====
class HX711:
    def __init__(self, dout_pin, pd_sck_pin, gain=128):
        try:
            print(f"🔧 Inicializando HX711 en DT:{dout_pin}, SCK:{pd_sck_pin}")
            
            # Configurar pines - sin PULL_UP para pines que no lo soportan
            self.PD_SCK = Pin(pd_sck_pin, Pin.OUT)
            
            # Para pines que solo son entrada (como 34, 35, 36, 39) no usar PULL_UP
            if dout_pin in [34, 35, 36, 39]:
                self.DOUT = Pin(dout_pin, Pin.IN)
            else:
                self.DOUT = Pin(dout_pin, Pin.IN, Pin.PULL_UP)
                
            self.GAIN = 1 if gain == 128 else (3 if gain == 64 else 2)
            self.OFFSET = 0
            self.SCALE = 1.0
            self.PD_SCK.value(0)
            time.sleep_ms(10)
            print(f"✅ HX711 inicializado correctamente")
        except Exception as e:
            print(f"❌ Error inicializando HX711: {e}")
            raise

    def is_ready(self, timeout_ms=1000):
        start = time.ticks_ms()
        while self.DOUT.value() == 1:
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                return False
            time.sleep_ms(2)
        return True

    def read_raw(self):
        try:
            if not self.is_ready():
                return None
            
            count = 0
            for _ in range(24):
                self.PD_SCK.value(1)
                time.sleep_us(2)
                count = (count << 1) | self.DOUT.value()
                self.PD_SCK.value(0)
                time.sleep_us(2)
            
            for _ in range(self.GAIN):
                self.PD_SCK.value(1)
                time.sleep_us(2)
                self.PD_SCK.value(0)
                time.sleep_us(2)
            
            if count & 0x800000:
                count -= 0x1000000
            
            return count
        except Exception as e:
            print(f"Error en read_raw: {e}")
            return None

    def get_mean_raw(self, times=5):
        readings = []
        for _ in range(times):
            r = self.read_raw()
            if r is not None:
                readings.append(r)
            time.sleep_ms(10)
        
        if not readings:
            return None
        
        # Filtrar outliers
        if len(readings) > 2:
            readings.sort()
            readings = readings[1:-1]
        
        return sum(readings) // len(readings)

    def tare(self, times=10):
        print("⏳ Aplicando tara...")
        raw = self.get_mean_raw(times)
        if raw is None:
            print("⚠️ Tara fallida - no se pudieron obtener lecturas")
            return False
        self.OFFSET = raw
        print(f"✅ Tara aplicada (OFFSET: {self.OFFSET})")
        return True

    def set_scale(self, scale):
        self.SCALE = scale if scale != 0 else 1.0
        print(f"✅ Escala configurada: {self.SCALE}")

    def get_weight(self, times=5):
        raw = self.get_mean_raw(times)
        if raw is None:
            return None
        return (raw - self.OFFSET) / self.SCALE * 1000

# ===== FUNCIONES DE CONEXIÓN =====
def conectar_wifi():
    try:
        print("📡 Conectando a WiFi...")
        wlan = network.WLAN(network.STA_IF)
        wlan.active(False)
        time.sleep(1)
        wlan.active(True)
        
        if not wlan.isconnected():
            print(f"🔗 Conectando a: {SSID}")
            wlan.connect(SSID, PASSWORD)
            
            timeout = 20
            while not wlan.isconnected() and timeout > 0:
                print(".", end="")
                time.sleep(1)
                timeout -= 1
            
        if wlan.isconnected():
            print(f"\n✅ WiFi conectado!")
            print(f"📶 IP: {wlan.ifconfig()[0]}")
            return wlan
        else:
            print("\n❌ No se pudo conectar al WiFi")
            return None
    except Exception as e:
        print(f"❌ Error en WiFi: {e}")
        return None

def mqtt_connect():
    try:
        print("🔌 Conectando a MQTT...")
        client = MQTTClient("ESP32_5_GALGAS", MQTT_BROKER, port=MQTT_PORT, keepalive=60)
        client.connect()
        print("✅ Conectado a broker MQTT")
        return client
    except Exception as e:
        print(f"❌ Error MQTT: {e}")
        return None

# ===== PROGRAMA PRINCIPAL =====
def main():
    print("🚀 Iniciando sistema de 5 galgas...")
    time.sleep(2)
    
    # Conectar WiFi
    wlan = conectar_wifi()
    if not wlan:
        print("⚠️ Continuando sin WiFi...")
    
    # Conectar MQTT (intentar varias veces)
    mqtt = None
    if wlan:
        for i in range(3):
            mqtt = mqtt_connect()
            if mqtt:
                break
            print(f"⚠️ Reintentando conexión MQTT... ({i+1}/3)")
            time.sleep(2)

    # Inicializar galgas
    galgas = []
    ventanas = [[] for _ in range(5)]
    
    print("\n🎯 Inicializando galgas...")
    for i, config in enumerate(GALGAS):
        print(f"\n🔧 Configurando Galga {i+1} (DT:{config['dt']}, SCK:{config['sck']})...")
        try:
            hx = HX711(config["dt"], config["sck"])
            print("⏳ Aplicando tara...")
            if hx.tare():
                hx.set_scale(config["scale"])
                galgas.append(hx)
                print(f"✅ Galga {i+1} inicializada correctamente")
            else:
                print(f"⚠️ Galga {i+1} tuvo problemas en la tara")
                galgas.append(None)
        except Exception as e:
            print(f"❌ Error crítico en Galga {i+1}: {e}")
            galgas.append(None)
        
        time.sleep(1)  # Pausa entre inicializaciones

    print(f"\n📊 Estado final: {sum(1 for g in galgas if g is not None)}/5 galgas operativas")
    
    if sum(1 for g in galgas if g is not None) == 0:
        print("❌ Ninguna galga funcionó. Verificar conexiones.")
        return
    
    print("🎯 Iniciando lecturas continuas...\n")

    while True:
        try:
            pesos = [0.0] * 5
            lecturas_validas = [False] * 5
            
            # Leer todas las galgas
            for i, hx in enumerate(galgas):
                if hx is not None:
                    peso = hx.get_weight()
                    if peso is not None:
                        ventanas[i].append(peso)
                        if len(ventanas[i]) > 5:
                            ventanas[i].pop(0)
                        
                        if len(ventanas[i]) > 0:
                            pesos[i] = sum(ventanas[i]) / len(ventanas[i])
                            lecturas_validas[i] = True
                    else:
                        print(f"⚠️ Galga {i+1} sin lectura")

            # Mostrar en consola
            display = ""
            for i in range(5):
                if lecturas_validas[i]:
                    display += f"G{i+1}:{pesos[i]:6.1f}g"
                else:
                    display += f"G{i+1}:{'--':>6}g"
                
                if i < 4:
                    display += " | "
            
            print(display)

            # Publicar en MQTT (solo si hay conexión)
            if mqtt:
                try:
                    for i in range(5):
                        if lecturas_validas[i]:
                            mqtt.publish(GALGAS[i]["topic"], f"{pesos[i]:.1f}")
                except Exception as e:
                    print(f"⚠️ Error MQTT: {e}")
                    mqtt = None  # Marcar como desconectado

            time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n🛑 Programa detenido por el usuario")
            break
        except Exception as e:
            print(f"⚠️ Error en loop: {e}")
            time.sleep(2)

# ===== EJECUTAR =====
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"💥 Error crítico: {e}")
        print("Reiniciando en 5 segundos...")
        time.sleep(5)
        import machine
        machine.reset()
