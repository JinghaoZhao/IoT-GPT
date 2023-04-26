# IoT-GPT
Build Raspberry Pi IoT Applications with ChatGPT.

## Installation

1. Clone this repository:
```
git clone git@github.com:JinghaoZhao/IoT-GPT.git
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