from ConfigParser import SafeConfigParser
import os

def ReadConfig(file, section):
	config = SafeConfigParser()
	mydir = os.path.dirname(os.path.abspath(__file__))
	path = os.path.join(os.getcwd(), file)
	dict1 = {}
	if os.path.isfile(path):
		config.read(path)
		if config.has_section(section):
			options = config.options(section)
			for option in options:
				try:
					dict1[option] = config.get(section, option)
					if dict1[option] == -1:
						print("Skip: %s" % option)
				except:
					print("Exception on %s" % option)
					dict1[option] = None
		else:
			return {}
	else:
		print("Config file not found")
	return dict1