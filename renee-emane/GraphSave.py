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

# Renee
# -*- coding: utf-8 -*-
import networkx as nx
from Location import Location
import Robot
import math
import sys

class Graph(object): 
	# Initialize the Graph 
	def __init__(self,robots):
		self.G = nx.Graph()
		self.robots = robots
		self.initializeGraph(self.robots)
	
	# based on all robots in the config file, add each node as 
	# G.add_node(RID, location_x=x, location_y=y, location_z=z)
	def initializeGraph(self, robots):
		for i, r in enumerate(robots):
			self.G.add_node(r.rid, location_x = r.location.getX(),
									location_y = r.location.getY(),
									location_z = r.location.getZ())
			# print ("INITIALIZE GRAPH ROBOT: ", r.rid)
			#initialize edges based on node locations
			if r.isSrc:
				self.src = r
				# print "FOUND SOURCE"
			if r.isDest:
				self.dest = r
				# print "FOUND DESTINATION"
		self.initializeGraph2(robots)
		self.calculateEndPoint()


	def initializeGraph2(self, robots):
		for i in robots:
			for j in robots:
				if i.rid != j.rid:
					# print("Edge added for:", i.rid, j.rid)
					self.G.add_edge(i.rid, j.rid, weight = self.calcRobotDist(i,j))
			

	# Update the graph with nodes and weighted edges
	def updateGraph(self, robot_id, all_robots):
		#print("START UPDATE GRAPH ~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+")
		robotLoc = all_robots.get(robot_id)
		#print("Robot location: ", robotLoc.getX(), robotLoc.getY(), robotLoc.getZ())

		self.G.add_node(robot_id, location_x = robotLoc.getX(),
									location_y = robotLoc.getY(),
									location_z = robotLoc.getZ())
		for r in all_robots:
			assert(type(r) == str)
			if r != robot_id:
				self.G[robot_id][r]['weight'] = self.calcLocationDist(robotLoc, all_robots[r])
				#self.G[r][robot_id]['weight'] = self.calcLocationDist(robotLoc, all_robots[r])

		# # 		print("IN LOOP")
		# # 		print(r)
		# # 		self.G[robot_id][r]
		# 		print("EDGE ROBT ID TYPE: ", type(r))
		# 		self.G[robot_id][r]["weight"] = self.calcLocationDist(robotLoc, all_robots[r])
		# 		#self.G.add_edge(robot_id, r, weight=self.calcLocationDist(robotLoc, all_robots[r]))
		# 		#self.G.add_edge(r, robot_id, weight=self.calcLocationDist(robotLoc, all_robots[r]))

		#print("END UPDATE GRAPH ~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+")

		# for the necessary node in graph, add location to graph node
		#self.G.add_node(robot_id)
		# self.G[robot_id]["location_x"] = robotLoc.getX()
		# self.G[robot_id]["location_y"] = robotLoc.getY()
		# self.G[robot_id]["location_z"] = robotLoc.getZ()
		
		# for i, r in enumerate(all_robots.keys()):
		# 	self.G[robot_id][r]["weight"] = calcDist(robLoc, r.getLocation()) 

        #a and b are shape and center parameters depending on the communication range and
        #variance of environmental fading.
        #We will set both to 1 for now.
	def calcRobotDist(self, one, two):
		x = (one.getLocation().getX() - two.getLocation().getX()) ** 2
		y = (one.getLocation().getY() - two.getLocation().getY()) ** 2
		z = (one.getLocation().getZ() - two.getLocation().getZ()) ** 2
		dist = math.sqrt(x + y + z)
		weight = 1 + math.exp( 0.05*(dist - 1))
		# den = 1 + math.exp(500-1)
		# ans = (weight * 500)/den
		return weight

	def calcLocationDist(self, one, two):
		x = (one.getX() - two.getX()) ** 2
		y = (one.getY() - two.getY()) ** 2
		z = (one.getZ() - two.getZ()) ** 2
		dist = math.sqrt(x + y + z)
		weight = 1 + math.exp( 0.05*(dist - 1))
		# den = 1 + math.exp(500-1)
		# ans = (weight * 500)/den
		return weight

	def getClosestInPath(self, robot):
		robot1 = None
		robot2 = None
		nodeList = nx.shortest_path(self.G, "-1", "-2", 'weight')
		
		#for r in nodeList:
		#	print(r)

		#print("ALL NODES -----------------------------------------------------------------")
		#print(self.G.nodes(data=True))
		if robot.rid in nodeList:
		#	print("IN NODE LIST")
			currIndex = nodeList.index(robot.rid)
			robot1 = nodeList[currIndex-1]
			robot2 = nodeList[currIndex+1]

		#	print(robot1)
		#	print(robot2)
		else:
		#	print("NOT IN NODE LIST")

			min1 = sys.maxint
			min2 = sys.maxint

			for neighbor in nodeList:
				neighborNode = self.G.node[neighbor]
				neighborLoc = Location(neighborNode['location_x'], neighborNode['location_y'], neighborNode['location_z'])

				weight = self.calcLocationDist(robot.getLocation(), neighborLoc)
				if weight < min1:
					if min1 < min2:
						min2 = min1
						robot2 = robot1
					min1 = weight
					robot1 = neighbor
				elif weight < min2:
					min2 = weight
					robot2 = neighbor	
				#print("min1: " + str(min1))
				#print("min2: " + str(min2))
			#print(robot1)
			#print(robot2)	
		# for i, r in enumerate(nodeList):
		# 	print(r)
		# 	if r.rid == robot.getID():
		# 		robot1 = nodeList[i-1]
		# 		robot2 = nodeList[i+1]

		return robot1, robot2

	def getLatLongCentroid(self, robot):
		r1, r2 = self.getClosestInPath(robot)
		r1Node = self.G.node[r1]
		r2Node = self.G.node[r2]

		#convert degrees to rads
		r1_lat = r1Node["location_x"] * (math.pi / 180.0)
		r1_long = r1Node["location_y"] * (math.pi / 180.0)
		
		r2_lat = r2Node["location_x"] * (math.pi / 180.0)
		r2_long = r2Node["location_y"] * (math.pi / 180.0)

		this_lat = robot.getLocation().getX() * (math.pi / 180.0)
		this_long = robot.getLocation().getY() * (math.pi / 180.0)

		#compute avg X Y Z vals
		r1_x = math.cos(r1_lat) * math.cos(r1_long)
		r1_y = math.cos(r1_lat) * math.sin(r1_long)
		r1_z = math.cos(r1_lat)

		r2_x = math.cos(r2_lat) * math.cos(r2_long)
		r2_y = math.cos(r2_lat) * math.sin(r2_long)
		r2_z = math.cos(r2_lat)

		this_x = math.cos(this_lat) * math.cos(this_long)
		this_y = math.cos(this_lat) * math.sin(this_long)
		this_z = math.cos(this_lat)

		x_avg = (r1_x + r2_x + this_x)/3.0
		y_avg = (r1_y + r2_y + this_y)/3.0
		z_avg = (r1_z + r2_z + this_z)/3.0

		#convert averages to lat long
		central_long = math.atan2(y_avg, x_avg)
		hyp = math.sqrt(x_avg*x_avg + y_avg*y_avg)
		central_lat = math.atan2(z_avg, hyp)

		newLoc = Location(central_lat * (180.0/math.pi), central_long * (180.0/math.pi), 0)

		# print("New Location - Graph:", newLoc.getX(), newLoc.getY())
		return newLoc


	def getCentroid(self, robot):
		r1, r2 = self.getClosestInPath(robot)
# self.G[robot_id]["location_x"] = robotLoc.getX()
		# self.G[robot_id]["location_y"] = robotLoc.getY()
		# self.G[robot_id]["location_z"] = robotLoc.getZ()
		r1Node = self.G.node[r1]
		r1Loc = Location(r1Node["location_x"], r1Node["location_y"], r1Node["location_z"])

		r2Node = self.G.node[r2]
		r2Loc = Location(r2Node["location_x"], r2Node["location_y"], r2Node["location_z"])
		
		cx = (robot.getLocation().getX() + r1Loc.getX() + r2Loc.getX())/3
		cy = (robot.getLocation().getY() + r1Loc.getY() + r2Loc.getY())/3
		cz = (robot.getLocation().getZ() + r1Loc.getZ() + r2Loc.getZ())/3
		location = Location(cx, cy, cz)
		return location

    #called on each robot to determine if it must move, and if it does, calls the emane function
    #with the appropriate centroid location to move to along with the robot id.
	def moveToNextLocation(self, robot):
		r1, r2 = self.getClosestInPath(robot)
		x = (robot.getLocation().getX() - self.endpointlocation.x) ** 2
		y = (robot.getLocation().getY() - self.endpointlocation.y) ** 2
		z = (robot.getLocation().getZ() - self.endpointlocation.z) ** 2
		thisDist = math.sqrt(x + y + z)

		x = (r1.getLocation().getX() - self.endpointlocation.x) ** 2
		y = (r1.getLocation().getY() - self.endpointlocation.y) ** 2
		z = (r1.getLocation().getZ() - self.endpointlocation.z) ** 2
		r1Dist = math.sqrt(x + y + z)

		x = (r2.getLocation().getX() - self.endpointlocation.x) ** 2
		y = (r2.getLocation().getY() - self.endpointlocation.y) ** 2
		z = (r2.getLocation().getZ() - self.endpointlocation.z) ** 2
		r2Dist = math.sqrt(x + y + z)

		if thisDist <= r1Dist and thisDist <= r2Dist:
			newLocation = getCentroid(robot)
			robot.setLocation(newLocation)
			return newLocation
			#call emane function here like:
			# emaneFunction(robot, newLocation)


	def calculateEndPoint(self):
		destx = self.dest.getLocation().getX()
		desty = self.dest.getLocation().getY()
		destz = self.dest.getLocation().getZ()

		srcx = self.src.getLocation().getX()
		srcy = self.src.getLocation().getY()
		srcz = self.src.getLocation().getZ()

		ansx = (destx + srcx) / 2
		ansy = (desty + srcy) / 2
		ansz = (destz + srcz) / 2

		self.endpointlocation = Location(ansx, ansy, ansz)


        
    