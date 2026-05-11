# ESP32 MQTT Telemetry & Control System

## 📌 Overview
This project is an end-to-end Internet of Things (IoT) solution demonstrating bidirectional communication between a microcontroller (ESP32) and a desktop client using the MQTT protocol. It features real-time sensor telemetry (temperature, humidity, distance) and remote hardware control (LED actuation) using structured JSON payloads.

## 🚀 Key Features

* **Bidirectional MQTT Communication:** Implements both publisher and subscriber logic on the microcontroller and the PC client.
* **Quality of Service (QoS 1):** Configured to guarantee message delivery (at least once) between the broker and the nodes.
* **Hardware Integration:** Reads environmental data from a DHT11 sensor and proximity data from an Ultrasonic sensor, controlling LEDs based on remote commands.
* **JSON Data Serialization:** All payloads are encoded and decoded as JSON objects for structured, scalable data transfer.
* **Asynchronous Polling:** Non-blocking message checking (`client.check_msg()`) on the microcontroller ensures continuous sensor monitoring.

## 🧠 Architecture
* **Node 1 (Microcontroller):** Runs MicroPython on an ESP32. Connects to Wi-Fi, reads sensor data (DHT11, Ultrasonic), and publishes to `pucpr/sala1/dados_v2` and `pucpr/sala2/dados_v2`. Subscribes to `pucpr/pc/comandos_v2` to receive actuation commands.
* **Node 2 (PC Client):** Runs standard Python using `paho-mqtt`. Subscribes to wildcard topics (`pucpr/+/dados_v2`) to monitor multiple rooms/sensors simultaneously. Sends commands (`led_on`, `led_off`, `status`).

## 🛠️ Technologies
* **Languages:** Python 3.x, MicroPython
* **Libraries:** `umqtt.simple` (MicroPython), `paho-mqtt` (PC), `json`, `machine`, `network`
* **Hardware:** ESP32, DHT11 Sensor, Ultrasonic Sensor, LEDs
* **Protocol:** MQTT (via HiveMQ / MQTT Dashboard public broker)

## ⚙️ How to Run

1. Clone this repository:
```bash
git clone [https://github.com/gabamaral13/esp32-mqtt-iot-system.git](https://github.com/gabamaral13/esp32-mqtt-iot-system.git)
```

2. **ESP32 Setup:** Flash the `main.py` script to your ESP32 using an IDE like Thonny. Ensure you update the `SSID` and `SENHA` variables with your local Wi-Fi credentials before running.

3. **PC Client Setup:** Install the required Python MQTT library:
```bash
pip install paho-mqtt
```

4. Run the PC client:
```bash
python pc_client.py
```
