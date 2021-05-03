import requests
import os
import re
import time
import logging

from .Encryption import Encryptor

from .Util import unzip, get_file_lines, write_file
# from .ScreenUploader import screen_upload_tft_file

version_file_path = './version.txt'
__VERSION__ = get_file_lines(version_file_path)[0].strip()


class GithubDownloader:
    def __init__(self, url=None, encrypted=False, path=".", unzip_path="."):
        # url = 'https://api.github.com/repos/MetaIndustry/printotype-firmware/releases/latest'
        self.url = url
        self.path = path + "/"
        self.unzipPath = self.path + unzip_path + "/"
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
        return __VERSION__.strip()

    def get_latest_version(self):
        return str(self.json['name'])

    def is_new_version(self):
        regex = '(\d+).(\d+).(\d+)'
        latest = self.get_latest_version()
        match = re.search(regex, latest)
        print('DEBUG VERSION:\n\tRemote Latest: {}\tCurrent: {}'.format(latest, self.get_current_version()))
        if match:
            if latest == self.get_current_version():
                logging.info('System up to date. {}'.format(__VERSION__))
                return False
            __NEW_VERSION__ = match.group()
            logging.info('There is new version: {}'.format(__NEW_VERSION__))
            return True

    def download(self):
        logging.info('Download Started...')
        logging.info('Zip File Name: {}. File Size: {}.'.format(self.get_zip_file_name(), self.get_file_size()))
        with open(self.encryptedPath + self.get_zip_file_name(), 'wb') as f:
            start_download_time = time.time()
            for chunk in self.get_stream().iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        logging.info('Download Finished in {:.2f} seconds.'.format(time.time() - start_download_time))

    def upgrade_system(self):
        if self.is_new_version():
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

                    # screen upgrade daha sonra eklenecek
                    # screen_upload_tft_file('file_path')

                write_file(version_file_path, self.get_latest_version())
            except (FileNotFoundError, OSError):
                logging.error('Firstly, you need to download the file!')
                pass
