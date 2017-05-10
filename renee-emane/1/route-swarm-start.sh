#!/bin/sh
sudo ./demo-stop
sudo ./demo-start
../scripts/olsrlinkview.py &
./LogCompiler.py &

xterm -title "Node 1" -e sudo bash -c "ssh -o PasswordAuthentication=no node-1; cd emane-tutorial/1; python Robot.py 1" &
xterm -title "Node 2" -e "ssh -o PasswordAuthentication=no node-2; cd emane-tutorial/1; python Robot.py 2" &
xterm -title "Node 3" -e "ssh -o PasswordAuthentication=no node-3; cd emane-tutorial/1; python Robot.py 3" &
xterm -title "Node 4" -e "ssh -o PasswordAuthentication=no node-4; cd emane-tutorial/1; python Robot.py 4" &
xterm -title "Node 5" -e "ssh -o PasswordAuthentication=no node-5; cd emane-tutorial/1; python Robot.py 5" &
xterm -title "Node 6" -e "ssh -o PasswordAuthentication=no node-6; cd emane-tutorial/1; python Robot.py 6" &
xterm -title "Node 7" -e "ssh -o PasswordAuthentication=no node-7; cd emane-tutorial/1; python Robot.py 7" &
xterm -title "Node 8" -e "ssh -o PasswordAuthdeentication=no node-8; cd emane-tutorial/1; python Robot.py 8" &


#chmode u+x RouteSwarmScript.sh 
