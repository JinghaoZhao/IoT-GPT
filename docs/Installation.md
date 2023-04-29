# Installation Notes

## CoAP DTLS Support

If you need DTLS support, the aiocoap library needs to be installed from [source](https://aiocoap.readthedocs.io/en/latest/installation.html). 

```bash
git clone https://github.com/chrysn/aiocoap
cd aiocoap
pip3 install --upgrade ".[tinydtls]"
```

A reference CoAP server could be setup with the following commands:
```bash
git clone https://github.com/obgm/libcoap.git --recursive
cd libcoap
./autogen.sh
./configure --with-tinydtls --disable-shared --disable-documentation
make
./examples/coap-server -k secretPSK
```


## MQTT TLS Support

Generate a certificate authority certificate and key.
```bash
openssl req -new -x509 -days <duration> -extensions v3_ca -keyout ca.key -out ca.crt
```

Generate a server key.
```bash
openssl genrsa -des3 -out server.key 2048
openssl req -out server.csr -key server.key -new
```
**NOTE:** When prompted for the CN (Common Name), please enter either your server (or broker) hostname or domain name.

Send the CSR to the CA, or sign it with your CA key:
```bash
penssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days <duration>
```

Generate a client key.
```bash
openssl genrsa -des3 -out client.key 2048
openssl req -out client.csr -key client.key -new
```
**NOTE:** When prompted for the CN (Common Name), the entered name will potentially be the user identity. Please check your IoT platform for the user identity format.

Send the CSR to the CA, or sign it with your CA key:
```bash
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days <duration>
```

A reference MQTT server could be setup with the [mosquitto](https://mosquitto.org/download/)

After installation, run the following commands. The sample configuration file is provided in this repository [here](mosquitto.conf)
```bash
mosquitto -c ./mosquitto.conf -v
```

You can also run a sample subscriber with
```bash
mosquitto_sub --cafile ./certs/ca.crt --cert ./certs/client.crt --key ./certs/client.key -d -h localhost -p 8883 -t 'test/topic' -v
```

or a sample publisher with
```bash
mosquitto_pub --cafile ./certs/ca.crt --cert ./certs/client.crt --key ./certs/client.key -d -h localhost -p 8883 -t 'test/topic' -m "hello"
```