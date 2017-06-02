import arrow
from NSFutilities import *
from multiprocessing import Process
import os


class DB_status:
    def __init__(self, **kwargs):
        self.starttime = arrow.utcnow()
        self.log_size = 0
        self.log_name = get_log_size()[0]
        Process(target=update_status, args=()).start()

    def update_status(self):
        while True:
            log_size = get_log_size()[1]
            if log_size != self.log_size:
                self.log_size = log_size
            os.system('clear')
            printForm(self)

    def printForm(self):
        print("NSF Logger Started At: {}").format(self.starttime)
        print("mysql '{}' table size: {} MB").format(self.log_name, self.log_size)
