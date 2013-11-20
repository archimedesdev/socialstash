__author__ = 'prad'


import time
import datetime
import calendar

value = datetime.datetime(2011, 1, 1, 3, 15, 29)
date_time = value.strftime("%Y-%m-%d %H:%M:%S")
pattern = '%Y-%m-%d %H:%M:%S'
epoch_utc = int(calendar.timegm(time.strptime(date_time, pattern)))
new_utc = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(epoch_utc))
print str(value)
print epoch_utc
print str(new_utc)
