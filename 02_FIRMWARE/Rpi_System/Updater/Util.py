import os
import zipfile
import requests
import datetime


####### FILE OPERATIONS ##########
def unzip(file, path):
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(path)
    os.remove(file)


def get_file_lines(file):
    f = open(file, "r")
    return f.readlines()


def get_file_line(file):
    f = open(file, "r")
    return f.readline()


def write_file(file, line):
    f = open(file, "w")
    f.write('{}\n'.format(line))
    f.close()


################################

####### OS OPERATIONS ##########
def is_folder_exist(path):
    return os.path.isdir(path)


def is_file_exist(path):
    return os.path.isfile(path)


################################

####### INTERNET OPERATIONS ##########
def check_internet_connection():
    url = "http://www.google.com"
    timeout = 3
    try:
        request = requests.get(url, timeout=timeout)
        print("[INFO] Connected to the Internet")
        return True
    except (requests.ConnectionError, requests.Timeout):
        print("[INFO] No internet connection.")
    return False


################################

######### TIME OPERATIONS #############
def get_full_time():
    dateDay = datetime.datetime.strftime(datetime.datetime.now(), '%d')
    dateMonth = datetime.datetime.strftime(datetime.datetime.now(), '%m')
    timeMin = datetime.datetime.strftime(datetime.datetime.now(), '%M')
    timeHour = datetime.datetime.strftime(datetime.datetime.now(), '%H')
    print('Tarih: ' + dateDay + '/' + dateMonth, 'Saat: ' + timeHour + ':' + timeMin)

    return dateDay, dateMonth, timeMin, timeHour
