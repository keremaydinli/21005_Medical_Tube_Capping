import time
import logging

from Updater.Update_System import GithubDownloader
from Updater.Util import check_internet_connection
from Communications.ElectroPrint import ElectroCommunication
from Communications.Nextion import ScreenCommunication
from Communications.Utils import serial_ports
from Communications.Protocol.Screen import s_protocol

logging.basicConfig(filename="./Logs/system.log", filemode='w', level=logging.DEBUG,
                    format='%(levelname)s : %(asctime)s : Line No. : %(lineno)d - %(message)s', )

# Parameters #
url = "https://api.github.com/repos/NLSS-Engineering/21005_Medical_Tube_Capping/releases/latest"
screenPort = '/dev/ttyAMA0'

# Objects #
motherboard = None
screen = None

feedrate = ' F8000'
total_tube_count = 0
emergency_stop = False
wait_and_stop = False

# Variables
send_file = 'temp_send_g_code_file.txt'
print('asd')


def startup_update():
    if check_internet_connection():
        gd = GithubDownloader(url, encrypted=True, path='./', unzip_path="./Files/EXTRACT/")
        # RELEASE: unzip path ve path girilmeyecek
        # gd.download()  # if AutoDownload is True, it's not necessary
        # if gd.is_new_version():
        # change screen to update screen
        # pass
        gd.upgrade_system()


def create_connections():
    global motherboard, screen
    _ports = serial_ports()
    print('ports: {}'.format(_ports))
    for _port in _ports:
        # motherboard = MotherBoardCommunication(_port, 250000)
        motherboard = ElectroCommunication(_port, 250000)
        time.sleep(3)
        if motherboard.is_connect():
            break
    if motherboard.is_connect():
        print('MotherBoard Port: {}'.format(motherboard.get_port()))
    screen = ScreenCommunication(screenPort)
    if screen.is_connect():
        print('Screen Connected.')
    else:
        motherboard = None
        print('ERROR: MotherBoard not connected.')


if __name__ == "__main__":
    try:
        startup_update()
    except:
        print('ERROR: Update System Failed.')

    create_connections()
    print('Ready to use.')

    # Must move G28 (HOMING)
    screen = ScreenCommunication(screenPort)  # will remove
    motherboard = ElectroCommunication('_port', 250000)  # will remove
    while True:
        try:
            if len(screen.last_received):
                received = screen.last_received.lower()
                print('main recv: {}'.format(received))
                if 'start' in received:
                    miktar = s_protocol(received)  # Received Screen Command Convert to MB Command Array
                    time.sleep(0.5)  # wait
                    # # Send Command to Motherboard
                    screen.send('page p_running')  # display process page
                    for i in range(miktar):
                        motherboard.start_printing(send_file)  # start process
                        while motherboard.connection.printing:  # wait until finish process
                            if len(screen.last_received):  # listen screen
                                received = screen.last_received.lower()  # received command from screen
                                if 'emergency-stop' in received:  # finish process emergency
                                    # Emergency Stop
                                    emergency_stop = True
                                    motherboard.stop()  # STOP process
                                    screen.last_received = ""  # restore last received command from screen
                                    received = ''  # restore last received command from screen
                                    time.sleep(1)  # wait
                                    # maybe add stopping screen
                                    break
                                elif 'wait-and-stop' in received:  # wait running process and after stop
                                    wait_and_stop = True
                            time.sleep(0.1)  # wait
                        if emergency_stop:
                            emergency_stop = False
                            break
                        total_tube_count += 1  # increment finish process count
                        screen.send('p_main.lbl_yapilanTup.val=' + str(total_tube_count))  # update main page process counter
                        screen.send('p_running.lbl_yapilanTup.val=' + str(total_tube_count))  # update process page process counter
                    time.sleep(0.5)  # wait
                    screen.send('page p_main')  # return main page
                elif 'ileri' in received:
                    # ileri:10
                    dist = float(received.split('-')[1])
                    motherboard.send_now('G91')
                    motherboard.send_now('G0 Y' + str(dist) + feedrate)
                    motherboard.send_now('G90')
                elif 'sag' in received:
                    # sag:1
                    dist = float(received.split('-')[1])
                    motherboard.send_now('G91')
                    motherboard.send_now('G0 X' + str(dist) + feedrate)
                    motherboard.send_now('G90')
                elif 'sol' in received:
                    # sol:0.1
                    dist = float(received.split('-')[1])
                    motherboard.send_now('G91')
                    motherboard.send_now('G0 X-' + str(dist) + feedrate)
                    motherboard.send_now('G90')
                elif 'geri' in received:
                    # geri:10
                    dist = float(received.split('-')[1])
                    motherboard.send_now('G91')
                    motherboard.send_now('G0 Y-' + str(dist) + feedrate)
                    motherboard.send_now('G90')
                elif 'home' in received:
                    # home
                    print('SEND: G28')
                    motherboard.send_now('G28')
                    motherboard.send_now('G0 X200 Y0' + feedrate)
                elif 'tupu' in received:
                    if 'tut' in received:
                        # tupu-tut
                        motherboard.send_now('M280 P2 S90')
                    elif 'birak' in received:
                        # tupu-birak
                        motherboard.send_now('M280 P2 S120')
                elif 'pompa' in received:
                    if 'doldur' in received:
                        # pompa-doldur
                        motherboard.send_now('T0')
                        motherboard.send_now('G91')
                        motherboard.send_now('G1 E540 F6000')
                        motherboard.send_now('G90')
                    elif 'bosalt' in received:
                        # pompa-bosalt
                        motherboard.send_now('T0')
                        motherboard.send_now('G91')
                        motherboard.send_now('G1 E-540 F6000')
                        motherboard.send_now('G90')

                screen.last_received = ""
                received = ''

        except:
            raise
        time.sleep(0.1)
