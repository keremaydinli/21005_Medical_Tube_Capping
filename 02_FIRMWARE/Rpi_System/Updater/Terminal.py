import subprocess
import threading
import logging


class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            logging.info('Terminal Thread started')
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()
            logging.info('Terminal Thread finished')

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            logging.info('Terminating process')
            self.process.terminate()
            thread.join()
        return self.process.returncode
