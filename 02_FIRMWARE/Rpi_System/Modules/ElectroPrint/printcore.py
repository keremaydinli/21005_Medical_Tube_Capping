import time
from Stream.JavaComm import JavaCommunication
from Utils.Comm import ElectroCommunication

# from scripts.raspiCamera import startCamera

skr = ElectroCommunication()
time.sleep(2)
rpi = JavaCommunication("localhost", 9999)
data = ""

if __name__ == '__main__':
    while True:
        if len(rpi.sendingList) > 0:
            if ':' in rpi.sendingList[0]:
                command = rpi.sendingList[0].split(':')[0]
                data = rpi.sendingList[0].split(':')[1]
                if 'SEND' in command and skr.isPrinting():
                    skr.sendNow(data)
                elif 'SEND' in command and not skr.isPrinting():
                    skr.send(data)
                elif 'START' in command:
                    if not '/root/Printotype' in data:
                        data = '/root/Printotype/Workspace/G-Codes/' + data
                    skr.startPrinting(data)
                elif 'CMD' in command:
                    if 'PAUSE' in data:
                        skr.pause()
                    elif 'RESUME' in data:
                        skr.resume()
                    elif 'STOP' in data:
                        skr.stop()
                    elif 'SHUTDOWN' in data:
                        skr.shutdown()
                    elif 'RESET' in data:
                        skr.reset()
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
            rpi.sendingList.pop(0)

        rpi.sendingLine2JAVA(skr.connection.line)
        rpi.sendingTemps2JAVA(skr.connection.hotend, skr.connection.hotbed,
                              skr.connection.targetHotend, skr.connection.targetHotbed)

        if skr.isPrinting():
            rpi.sendingProgress2JAVA(skr.connection.queueindex, skr.connection.mainqueue)

        if skr.connection.finished:
            rpi.sendingIsFinished2JAVA()

        if len(rpi.sendingList) == 0:
            time.sleep(0.1)
