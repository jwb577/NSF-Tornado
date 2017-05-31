from queue import Queue
from canTools import CanTools
from concurrent.futures import ThreadPoolExecutor
from NSFutilities import *


class NSFlogger:
    def __init__(self, **kwargs):
        self.q = Queue(maxsize=0)
        try:
            self.blocksize = kwargs.get('blocksize')
            self.interface = kwargs.get('interface')
        except KeyError:
            print ('KeyError on NSFlogger constructor')
    def push(self):
        block = []
        while self.running:
            if q.qsize() > self.blocksize and len(block)<self.blocksize:
                block.append(q.get())
            elif len(block) == self.blocksize:
                log_message_block(block)
            else: pass

    def listen(self, bus):
        while self.running:
            q.put(bus.readMessageRaw())

    def start(self):
        bus = CanTools(self.interface)
        self.running = True
        with ThreadPoolExecutor(max_workers=2) as worker:
            worker.submit(self.listen, bus)
            worker.submit(self.push)

    def stop(self):
        self.running = False

if __name__ == '__main__':
    can0 = NSFlogger(blocksize=1000, interface='can0')
    can1 = NSFlogger(blocksize=1000, interface='can1')
    can0.start()
    can1.start()
