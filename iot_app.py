import json
import time
from modem_manager import ModemManager
from wifi_manager import WifiManager
from protocol_manager import ProtocolManager
from sensor_manager import SensorManager

# Load JSON configuration
with open('config.json', 'r') as file:
    config = json.load(file)

# Initialize sensor
sensor_manager = SensorManager(config['sensors'])

# Network configuration
network_config = config['networks'][0]  # Get the first network in configuration
network_category = network_config['category']

if network_category == 'cellular':
    modem_manager = ModemManager(network_config)
    modem_manager.connect()
elif network_category == 'wifi':
    wifi_manager = WifiManager(network_config)
    wifi_manager.connect()

# Application protocol configuration
protocol_config = config['protocol']
protocol_manager = ProtocolManager(protocol_config)

# Main loop
traffic_interval = config['traffic_interval']
while True:
    try:
        # Read sensor data
        temperature = sensor_manager.read_temperature()
        humidity = sensor_manager.read_humidity()

        # Publish sensor data
        message = {
            "temperature": temperature,
            "humidity": humidity
        }
        protocol_manager.publish(json.dumps(message))
        print(f"Published data: {message}")

        # Sleep for the traffic interval
        time.sleep(traffic_interval)

    except RuntimeError as error:
        print(error.args[0])
        time.sleep(2.0)
    except Exception as error:
        protocol_manager.disconnect()
        raise error