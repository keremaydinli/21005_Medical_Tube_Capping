import time
import logging

import Configurations
from Updater.Update_System import GithubDownloader
from Updater.Util import check_internet_connection
# from Communications.MotherBoard import MotherBoardCommunication
from Communications.ElectroPrint import ElectroCommunication
from Communications.Screen import ScreenCommunication
from Communications.Utils import serial_ports
from Communications.Protocol.Screen import s_protocol

logging.basicConfig(filename="./Logs/system.log", filemode='w', level=logging.DEBUG, format='%(levelname)s : %(asctime)s : Line No. : %(lineno)d - %(message)s',)

# Parameters #
url = "https://api.github.com/repos/NLSS-Engineering/21005_Medical_Tube_Capping/releases/latest"
screenPort = '/dev/ttyAMA0'

# Objects #
motherboard = None
screen = None

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
    screen = ScreenCommunication(screenPort)
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
    else:
        motherboard = None
        print('ERROR: MotherBoard not connected.')


if __name__ == "__main__":
    if not Configurations.DEV_MOD:
       startup_update()

    # create_connections()
    print('Ready to use.')

    # Must move G28 (HOMING)
    s_protocol('start:121-13')

    # Received Screen Command Convert to MB Command Array
    # commands = str(s_protocol(screen.last_received))
    #
    # # Send Command to Motherboard
    # motherboard.startPrinting(send_file)
