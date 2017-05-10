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
		#### TODO: initialize graph using pre-determined set of robots and their initial locations (add a function for this)
		self.graph = graph

		# Sockets for sending and receiving messages
		self.receiveSocket = None
		self.sendSocket = None
		self.isSrc = isSrc
		self.isDest = isDest

		# Map RID to current location of other robots in the flow.
		self.all_robots = {}

		# NETWORK 
	# 	self.xCounter = 0;
	 	self.messageCounter = 0;
	#	self.messageTracker = {}


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
		#print ("FLOW ID %s SRC %s DEST %s" %(flow.fid, flow.src, flow.dest))
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

		#Commented out line below just to keep style same for now. sendThread lines do same thing as startComController func
		#self.startComController(self.location, self.sendPort)

	# Receive incoming messages from other Robots about location changes, and process them
	def listenForBroadcasts(self):
		while True:
			# print("Waiting for data")
			loc, IP = self.sendSocket.recvfrom(10240)
			#print "Recieved data"
			#print loc
			# print IP
			loc = pickle.loads(loc)
			IP = str(IP[0])
			# print ("loc: ", loc)
			nodeData = loc.split(' ')
			senderID = nodeData[0]
			messageID = nodeData[1]
			positionNode = nodeData[2]
			newX = float(nodeData[3])
			newY = float(nodeData[4])
			newZ = float(nodeData[5])
			newLocation = Location(newX, newY, newZ)
			self.updateLocation(positionNode, newLocation)
			#print 'Robot at this IP: {} is at this Location: {}, {}, {}'.format(positionNode, loc.getX(), loc.getY(), loc.getZ())

	# Starts comm controller thread to send pickle of location, IP
	def startComController(self, new_location=None, port=None):
		transmission = Thread(target = self.commController(new_location, port))
		transmission.start()


	# Update new location of a Robot in the map and in the graph, call to update motion of this robot
	def updateLocation(self, rID, location):
		self.all_robots[rID] = location
		self.graph.updateGraph(rID, self.all_robots)

	# # Starts motion controller thread to compute, update, and send new location of this robot
	# def updateMotion(self):
	# 	motion = Thread(targetest = self.motionController)
	# 	motion.start()

	# # Compute my new location based on triangulation, move to new location.
	# def motionController(self):
	# 	##### TODO: based on neighbors' locations, calculate new location and move there (Graph work)
	# 	self.location = Graph.moveToNextLocation(self)
	# 	if self.getOldLocation() != self.getLocation():
	# 		self.graph.updateGraph(self, self.all_robots)
			

	# Send pickled data over to all robots in the flow
	#Jake: Removed new_location and port parameters for commController function.
	def commController(self):
		#print "hit com port " + str(port)
		# format location data for sending
		while True:
	 		newID = str(self.rid) + " " + str(self.messageCounter)
	 		#updates robot.location with new location
	 		newLoc = self.graph.getCentroid(self)
	 		# locMovementVector = calcDirectionVector(self.location, newLoc)
	 		#print("newLoc x y z ", newLoc.x, newLoc.y, newLoc.z)

	 		# moveX = self.location.getLat() + (locMovementVector.getLat())
	 		# moveY = self.location.getLon() + (locMovementVector.getLon())
	 		# moveZ = self.location.getAlt() + (locMovementVector.getAlt())
	 		# moveLoc = Location(moveX, moveY, moveZ)

	 		moveLoc = newLoc

	 		# newLoc.x += locMovementVector.x * 5
	 		# newLoc.y += locMovementVector.y * 5
	 		# newLoc.z += locMovementVector.z * 5

	 		# print("newLocAfterMovement x y z ", newLoc.x, newLoc.y, newLoc.z)

			locationData = newID + ' ' + str(self.rid) + ' '+ str(moveLoc.getLat()) + ' '+ str(moveLoc.getLon()) + ' '+ str(moveLoc.getAlt())
	 		print(locationData)
	 		self.setLocation(moveLoc)
	 		self.updateLocation(self.rid, moveLoc)

	 		#locationData = newID + ' ' + str(self.rid) + ' '+ str(new_location.getX()) + ' '+ str(new_location.getY()) + ' '+ str(new_location.getZ())

	 		#print "location data: " + locationData
	 		# pickle then send data
			data_string = pickle.dumps(locationData)
			self.sendSocket.sendto(data_string, (MCAST_GRP, MCAST_PORT))
			#print "data sent"
			# increase message count
			self.messageCounter = self.messageCounter + 1
			time.sleep(0.5)


def validateArguments():
	if len(sys.argv) != 2:
		sys.exit("Incorrect number of arguments.\nCorrect Format: ./NodeLeader.py <int: node number>");
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
	srcLoc = Location(float(srcDict["lat"]), float(srcDict["lon"]), float(srcDict["alt"]))
	srcNode = Robot("-1", srcLoc, srcFID, None, 6666, 6666, isSrc = True)
	robots.append(srcNode)

	dstFID = dstDict["fid"]
	dstLoc = Location(float(dstDict["lat"]), float(dstDict["lon"]), float(dstDict["alt"]))
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
		lat = float(robotDict['lat'])
		lon = float(robotDict['lon'])
		alt = float(robotDict['alt'])

		loc = Location(lat, lon, alt)

		newRobot = Robot(rID, loc, fID, None, 6666, 6666)
		robots.append(newRobot)
		if rID == runtimeID:
			thisRobot = newRobot
		index += 1

	if (thisRobot == None):
		sys.exit("No [R%s] found in swarm.cfg" % runtimeID)

	#print(thisRobot)
	
	thisRobot.all_robots["-1"] = srcLoc
	thisRobot.all_robots["-2"] = dstLoc
	currFlow = Flow.Flow(thisRobot.fid, robots, srcNode, dstNode)
	thisRobot.setFlowAndGraph(currFlow, robots)
	thisRobot.establishConnections()

	return robots

def calcDirectionVector(a, b):
	print("calc direction vector")
	lat = (b.getLat() - a.getLat())
	lon = (b.getLon() - a.getLon())
	alt = (b.getAlt() - a.getAlt())

	x2 = (lat) ** 2
	y2 = (lon) ** 2
	z2 = (alt) ** 2
	
	length = math.sqrt(x2 + y2 + z2)

	if length != 0:
		uX = lat/length
		uY = lon/length
		uZ = alt/length
		#print("X", x, "  UX", uX, " Length ", length)
		return Location(uX, uY, uZ)
	else:
		return Location(0)


if __name__ == '__main__':
	rID = validateArguments()
	robots = initRobotFromCfg(rID)
