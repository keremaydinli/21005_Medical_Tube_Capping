import requests
import os
import re
import time
import logging

from .Encryption import Encryptor
from .Util import unzip, getFileLines, write_file
from .Terminal import Command

version_file_path = './version.txt'
__VERSION__ = getFileLines(version_file_path)[0]


class GithubDownloader:
    def __init__(self, url=None, encrypted=False, auto_download=True, path=".", unzip_path="."):
        # url = 'https://api.github.com/repos/MetaIndustry/printotype-firmware/releases/latest'
        self.url = url
        self.path = path + "/"
        self.unzipPath = self.path + unzip_path + "/"
        self.AutoDownload = auto_download
        self.context = requests.get(self.url)
        self.json = self.context.json()
        self.packageName = None
        self.stream = None
        self.fileName = None
        self.size = None
        self.process = None
        self.zipIndex = 0
        self.encryptedPath = self.path + '/'
        self.decryptedPath = self.path + '/_'
        if encrypted:
            self.encryptor = Encryptor()
        else:
            self.encryptor = None
        logging.basicConfig(filename="./Logs/system.log", level=logging.NOTSET)

    def set_encryptor_key(self, encryptor):
        self.encryptor.load_key(encryptor)

    def get_package_name(self):
        self.packageName = self.json['assets'][self.zipIndex]['url']
        return self.packageName

    def get_stream(self):
        self.stream = requests.get(self.get_package_name(), headers={"Accept": "application/octet-stream"})
        return self.stream

    def get_zip_file_name(self):
        self.fileName = self.json['assets'][self.zipIndex]['name']
        return self.fileName

    def get_file_size(self):
        self.size = self.json['assets'][self.zipIndex]['size']
        return self.size

    def decrypt_file(self, file1, file2):
        self.encryptor.decrypt_file(file1, file2)

    def set_zip_index(self, index):
        self.zipIndex = index

    @staticmethod
    def get_current_version():
        return __VERSION__

    def get_latest_version(self):
        return str(self.json['name'])

    def is_new_version(self):
        regex = '(\d+).(\d+).(\d+)'
        latest = self.get_latest_version()
        match = re.search(regex, latest)
        if match:
            if latest == __VERSION__:  # TODO: latest and version are same but not match
                logging.info('System up to date. {}'.format(__VERSION__))
                return False
            __NEW_VERSION__ = match.group()
            logging.info('There is new version: {}'.format(__NEW_VERSION__))
            return True

    def download(self):
        logging.info('Download Started...\n[INFO] Zip File Name: {}. File Size: {}.'
                     .format(self.get_zip_file_name(), self.get_file_size()))
        with open(self.encryptedPath + self.get_zip_file_name(), 'wb') as f:
            startDownloadTime = time.time()
            for chunk in self.get_stream().iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        logging.info('Download Finished in {:.2f} seconds.'.format(time.time() - startDownloadTime))

    def upgrade_system(self):
        if self.is_new_version():
            if self.AutoDownload:
                self.download()

            try:
                if self.encryptor:
                    logging.info('Decrypting...')
                    self.decrypt_file(self.encryptedPath + self.get_zip_file_name(),
                                      self.decryptedPath + self.get_zip_file_name())
                    os.remove(self.encryptedPath + self.get_zip_file_name())
                    unzip(self.decryptedPath + self.get_zip_file_name(), self.unzipPath)
                    logging.info('Decrypting Finished.')
                    logging.debug('System Upgraded.')
                self.upgrade_screen()
                write_file(version_file_path, self.get_latest_version())
            except (FileNotFoundError, OSError):
                logging.error('Firstly, you need to download the file!')
                pass

    def upgrade_screen(self):
        logging.info('Screen is Upgrading...')
        # c = Command("python3 upgrader.py kaucukScreenDesign.tft")
        c = Command("dir ..")
        if c.run(9999) == 0:
            logging.debug('Screen Upgraded.')
