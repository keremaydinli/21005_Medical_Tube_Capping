import time
import re
import serial
import threading


class MotherBoardCommunication:
    def __init__(self, port=None, baudrate=250000):
        self.port = port
        self.baudrate = baudrate
        self.connection = None
        self.line = None
        self.ready = False
        self.send_list = []
        self.connect()
        threading.Thread(target=self.listen).start()
        threading.Thread(target=self._sender).start()

    def connect(self):
        if self.connection:
            self.disconnect()
        if self.port and self.baudrate:
            print(self.port, self.baudrate)
            self.connection = serial.Serial(self.port, self.baudrate, timeout=0.25)

    def is_connect(self):
        return self.connection.isOpen()

    def disconnect(self):
        self.connection.close()

    def send(self, string):
        self.send_list.append(string)

    def send_now(self, string):
        self.connection.write((string + '\r\n').encode())

    def _sender(self):
        while True:
            if len(self.send_list):
                self.connection.write((self.send_list[0] + '\r\n').encode())
                self.connection.write(('M400' + '\r\n').encode())
                self.send_list.pop(0)
            time.sleep(0.1)

    def read(self):
        return self.connection.readline().decode().strip()

    def listen(self):
        while self.connection:
            self.line = self.read()
            if len(self.line):
                print('From Mother Board: {}'.format(self.line))

    def is_ready(self):
        return self.ready

    def get_port(self):
        return self.port
