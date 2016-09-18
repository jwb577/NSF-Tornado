from canTools import CanTools
from NSFutilities import *
from multiprocessing import Process, Queue
import arrow


class NSFlogger:
    def __init__(self, **kwargs):
        self.q = Queue(maxsize=0)
        try:
            self.blocksize = kwargs.get('blocksize')
            self.interface = kwargs.get('interface')
        except KeyError:
            print ('KeyError on NSFlogger constructor')
    def push(self, q):
        print('push started on '+ self.interface)
        block = []
        while self.running:
            if q.qsize() > self.blocksize and len(block)<self.blocksize:
                block.append(q.get())
                print (self.interface)
            elif len(block) == self.blocksize:
                print('attempting to log block to mysql')
                log_message_block(block)
                del block[:]
            else:
                pass

    def listen(self, bus, q):
        print ('started to listen on ' + self.interface)
        while True:
       	    message = bus.readMessage()
            utc = arrow.utcnow()
            timestamp = str(utc.timestamp) + '.' + str(utc.microsecond)
            q.put((timestamp, message))

    def start(self):
        bus = CanTools(self.interface)
        self.running = True
        print('started on '+self.interface)
        Process(target=self.listen, args=(bus,self.q)).start()
        Process(target=self.push, args=(self.q,)).start()

    def stop(self):
        self.running = False

if __name__ == '__main__':
    can0 = NSFlogger(blocksize=1000, interface='can0')
    can1 = NSFlogger(blocksize=1000, interface='can1')
    can1.start()
    can0.start()
