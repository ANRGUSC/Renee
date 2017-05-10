

class Location():

	# def __init__(self, x, y, z):
	# 	self.x = x
	# 	self.y = y
	# 	self.z = z 

	def __init__(self, lat, lon, alt):
		self.lat = lat
		self.lon = lon
		self.alt = alt

	# def getX(self):
	# 	return self.x

	# def getY(self):
	# 	return self.y

	# def getZ(self):
	# 	return self.z

	def getLat(self):
		return self.lat

	def getLon(self):
		return self.lon

	def getAlt(self):
		return self.alt