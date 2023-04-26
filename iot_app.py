import json
import time
import yaml
from network_manager import NetworkManager
from protocol_manager import ProtocolManager
from sensor_manager import SensorManager

def main():
    # Load configuration
    with open("config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    # Initialize SensorManager
    sensor_manager = SensorManager(config['sensors'])

    # Initialize NetowrkManager
    network_manager = NetworkManager(config['networks'])
    network_manager.connect()

    # Configure application protocol
    protocol_config = config['protocol']
    protocol_manager = ProtocolManager(protocol_config)

    # Configure traffic interval
    traffic_interval = config['traffic_interval']

    # Main loop
    while True:
        try:
            # Read sensor data
            sensor_message = sensor_manager.generate_message()

            protocol_manager.publish(json.dumps(sensor_message))
            print(f"Published data: {sensor_message}")

            # Sleep for the traffic interval
            time.sleep(traffic_interval)

        except RuntimeError as error:
            print(error.args[0])
            time.sleep(2.0)
        except Exception as error:
            protocol_manager.disconnect()
            raise error

if __name__ == "__main__":
    main()