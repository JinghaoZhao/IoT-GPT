import time
import paho.mqtt.client as mqtt
from aiocoap import Context, Message
from aiocoap.numbers.codes import Code
import asyncio


class ProtocolManager:
    def __init__(self, protocol_config):
        self.connected_flag = False
        self.protocol = protocol_config['type']
        self.broker = protocol_config['broker']
        self.port = protocol_config['port']
        self.username = protocol_config['username']
        self.password = protocol_config['password']
        self.topic = protocol_config['topic']
        self.encryption = protocol_config['security']['encryption']

        if self.protocol == 'MQTT':
            self.client = mqtt.Client()
            self.client.username_pw_set(self.username, self.password)
            if self.encryption == "TLS":
                self.ca_certificate_path = protocol_config['security']['ca_certificate_path']
                self.client_certificate_path = protocol_config['security']['client_certificate_path']
                self.client_key_path = protocol_config['security']['client_key_path']
                if not self.ca_certificate_path or not self.client_certificate_path or not self.client_key_path:
                    raise ValueError("Please set the TLS certificates in the config")
                self.client.tls_set(ca_certs=self.ca_certificate_path,
                                    certfile=self.client_certificate_path,
                                    keyfile=self.client_key_path)

        elif self.protocol == 'CoAP':
            self.context = None
            self.psk_store = None
            if self.encryption == "DTLS":
                self.psk = protocol_config['security']['psk']
                if not self.psk:
                    raise ValueError("Please set the PSK in the config")
                self.psk_store = {
                    f"coaps://{self.broker}:{self.port}/*": {
                        "dtls": {
                            "psk": self.psk.encode(),
                            "client-identity": self.username.encode()
                        }
                    }
                }

    def mqtt_on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected_flag = True
            print("MQTT broker connected.")
        else:
            print("Bad MQTT connection; Returned code=", rc)

    def mqtt_connect(self):
        self.client.on_connect = self.mqtt_on_connect
        self.client.loop_start()
        self.client.connect(self.broker, self.port)
        while not self.connected_flag:
            print("Waiting for MQTT broker connection...")
            time.sleep(1)

    async def create_coap_context(self):
        if self.context is None:
            self.context = await Context.create_client_context()
            if self.encryption == "DTLS":
                self.context.client_credentials.load_from_dict(self.psk_store)

    async def publish_coap(self, topic, message):
        await self.create_coap_context()

        protocol = "coaps" if self.psk_store else "coap"
        uri = f"{protocol}://{self.broker}:{self.port}/{topic}"

        request = Message(code=Code.POST, uri=uri, payload=message.encode())
        response = await self.context.request(request).response

        return response.code

    def publish(self, message):
        if self.protocol == 'MQTT':
            self.client.publish(self.topic, message)
        elif self.protocol == 'CoAP':
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.publish_coap(self.topic, message))

    def connect(self):
        if self.protocol == 'MQTT':
            self.mqtt_connect()
    def disconnect(self):
        if self.protocol == 'MQTT':
            self.client.loop_stop()
            self.client.disconnect()
