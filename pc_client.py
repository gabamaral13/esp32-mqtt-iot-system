import paho.mqtt.client as mqtt
import json

BROKER = "broker.mqttdashboard.com"
PORTA = 1883
TOPICO_PUBLICAR = "pucpr/pc/comandos_v2"
TOPICO_ASSINAR = "pucpr/+/dados_v2"
CLIENT_ID = "401153311_PC"

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("[PC] Conectado ao broker MQTT!")
        client.subscribe(TOPICO_ASSINAR, qos=1)
        print(f"[PC] Inscrito no topico: {TOPICO_ASSINAR}, (Qos 1)")
    else:
        print(f"[PC] Falha na conexao, codigo: {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    
    print(f"\n[PC] Mensagem recebida em '{msg.topic}': {payload}")
    print(f"[DEBUG] QoS: {msg.qos} | DUP: {msg.dup}")

    try:
        dados = json.loads(payload)
        if "temperatura" in dados:
            print(f" -> Temperatura: {dados['temperatura']} C")
        if "umidade" in dados:
            print(f" -> Umidade: {dados['umidade']} %")
        if "led" in dados:
            print(f" -> Estado do LED: {dados['led']}")
    except json.JSONDecodeError:
        print(f" -> Dado em texto puro: {payload}")

def on_disconnect(client, userdata, flags, rc, properties):
    print(f"[PC] Desconectado do broker (rc={rc})")

def quality_of_service():
    print("\n--- NIVEIS DE QoS ---")
    print("QoS 0: Entrega no maximo uma vez (sem garantia)")
    print("QoS 1: Entrega pelo menos uma vez (pode duplicar)  <-- USADO")
    print("QoS 2: Entrega exatamente uma vez (mais seguro, mais lento)")

def main():
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=CLIENT_ID,
        clean_session=False 
    )

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    print(f"[PC] Conectando a {BROKER}:{PORTA}...")
    client.connect(BROKER, PORTA, 60)
    client.loop_start()

    print(quality_of_service())

    print("\n--- COMANDOS DISPONIVEIS ---")
    print(" led_on -> Liga o LED")
    print(" led_off -> Desliga o LED")
    print(" status -> Solicita dados do sensor")
    print(" sair -> Encerra o programa")
    print(" (ou digite qualquer texto para enviar)\n")

    try:
        while True:
            comando = input("[PC] Digite um comando: ").strip()

            if comando.lower() == "sair":
                break

            if comando:
                mensagem = json.dumps({"comando": comando})
                client.publish(TOPICO_PUBLICAR, mensagem, qos=1)

                print(f"[PC] Publicado em '{TOPICO_PUBLICAR}' (QoS 1): {mensagem}")

    except KeyboardInterrupt:
        print("\n[PC] Interrompido pelo usuario.")

    finally:
        client.loop_stop()
        client.disconnect()
        print("[PC] Encerrado.")

if __name__ == "__main__":
    main()