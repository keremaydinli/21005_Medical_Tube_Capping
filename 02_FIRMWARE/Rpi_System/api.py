import random
import time

import Configurations
from updater.Update_System import GithubDownloader
from updater.Util import checkInternetConnection
from Communications.MotherBoard import MotherBoardCommunication
from Communications.Screen import ScreenCommunication
from Communications.Utils import serial_ports

# Parameters #
url = "https://api.github.com/repos/NLSS-Engineering/21005_Medical_Tube_Capping/releases/latest"
screenPort = ''

# Objects #
motherboard = None
screen = None


def startup_update():
    if checkInternetConnection():
        gd = GithubDownloader(url, encrypted=True, auto_download=True, path='./', unzip_path="./Files/EXTRACT/")
        # RELEASE: unzip path ve path girilmeyecek
        # gd.download()  # if AutoDownload is True, it's not necessary
        if gd.is_new_version():
            # change screen to update screen
            pass
        gd.upgrade_system()


def create_connections():
    global motherboard, screen
    # screen = ScreenCommunication(screenPort)
    _ports = serial_ports()
    print('ports: {}'.format(_ports))
    for _port in _ports:
        motherboard = MotherBoardCommunication(_port, 250000)
        time.sleep(1)
        if motherboard.is_connect():
            break
    print('MotherBoard Port: {}'.format(motherboard.get_port()))


if __name__ == "__main__":
    if not Configurations.DEV_MOD:
        startup_update()

    create_connections()

