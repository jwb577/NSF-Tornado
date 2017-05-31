from NSFutilities import *
import time
import arrow

list = []
utc = arrow.utcnow()
timestamp = str(utc.timestamp) +'.'+ str(utc.microsecond)
for counter in range(0,10000):
	list.append((counter, 'test CAN message'))
start = time.time()
log_message_block(list)
end = time.time()
print(end - start)
