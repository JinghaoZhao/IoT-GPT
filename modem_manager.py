import serial
import time
import re

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

    def close(self):
        self.modem.close()
