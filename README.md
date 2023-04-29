# IoT-GPT
Raspberry Pi IoT Platform powered by GPT-4. Customize your own IoT application with natural language.

![IoTGPT.jpg](docs%2FIoTGPT.jpg)

## Installation

1. Clone this repository and install the required packages:
```
git clone https://github.com/JinghaoZhao/IoT-GPT.git
pip install -r requirements.txt
```
2. Create a `.env` file to put your API key:
```
OPENAI_API_KEY=sk-xxxxxx
```
3. Run the IoT-GPT:
```
python run.py
```
4. Open your web browser at http://127.0.0.1:7860 to generate your own IoT application config.
5. Store the config as config.json, then run the IoT application on your Raspberry Pi:
```
python iot_app.py
```

## Security Support

If you need security support, such as setting up CoAP DTLS or generate TLS certs for MQTT, please refer the [Installation Notes](docs/Installation.md).