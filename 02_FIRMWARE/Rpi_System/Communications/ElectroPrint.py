import serial
from .Modules.Printrun.Core import gcoder
from .Modules.Printrun.Core.printcore import printcore


class ElectroCommunication():
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
        print("try to conenct")
        tempConn = printcore(self.port, self.baud)
        if self.baud is not None and self.port is not None:
            if tempConn.online:
                self.online = True
                print("connected")
                return tempConn
        else:
            print("[ERROR] Baud and Port must be valid.")

    def is_connect(self):
        return self.connection.printer.isOpen()

    def is_ready(self):
        return self.ready

    def get_port(self):
        return self.port

    def startPrinting(self, file):
        gcode = [i.strip() for i in open(file)]
        gcode = gcoder.LightGCode(gcode)
        self.printing = True
        self.connection.startprint(gcode)

    def sendNow(self, cmd):
        self.connection.send_now(cmd)

    def send(self, cmd):
        self.connection.send(cmd)

    def pause(self):
        self.connection.pause()
        self.send("G91")
        self.send("G0 Z5")
        self.send("G90")
        self.send("G90")
        self.send("G0 X200 Y0")

    def resume(self):
        self.connection.resume()

    def stop(self):
        self.printing = False
        self.connection.cancelprint()
        self.send("M104 S0")
        self.send("M107")
        self.send("G91")
        self.send("G0 Z5")
        self.send("G90")
        self.send("G90")
        self.send("G0 X200 Y0")

    def disconnect(self):
        self.connection.disconnect()

    def reset(self):
        self.disconnect()
        self.connect()

    def isPrinting(self):
        return self.connection.printing

    def isOnline(self):
        return self.connection.isOnline()
