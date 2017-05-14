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
			self.G.add_node(r.rid, x = r.location.getX(),
									y = r.location.getY(),
									z = r.location.getZ())
			#initialize edges based on node locations
			if r.isSrc:
				self.src = r
			if r.isDest:
				self.dest = r
		self.initializeGraph2(robots)

	def initializeGraph2(self, robots):
		for i in robots:
			for j in robots:
				if i.rid != j.rid:
					self.G.add_edge(i.rid, j.rid, weight = self.calcRobotDist(i,j))
			

	# Update the graph with nodes and weighted edges
	def updateGraph(self, robot_id, all_robots):
		robotLoc = all_robots.get(robot_id)
		self.G.add_node(robot_id, x = robotLoc.getX(),
									y = robotLoc.getY(),
									z = robotLoc.getZ())
		for r in all_robots:
			if r != robot_id:
				self.G[robot_id][r]['weight'] = self.calcLocationDist(robotLoc, all_robots[r])
	
	#a and b are shape and center parameters depending on the communication range and
    #variance of environmental fading.
    #We will set both to 1 for now.
	def calcRobotDist(self, one, two):
		x = (one.getLocation().getX() - two.getLocation().getX()) ** 2
		y = (one.getLocation().getY() - two.getLocation().getY()) ** 2
		z = (one.getLocation().getZ() - two.getLocation().getZ()) ** 2
		dist = math.sqrt(x + y + z)
		weight = 1 + math.exp( 0.05*(dist - 1))
		return weight

	def calcLocationDist(self, one, two):
		x = (one.getX() - two.getX()) ** 2
		y = (one.getY() - two.getY()) ** 2
		z = (one.getZ() - two.getZ()) ** 2
		dist = math.sqrt(x + y + z)
		weight = 1 + math.exp( 0.05*(dist - 1))
		return weight

	def getClosestInPath(self, robot):
		robot1 = None
		robot2 = None
		nodeList = nx.shortest_path(self.G, "-1", "-2", 'weight')

		if robot.rid in nodeList:
			currIndex = nodeList.index(robot.rid)
			robot1 = nodeList[currIndex-1]
			robot2 = nodeList[currIndex+1]

		else:
			min1 = sys.float_info.max
			min2 = sys.float_info.max

			for neighbor in nodeList:
				neighborNode = self.G.node[neighbor]
				neighborLoc = Location(neighborNode['x'], neighborNode['y'], neighborNode['z'])

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
		return robot1, robot2

	def getCentroid(self, robot):

		r1, r2 = self.getClosestInPath(robot)
		# self.G[robot_id]["location_x"] = robotLoc.getX()
		# self.G[robot_id]["location_y"] = robotLoc.getY()
		# self.G[robot_id]["location_z"] = robotLoc.getZ()
		r1Node = self.G.node[r1]
		r1Loc = Location(r1Node["x"], r1Node["y"], r1Node["z"])

		r2Node = self.G.node[r2]
		r2Loc = Location(r2Node["x"], r2Node["y"], r2Node["z"])
		
		cx = (robot.getLocation().getX() + r1Loc.getX() + r2Loc.getX())/3
		cy = (robot.getLocation().getY() + r1Loc.getY() + r2Loc.getY())/3
		cz = (robot.getLocation().getZ() + r1Loc.getZ() + r2Loc.getZ())/3
		location = Location(cx, cy, cz)
		return location
