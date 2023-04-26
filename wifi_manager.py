import re
import subprocess


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
