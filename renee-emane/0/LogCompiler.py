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
import pickle
import CFGReader

class LogCompiler(object):
	def __init__(self, receivePort):
		self.__receivePort = receivePort
		self.receiveSocket = None
		self.currTimeInterval = 0
		self.nodes = {}	
		self.messageTracker = {}
		#self.logFile = open('/home/dev/401/emane-tutorial/scenario/scenario.eel', 'w', 1)
		self.logFile = open('../scenario/scenario.eel', 'w', 1)
		self.initLogFileFromCfg()


	def initLogFileFromCfg(self):
		done = False
		index = 1

		while done == False:
			section = "R" + str(index)
			robotDict = CFGReader.ReadConfig("swarm.cfg", section)
			if not robotDict:
				done = True
				break

			rID = robotDict['rid']
			loc = Location(float(robotDict["lat"]), float(robotDict["lon"]), float(robotDict["alt"]))
			self.nodes[rID] = loc
			index += 1

		srcDict = CFGReader.ReadConfig("swarm.cfg", "src")
		dstDict = CFGReader.ReadConfig("swarm.cfg", "dst")
		
		if not srcDict:
			sys.exit("No [src] found in swarm.cfg")
		if not dstDict:
			sys.exit("No [dst] found in swarm.cfg")

		srcLoc = Location(float(srcDict["lat"]), float(srcDict["lon"]), float(srcDict["alt"]))
		dstLoc = Location(float(dstDict["lat"]), float(dstDict["lon"]), float(dstDict["alt"]))
		self.nodes[index] = srcLoc
		self.nodes[index + 1] = dstLoc

		for i in range(11):
			self.currTimeInterval = i
			for rID in sorted(self.nodes.iterkeys()):
				nodeLoc = self.nodes[rID]
				logLine = str(i) + '.0 nem:' + str(rID) + ' location gps ' + str(nodeLoc.getLat()) + ',' + str(nodeLoc.getLon())+ ',' +str(nodeLoc.getAlt()) + '\n'
				self.logFile.write(logLine)


	def start(self):
		self.setupConnection()

		output = Thread(target = self.outputNodeData)
		output.start()


	def setupConnection(self):
		self.receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.receiveSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.receiveSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.receiveSocket.bind(('', self.__receivePort))

		connection = Thread(target = self.listen)
		connection.start()

	def listen(self):
		messageCounter = 0;
		#self.messageTracker['002'] =1;
		while True:
			socketData = self.receiveSocket.recv(10240)

			data= pickle.loads(socketData)
			data = data.strip()
			nodeData = data.split(' ')
			senderID = nodeData[0]
			messageID = nodeData[1]
			if ((nodeData[0] + nodeData[1]) in self.messageTracker):
				randomLoc = None
				#self.receiveSocket.sendto(nodeData[1] + ' ' + nodeData[2] + ' ' + nodeData[3] + ' ' + nodeData[4] + ' ' + nodeData[5] + ' pass it on', (MCAST_GRP, MCAST_PORT))
			else:
				newPickle = nodeData[0] + ' ' + nodeData[1] + ' ' + nodeData[2] + ' ' + nodeData[3] + ' ' + nodeData[4] + ' ' + nodeData[5] + ' LC: pass it on'
				pickledData = pickle.dumps(newPickle)
				self.receiveSocket.sendto(pickledData,('<broadcast>', 6789))
				messageCounter +=1
				self.updateTracker(nodeData[0]+ nodeData[1])
			nodeNum = nodeData[2]
			nodeLocation = Location(nodeData[3], nodeData[4], nodeData[5])
			self.nodes[nodeNum] = nodeLocation
			#self.receiveSocket.sendto('1 1 1 1', (MCAST_GRP, MCAST_PORT))
	  		#time.sleep(1)
	  		#self.receiveSocket.sendto('1 2 1 1', (MCAST_GRP, MCAST_PORT))
	  		#time.sleep(1)
	  		#self.receiveSocket.sendto('1 3 1 1', (MCAST_GRP, MCAST_PORT))
  		
  	def updateTracker(self, nodeNumber):
		if nodeNumber in self.messageTracker:
			self.messageTracker[nodeNumber] +=1;
		else:
			self.messageTracker[nodeNumber] = 1;

	def outputNodeData(self):
		while True:
			for node in sorted(self.nodes):
				logLine = str(self.currTimeInterval) + '.0 nem:' + str(node) + ' location gps ' + str(self.nodes[node].getLat()) + ',' + str(self.nodes[node].getLon())+ ',' +str(self.nodes[node].getAlt()) + '\n'
				self.logFile.write(logLine)
			self.currTimeInterval += 1
			time.sleep(1)



	

if __name__ == '__main__':
	compiler = LogCompiler(6666)
	compiler.start()
