import board
import adafruit_dht
import time

class SensorManager:
    def __init__(self, sensor_config):
        sensor_model = sensor_config[0]['model']
        sensor_pin = sensor_config[0]['pin']
        if sensor_model == 'DHT22':
            self.sensor = adafruit_dht.DHT22(getattr(board, f'D{sensor_pin}'))
        else:
            raise ValueError("Unsupported sensor model.")

    def read_temperature(self):
        return self.sensor.temperature

    def read_humidity(self):
        return self.sensor.humidity

    def generate_message(self):
        # Read sensor data
        temperature = self.read_temperature()
        humidity = self.read_humidity()

        # get datetime with format: year-month-day time
        datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # Publish sensor data
        message = {
            "datetime": datetime,
            "temperature": temperature,
            "humidity": humidity
        }

        return message