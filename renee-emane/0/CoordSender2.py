#!/usr/bin/python

###### LogCompiler.py ######
# Author: Jake Goodman & Jess Koe		#
######################

#socat STDIO UDP4-DATAGRAM:10.99.0.255:6666,bind=:6666,broadcast
#This sets you up to broadcast and receive messages on port 6666

import socket
from threading import Thread
from Location import Location
import time

MCAST_GRP = '10.99.0.255'
MCAST_PORT = 6666

class CoordinateSender(object):
	def __init__(self, receivePort):
		self.__receivePort = receivePort
		self.receiveSocket = None
		self.currTimeInterval = 0
		self.nodes = {}	
		#self.logFile = open('/home/emane-tutorial/scenario/scenario.eel', 'w', 1)

	def start(self):
		self.setupConnection()

		output = Thread(target = self.outputNodeData)
		output.start()


	def setupConnection(self):
		self.receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.receiveSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.receiveSocket.bind(('', self.__receivePort))

		connection = Thread(target = self.listen)
		connection.start()

	def listen(self):
		yCounter = 5;
		while (yCounter <= 200):
			locationData1 = '1 100 200 0'
			locationData2 = '2 200 '+ str(yCounter) + ' 0'
			locationData3 = '3 300 200 0'
			self.receiveSocket.sendto(locationData1, (MCAST_GRP, MCAST_PORT))
	  		self.receiveSocket.sendto(locationData2, (MCAST_GRP, MCAST_PORT))
	  		self.receiveSocket.sendto(locationData3, (MCAST_GRP, MCAST_PORT))
	  		time.sleep(1)
	  		data= self.receiveSocket.recv(10240)
			data = data.strip()
			print("Recieved Data:", data)
			nodeData = data.split(' ')
			nodeNum = nodeData[0]
			nodeLocation = Location(nodeData[1], nodeData[2], nodeData[3])
			self.nodes[nodeNum] = nodeLocation
			print(len(self.nodes))
			yCounter += 1
			

	def outputNodeData(self):
		while True:
			for node in self.nodes:
				logLine = str(self.currTimeInterval) + '.0 nem:' + str(node) + ' location gps ' + str(self.nodes[node].getX()) + ',' + str(self.nodes[node].getY())+ ',' +str(self.nodes[node].getZ()) + '\n'
				#self.logFile.write(logLine)
			self.currTimeInterval += 1
			time.sleep(3)

	

if __name__ == '__main__':
	sender = CoordinateSender(6666)
	sender.start()