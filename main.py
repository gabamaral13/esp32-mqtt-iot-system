# main.py - Aplicacao MQTT no microcontrolador
# Execute este arquivo pelo Thonny (Run > Run current script)
import network
from umqtt.simple import MQTTClient
import machine
import time
import json
import random
import dht

# ==== CONFIGURACOES - ALTERE AQUI ====
SSID = "Visitantes" # <-- Wi-Fi: nome da rede
SENHA = "" # <-- Wi-Fi: senha
BROKER = "broker.mqttdashboard.com"
PORTA = 1883
CLIENT_ID = "40115331_main" # Use seu RA para evitar conflito
TOPICO_SALA1 = "pucpr/sala1/dados_v2"# Micro publica aqui - TOPICO 1
TOPICO_SALA2 = "pucpr/sala2/dados_v2"# Micro publica aqui - TOPICO 2
TOPICO_ASSINAR = "pucpr/pc/comandos_v2" # Micro recebe daqui
# LED integrado (ajuste o pino conforme sua placa)
# ESP32: pino 2 | Pico W: pino "LED" | ESP8266: pino 2

#sensor DHT11
sensor = dht.DHT11(machine.Pin(19))

#sensor ultrassonico
trig = machine.Pin(22, machine.Pin.OUT)
echo = machine.Pin(21, machine.Pin.IN)

#LEDS
led1 = machine.Pin(4, machine.Pin.OUT)
led2 = machine.Pin(5, machine.Pin.OUT)


# ---- Conexao Wi-Fi ----
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando ao Wi-Fi...")
        wlan.connect(SSID, SENHA)
        tentativas = 0
        while not wlan.isconnected() and tentativas < 20:
            time.sleep(1)
            tentativas += 1
            print(f" Tentativa {tentativas}/20...")
    if wlan.isconnected():
        print(f"Wi-Fi conectado! IP: {wlan.ifconfig()[0]}")
        return True
    else:
        print("ERRO: Nao foi possivel conectar ao Wi-Fi")
        return False
    
# --- Medir a distância ----
def medir_distancia():
    trig.off()
    time.sleep_us(2)
    trig.on()
    time.sleep_us(10)
    trig.off()

    while echo.value() == 0:
        pulse_start = time.ticks_us()
    while echo.value() == 1:
        pulse_end = time.ticks_us()

    pulse_duration = time.ticks_diff(pulse_end, pulse_start)

    return (pulse_duration / 2) * 0.0343
        
# ---- Callback de mensagens recebidas ----
def callback_mensagem(topico, mensagem):
    global led_estado
    topico = topico.decode("utf-8")
    payload = mensagem.decode("utf-8")
    print(f"[MICRO] Recebido em '{topico}': {payload}")
    try:
        dados = json.loads(payload)
        comando = dados.get("comando", "")
        if comando == "led_on":
            led1.value(1)
            led2.value(1)
            print("[MICRO] LEDs ligados!")
            publicar_estado()
        elif comando == "led_off":
            led1.value(0)
            led2.value(0)
            print("[MICRO] LEDs desligados!")
            publicar_estado()
        elif comando == "status":
            publicar_dados_sensor()
        else:
            print(f"[MICRO] Comando desconhecido: {comando}")
    except Exception as e:
        print(f"[MICRO] Erro ao processar: {e}")
        
# ---- Funcoes de publicacao ----
def publicar_estado():
    estado = "ligados" if led1.value() == 1 and led2.value() == 1 else "desligados"
    msg = json.dumps({"leds": estado})
    client.publish(TOPICO_SALA1, msg)
    client.publish(TOPICO_SALA2, msg)
    print(f"[MICRO] Publicado: {msg}")
    
    
def publicar_dados_sensor():
# Simulacao de dados de sensor
# Em um projeto real, leia sensores reais aqui (DHT22, BMP280, etc.)
    sensor.measure()
    leds_estado = "ligados" if led1.value() == 1 and led2.value() == 1 else "desligados"

    #topico sala 1 -- SENSOR DHT
    sala1 = {
    "temperatura": sensor.temperature(),
    "umidade": sensor.humidity(),
    "leds": leds_estado
    }
    
    #topico sala 2 -- SENSOR ULTRASSONICO
    sala2 = {
    "distancia": round(medir_distancia(), 2),
    "leds": leds_estado    
    }
    
    msg1 = json.dumps(sala1)
    msg2 = json.dumps(sala2)
    client.publish(TOPICO_SALA1, msg1, qos=1)
    client.publish(TOPICO_SALA2, msg2, qos=1)
    print(f"[MICRO] Dados SALA 1: {sala1} | Dados SALA 2: {sala2}")
    
    # ---- Conexao e loop principal ----
if not conectar_wifi():
    print("Abortando: sem Wi-Fi.")
    raise SystemExit
print("[MICRO] Conectando ao broker MQTT...")
client = MQTTClient(CLIENT_ID, BROKER, port=PORTA)
client.set_callback(callback_mensagem)
client.connect()
print(f"[MICRO] Conectado a {BROKER}")
client.subscribe(TOPICO_ASSINAR)
print(f"[MICRO] Inscrito em: {TOPICO_ASSINAR}")
print("[MICRO] Aguardando comandos...\n")
        
    # Loop principal
contador = 0
try:
    while True:
    # Verifica novas mensagens (nao-bloqueante)
        client.check_msg()
    # A cada 30 segundos, publica dados automaticamente
        contador += 1
        if contador >= 30:
            publicar_dados_sensor()
            contador = 0
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[MICRO] Interrompido pelo usuario.")
finally:
    client.disconnect()
    print("[MICRO] Desconectado do broker.")