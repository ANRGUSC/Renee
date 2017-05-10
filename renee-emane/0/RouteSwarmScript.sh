#!/bin/sh
sudo ./demo-stop
sudo ./demo-start
../scripts/olsrlinkview.py &
./LogCompiler.py &

xterm -title "Node 1" -e "ssh -o PasswordAuthentication=no node-1; cd 401/emane-tutorial/0; python Robot.py 1" &
xterm -title "Node 2" -e "ssh -o PasswordAuthentication=no node-2; cd 401/emane-tutorial/0; python Robot.py 2" &
xterm -title "Node 3" -e "ssh -o PasswordAuthentication=no node-3; cd 401/emane-tutorial/0; python Robot.py 3" &
xterm -title "Node 4" -e "ssh -o PasswordAuthentication=no node-4; cd 401/emane-tutorial/0; python Robot.py 4" &
xterm -title "Node 5" -e "ssh -o PasswordAuthentication=no node-5; cd 401/emane-tutorial/0; python Robot.py 5" &
# xterm -title "Node 6" -e "ssh -o PasswordAuthentication=no node-6; cd 401/emane-tutorial/0; python Robot.py 6" &


#chmode u+x RouteSwarmScript.sh 
