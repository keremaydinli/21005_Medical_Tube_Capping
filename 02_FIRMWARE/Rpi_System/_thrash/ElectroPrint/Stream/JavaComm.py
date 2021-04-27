import socket
import threading
import time


class JavaCommunication:
    def __init__(self, IP, port):
        self.IP = IP
        self.port = port
        self.connection = None
        self.createCommunication()
        self.sendingList = []
        self.printing = False
        self.readThread = threading.Thread(target=self.listeningJAVA)
        self.readThread.start()
        self.lastSended = ""

    def createCommunication(self):
        self.connection = socket.socket()
        self.connection.connect((self.IP, self.port))
        time.sleep(1)

    def listeningJAVA(self):
        print("[INFO] Listening Java Thread Started.")
        while True:
            recv = self.connection.recv(1024).decode()
            try:
                if 'SEND' in recv.split(':')[0] and self.isPrinting():
                    self.sendingList.insert(0, recv)
                else:
                    self.sendingList.append(recv)
            except:
                print('[ERROR] Unkown recv protocol: ', recv)

    def sendingJAVA(self, command):
        self.connection.send(len(command).to_bytes(2, byteorder='big'))
        self.connection.send(command.encode())

    def sendingTemps2JAVA(self, tempN, tempB, targetTempN, targetTempB):
        self.sendingJAVA(
            'TEMPS:' + str(float(tempN)) + ':' + str(float(targetTempN)) + ':' + str(float(tempB)) + ':' + str(
                float(targetTempB)))

    def sendingLine2JAVA(self, line):
        if len(line) > 1 and line is not self.lastSended:
            self.sendingJAVA('LINE:' + line)
            self.lastSended = line

    def sendingProgress2JAVA(self, queueindex, mainqueue):
        progress = (queueindex - 2) / len(mainqueue) * 100
        self.sendingJAVA('PROGRESS:' + str(int(progress)))

    def sendingIsFinished2JAVA(self):
        self.sendingJAVA('FINISHED')

    def clearSendingList(self):
        self.sendingList.clear()

    ## GETTERS ##
    def getIP(self):
        return self.IP

    def getPort(self):
        return self.port

    def isPrinting(self):
        return self.printing

    def isOnline(self):
        # TODO: TEST
        return self.connection.is_online()

    ## SETTERS ##
    def setIP(self, IP):
        self.IP = IP

    def setPort(self, port):
        self.port = port

    def setPrinting(self, printing):
        self.printing = printing
