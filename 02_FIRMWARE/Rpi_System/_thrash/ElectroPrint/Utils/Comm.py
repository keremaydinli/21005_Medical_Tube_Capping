import serial
from Core import gcoder
from Core.printcore import printcore
from Utils.Util import serialList


class ElectroCommunication():
    def __init__(self, port=None, baud=250000, autoConnect=True):
        self.connectablePorts = []
        self.baud = baud
        self.port = self.autoDetectPort(autoConnect, port)
        self.online = False
        self.connection = self.connect()
        self.printing = False
        self.sendingList = []

    def autoDetectPort(self, autoDetect, port):
        if not autoDetect:
            if port is None:
                print("[ERROR] Baud must not None.")
            else:
                return port
        else:
            allPorts = serialList()
            print("[INFO] ALL PORTS: {}".format(allPorts))
            for item in allPorts:
                tempComm = serial.Serial(item, self.baud)
                print(type(tempComm.isOpen()))
                if tempComm.isOpen():
                    self.connectablePorts.append(item)
                tempComm.close()
            if len(self.connectablePorts) > 1:
                print("[ERROR] There are too much connectable ports.")
            elif len(self.connectablePorts) == 0:
                print("[ERROR] There is no connectable port.")
            else:
                print("[INFO] There are 1(one) connectable port.")
                return self.connectablePorts[0]
        return None

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
        self.connection._disconnect()

    def reset(self):
        self.disconnect()
        self.connect()

    def isPrinting(self):
        return self.connection.printing

    def isOnline(self):
        return self.connection.is_online()
