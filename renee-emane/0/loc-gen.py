#!/usr/bin/env python
import time
import os
import sys

directory = os.path.dirname('scenario.eel')

def validateArguments():
	if len(sys.argv) != 2:
		sys.exit("Incorrect number of arguments.\nCorrect Format: ./loc-gen.py <int: node number>");
	try:
		int(sys.argv[1])
	except ValueError:
		sys.exit("Incorrect argument type. \nCorrect Format: ./loc-gen.py <int: node number>");

def writeLocationForNodeNumber(nodeNumber):
	f  = open('/home/dev/401/emane-tutorial/scenario/scenario.eel', 'a', 1)
	counter = 0
	while True:
		logLine = str(counter) + '.0 nem:' + str(nodeNumber) + ' location gps ' + str(counter) + ',' + str(counter) + '\n'
		f.write(logLine)
		counter += 1
		if counter > 40 :	
			time.sleep(1)

		if counter == 400:
			break

if __name__ == '__main__':
	validateArguments()
	nodeNum = int(sys.argv[1])
	writeLocationForNodeNumber(nodeNum)

