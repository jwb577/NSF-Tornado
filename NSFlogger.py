

from canTools import CanTools
from NSFutilities import *
from tornado import gen
from tornado.queues import Queue
from tornado.ioloop import IOLoop
import arrow


class NSFlogger:
    def __init__(self, **kwargs):
        self.q = Queue(maxsize=0)
        try:
            self.blocksize = kwargs.get('blocksize')
            self.interface = kwargs.get('interface')
        except KeyError:
            print ('KeyError on NSFlogger constructor')
    
    @gen.coroutine
    def push(self, q):
        block = []
        while self.running:
            if q.qsize() > self.blocksize and len(block)<self.blocksize:
                block.append(q.get())
            elif len(block) == self.blocksize:
                log_message_block(block)
                del block[:]
            else:
                pass
    @gen.coroutine
    def listen(self, bus, q):
        while True:
       	    message = bus.readMessage()
            utc = arrow.utcnow()
            timestamp = [str(utc.timestamp),str(utc.microsecond)].join('.')
            q.put((timestamp, message))
    
    @gen.coroutine
    def start(self):
        bus = CanTools(self.interface)
        self.running = True
        IOLoop.current().spawn_callback(listen(bus, self.q))
        IOLoop.current().spawn_callback(push(self.q))
        yield quit

    def stop(self):
        self.running = False

    @gen.coroutine
    def quit(self):
        try:
            while self.running;
        finally: print ("Stop logging on {}".fomat(self.interface))
 
if __name__ == '__main__':
    can0 = NSFlogger(blocksize=1000, interface='can0')
    can1 = NSFlogger(blocksize=1000, interface='can1')
    can1.start()
    can0.start()
