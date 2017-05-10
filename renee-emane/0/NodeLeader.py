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
import sys

MCAST_GRP = '10.99.0.255'
MCAST_PORT = 6666


def validateArguments():
	if len(sys.argv) != 2:
		sys.exit("Incorrect number of arguments.\nCorrect Format: ./NodeLeader.py <int: node number>");
	try:
		int(sys.argv[1])
	except ValueError:
		sys.exit("Incorrect argument type. \nCorrect Format: ./NodeLeader.py <int: node number>");

class NodeLeader(object):
	def __init__(self, nID, receivePort):
		self.__receivePort = receivePort
		self.receiveSocket = None
		self.nodes = {}	
		self.id = nID

	def start(self):
		self.setupConnection()

	def setupConnection(self):
		self.receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.receiveSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.receiveSocket.bind(('', self.__receivePort))

		locGen = Thread(target = self.broadcastLocation)
		locGen.start()

		listener = Thread(target = self.recieveBroadcasts)
		listener.start()

	def broadcastLocation(self):
		xCounter = 0;
		while True:
			locationData = str(self.id) + ' ' + str(xCounter) + ' ' + str(xCounter) + ' 1'
			self.receiveSocket.sendto(locationData, (MCAST_GRP, MCAST_PORT))
			xCounter += 1
	  		time.sleep(1)
	
	def	recieveBroadcasts(self):
		while True:
			data = self.receiveSocket.recv(10240)
			data = data.strip()
			print("Recieved Data:", data)
			nodeData = data.split(' ')
			nodeNum = nodeData[0]
			nodeLocation = Location(nodeData[1], nodeData[2], nodeData[3])
			self.nodes[nodeNum] = nodeLocation	

if __name__ == '__main__':
	validateArguments()
	leader = NodeLeader(sys.argv[1], 6666)
	leader.start()
