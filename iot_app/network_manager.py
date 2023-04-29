import re
import subprocess
import serial
import time

class WifiManager:
    def __init__(self, config):
        self.ssid = config['ssid']
        self.password = config['password']

    def is_connected(self):
        result = subprocess.run(["iwconfig"], capture_output=True, text=True)
        match = re.search(r'ESSID:"([^"]+)"', result.stdout)

        if match:
            current_ssid = match.group(1)
            return current_ssid == self.ssid
        else:
            return False

    def connect(self):
        if self.is_connected():
            print(f"Already connected to Wi-Fi network: {self.ssid}")
        else:
            print("Connecting to Wi-Fi network...")
            subprocess.run(["sudo", "nmcli", "dev", "wifi", "connect", self.ssid, "password", self.password], check=True)
            print(f"Connected to Wi-Fi network: {self.ssid}")

    def disconnect(self):
        if self.is_connected():
            print("Disconnecting from Wi-Fi network...")
            subprocess.run(["sudo", "nmcli", "dev", "disconnect", "wlan0"], check=True)
            print(f"Disconnected from Wi-Fi network: {self.ssid}")
        else:
            print(f"Already disconnected from Wi-Fi network: {self.ssid}")


class ModemManager:
    def __init__(self, config):
        modem_port = self.find_modem_ttyusb()
        if not modem_port:
            modem_port = '/dev/ttyUSB2'
        modem_baudrate = 115200
        self.modem = serial.Serial(modem_port, modem_baudrate, timeout=1)
        self.apn = config['apn']
        self.username = config['username']
        self.password = config['password']

    def find_modem_ttyusb(self):
        tty_pattern = r'ttyUSB\d+'

        for port_info in serial.tools.list_ports.comports():
            print(port_info)
            port = port_info.device
            description = port_info.description

            # Check if the port's description contains "modem" or "Modem"
            if re.search(r"(?i)modem", description) and re.match(tty_pattern, port):
                return port

        return None

    def connect(self):
        # Set APN
        self.modem.write(b'AT+CGDCONT=1,"IP","' + self.apn.encode() + b'"\r')
        time.sleep(1)
        self.modem.write(b'AT+CGACT=1,1\r')
        time.sleep(1)

    def disconnect(self):
        self.modem.write(b'AT+CGACT=0,1\r')
        time.sleep(1)
        self.close()

    def close(self):
        self.modem.close()


class NetworkManager:
    def __init__(self, network_config):
        self.config = network_config[0]  # Get the first network in configuration
        network_category = self.config['category']
        self.network_manager = None

        if network_category == 'cellular':
            self.network_manager = ModemManager(self.config)
        elif network_category == 'wifi':
            self.network_manager = WifiManager(self.config)

    def connect(self):
        self.network_manager.connect()

    def disconnect(self):
        self.network_manager.disconnect()