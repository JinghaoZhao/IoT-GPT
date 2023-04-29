import gradio as gr
import json
import requests
import os
from termcolor import colored

API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

with open('config.yaml', 'r') as file:
    config = file.read()

IoTGPT_prompt = """Now you are an expert IoT configuration developer and programmer. 
    You need to fill the following YAML configurations according to the user input for a Raspberry Pi IoT application. 
    The sensor type could be temperature, humidity, pressure, etc. 
    The network could be NB-IoT, Cat-M, LTE, 5G, WiFi, etc. Only one network need to be configured.  
    The traffic interval is the value of seconds between two transmissions. 
    The IoT protocol could be CoAP or MQTT. 
    The default port is 1883 for MQTT not encrypted, 8883 for MQTT encrypted, 5683 for CoAP not encrypted, 5684 for CoAP encrypted.
    If you need any details clarified, please ask questions until all issues are clarified.
    The output yaml does not need to include comments.
    Here is an example YAML format:""" + config


def generate_response(system_msg, inputs, top_p, temperature, chat_counter, chatbot=[], history=[]):
    global generated_yaml_config
    generated_yaml_config = "No configuration availabile yet."
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
    print(colored("Inputs: ", "green"), colored(inputs, "green"))
    response = requests.post(API_URL, headers=headers, json=payload, stream=True)
    token_counter = 0
    partial_words = ""

    response_complete = False

    counter = 0
    for chunk in response.iter_lines():
        if counter == 0:
            counter += 1
            continue

        if response_complete:
            print(colored("Response: ", "yellow"), colored(partial_words, "yellow"))

            # Extract YAML config from response and update the text box
            yaml_start = partial_words.find("```yaml")
            yaml_end = partial_words.find("```", yaml_start + 7)
            print(yaml_start, yaml_end)
            if yaml_start != -1 and yaml_end != -1:
                yaml_config = partial_words[yaml_start + 7: yaml_end].strip()
                print(colored(yaml_config, "red"))
                generated_yaml_config = yaml_config
            break

        if chunk.decode():
            chunk = chunk.decode()

            # Check if the chatbot is done generating the response
            if len(chunk) > 12 and "finish_reason" in json.loads(chunk[6:])['choices'][0]:
                response_complete = json.loads(chunk[6:])['choices'][0].get("finish_reason", None) == "stop"

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

def fill_output_box():
    return gr.update(value=generated_yaml_config)

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
            theme=theme,
            title="IoT-GPT",
    ) as demo:
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
            with gr.Row():
                with gr.Column(scale=7):
                    chatbot = gr.Chatbot(
                        label='IoT-GPT',
                        elem_id="chatbot"
                    )
                with gr.Column(scale=3):
                    save_config = gr.Button(
                        value="Save Configuration",
                    ).style(full_width=True)
                    yaml_output = gr.Textbox(
                        label="Generated IoT Configuration",
                        lines=20
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
                    examples=[
                        ["I want to build a temperature sensor IoT app."],
                        ["I want to build a temperature sensor IoT app with DHT22 connected to GPIO 15. The network uses NB-IoT with APN testapn. The application protocol uses MQTT with the following info broker: mqtt.example.com, default port, username: testuser, password: testpass topic: temp, security uses TLS."],
                        ["I want to build a temperature sensor IoT app with DHT22 connected to GPIO 15. The network uses NB-IoT with APN testapn. The application protocol uses CoAP with the following info broker: coap.example.com, default port, username: testuser, password: testpass topic: temp, security uses DTLS, psk 123456"],
                    ],
                    inputs=inputs)

            with gr.Accordion("Parameters", open=False):
                top_p = gr.Slider(minimum=-0, maximum=1.0, value=0.5, step=0.05, interactive=True,
                                  label="Top-p (nucleus sampling)", )
                temperature = gr.Slider(minimum=-0, maximum=5.0, value=0.5, step=0.1, interactive=True,
                                        label="Temperature", )
                chat_counter = gr.Number(value=0, visible=True, precision=0)

        inputs.submit(generate_response, [system_msg, inputs, top_p, temperature, chat_counter, chatbot, state],
                      [chatbot, state, chat_counter], ).then(fill_output_box, [], [yaml_output])
        b1.click(generate_response, [system_msg, inputs, top_p, temperature, chat_counter, chatbot, state],
                 [chatbot, state, chat_counter], ).then(fill_output_box, [], [yaml_output])

        inputs.submit(set_visible_false, [], [system_msg])
        b1.click(set_visible_false, [], [system_msg])
        inputs.submit(set_visible_true, [], [accordion_msg])
        b1.click(set_visible_true, [], [accordion_msg])

        b1.click(reset_textbox, [], [inputs])
        inputs.submit(reset_textbox, [], [inputs])

    demo.queue(max_size=99, concurrency_count=20).launch(debug=True)

if __name__ == "__main__":
    main()
