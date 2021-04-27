import os
import sys
import glob
try:
    import winreg
except ImportError:
    try:
        import _winreg as winreg
    except ImportError:
        pass

import serial


# CrossPlatform
def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    print(result)
    return result


# Rpi
def serialList():
    if os.name == "nt":
        candidates = []
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, "HARDWARE\\DEVICEMAP\\SERIALCOMM"
            )
            i = 0
            while True:
                candidates += [winreg.EnumValue(key, i)[1]]
                i += 1
        except Exception:
            pass
    else:
        candidates = (
                glob.glob("/dev/ttyUSB*")
                + glob.glob("/dev/ttyACM*")
                + glob.glob("/dev/tty.usb*")
                + glob.glob("/dev/cu.*")
                + glob.glob("/dev/cuaU*")
                + glob.glob("/dev/ttyS*")
                + glob.glob("/dev/rfcomm*")
        )
    return candidates


def shutdown():
    os.system('omxplayer --no-keys /etc/Printotype/intro.mp4')  # outro play  ( intro service den cekilecek kullanımı )
    # time.sleep(15)  # video süresi - 2
    os.system('sudo shutdown -a now')
