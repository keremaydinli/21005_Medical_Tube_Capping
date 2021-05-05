import time
import glob
import logging
import os

# from Updater.Update_System import GithubDownloader, get_version_file_path
# from Updater.ScreenUploader import screen_upload_tft_file
from Updater.Util import write_file
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

# Variables
screen_upload_file = 'gui.tft'
# send_file = 'temp_send_g_code_file.txt'
send_file = 'test_gcode.txt'
feedrate = ' F8000'
total_tube_count = 0
emergency_stop = False
wait_and_stop = False
extract_files_path = "./Files/EXTRACT/"


def startup_update():
    if check_internet_connection():
        print('6')
        gd = GithubDownloader(url, encrypted=True, path='./Files', unzip_path=extract_files_path)
        if gd.is_new_version():  # if new version
            gd.upgrade_system()  # system upgrade
            if glob.glob(extract_files_path + screen_upload_file,
                         recursive=True):  # if screen_upload_file in downloaded files
                screen_upload_file_path = os.path.abspath(screen_upload_file)  # get abspath
                screen.send('page p_update')
                screen_upload_tft_file(screen_upload_file_path)  # upload screen
            write_file(get_version_file_path(), gd.get_latest_version())
            screen.send('page p_restart')
            time.sleep(3)  # wait
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


if __name__ == "__main__":
    screen = ScreenCommunication(screenPort)  # Its needed for system upgrade page

    #     try:
    #         startup_update()
    #     except:
    #         print('ERROR: Update System Failed.')

    create_connections()
    screen.send('page p_main')  # set screen page to main page
    print('Ready to use.')

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
                                    create_connections(1)  # restart connection and wait 1 sec
                                    motherboard.send_now("M84 X Y")  # go home
                                    screen.send('page p_stopped')
                                    screen.last_received = ""  # restore last received command from screen
                                    received = ''  # restore last received command from screen
                                    time.sleep(2)  # wait
                                    # maybe add stopping screen
                                    break
                                elif 'wait-and-stop' in received:  # wait running process and after stop
                                    wait_and_stop = True
                            time.sleep(0.1)  # wait
                        if emergency_stop:
                            emergency_stop = False
                            break

                        # total tube count update
                        total_tube_count += 1  # increment finish process count
                        print('DEBUG: total_tube_count:{}'.format(total_tube_count))
                        screen.send(
                            'p_main.lbl_yapilanTup.val=' + str(total_tube_count))  # update main page process counter
                        screen.send('p_running.lbl_yapilanTup.val=' + str(
                            total_tube_count))  # update process page process counter

                        if wait_and_stop:
                            wait_and_stop = False
                            motherboard.connection.cancelprint()  # cancel process queue
                            time.sleep(0.5)  # wait
                            motherboard.send_now("G1 X200 Y0 F8000")  # go park position
                            time.sleep(1)
                            screen.send('page p_main')  # return main page
                            break

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
                elif 'up' in received:
                    dist = float(received.split('-')[1])
                    motherboard.send_now('G91')
                    motherboard.send_now('G0 Z' + str(dist) + feedrate)
                    motherboard.send_now('G90')
                elif 'down' in received:
                    dist = float(received.split('-')[1])
                    motherboard.send_now('G91')
                    motherboard.send_now('G0 Z-' + str(dist) + feedrate)
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
                elif 'dispanser' in received:
                    if 'ac' in received:
                        motherboard.send_now('M280 P3 S120')
                    elif 'kapat' in received:
                        motherboard.send_now('M280 P3 S70')


                screen.last_received = ""
                received = ''

        except:
            raise
        time.sleep(0.1)
