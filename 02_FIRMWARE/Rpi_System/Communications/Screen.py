import time
import serial


class ScreenCommunication:
    def __init__(self, port=None, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.connection = None
        self.last_received = None
        self.line = None
        self.eof = b'\xff\xff\xff'
        self.connect()

    def connect(self):
        if self.port and self.baudrate:
            self.connection = serial.Serial(self.port, self.baudrate)
            self.send('connect')
            time.sleep(1)
            self.send('')  # 'page page0'  -> main page

    def send(self, command):
        self.connection.write(command.encode())
        self.connection.write(self.eof)

    def is_connect(self):
        return self.connection.is_open()

    def disconnect(self):
        self.connection.close()

    def read(self):
        return self.connection.read(128)

    def listen(self):
        while self.connection:
            self.line = self.read()
            if self.line and self.last_received is not self.line:
                self.line = str(self.line.strip(self.eof), 'ascii')
                print('From Screen: {}'.format(self.line))
                self.last_received = self.line

    def get_port(self):
        return self.port
