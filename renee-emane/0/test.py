#!/usr/bin/env python
import time
import os

directory = os.path.dirname('scenario.eel')

f  = open('/home/dev/401/emane-tutorial/scenario/scenario.eel', 'w')
f.truncate()
counter = 0
while True:
	for i in range(1, 11):
		logLine = str(counter) + '.0 nem:' + str(i) + ' location gps ' + str(counter) + ',' + str(counter) + '\n'
		f.write(logLine)
	counter += 1

	if counter > 40 :	
		time.sleep(1)

	if counter == 400:
		break




