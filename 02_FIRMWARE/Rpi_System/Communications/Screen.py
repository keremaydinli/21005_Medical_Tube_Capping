import threading
import time
import serial


class ScreenCommunication:
    def __init__(self, port=None, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.connection = None
        self.last_received = ""
        self.line = None
        self.eof = b'\xff\xff\xff'
        self.connect()
        threading.Thread(target=self.listen).start()

    def connect(self):
        if self.port and self.baudrate:
            self.connection = serial.Serial(self.port, self.baudrate, timeout=0.25)
            self.send('connect')
            time.sleep(1)
            self.send('page p_main')  # 'page page0'  -> main page

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
            self.line = self.read().strip(self.eof)
            if len(self.line):
                self.line = self.line.decode('ascii')
                print('From Screen: {}'.format(self.line))
                self.last_received = self.line
                self.line = ""

    def get_port(self):
        return self.port
