import os
import socket
import threading
import time
from printrun import gcoder
from printrun.printcore import printcore
# from scripts.raspiCamera import startCamera

s = socket.socket()
port = 9999
s.connect(('localhost', port))

sendingList = []
data = ""
lineNum = -1
startGcode = [i.strip() for i in open('startEnd/startGcode.txt')]
endGcode = [i.strip() for i in open('startEnd/endGcode.txt')]

baud = 250000
p = printcore('/dev/ttyUSB0', baud)
# p = printcore('COM4', baud)
time.sleep(2)


def startPrinting(f):
    global p, startGcode
    print("Printing: %s on %s with baudrate %d" % (f, port, baud))
    gcode = [i.strip() for i in open(f)]  # or pass in your own array of gcode lines instead of reading from a file
    # start end gcodelar buraya eklenecek
    # gcode = startGcode + gcode + endGcode
    gcode = gcoder.LightGCode(gcode)
    p.startprint(gcode)  # this will start a print


def sendNow(cmd):
    global p
    # If you need to interact with the printer:
    p.send_now(cmd)  # this will send M105 immediately, ahead of the rest of the print


def send(cmd):
    global p
    p.send(cmd)


def pause():
    global p
    p.pause()  # use these to pause/resume the current print


def resume():
    global p
    p.resume()


def stop():
    global p
    p.cancelprint()


def disconnect():
    global p
    p.disconnect()  # this is how you disconnect from the printer once you are done. This will also stop running prints


def reset():
    global p
    disconnect()
    p.connect()


def isPrinting():
    global p
    return p.printing


def listeningJAVA():
    global sendingList
    while True:
        recv = s.recv(1024).decode()
        try:
            if 'SEND' in recv.split(':')[0] and isPrinting():
                sendingList.insert(0, recv)
            else:
                sendingList.append(recv)
        except:
            print('[ERROR] Unkown recv protocol: ', recv)


def sendingJAVA(command):
    s.send(len(command).to_bytes(2, byteorder='big'))
    s.send(command.encode())


def sendingTemps2JAVA():
    global p
    tempN = p.hotend
    tempB = p.hotbed
    targetTempN = p.targetHotend
    targetTempB = p.targetHotbed
    sendingJAVA('TEMPS:' + str(float(tempN)) + ':' + str(float(targetTempN)) + ':' + str(float(tempB)) + ':' + str(
        float(targetTempB)))


def sendingLine2JAVA():
    if p.line is not None:
        sendingJAVA('LINE:' + p.line)
        p.line = None


def sendingProgress2JAVA():
    global p
    # secondsremain, secondsestimate, progress = p.get_eta()
    progress = (p.queueindex - 2) / len(p.mainqueue) * 100
    sendingJAVA('PROGRESS:' + str(int(progress)))


def sendingIsFinished2JAVA():
    global p
    sendingJAVA('FINISHED')
    p.finished = False

def send2MKS(cmd):
    global p
    p.write((cmd + '\r\n').encode('UTF-8'))


def shutdown():
    sendingList.clear()
    sendingList.append('SEND:M112')
    sendingList.append('SEND:G28')
    os.system('omxplayer --no-keys /etc/Printotype/intro.mp4')  # outro play  ( intro service den cekilecek kullanımı )
    # time.sleep(15)  # video süresi - 2
    sendingList.append('SEND:M112')
    os.system('sudo shutdown -a now')


if __name__ == '__main__':

    listen = threading.Thread(target=listeningJAVA)
    listen.start()

    for line in startGcode:
        send(line)

    while True:
        if len(sendingList) > 0:
            if ':' in sendingList[0]:
                command = sendingList[0].split(':')[0]
                data = sendingList[0].split(':')[1]
                if 'SEND' in command and isPrinting():
                    sendNow(data)
                elif 'SEND' in command and not isPrinting():
                    send(data)
                elif 'START' in command:
                    startPrinting(data)
                elif 'CMD' in command:
                    if 'PAUSE' in data:
                        pause()
                    elif 'RESUME' in data:
                        resume()
                    elif 'STOP' in data:
                        stop()
                    elif 'SHUTDOWN' in data:
                        shutdown()
                    elif 'RESET' in data:
                        reset()
                    elif 'EMERGENCY' in data:
                        pass
                    # elif 'CAMERA' in data:
                    #     subCommand = sendingList[0].split(':')[2]
                    #     if 'START' in subCommand:
                    #         pass
                    #     elif 'STOP' in subCommand:
                    #         pass
                    #     else:
                    #         print('[ERROR] Unkown CAMERA subcommand.')
                    else:
                        print('[ERROR] Unkown CMD data')
                else:
                    print('[ERROR] Unkown COMMAND')
            sendingList.pop(0)

        sendingLine2JAVA()
        sendingTemps2JAVA()

        if isPrinting():
            sendingProgress2JAVA()

        if p.finished:
            sendingIsFinished2JAVA()

        if len(sendingList) == 0:
            time.sleep(0.1)
