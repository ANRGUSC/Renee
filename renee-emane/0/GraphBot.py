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
import networkx as nx


class LogCompiler(object):
	def __init__(self, receivePort):
		self.robots = {}	
		self.graph = nx.Graph()
		self.rID = 1
		#self.logFile = open('/home/emane-tutorial/scenario/scenario.eel', 'w', 1)
		self.initGraph()

	def initGraph(self):
		src = Location(10, 10, 0)
		dst = Location(100, 100, 0)
		loc1 = Location(30, 60, 0)
		loc2 = Location(40, 10, 0)
		loc3 = Location(90, 60, 0)
		
		self.graph.add_node('S')
		self.graph.add_node('D')
		self.graph.add_node(1)
		self.graph.add_node(2)
		self.graph.add_node(3)

		w_s1 = Location.distance(src, loc1)
		w_s2 = Location.distance(src, loc2)
		w_s3 = Location.distance(src, loc3)

		w_12 = Location.distance(loc1, loc2)
		w_13 = Location.distance(loc1, loc3)
		w_1d = Location.distance(loc1, dst)

		w_23 = Location.distance(loc2, loc3)
		w_2d = Location.distance(loc2, dst)

		w_3d = Location.distance(loc3, dst)

		self.graph.add_edge('S', 1, weight=w_s1)
		self.graph.add_edge('S', 2, weight=w_s2)
		self.graph.add_edge('S', 3, weight=w_s3)
		self.graph.add_edge(1, 2, weight=w_12)
		self.graph.add_edge(1, 3, weight=w_13)
		self.graph.add_edge(1, 'D', weight=w_1d)
		self.graph.add_edge(2, 3, weight=w_23)
		self.graph.add_edge(2, 'D', weight=w_2d)
		self.graph.add_edge(3, 'D', weight=w_3d)

		print(self.graph.nodes())
		print(self.graph.edges())
		print(self.graph.neighbors(self.rID))

		# shortest_path = nx.find_cliques(self.graph)

		mst = nx.minimum_spanning_tree(self.graph)
		print(mst.nodes())


	
	# def start(self):
	# 	self.setupConnection()

	# 	output = Thread(target = self.outputNodeData)
	# 	output.start()


	# def setupConnection(self):
	# 	self.receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# 	self.receiveSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	# 	self.receiveSocket.bind(('', self.__receivePort))

	# 	connection = Thread(target = self.listen)
	# 	connection.start()

	# def listen(self):
	# 	xCounter = 0;
	# 	while True:
	# 		locationData = '1 '+ str(xCounter) + ' 1 1'
	# 		self.receiveSocket.sendto(locationData, (MCAST_GRP, MCAST_PORT))
	#   		time.sleep(1)
	#   		data= self.receiveSocket.recv(10240)
	# 		data = data.strip()
	# 		print("Recieved Data:", data)
	# 		nodeData = data.split(' ')
	# 		nodeNum = nodeData[0]
	# 		nodeLocation = Location(nodeData[1], nodeData[2], nodeData[3])
	# 		self.nodes[nodeNum] = nodeLocation
	# 		print(len(self.nodes))
	# 		xCounter += 1
			

	# def outputNodeData(self):
	# 	while True:
	# 		for node in self.nodes:
	# 			logLine = str(self.currTimeInterval) + '.0 nem:' + str(node) + ' location gps ' + str(self.nodes[node].getX()) + ',' + str(self.nodes[node].getY())+ ',' +str(self.nodes[node].getZ()) + '\n'
	# 			#self.logFile.write(logLine)
	# 		self.currTimeInterval += 1
	# 		time.sleep(3)

	

if __name__ == '__main__':
	compiler = LogCompiler(6666)
	# compiler.start()
