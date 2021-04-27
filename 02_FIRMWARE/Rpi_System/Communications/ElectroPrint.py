from .Modules.Printrun.Core import gcoder
from .Modules.Printrun.Core.printcore import printcore


class ElectroCommunication:
    def __init__(self, port=None, baud=250000):
        self.connectablePorts = []
        self.baud = baud
        self.port = port
        self.online = False
        self.connection = self.connect()
        self.printing = False
        self.sendingList = []

    def disconnect(self):
        if self.connection.isOpen():
            self.online = False
            self.connection.close()
            self.connection = None

    def connect(self):
        temp_conn = printcore(self.port, self.baud)
        if self.baud is not None and self.port is not None:
            if temp_conn.online:
                self.online = True
                return temp_conn
        else:
            print("[ERROR] Baud and Port must be valid.")

    def is_connect(self):
        return self.connection.printer.isOpen()

    def get_port(self):
        return self.port

    def start_printing(self, file):
        gcode = [i.strip() for i in open(file)]
        gcode = gcoder.LightGCode(gcode)
        self.printing = True
        self.connection.startprint(gcode)

    def send_now(self, cmd):
        self.connection.send_now(cmd)

    def send(self, cmd):
        self.connection.send(cmd)
        self.connection.send("M400")

    def pause(self):
        self.connection.pause()
        self.send("G90")
        self.send("G90")
        self.send("G0 X200 Y0 F8000")

    def resume(self):
        self.connection.resume()

    def stop(self):
        self.printing = False
        self.connection.cancelprint()
        self.send("G90")
        self.send("G90")
        self.send("G0 X200 Y0 F8000")

    def _disconnect(self):
        self.connection.disconnect()

    def reset(self):
        self._disconnect()
        self.connect()

    def is_printing(self):
        return self.connection.printing

    def is_online(self):
        return self.connection.isOnline()
