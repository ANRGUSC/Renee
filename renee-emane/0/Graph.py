# RouteSwarm
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
			self.G.add_node(r.rid, latitude = r.location.getLat(),
									longitude = r.location.getLon(),
									altitude = r.location.getAlt())
			print ("INITIALIZE GRAPH ROBOT: ", r.rid)
			#initialize edges based on node locations
			if r.isSrc:
				self.src = r
				print "FOUND SOURCE"
			if r.isDest:
				self.dest = r
				print "FOUND DESTINATION"
		self.initializeGraph2(robots)
		self.calculateEndPoint()


	def initializeGraph2(self, robots):
		for i in robots:
			for j in robots:
				if i.rid != j.rid:
					print("Edge added for:", i.rid, j.rid)
					self.G.add_edge(i.rid, j.rid, weight = self.calcRobotDist(i,j))
			

	# Update the graph with nodes and weighted edges
	def updateGraph(self, robot_id, all_robots):
		robotLoc = all_robots.get(robot_id)
		self.G.add_node(robot_id, latitude = robotLoc.getLat(),
									longtitude = robotLoc.getLon(),
									altitude = robotLoc.getAlt())
		for r in all_robots:
			#assert(type(r) == str)
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
		one_lat_rads = one.getLocation().getLat() * (math.pi/180.0)
		one_lon_rads = one.getLocation().getLon() * (math.pi/180.0)
		two_lat_rads = two.getLocation().getLat() * (math.pi/180.0)
		two_lon_rads = two.getLocation().getLon() * (math.pi/180.0)
		delta_lat = two_lat_rads - one_lat_rads
		delta_lon = two_lon_rads - one_lon_rads

		a = math.sin(delta_lat/2.0) * math.sin(delta_lat/2.0) + math.cos(one_lat_rads) * math.cos(two_lat_rads) * math.sin(delta_lon/2.0) * math.sin(delta_lon/2.0)
		c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
		d = 6371000 * c
		# print("latitude 1", one.getLocation().getLat(), one_lat_rads)
		# print("longitude 1", one.getLocation().getLon(), one_lon_rads)
		# print("latitude 2", two.getLocation().getLat(), two_lat_rads)
		# print("longitude 2", two.getLocation().getLon(), two_lon_rads)
		# print(delta_lat, delta_lon)
		# print(d)
		weight = 1.0 + math.exp(1.0*(d))

		return weight

	def calcLocationDist(self, one, two):
		one_lat_rads = one.getLat() * (math.pi/180.0)
		one_lon_rads = one.getLon() * (math.pi/180.0)
		two_lat_rads = two.getLat() * (math.pi/180.0)
		two_lon_rads = two.getLon() * (math.pi/180.0)
		delta_lat = two_lat_rads - one_lat_rads
		delta_lon = two_lon_rads - one_lon_rads

		a = math.sin(delta_lat/2.0) * math.sin(delta_lat/2.0) + math.cos(one_lat_rads) * math.cos(two_lat_rads) * math.sin(delta_lon/2.0) * math.sin(delta_lon/2.0)
		c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
		d = 6371000 * c
		# print("latitude 1", one.getLat(), one_lat_rads)
		# print("longitude 1", one.getLon(), one_lon_rads)
		# print("latitude 2", two.getLat(), two_lat_rads)
		# print("longitude 2", two.getLon(), two_lon_rads)
		# print(delta_lat, delta_lon)
		# print(d)
		weight = 1.0 + math.exp(1.0*(d))
		return weight

	def getClosestInPath(self, robot):
		robot1 = None
		robot2 = None
		nodeList = nx.shortest_path(self.G, "-1", "-2", 'weight')
		
		#for r in nodeList:
		#	print(r)

		#print("ALL NODES -----------------------------------------------------------------")
		#print(self.G.nodes(data=True))

		print("Node List", nodeList)
		# print("Source/Dest weight: ", self.G['-1']['-2']['weight'])

		if robot.rid in nodeList:
			print("IN NODE LIST")
			currIndex = nodeList.index(robot.rid)
			robot1 = nodeList[currIndex-1]
			robot2 = nodeList[currIndex+1]

		#	print(robot1)
		#	print(robot2)
		else:
			print("NOT IN NODE LIST")

			min1 = sys.float_info.max
			min2 = sys.float_info.max

			for neighbor in nodeList:
				neighborNode = self.G.node[neighbor]
				neighborLoc = Location(neighborNode['latitude'], neighborNode['longitude'], neighborNode['altitude'])

				weight = self.calcLocationDist(robot.getLocation(), neighborLoc)
				# print("neighbor weight", neighbor, ": ", weight)

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
		print("Neighbors:", robot1, robot2)
		return robot1, robot2

		# longitude = x, latitude = y, altitude = z
	def getCentroid(self, robot):
		r1, r2 = self.getClosestInPath(robot)
		
		#Calc Current Robot's (X,Y,Z)
		# curr_node = self.G.node[curr_node]
		
		curr_loc = robot.getLocation()
		curr_lat_rads = curr_loc.getLat() * float(math.pi/180.0)
		curr_lon_rads = curr_loc.getLon() * float(math.pi/180.0)
		print("Current Location:", curr_loc.getLat(), curr_loc.getLon(), curr_loc.getAlt())

		curr_x = math.cos(curr_lat_rads) * math.cos(curr_lon_rads)
		curr_y = math.cos(curr_lat_rads) * math.sin(curr_lon_rads)
		curr_z = math.sin(curr_lat_rads)


		#Calc Left Neighbors (X,Y,Z)
		r1_node = self.G.node[r1]
		r1_loc = Location(r1_node["latitude"], r1_node["longitude"], r1_node["altitude"])
		
		r1_lat_rads = r1_loc.getLat() * float(math.pi/180.0)
		r1_lon_rads = r1_loc.getLon() * float(math.pi/180.0)
		print(r1, " Location:", r1_loc.getLat(), r1_loc.getLon(), r1_loc.getAlt())

		r1_x = math.cos(r1_lat_rads) * math.cos(r1_lon_rads)
		r1_y = math.cos(r1_lat_rads) * math.sin(r1_lon_rads)
		r1_z = math.sin(r1_lat_rads)


		#Calc Right Neighbor's (X,Y,Z)
		r2_node = self.G.node[r2]
		r2_loc = Location(r2_node["latitude"], r2_node["longitude"], r2_node["altitude"])
		
		r2_lat_rads = r2_loc.getLat() * float(math.pi/180.0)
		r2_lon_rads = r2_loc.getLon() * float(math.pi/180.0)
		print(r2, " Location:", r2_loc.getLat(), r2_loc.getLon(), r2_loc.getAlt())


		r2_x = math.cos(r2_lat_rads) * math.cos(r2_lon_rads)
		r2_y = math.cos(r2_lat_rads) * math.sin(r2_lon_rads)
		r2_z = math.sin(r2_lat_rads)
		
		#Calc average (X, Y, Z)
		x = (curr_x + r1_x + r2_x) / 3.0
		y = (curr_y + r1_y + r2_y) / 3.0
		z = (curr_z + r1_z + r2_z) / 3.0

		#Calc central (Lat, Lon)
		central_lon = math.atan2(y, x)
		central_hyp = math.sqrt(x*x + y*y)
		central_lat = math.atan2(z, central_hyp)

		#Convert back to degrees
		latitude = central_lat * (180.0/math.pi)
		longitude = central_lon * (180.0/math.pi)
		print("Centroid Location:", latitude, longitude, 1.0)

		return Location(latitude, longitude, 1.0)

	def calculateEndPoint(self):
		# dest
		# convert lat, lon to radians
		p = float(math.pi/180.0)

		dest_lat_rads = self.dest.getLocation().getLat() * p
		dest_lon_rads = self.dest.getLocation().getLon() * p

		dest_x = math.cos(dest_lat_rads) * math.cos(dest_lon_rads)
		dest_y = math.cos(dest_lat_rads) * math.sin(dest_lon_rads)
		dest_z = math.sin(dest_lat_rads)

		src_lat_rads = self.src.getLocation().getLat() * p
		src_lon_rads = self.src.getLocation().getLon() * p

		src_x = math.cos(src_lat_rads) * math.cos(src_lon_rads)
		src_y = math.cos(src_lat_rads) * math.sin(src_lon_rads)
		src_z = math.sin(src_lat_rads)

		# calculate end point
		ans_x = (dest_x + src_x) / 2
		ans_y = (dest_y + src_y) / 2
		ans_z = (dest_z + src_z) / 2

		# convert x,y,z coords to lat and long
		lon = math.atan2(ans_y, ans_x)
		hyp = math.sqrt(ans_x*ans_x + ans_y*ans_y)
		lat = math.atan2(ans_z, hyp)

		# convert back to degrees
		lonDegrees = lon * (180.0/math.pi)
		latDegrees = lat * (180.0/math.pi)

		self.endpointlocation = Location(latDegrees, lonDegrees, 0)
