import time
import glob
import logging
import os

from Updater.Update_System import GithubDownloader, get_version_file_path
from Updater.ScreenUploader import file_path
from Updater.Util import write_file
from Updater.Util import check_internet_connection
from Communications.ElectroPrint import ElectroCommunication
from Communications.Nextion import ScreenCommunication
from Communications.Utils import serial_ports
from Communications.Protocol.Screen import s_protocol
from ArmFunctions import Motor, Servo, Move

logging.basicConfig(filename="./Logs/system.log", filemode='w', level=logging.DEBUG,
                    format='%(levelname)s : %(asctime)s : Line No. : %(lineno)d - %(message)s', )

# Parameters #
# TODO: PUBLIC REPO UZERINDEN YAPILACAK
url = "https://api.github.com/repos/NLSS-Engineering-Public/21005_Medical_Tube_Capping/releases/latest"
screenPort = '/dev/ttyAMA0'

# Objects #
motherboard = None
screen = None

# Variables
screen_upload_file = '/gui.tft'
# send_file = 'temp_send_g_code_file.txt'
# TODO: SEND_FILE ISMI DEGISTIRILECEK
send_file = 'test_gcode.gcode'
tup_ver_file = 'tup_ver.gcode'
feedrate = ' F8000'
total_tube_count = 0
emergency_stop = False
wait_and_stop = False
# extract_files_path = "./Files/EXTRACT/"


def startup_update():
    if check_internet_connection():
        # gd = GithubDownloader(url, encrypted=True, path='./Files', unzip_path=extract_files_path)
        gd = GithubDownloader(url, encrypted=True)
        if gd.is_new_version():  # if new version
            screen.send('page p_update')
            gd.upgrade_system()  # system upgrade
            pwd = os.getcwd()
            if glob.glob(pwd + screen_upload_file,
                         recursive=True):  # if screen_upload_file in downloaded files
                file_path = os.path.abspath(screen_upload_file)  # get abspath
                screen.send('page p_restart')
                time.sleep(2)
                os.system('python ' + pwd + '/Updater/ScreenUploader.py')
                os.remove(pwd + screen_upload_file)
            write_file(get_version_file_path(), gd.get_latest_version())
            # time.sleep(3)  # wait
            # screen.send('page p_main')
            os.system('sudo shutdown -r now')


def create_connections(delay=2):
    global motherboard, screen
    _ports = serial_ports()
    for _port in _ports:
        motherboard = ElectroCommunication(_port, 250000)
        time.sleep(0.1)
        if motherboard.is_connect():
            break
    time.sleep(delay)
    motherboard.send_now('M106 S255')


if __name__ == "__main__":
    screen = ScreenCommunication(screenPort)  # Its needed for system upgrade page

    try:
        startup_update()
    except:
        print('ERROR: Update System Failed.')

    create_connections()
    print('Ready to use.')
    screen.send('page p_main')  # set screen page to main page
    # Must move G28 (HOMING)

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
                                    motherboard._disconnect()  # restart connection
                                    create_connections(1)  # restart connection
                                    motherboard.send_now("M84 X Y")  # go home
                                    screen.send('page p_stopped')
                                    screen.last_received = ""  # restore last received command from screen
                                    received = ''  # restore last received command from screen
                                    time.sleep(2)  # wait
                                    break
                                elif 'wait-and-stop' in received:  # wait running process and after stop
                                    wait_and_stop = True
                            time.sleep(0.1)  # wait

                        if emergency_stop:
                            break

                        # total tube count update
                        total_tube_count += 1  # increment finish process count
                        print('DEBUG: total_tube_count:{}'.format(total_tube_count))
                        screen.send(
                            'p_main.lbl_yapilanTup.val=' + str(total_tube_count))  # update main page process counter
                        screen.send('p_running.lbl_yapilanTup.val=' + str(
                            total_tube_count))  # update process page process counter

                        if wait_and_stop:
                            motherboard.connection.cancelprint()  # cancel process queue
                            time.sleep(0.5)  # wait
                            motherboard.send_now("G1 X200 Y0 F8000")  # go park position
                            time.sleep(1)
                            screen.send('page p_main')  # return main page
                            break
                    if not wait_and_stop and not emergency_stop:
                        screen.send('page p_main')  # return main page
                    else:
                        wait_and_stop = False
                        emergency_stop = False
                elif 'ileri' in received:
                    # ileri:10
                    dist = float(received.split('-')[1])
                    Move.forward(motherboard, dist)
                elif 'sag' in received:
                    # sag:1
                    dist = float(received.split('-')[1])
                    Move.right(motherboard, dist)
                elif 'sol' in received:
                    # sol:0.1
                    dist = float(received.split('-')[1])
                    Move.left(motherboard, dist)
                elif 'geri' in received:
                    # geri:10
                    dist = float(received.split('-')[1])
                    Move.backward(motherboard, dist)
                elif 'yukari' in received:
                    dist = float(received.split('-')[1])
                    Move.up(motherboard, dist)
                elif 'down' in received:
                    dist = float(received.split('-')[1])
                    Move.down(motherboard, dist)
                elif 'home' in received:
                    # home
                    Move.home(motherboard, go_park_position=True)
                elif 'tup' in received:
                    if 'tut' in received:
                        # tup-tut
                        Servo.run(motherboard, 2, 90)
                    elif 'birak' in received:
                        # tup-birak
                        Servo.run(motherboard, 2, 120)
                    elif 'ver' in received:
                        # tup-ver
                        motherboard.start_printing(tup_ver_file)  # start process
                elif 'pompa' in received:
                    if 'doldur' in received:
                        # pompa-doldur
                        Motor.run(motherboard, 0, 540, 6000)
                    elif 'bosalt' in received:
                        # pompa-bosalt
                        Motor.run(motherboard, 0, -540, 6000)
                elif 'disp' in received:
                    # sol acik asagi -> P1
                    # sag acik yukari -> P3
                    if '1' in received:
                        if 'ac' in received:
                            # disp-1-ac
                            Servo.run(motherboard, 1, 140)
                        elif 'kapat' in received:
                            # disp - 1 - kapat
                            Servo.run(motherboard, 1, 90)
                    elif '2' in received:
                        if 'ac' in received:
                            # disp-2-ac
                            Servo.run(motherboard, 3, 130)
                        elif 'kapat' in received:
                            # disp-2-kapat
                            Servo.run(motherboard, 3, 90)
                elif 'kapak' in received:
                    #  cover turning
                    if 'duz' in received:
                        # kapak - duz
                        Motor.run(motherboard, 1, 300)
                    elif 'ters' in received:
                        # kapak-ters
                        Motor.run(motherboard, 1, -300)


                screen.last_received = ""
                received = ''

        except IndexError:
            pass
        except:
            raise
        time.sleep(0.1)
