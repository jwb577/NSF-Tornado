import MySQLdb
import arrow
import random

myDB = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='hurricane', db='logger_data')
cursor = myDB.cursor()
for counter in range(0,100):
	currenttime = arrow.now()
	cursor.execute("INSERT INTO log VALUES ('{}{}','{}');".format(str(currenttime.timestamp),str(currenttime.microsecond/1e6), str(random.randrange(1000000,2000000,1))))
	myDB.commit()
	print "{} inserted correctly".format(counter)
