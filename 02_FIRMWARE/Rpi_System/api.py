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
running = False
total_tube_count = 0

# Variables
send_file = 'temp_send_g_code_file.txt'


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
    if screen.is_connect():
        print('Screen Connected.')
    else:
        motherboard = None
        print('ERROR: MotherBoard not connected.')
    screen = ScreenCommunication(screenPort)


if __name__ == "__main__":
    # arr = s_protocol('start:21-13')
    startup_update()

    create_connections()
    print('Ready to use.')

    # Must move G28 (HOMING)

    while True:
        try:
            if len(screen.last_received) and not running:
                received = screen.last_received
                if 'acil-stop' in received:
                    # Emergency Stop
                    # motherboard.sendNow('M112')
                    motherboard.stop()
                    screen.send('page p_main')
                elif 'start':
                    # Received Screen Command Convert to MB Command Array
                    commands = s_protocol(received)

                    # # Send Command to Motherboard
                    motherboard.start_printing(send_file)
                    screen.send('page p_running')
                    running = True
                elif 'ileri' in received:
                    # ileri:10
                    dist = float(received.split(':')[1])
                    motherboard.send_now('G91')
                    motherboard.send_now('G0 X' + str(dist) + feedrate)
                    motherboard.send_now('G90')
                elif 'sag' in received:
                    # sag:1
                    dist = float(received.split(':')[1])
                    motherboard.send_now('G91')
                    motherboard.send_now('G0 Y' + str(dist) + feedrate)
                    motherboard.send_now('G90')
                elif 'sol' in received:
                    # sol:0.1
                    dist = float(received.split(':')[1])
                    motherboard.send_now('G91')
                    motherboard.send_now('G0 Y-' + str(dist) + feedrate)
                    motherboard.send_now('G90')
                elif 'geri' in received:
                    # geri:10
                    dist = float(received.split(':')[1])
                    motherboard.send_now('G91')
                    motherboard.send_now('G0 X-' + str(dist) + feedrate)
                    motherboard.send_now('G90')
                elif 'home' in received:
                    # home
                    motherboard.send_now('G28')
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
                        motherboard.send_now('G1 E135' + feedrate)
                        motherboard.send_now('G90')
                    elif 'bosalt' in received:
                        # pompa-bosalt
                        motherboard.send_now('T0')
                        motherboard.send_now('G91')
                        motherboard.send_now('G1 E-135' + feedrate)
                        motherboard.send_now('G90')

                screen.last_received = ""
            elif running:
                tube_count = motherboard.get_tube_count()
                total_tube_count += tube_count
                screen.send('p_main.lbl_yapilanTup.txt="'+str(total_tube_count)+'"')
                screen.send('p_running.lbl_yapilanTup.txt="'+str(total_tube_count)+'"')

        except:
            pass

        if running and not motherboard.get_running() and running != motherboard.get_running():
            screen.send('page p_running')
            running = False
        time.sleep(0.1)
