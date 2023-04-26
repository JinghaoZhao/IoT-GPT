import paho.mqtt.client as mqtt
from aiocoap import Context, Message
from aiocoap.numbers.codes import Code
import asyncio


class ProtocolManager:
    def __init__(self, protocol_config):
        self.protocol = protocol_config['type']
        self.broker = protocol_config['broker']
        self.port = protocol_config['port']
        self.username = protocol_config['username']
        self.password = protocol_config['password']
        self.topic = protocol_config['topic']
        self.encryption = protocol_config['security']['encryption']
        self.certificate_path = protocol_config['security']['certificate_path']

        if self.protocol == 'MQTT':
            self.client = mqtt.Client()
            self.client.username_pw_set(self.username, self.password)
            self.client.tls_set(self.certificate_path)
            self.client.connect(self.broker, self.port)

        elif self.protocol == 'CoAP':
            self.context = None
            self.psk_store = {
                f"coaps://{self.broker}/*": {
                    "dtls": {
                        "psk": self.password.encode(),
                        "client-identity": self.username.encode()
                    }
                }
            }

    async def create_coap_context(self):
        if self.context is None:
            self.context = await Context.create_client_context()
            self.context.client_credentials.load_from_dict(self.psk_store)

    async def publish_coap(self, topic, message):
        await self.create_coap_context()

        protocol = "coaps" if self.certificate_path else "coap"
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

    def disconnect(self):
        if self.protocol == 'MQTT':
            self.client.disconnect()
