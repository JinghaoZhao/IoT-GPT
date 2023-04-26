import gradio as gr
import json
import requests
import os

API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

with open('config_template.json', 'r') as file:
    config = file.read()

IoTGPT_prompt = """Now you are an expert IoT configuration developer and programmer. 
    You need to fill the following JSON configurations according to the user input. 
    The JSON configuration is required by a Raspberry Pi IoT application. 
    The sensor type could be temperature, humidity, pressure, etc. 
    The network could be NB-IoT, Cat-M, LTE, 5G, WiFi, etc. Only one network need to be configured.  
    The traffic interval is the value of seconds between two transmissions. 
    The IoT protocol could be CoAP or MQTT. 
    If you need any details clarified, please ask questions until all issues are clarified.
    Here is an example json format:""" + config


def generate_response(system_msg, inputs, top_p, temperature, chat_counter, chatbot=[], history=[]):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    if system_msg.strip() == '':
        initial_message = [{"role": "user", "content": f"{inputs}"}]
        multi_turn_message = []
    else:
        initial_message = [{"role": "system", "content": system_msg},
                           {"role": "user", "content": f"{inputs}"}]
        multi_turn_message = [{"role": "system", "content": system_msg}]

    if chat_counter == 0:
        payload = {
            "model": "gpt-4",
            "messages": initial_message,
            "temperature": 0.5,
            "top_p": 0.5,
            "n": 1,
            "stream": True,
            "presence_penalty": 0,
            "frequency_penalty": 0,
        }
    else:
        messages = multi_turn_message
        for data in chatbot:
            user = {"role": "user", "content": data[0]}
            assistant = {"role": "assistant", "content": data[1]}
            messages.extend([user, assistant])
        temp = {"role": "user", "content": inputs}
        messages.append(temp)

        payload = {
            "model": "gpt-4",
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "n": 1,
            "stream": True,
            "presence_penalty": 0,
            "frequency_penalty": 0, }

    chat_counter += 1
    history.append(inputs)
    response = requests.post(API_URL, headers=headers, json=payload, stream=True)
    token_counter = 0
    partial_words = ""

    counter = 0
    for chunk in response.iter_lines():
        if counter == 0:
            counter += 1
            continue
        if chunk.decode():
            chunk = chunk.decode()
            if len(chunk) > 12 and "content" in json.loads(chunk[6:])['choices'][0]['delta']:
                partial_words = partial_words + json.loads(chunk[6:])['choices'][0]["delta"]["content"]
                if token_counter == 0:
                    history.append(" " + partial_words)
                else:
                    history[-1] = partial_words
                chat = [(history[i], history[i + 1]) for i in range(0, len(history) - 1, 2)]
                token_counter += 1
                yield chat, history, chat_counter, response


def reset_textbox():
    return gr.update(value='')


def set_visible_false():
    return gr.update(visible=False)


def set_visible_true():
    return gr.update(visible=True)

def main():

    title = """<h1 align="center">IoT-GPT</h1>"""

    system_msg_info = """A conversation could begin with a system message to gently instruct the assistant."""

    theme = gr.themes.Soft(text_size=gr.themes.sizes.text_md)

    with gr.Blocks(
            css="""#col_container { margin-left: auto; margin-right: auto;} #chatbot {height: 520px; overflow: auto;}""",
            theme=theme) as demo:
        gr.HTML(title)

        with gr.Column(elem_id="col_container"):
            with gr.Accordion(label="System message:", open=False):
                system_msg = gr.Textbox(
                    label="Instruct the AI Assistant to set its beaviour",
                    info=system_msg_info,
                    value=IoTGPT_prompt
                )
                accordion_msg = gr.HTML(
                    value="Refresh the app to reset system message",
                    visible=False
                )
            chatbot = gr.Chatbot(
                label='IoT-GPT',
                elem_id="chatbot"
            )
            state = gr.State([])
            with gr.Row():
                with gr.Column(scale=8):
                    inputs = gr.Textbox(
                        placeholder="What IoT apps do you want to build?",
                        lines=1,
                        label="Type an input and press Enter"
                    )
                with gr.Column(scale=2):
                    b1 = gr.Button().style(full_width=True)

            with gr.Accordion(label="Examples", open=True):
                gr.Examples(
                    examples=[[
                                  "I want to build a temperature sensor IoT app with BME280 connected to GPIO 15. The network uses NB-IoT with APN testapn. The application protocol uses MQTT with the following info broker: mqtt.example.com, default port, username: testuser, password: testpass topic: temp, security uses TLS, no cert."],
                              ["I want to build a GPS tracker IoT app."],
                              ],
                    inputs=inputs)

            with gr.Accordion("Parameters", open=False):
                top_p = gr.Slider(minimum=-0, maximum=1.0, value=0.5, step=0.05, interactive=True,
                                  label="Top-p (nucleus sampling)", )
                temperature = gr.Slider(minimum=-0, maximum=5.0, value=0.5, step=0.1, interactive=True,
                                        label="Temperature", )
                chat_counter = gr.Number(value=0, visible=False, precision=0)

        inputs.submit(generate_response, [system_msg, inputs, top_p, temperature, chat_counter, chatbot, state],
                      [chatbot, state, chat_counter], )
        b1.click(generate_response, [system_msg, inputs, top_p, temperature, chat_counter, chatbot, state],
                 [chatbot, state, chat_counter], )

        inputs.submit(set_visible_false, [], [system_msg])
        b1.click(set_visible_false, [], [system_msg])
        inputs.submit(set_visible_true, [], [accordion_msg])
        b1.click(set_visible_true, [], [accordion_msg])

        b1.click(reset_textbox, [], [inputs])
        inputs.submit(reset_textbox, [], [inputs])

    demo.queue(max_size=99, concurrency_count=20).launch(debug=True)

if __name__ == "__main__":
    main()
