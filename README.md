# Robotic Wireless Network: Renee Emulator
-------------------

## Introduction
The goal of this project was to build an emulation and visualization tool which can display several robots in a network flow. We accomplished this by using EMANE, a tool used to simulate a network and Linux containers within the network. Each Linux container runs an instance of Robot to behave as a node in the network, which uses an instance of Graph to track the
locations of other nodes in the network and calculate where the node should move to line up in its flow.

## Setup Instructions

### Setting up the pre-configured virtual machine (recommended): 
1. Download VirtualBox Manager and the CentOS EMANE Demo Virtual Machine from https://drive.google.com/a/usc.edu/file/d/0B5ViCEcBphtIMzhkRUpJR3Vab3c/view?usp=sharing.
2. Open VirtualBox Manager. 
3. Under the File Tab, select Import Appliance. 
4. Find where the EMANE Demo Virtual Machine is located on your computer and select it. It should appear in VirtualBox Manager. 
5. Start running the virtual machine. The credentials are:
```
Username: emane
Password: emanedemo
```
If VirtualBox Manager gives you an error, follow the workaround below (adapted from: https://www.virtualbox.org/ticket/14469):

1. Go to the the new EMANE VM (imported appliance)and click on the settings button
2. Select Ports->USB tab
3. Disable USB and hit save
4. Return to the same place in the settings menu and check to make sure USB is enabled again
5. Save and start the new EMANE VM



In the terminal, navigate to the folder `emane-tutorial/route-swarm`.
Run the `route-swarm-start.sh` script in the terminal to start the
emulation (both the scripts and the GUI):
```shell
cd emane-tutorial/route-swarm
sudo sh ./route-swarm-start.sh
```
Note: sudo is required for all nodes to run properly.
When you are ready to end the emulation, use the route-swarm-stop.sh
command in the host terminal:
```shell
sudo sh ./route-swarm-stop.sh
```
--------------------------------------------------------------
### Manual virtual machine installation (not recommended):

#### Preliminary Setup:
1. If you are not running Linux, download a Linux/Ubuntu 14.04 virtual machine
2. To download Python 2.7, enter the command: `sudo apt-get install python2.7`
3. To download the networkx Python library, enter the command: `pip install networkx`
4. Setup the sshd config properly:
```shell
$ mkdir ~/.ssh
$ chmod 700 ~/.ssh
$ ssh-keygen -t rsa
$ cd ~/.ssh
$ cat id_rsa.pub  >> authorized_keys
```

#### Download and set up EMANE framework:

If the below instructions do not work, here are the links to where the directions are:
1. https://github.com/adjacentlink/emane/wiki/Install
1. https://github.com/adjacentlink/emane/wiki/Install#ubuntu-1404-lts-amd64
2. https://github.com/adjacentlink/emane/wiki/Install#ubuntu-1604-lts-amd64

#### Directions:
1. Type this into terminal: 
`wget https://adjacentlink.com/downloads/emane/emane-1.0.1-release-1.ubuntu-16_04.amd64.tar.gz`
2. Then type:
```shell
$ tar zxvf emane-1.0.1-release-1.ubuntu-16_04.amd64.tar.gz 
$ cd emane-1.0.1-release-1/debs/ubuntu-16_04/amd64
$ sudo dpkg -i *.deb
$ sudo apt-get install -f
$ cd ~
```
3. Install Necessary Packages: 
```shell
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get install python-pip libcurl4-gnutls-dev librtmp-dev lxc bridge-utils mgen fping gpsd gpsd-clients iperf multitail olsrd openssh-server python-tk python-pmw python-lxml python-stdeb build-essential python-pycurl
```
Or,
```shell
$ sudo yum install lxc bridge-utils fping gpsd gpsd-clients iperf multitail openssh-server tkinter python-pmw python-lxml
```

4. Install pynodestatviz
```shell
$ git clone git@github.com:ANRGUSC/pynodestatviz.git
$ cd pynodestatviz
$ make deb
$ sudo dpkg -i deb_dist/pynodestatviz*.deb
$ cd ~
```
5. Clone our code and replace `pynodestatviz` in `usr/lib/python2.7/dist-packages` with the directory named `pynodestatviz`
```shell
$ git clone git@github.com:ANRGUSC/Renee.git
$ cd Renee/1
$ make
```

6. (demo only) To setup demo update your /etc/hosts file to include the following:
```shell
10.99.0.1 node-1
10.99.0.2 node-2
10.99.0.3 node-3
10.99.0.4 node-4
10.99.0.5 node-5
10.99.0.6 node-6
10.99.0.7 node-7
10.99.0.8 node-8
10.99.0.9 node-9
10.99.0.10 node-10
10.99.0.100 node-server
10.100.0.1 radio-1
10.100.0.2 radio-2
10.100.0.3 radio-3
10.100.0.4 radio-4
10.100.0.5 radio-5
10.100.0.6 radio-6
10.100.0.7 radio-7
10.100.0.8 radio-8
10.100.0.9 radio-9
10.100.0.10 radio-10
```

##### To run the simulator:
1. Enter command: `sudo ./renee-start.sh`
2. Wait about 30 seconds to observe activity in the GUI
3. To Stop Enter command: `sudo ./renee-stop.sh`

Note: In the First time, you might have to manually enter "Yes" in each of the opened xterm to enter the ssh key into known-hosts file.

-------------------------------------------------------------------------------
## Configuring Emulation

### Initial Node Configuration:
All initial node data is to be put in `swarm.cfg` in the following format:
```shell
[src]
x = 40.031227
y = 74.523247
z = 1
fid = 001
[dst]
x = 40.031165
y = 74.523412
z = 1
fid = 001
[R#]
x = 40.031075
y = 74.523518
z = 1
rid = #
fid = 001
```
Note: you must have 1 [src] and 1 [dst], and 1 - 8 [R#] nodes
where # is replaced with a number 1-8.

Next, open `renee-start.sh`. You will see the first 4 lines which set up EMANE, the GUI, and the LogCompiler. Lines 7-14 start up each node desired node container. Comment out the lines for nodes that you have not included in your swarm.cfg file. 

### Motion Controller Configuration:
To change the location that each node will move to, go into `Robot.py` and in the commController function, change the value of newLoc to be the new location you would like to move in the direction of.

### Pathloss Configuration:
See *Pathloss & The Physical Layer Model* for configuration instructions.

-----------------------------------------------------------------------------------
## Class Definitions:

#### ROBOT #####
1. The Robot class identifies a Robot instance with an id, its current location, its current flow and a private instance of network graph. 
2. It instantiates itself with the help of config files robot.cfg, flow.cfg and location.cfg.
3. It creates 4 parallel threads
    a. Swarm - Update network graph based on information of all Robots
    b. Communication - Send my current info (rid, location, fid) to communication subsystem (send-command.cfg)
    c. Motion - Calculate the required motion for me based on other robots in flow PATH and send this new location to motion subsystem (motion-command.cfg)
    d. Location - update the current location (as it might have changed after motion)
4. Additionally, it contains list of all robots as a global object

#### HOST ####
1. The Host class identifies a Host (end-point) with id and location

#### FLOW ####
1. The Flow class identifies a Flow with id, source host, destination host and set of robots serving the flow.

#### LOCATION ####
1. The Location class identifies a Location with x, y and z.
2. It has APIs to calculate centroid of robots and distance between two locations


#### GRAPH ####
1. The Graph class identifies the network graph containing robots and hosts as nodes and distance as weigted edges
2. It currently provides shortestPath

#### HELPER ####
1. Provides API to read and write config files


---------------------------------------------------------------------------------------
## Class Diagrams

### Robot 
The *Robot class* is an instance of a node in a flow configuration. It opens a socket to send and receive broadcast messages from other nodes in the network. Each message is tagged with an id number, and Robot stores a set of message ids it’s already sent before deciding whether or not to rebroadcast incoming messages to other nodes.​ ​ The Robot class also has a Graph instance which is used to calculate its future location. Each Robot instance is run on a separate Linux container in EMANE.

#### Attributes:
- **sendPort** : int
- **receivePort** : int
- **rid** : String
- **oldLocation** : Location
- **location** : Location
- **fid** : int
- **graph** : Graph
- **receiveSocket** : socket
- **sendSocket** : socket
- **isSrc** : boolean
- **isDest** : boolean
- **all_robots** : map
- **messageCounter** : int 

#### Functions:
+ `def __init__(self, rid, location, fid, graph, sendPort, receivePort, isSrc=False, isDest=False)`
+ `def __str__(self)`
+ `fetchID(self)`
+ `setID(self, rid)`
+ `getID(self)`
+ `fetchFlow(self)`
+ `setFlowAndGraph(self, flow, robots)`
+ `getFlow(self)`
+ `fetchLocation(self)`
+ `setLocation(self, loc)`
+ `getLocation(self, loc)`
+ `getOldLocation(self)`
+ `establishConnections(self)`
+ `listenForBroadcasts(self)`
+ `startComController(self, new_location=None, port=None)`
+ `sendLocation(self, new_location=None, port=None)`
+ `updateLocation(self, rID, location)`
+ `updateMotion(self)`
+ `motionController(self)`
+ `commController(self)`

### Graph

The *Graph class* utilizes the `networkx` library to create an undirected graph configuration of all the nodes in a particular flow. Each instance of Robot contains an instance of Graph in order to track other Robots’ locations and find the closest neighbors with which to compute the centroid. The Graph is updated with each location update received from broadcast messages.
#### Attributes:
- **G** : undirected graph
- **robots** : array of Robot objects
- **src** : Robot
- **dest** : Robot
- **endpointlocation** : Location

#### Functions:
+ `def __init__(self,robots)`
+ `def initializeGraph(self, robots)`
+ `def initializeGraph2(self, robots)`
+ `def updateGraph(self, robot_id, all_robots)`
+ `def calcRobotDist(self, one, two)`
+ `def calcLocationDist(self, one, two)`
+ `def getClosestInPath(self, robot)`
+ `def getCentroid(self, robot)`
+ `def moveToNextLocation(self, robot)`
+ `def calculateEndPoint(self)`

### LogCompiler

*LogCompiler* opens a socket and receives input from all nodes within a network. Whenever a node sends updates about their
position, LogCompiler writes the information to `scenario.eel`. EMANE then reads from scenario.eel to get the position of all nodes on the networks and display those locations in the EMANE GUI. It also rebroadcasts messages it receives from the other nodes in the network to implement flooding while controlling the number of times a message is forwarded through the network. LogCompiler does not generate any original messages of its own. Each message is tagged with an id number, and LogCompiler stores a set of message ids it’s already sent before deciding whether or not to forward incoming messages.

#### Attributes:
- **_receivePort** : int
- **receiveSocket** : socket
- **currTimeInterval** : int
- **nodes** : dictionary
- **messageTracker** : dictionary
- **logFile** : file
- **outputNodeData**

#### Functions:
+ `def initLogFileFromCfg(self)`
+ `def start(self)`
+ `def setupConnection(self)`
+ `def listen(self)`
+ `def updateTracker(self, nodeNumber)`
+ `def outputNodeData(self)`
+ `if __name__ == '__main__'`

-----------------------------------------------------------------------
## Flow Diagram
![alt text](https://github.com/ANRGUSC/Renee/blob/master/flow.png "flow")

-------------------------------------------------------------------------
## Component Diagrams

![alt text](https://github.com/ANRGUSC/Renee/blob/master/components.png "components")

-------------------------------------------------------------------------
## Sequence Diagrams

![alt text](https://github.com/ANRGUSC/Renee/blob/master/sequence.png "sequence")

-------------------------------------------------------------------------
## Class/Method Descriptions

### Graph.py 
This class is used to handle all location calculations. Each node will run Robot.py, each containing an instance of the Graph class. As each Robot receives location data from all other Robots in its network, their locations will be updated in the graph, and used to calculate this Robot’s next location, which it will then broadcast out to all other Robots in the network. Location calculations utilize the following functions:

-   **__init__(self, robots):** Creates a graph, which is present on each robot. Creates an array of present robots on each robot and calls initializeGraph.
-   **initializeGraph(self, robots):** Adds a node to the graph for each known robot in the network. Adds Source and Destination node information. And adds edges between all communicable nodes, with weights based on a function that exponentially maps distance to weight.
-   **initializeGraph2(self, robots):** This is an extension of initializeGraph. It basically initializes/calculates the edges of the graph by calling calcDist.
-   **calcDist(self, one, two):** Calculates the distance between two robots based on the weighted regression algorithm given.
-   **calculateEndPoint(self):** Calculate the final location where the robot must ultimately go to.
-   **updateGraph(self, robot_ID, allRobots):** Updates graph with all current robot locations that have been recieved over the network.
-   **moveToNextLocation(self, robot):** Called on each robot to determine if it needs to move, and if it does, calculates and returns the centroid location that it must move to.
-   **getCentroid(self, robot):** Returns a Location for the centroid of a robot and its two neighbors.
-   **getClosestInPath(self, robot):** Returns the left and right neighbor of the given Robot in the shortest path between source and destination 

### Robot.py
This class acts as an instance of a robot. Each Robot belongs to both a flow and the overall network graph. It also has two sockets to send and receive location data from other Robot instances in the graph. The networking code from `CoordinateSender.py` has been integrated into the Robot code. Based on the locations of other Robot instances, it will update its own graph of robots’ information and its own position if needed.

-   **fetchID(self):** Gets the robot ID from a config file robot.cfg.
-   **setID(self, rid):** Sets the robot ID based on the rid passed in
-   **getID(self):** Returns the rid of the robot
-   **fetchFlow(self):** Fetches the flow the robot belongs to from the config file `flow.cfg` and sets the robot’s information about its flow.
-   **setFlowAndGraph(self, flow, robots):** Sets the flow the robot belongs to based on the flow. Also initializes the robot’s graph of other robots and their positions.
-   **getFlow(self):** Returns the flow a robot instance belongs to.
-   **fetchLocation(self):** Fetches the original robot location from the config file `flow.cfg`.
-   **setLocation(self, loc):** Marks the robot’s current location as its “old” location and sets a new location loc as its current location.
-   **getLocation(self):** Returns the robot’s current location.
-   **establishConnections(self):** Sets up a socket for receiving and sending broadcast messages. Starts a thread for both sending and receiving messages to and from other robots in the network.
-   **listenForBroadcasts(self):** Waits for incoming messages from other robots in the network. Once it receives a message, it unpickles the data to get information for a certain node’s position. Once it gets the node ID and position, Robot creates a Location instance representing the position and calls updateLocation (more details about this method later). It will also rebroadcast the message to other Robot instances in the graph unless it has already broadcasted the specific message at an earlier point in time.
-   **updateLocation(self, rID, location):** Updates the location of a Robot in a map containing the locations of all Robot instances, then updates the Graph instance as well to start position calculations.
-   **commController(self):** Continually calculates the next location of the Robot, calculates the unit vector pointing from the robot’s current location to that next location, multiplies the unit vector by a delta weight (how far we want the robot to move in each update) and updates the current location with that new vector, then broadcasts its current location. This occurs twice every second.
-   **validateArguments():** Determines if the correct number of arguments have been passed in when instantiating a Robot instance 
-   **initRobotFromCfg(runtimeID):** Based on the config file `swarm.cfg`, fetches flow information such as the source and destination of the flow. Creates the Robot’s record of the source and destination node positions for the flow. Reads in information about all robots in the flow and identifies which information belongs to the Robot instance calling the function. Then it calls the methods `setFlowAndGraph(currFlow, robots)` and `establishConnections()` to
finish setting up the Robot instance.
-   **__main__ method :** Based on command line input, calls functions to initialize a Robot instance.

### ReneeScript.sh
Shell script that will start the emulator. It starts EMANE, opens the GUI, and starts the LogCompiler (which writes location coordinates to the scenario.eel file which the GUI will read from), and then opens up a terminal for each node (number must be hard-coded prior runtime), sshs into a particular node IP on each terminal, and then and runs an instance of Robot on each.

-------------------------------------------------------
## GUI Components
The left side of the olsrlinkview GUI displays the nodes and their relative positions to each other. Each labelled square in the olsrlinkview GUI represents a node in the network. Links between nodes are displayed as colored lines. The right side of the GUI displays a table with each of the nodes’ longitude and latitude positions which change as reflected in the `scenario.eel` file.

### Link colors (based on link quality):
-   Black (greater than 0.75)
-   Blue (0.5 - 0.75)
-   Yellow (0.25 - 0.5)
-   Red (less than 0.25)


## Pathloss & The Physical Layer Model
Information compiled from​ ​ AdjacentLink Documentation: https://github.com/adjacentlink/emane/wiki/Physical-Layer-Model

### Pathloss:
For each received packet, the physical layer computes the receiver power associated with that packet, and if the rxPower
is less than the rxSensitivity, the packet is silenty discarded:
```
rxPower = txPower + txAntennaGain + rxAntennaGain − pathloss
rxSensitivity = −174 + noiseFigure + 10log(bandWidth)
```

### Configuration:
Physical Layer Model configurations are made in `rfpipenem.xml`, in between the <phy></phy> tags.

### Sample configuration (in rfpipenem.xml):
```xml
<nem>
    <transport definition="transvirtual.xml"/>
    <mac definition="rfpipemac.xml"/>
    <phy>
        <param name="fixedantennagain"          value="0.0"/>
        <param name="fixedantennagainenable"    value="on"/>
        <param name="bandwidth"                 value="10M"/>
        <param name="noisemode"                 value="outofband"/>
        <param name="propagationmodel"          value="freespace"/>
        <param name="systemnoisefigure"         value="4.0"/>
        <param name="txpower"                   value="0.0"/>
        <param name="subid"                     value="1"/>
    </phy>
</nem>
```

### Configuration Parameters:
#### bandwidth
Defines receiver bandwidth in Hz and also serves as the default bandwidth for OTA transmissions when not provided
by the MAC.
#### fixedantennagain
Defines the antenna gain in dBi and is valid only when fixedantennagainenable is enabled.
#### fixedantennagainenable
Defines whether fixed antenna gain is used or whether antenna profiles are in use.
#### frequency
Defines the default transmit center frequency in Hz when not provided by the MAC.
#### frequencyofinterest
Defines a set of center frequencies in Hz that are monitored for reception as either in-band or out-of-band.
#### noisebinsize
Defines the noise bin size in microseconds and translates into timing accuracy associated with aligning the start and
end of reception times of multiple packets for modeling of interference effects.
#### noisemaxclampenable
Defines whether segment offset, segment duration and message propagation associated with a received packet will
be clamped to their respective maximums defined by noisemaxsegmentoffset, noisemaxsegmentduration and
noisemaxmessagepropagation. When disabled, any packet with an above max value will be dropped.
#### noisemaxmessagepropagation
Noise maximum message propagation in microseconds.
#### noisemaxsegmentduration
Noise maximum segment duration in microseconds.
#### noisemaxsegmentoffset
Noise maximum segment offset in microseconds.
#### noisemode
Defines the noise processing mode of operation: none, all or outofband.
#### propagationmodel
Defines the pathloss mode of operation: precomputed, 2ray or freespace.
#### subid
Defines the emulator PHY subid used by multiple NEM definitions. Once instantiated, these NEMs may be using the
same frequency. In order to differentiate between emulator PHY instances for different waveforms, the subid is used as
part of the unique waveform identifying tuple: PHY Layer Registration Id, emulator PHY subid and packet center
frequency.
#### systemnoisefigure
Defines the system noise figure in dB and is used to determine the receiver sensitivity.
#### timesyncthreshold
Defines the time sync detection threshold in microseconds. If a received OTA message is more than this threshold, the
message reception time will be used as the source transmission time instead of the time contained in the Common PHY Header. This allows the emulator to be used across distributed nodes without time sync.
#### txpower
Defines the transmit power in dBm.
