#!/bin/sh

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
sudo ./demo-stop
sudo ./demo-start
../scripts/olsrlinkview.py &
./LogCompiler.py &

xterm -title "Node 1" -e ssh -o PasswordAuthentication=no node-1 -t "cd $PWD; python Robot.py 1; bash" &
xterm -title "Node 2" -e ssh -o PasswordAuthentication=no node-2 -t "cd $PWD; python Robot.py 2; bash" &
xterm -title "Node 3" -e ssh -o PasswordAuthentication=no node-3 -t "cd $PWD; python Robot.py 3; bash" &
xterm -title "Node 4" -e ssh -o PasswordAuthentication=no node-4 -t "cd $PWD; python Robot.py 4; bash" &
xterm -title "Node 5" -e ssh -o PasswordAuthentication=no node-5 -t "cd $PWD; python Robot.py 5; bash" &
xterm -title "Node 6" -e ssh -o PasswordAuthentication=no node-6 -t "cd $PWD; python Robot.py 6; bash" &
xterm -title "Node 7" -e ssh -o PasswordAuthentication=no node-7 -t "cd $PWD; python Robot.py 7; bash" &
xterm -title "Node 8" -e ssh -o PasswordAuthentication=no node-8 -t "cd $PWD; python Robot.py 8; bash" &
