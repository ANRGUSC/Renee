#   Copyright (c) 2017, Autonomous Networks Research Group. All rights reserved.
#   Developed by:
#   Autonomous Networks Research Group (ANRG)
#   University of Southern California
#   http://anrg.usc.edu/
 
#   Contributors:
#   Vidhi Goel
#   Jake Goodman
#   Jessica Koe
#   Jun Shin
#   Davina Zahabian
#   Pradipta Ghosh
#   Bhaskar Krishnamachari
   
#   Contacts:
#   Pradipta Ghosh <pradiptg@usc.edu>
#   Bhaskar Krishnamachari <bkrishna@usc.edu>
 
#   Permission is hereby granted, free of charge, to any person obtaining a copy 
#   of this software and associated documentation files (the "Software"), to deal
#   with the Software without restriction, including without limitation the 
#   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or 
#   sell copies of the Software, and to permit persons to whom the Software is 
#   furnished to do so, subject to the following conditions:

#   - Redistributions of source code must retain the above copyright notice, this
#       list of conditions and the following disclaimers.
#   - Redistributions in binary form must reproduce the above copyright notice, 
#       this list of conditions and the following disclaimers in the 
#       documentation and/or other materials provided with the distribution.
#   - Neither the names of Autonomous Networks Research Group, nor University of 
#       Southern California, nor the names of its contributors may be used to 
#       endorse or promote products derived from this Software without specific 
#       prior written permission.
#   - A citation to the Autonomous Networks Research Group must be included in 
#       any publications benefiting from the use of the Software.

#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
#   CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH 
#   THE SOFTWARE.


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
import math

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
			loc = Location(float(robotDict["x"]), float(robotDict["y"]), float(robotDict["z"]))
			self.nodes[rID] = self.xyzToLatLong(loc.getX(), loc.getY(), loc.getZ())
			index += 1

		srcDict = CFGReader.ReadConfig("swarm.cfg", "src")
		dstDict = CFGReader.ReadConfig("swarm.cfg", "dst")
		
		if not srcDict:
			sys.exit("No [src] found in swarm.cfg")
		if not dstDict:
			sys.exit("No [dst] found in swarm.cfg")

		srcLoc = Location(float(srcDict["x"]), float(srcDict["y"]), float(srcDict["z"]))
		dstLoc = Location(float(dstDict["x"]), float(dstDict["y"]), float(dstDict["z"]))
		self.nodes[index] = self.xyzToLatLong(srcLoc.getX(), srcLoc.getY(), srcLoc.getZ())
		self.nodes[index + 1] = self.xyzToLatLong(dstLoc.getX(), dstLoc.getY(), dstLoc.getZ())

		for i in range(11):
			self.currTimeInterval = i
			for rID in sorted(self.nodes.iterkeys()):
				nodeLoc = self.nodes[rID]
				latLongLoc = self.xyzToLatLong(nodeLoc.getX(), nodeLoc.getY(), nodeLoc.getZ())
				logLine = str(i) + '.0 nem:' + str(rID) + ' location gps ' + str(latLongLoc.getX()) + ',' + str(latLongLoc.getY())+ ',' +str(latLongLoc.getZ()) + '\n'
				self.logFile.write(logLine)
		self.currTimeInterval += 1


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
			nodeLocation = self.xyzToLatLong(nodeData[3], nodeData[4], nodeData[5])#Location(nodeData[3], nodeData[4], nodeData[5])
			self.nodes[nodeNum] = nodeLocation
			#self.receiveSocket.sendto('1 1 1 1', (MCAST_GRP, MCAST_PORT))
	  		#time.sleep(1)
	  		#self.receiveSocket.sendto('1 2 1 1', (MCAST_GRP, MCAST_PORT))
	  		#time.sleep(1)
	  		#self.receiveSocket.sendto('1 3 1 1', (MCAST_GRP, MCAST_PORT))
  		
  	def xyzToLatLong(self, x, y, z):
  		x = float(x)
  		y = float(y)
  		z = float(z)
  		r = 6731
  		long_0 = 0.0;
		#________________________________________________

		lon = long_0 + (x/r)
		lat = (2 * math.atan(math.exp(y/r))) - (math.pi / 2.0)

		lat *= (180.0/math.pi)
		lon *= (180.0/math.pi)

		# print("X", x)
		# print("Y", y)
		# print("Z", z)
		# print("lat:", lat)
		# print("long", lon)
		# print("LC: Lat, Long:", lat, lon)
		#________________________________________________
  		# r = math.sqrt(math.pow(x, 2) + math.pow(y, 2) + math.pow(z,2))
 
  		# lat = math.asin(z/r) * (180.0 / math.pi)
  		# lon = math.atan2(y, x) * (180.0 / math.pi)
  		# print("XYZ:", x, y, z)
  		# print("Lat/Long", lat, lon)

  		# return Location(lat, lon, 1.0)
  		#________________________________________________
  		# r = math.sqrt(math.pow(x, 2) + math.pow(y, 2) + math.pow(x,2))

  		# lat = math.asin(z/r) * (180/math.pi)
  		# lon = 0.0
  		# if (x > 0):
  		# 	lon = math.atan(y/x) * (180/math.pi)
  		# elif (y > 0):
  		# 	lon = math.atan(y/x) * (180/math.pi) + 180
  		# else:
  		# 	lon = math.atan(y/x) * (180/math.pi) - 180

  		return Location(lat, lon, 1.0)


  	def updateTracker(self, nodeNumber):
		if nodeNumber in self.messageTracker:
			self.messageTracker[nodeNumber] +=1;
		else:
			self.messageTracker[nodeNumber] = 1;

	def outputNodeData(self):
		while True:
			for node in sorted(self.nodes):
				logLine = str(self.currTimeInterval) + '.0 nem:' + str(node) + ' location gps ' + str(self.nodes[node].getX()) + ',' + str(self.nodes[node].getY())+ ',' +str(self.nodes[node].getZ()) + '\n'
				self.logFile.write(logLine)
			self.currTimeInterval += 1
			time.sleep(1)



	

if __name__ == '__main__':
	compiler = LogCompiler(6666)
	compiler.start()

