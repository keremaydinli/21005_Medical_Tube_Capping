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
    # arr = s_protocol('start:21-13')
    startup_update()

    create_connections()
    print('Ready to use.')

    # Must move G28 (HOMING)

    while True:
        try:
            if len(screen.last_received):
                received = screen.last_received.lower()
                print('main recv: {}'.format(received))
                if 'acil-stop' in received:
                    # Emergency Stop
                    # motherboard.sendNow('M112')
                    motherboard.stop()
                    screen.last_received = ""
                    received = ''
                    time.sleep(1)
                    screen.send('page p_main')
                elif 'start' in received:
                    # Received Screen Command Convert to MB Command Array
                    miktar = s_protocol(received)
                    time.sleep(0.5)
                    # # Send Command to Motherboard
                    screen.send('page p_running')
                    for i in range(miktar):
                        motherboard.start_printing(send_file)
                        total_tube_count += 1
                        screen.send('p_main.lbl_yapilanTup.val=' + str(total_tube_count))
                        screen.send('p_running.lbl_yapilanTup.val=' + str(total_tube_count))
                    time.sleep(0.5)
                    screen.send('page p_main')
                    # running = True
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
        #             elif running:
        #                 screen.send('p_main.lbl_yapilanTup.val='+str())
        #                 screen.send('p_running.lbl_yapilanTup.val='+str(motherboard.get_tube_count()))

        except:
            raise

        #         if running and not motherboard.get_running() and running != motherboard.get_running():
        #             screen.send('page p_running')
        #             running = False
        time.sleep(0.1)
