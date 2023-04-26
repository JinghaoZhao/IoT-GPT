import board
import adafruit_dht

class SensorManager:
    def __init__(self, sensors):
        sensor_model = sensors[0]['model']
        sensor_pin = sensors[0]['pin']
        if sensor_model == 'DHT22':
            self.sensor = adafruit_dht.DHT22(getattr(board, f'D{sensor_pin}'))
        else:
            raise ValueError("Unsupported sensor model.")

    def read_temperature(self):
        return self.sensor.temperature

    def read_humidity(self):
        return self.sensor.humidity