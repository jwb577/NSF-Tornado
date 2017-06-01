from canTools import CanTools
from NSFutilities import *
from multiprocessing import Process, Queue

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
                block.append(str(q.get()))
            elif len(block) == self.blocksize:
                print('attempting to log block to mysql')
                log_message_block(block)
            else:
                pass

    def listen(self, bus, q):
        while True:
       	    message = bus.readMessageRaw()
            q.put(message)

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
    bus0 = CanTools(can0.interface)
    bus1 = CanTools(can1.interface)
    can1.listen(bus1)
    can0.listen(bus0)
