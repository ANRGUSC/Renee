###### Robot.py ######
# Author: Davina Zahabian #
# This is the class definition of the Robot class, which is an instance of a node in a flow configuration. #
######################

import socket
import struct
import os
import sys
from threading import Thread
import pickle
import time
from Location import Location
import Flow
import Graph
import CFGReader
import math

MCAST_GRP = '10.99.0.255'
MCAST_PORT = 6666

class Robot(object):

	# Constructor
	def __init__(self, rid, location, fid, graph, sendPort, receivePort, isSrc=False, isDest=False):
		self.sendPort = sendPort
		self.receivePort = receivePort
		self.rid = rid
		self.location = location
		self.oldlocation = self.location
		self.fid = fid
		self.graph = graph

		# Sockets for sending and receiving messages
		self.receiveSocket = None
		self.sendSocket = None
		self.isSrc = isSrc
		self.isDest = isDest

		# Map RID to current location of other robots in the flow.
		self.all_robots = {}
	 	self.messageCounter = 0;


	def __str__(self):
		return ("R ID: %s | X: %s | Y: %s | Z: %s" % (self.rid, self.location.x, self.location.y, self.location.z))

	
	# Fetch Robot from the config file
	def fetchID(self):
		rid = Helper.ReadConfig("model/robot.cfg", "Robot Information")['id']
		#print ("RID %s" %rid)
		self.setID(rid)

	# Set the robot ID
	def setID(self, rid):
		self.rid = rid

	# Get the robot ID
	def getID(self):
		return self.rid

	# Fetch the flow from config file and also the details of source and dest end hosts
	def fetchFlow(self):
		fid = Helper.ReadConfig("model/flow.cfg", "Flow Information")['id']

		sid = Helper.ReadConfig("model/flow.cfg", "Flow Information")['src']
		s_loc = Location(Helper.ReadConfig("model/location_e.cfg", sid)['x'],
						Helper.ReadConfig("model/location_e.cfg", sid)['y'],
						Helper.ReadConfig("model/location_e.cfg", sid)['z'])
		src = Host.Host(sid, s_loc)

		did = Helper.ReadConfig("model/flow.cfg", "Flow Information")['dest']
		d_loc = Location(Helper.ReadConfig("model/location_e.cfg", did)['x'],
						Helper.ReadConfig("model/location_e.cfg", did)['y'],
						Helper.ReadConfig("model/location_e.cfg", did)['z'])
		dest = Host.Host(did, d_loc)

		flow = Flow.Flow(fid, src, dest)
		self.setFlow(flow)

	# Set the Flow for this robot
	def setFlowAndGraph(self, flow, robots):
		self.flow = flow
		self.graph = Graph.Graph(robots)

	# Get the flow for this robot
	def getFlow(self):
		return self.flow

	# Fetch the location of the robot from config file
	def fetchLocation(self):
		loc = Location(Helper.ReadConfig("model/location.cfg", "Location")['x'],
						Helper.ReadConfig("model/location.cfg", "Location")['y'],
						Helper.ReadConfig("model/location.cfg", "Location")['z'])
		#print ("Location x %d y %d z %d " %(loc.x, loc.y, loc.z))
		self.setLocation(loc)

	def setLocation(self, loc):
		self.oldLocation = self.location
		self.location = loc

	def getLocation(self):
		return self.location

	def getOldLocation(self):
		return self.oldLocation

	# Set up connections with other robots upon instantiation (all nodes are known at runtime, nodes preconfigured)
	def establishConnections(self):
		# set up both sockets
		self.sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.sendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sendSocket.bind(('', self.sendPort))

		# self.receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# self.receiveSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		# self.receiveSocket.bind(('', self.receivePort))

		# Start thread to wait for messages from other Robots
		recieveThread = Thread(target = self.listenForBroadcasts)
		recieveThread.start()

		# Start thread to periodically generate location and broadcast to network
		sendThread = Thread(target = self.commController)
		sendThread.start() 

		motionThread = Thread(target = self.motionController)
		motionThread.start()


	# Receive incoming messages from other Robots about location changes, and process them
	def listenForBroadcasts(self):
		while True:
			loc, IP = self.sendSocket.recvfrom(10240)

			loc = pickle.loads(loc)
			IP = str(IP[0])
			nodeData = loc.split(' ')
			senderID = nodeData[0]
			messageID = nodeData[1]
			positionNode = nodeData[2]
			newX = float(nodeData[3])
			newY = float(nodeData[4])
			newZ = float(nodeData[5])
			newLocation = Location(newX, newY, newZ)
			self.updateLocation(positionNode, newLocation)

	# Starts comm controller thread to send pickle of location, IP
	def startComController(self, new_location=None, port=None):
		transmission = Thread(target = self.commController(new_location, port))
		transmission.start()


	# Update new location of a Robot in the map and in the graph, call to update motion of this robot
	def updateLocation(self, rID, location):
		self.all_robots[rID] = location
		self.graph.updateGraph(rID, self.all_robots)
			

	# Periodically move towards desired location in configurable intervals
	def motionController(self):
		while True:
			newLoc = self.graph.getCentroid(self)
			locMovementVector = calcDirectionVector(self.location, newLoc)

			moveX = self.location.getX() + (locMovementVector.getX()*5)
			moveY = self.location.getY() + (locMovementVector.getY()*5)
			moveZ = self.location.getZ() + (locMovementVector.getZ()*5)
			moveLoc = Location(moveX, moveY, moveZ)

			self.setLocation(moveLoc)
		 	self.updateLocation(self.rid, moveLoc)
		 	time.sleep(0.5)

	def commController(self):
		# format location data for sending
		while True:
			newID = str(self.rid) + " " + str(self.messageCounter)
	 		myLoc = self.location
			locationData = newID + ' ' + str(self.rid) + ' '+ str(myLoc.getX()) + ' '+ str(myLoc.getY()) + ' '+ str(myLoc.getZ())
			data_string = pickle.dumps(locationData)
			self.sendSocket.sendto(data_string, (MCAST_GRP, MCAST_PORT))
			self.messageCounter = self.messageCounter + 1
			time.sleep(0.5)


def validateArguments():
	if len(sys.argv) != 2:
		sys.exit("Incorrect number of arguments");
	return sys.argv[1]
	

def initRobotFromCfg(runtimeID):
	done = False
	index = 1
	robots = []
	thisRobot = None

	srcDict = CFGReader.ReadConfig("swarm.cfg", "src")
	dstDict = CFGReader.ReadConfig("swarm.cfg", "dst")
	
	if not srcDict:
		sys.exit("No [src] found in swarm.cfg")
	if not dstDict:
		sys.exit("No [dst] found in swarm.cfg")

	srcFID = srcDict["fid"]
	srcLoc = Location(float(srcDict["x"]), float(srcDict["y"]), float(srcDict["z"]))
	srcNode = Robot("-1", srcLoc, srcFID, None, 6666, 6666, isSrc = True)
	robots.append(srcNode)

	dstFID = dstDict["fid"]
	dstLoc = Location(float(dstDict["x"]), float(dstDict["y"]), float(dstDict["z"]))
	dstNode = Robot("-2", dstLoc, dstFID, None, 6666, 6666, isDest = True)
	robots.append(dstNode)


	while done == False:
		section = "R" + str(index)
		robotDict = CFGReader.ReadConfig("swarm.cfg", section)
		if not robotDict:
			done = True
			break

		rID = robotDict['rid']
		fID = robotDict['fid']
		x = float(robotDict['x'])
		y = float(robotDict['y'])
		z = float(robotDict['z'])

		loc = Location(x, y, z)

		newRobot = Robot(rID, loc, fID, None, 6666, 6666)
		robots.append(newRobot)
		if rID == runtimeID:
			thisRobot = newRobot
		index += 1

	if (thisRobot == None):
		sys.exit("No [R%s] found in swarm.cfg" % runtimeID)

	
	thisRobot.all_robots["-1"] = srcLoc
	thisRobot.all_robots["-2"] = dstLoc
	currFlow = Flow.Flow(thisRobot.fid, robots, srcNode, dstNode)
	thisRobot.setFlowAndGraph(currFlow, robots)
	thisRobot.establishConnections()

	return robots

def calcDirectionVector(a, b):
	x = (b.getX() - a.getX())
	y = (b.getY() - a.getY())
	z = (b.getZ() - a.getZ())

	x2 = (x) ** 2
	y2 = (y) ** 2
	z2 = (z) ** 2
	
	length = math.sqrt(x2 + y2 + z2)

	if length != 0:
		uX = x/length
		uY = y/length
		uZ = z/length
		return Location(uX, uY, uZ)
	else:
		return Location(0, 0, 0)


if __name__ == '__main__':
	rID = validateArguments()
	robots = initRobotFromCfg(rID)
