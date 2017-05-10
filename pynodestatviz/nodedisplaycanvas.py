#
# Copyright (c) 2012 - DRS CenGen, LLC, Columbia, Maryland
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
# * Neither the name of DRS CenGen, LLC nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

from Tkinter import *
import Pmw
   
class NodeDisplayCanvas(Pmw.ScrolledCanvas):
    def __init__(self,parent=None):
        Pmw.ScrolledCanvas.__init__(self,
                                    parent,
                                    labelpos = 'n',
                                    label_text='')
        self._nodes = {}
        self._nodeIdNameMap = {}
        self._selectedNode = None
        self._canvas = self.interior()
        self._edges = []

        self._canvas.configure(background='white')

        # self._canvas.tag_bind("node","<B1-Motion>",self._moveNode)
        # self._canvas.tag_bind("node","<Button-1>",self._selectNode)
        # self._canvas.tag_bind("node","<B1-ButtonRelease>",self._deselectNode)

    def getNodeLocations(self):
        locations = []

        for node in self._nodes:
            locations.append((node,
                              self._nodes[node]['x'],
                              self._nodes[node]['y']))

        return locations

    def clear(self):
        self._canvas.delete("edge")
        self._canvas.delete("node")
        self._canvas.delete("label")
        self._nodeIdNameMap = {}
        self._nodes = {}

    def addNode(self,name,x,y,color):
        if name in self._nodes:
            # if self._nodes[name]['color'] != color:
            #     self._canvas.itemconfigure(self._nodes[name]['canvasId'],fill=color)
            #     self._nodes[name]['color'] = color

            # if float(self._nodes[name]['x']) != x:
            #     self._canvas.itemconfigure(self._nodes[name]['canvasId'], x=x)
            #     self._canvas.coords(self._nodes[name]['canvasId'], )
            #     self._nodes[name]['x'] = x
            self._canvas.delete("edge-%s" % name)
            self._canvas.delete(self._nodes[name]['canvasId'])
            self._canvas.delete(self._nodes[name]['labelId'])
            self._nodes[name] = \
                { 
                'x': x,
                'y': y,
                'color' : color,
                'edges': {},
                'redges': {},
                'canvasId' : None,
                'labelId' : None,
                }

            # canvasId property set in _drawNode
            self._drawNode(name)

            self._nodeIdNameMap[self._nodes[name]['canvasId']] = name

            
        else:
            self._nodes[name] = \
                { 
                'x': x,
                'y': y,
                'color' : color,
                'edges': {},
                'redges': {},
                'canvasId' : None,
                'labelId'  : None,
                }

            # canvasId property set in _drawNode
            self._drawNode(name)

            self._nodeIdNameMap[self._nodes[name]['canvasId']] = name

    def deleteNode(self,name):
        self._canvas.delete("node-%s" % name)
        self._canvas.delete("label-%s" % name)
        self._canvas.delete("edge-%s" % name)
        
        for source in self._nodes[name]['redges']:
            del self._nodes[souce]['edge'][name]

        del self._nodeIdNameMap[self._nodes[name]['canvasId']]
        del self._nodes[name]
        
    def addEdge(self,source,destination,color,color2,style):
        
        if source in self._nodes and \
                destination in  self._nodes:
            
            if not color2:
                color2 = color

            self._drawEdge(source,destination,color,color2,style,False)

    def deleteEdge(self,source,destination):
        if destination in self._nodes[source]['edges']:
            del self._nodes[source]['edges'][destination]
            del self._nodes[destination]['redges'][source]
            self._canvas.delete("edge-%s_to_%s" % (source,destination))

    def _drawEdge(self,source,destination,color,color2,style,force):
        xsrc = self._nodes[source]['x']
        ysrc = self._nodes[source]['y']
        xdst = self._nodes[destination]['x']
        ydst = self._nodes[destination]['y']

        if destination in self._nodes[source]['edges']:
            if force or \
                    ysrc !=  self._nodes[source]['edges'][destination]['ysrc'] or \
                    xsrc !=  self._nodes[source]['edges'][destination]['xsrc'] or \
                    ydst !=  self._nodes[source]['edges'][destination]['ydst'] or \
                    ydst !=  self._nodes[source]['edges'][destination]['ydst'] or \
                    color != self._nodes[source]['edges'][destination]['color'] or \
                    color2 != self._nodes[source]['edges'][destination]['color2'] or \
                    style != self._nodes[source]['edges'][destination]['style']:
                self.deleteEdge(source,destination)
            else:
                return
        
        self._nodes[source]['edges'][destination] = {'color' : color,
                                                     'color2' : color2,
                                                     'style' : style,
                                                     'xsrc'  : xsrc,
                                                     'ysrc'  : ysrc,
                                                     'xdst'  : xdst,
                                                     'ydst'  : ydst,
                                                     }

        self._nodes[destination]['redges'][source] = {}

        if style == "dash_to_solid" or style == "dash":
            dash=2
        else:
            dash=None

        self._edges.append(self._canvas.create_line(xsrc,
                                 ysrc,
                                 (xsrc + xdst) /2,
                                 (ysrc + ydst) /2,
                                 tags = (str(source),
                                         str(destination),
                                         'edge',
                                         "edge-%s" % source,
                                         "edge-%s" % destination,
                                         "edge-%s_to_%s" %(source,destination)),
                                 width=2,
                                 fill = color,
                                 dash=dash))
        
        if style == "solid_to_dash" or style == "dash":
            dash=2
        else:
            dash=None

        self._edges.append(self._canvas.create_line((xsrc + xdst) / 2,
                                 (ysrc + ydst) / 2,
                                 xdst,
                                 ydst,
                                 tags = (str(source),
                                         str(destination),
                                         'edge',
                                         "edge-%s" % source,
                                         "edge-%s" % destination,
                                         "edge-%s_to_%s" %(source,destination)),
                                 dash=dash,
                                 width=2,
                                 fill = color2))

        
        self._canvas.tag_lower('edge','label')
        self._canvas.tag_lower('edge','node')

    def _redrawEdges(self,name):
        
        self._canvas.delete("edge-%s" % name)

        
        for destination in self._nodes[name]['edges']:
            self._drawEdge(name,
                           destination,
                           self._nodes[name]['edges'][destination]['color'],
                           self._nodes[name]['edges'][destination]['color2'],
                           self._nodes[name]['edges'][destination]['style'],
                           True)

        for source in self._nodes[name]['redges']:
            self._drawEdge(source,
                           name,
                           self._nodes[source]['edges'][name]['color'],
                           self._nodes[source]['edges'][name]['color2'],
                           self._nodes[source]['edges'][name]['style'],
                           True)
            
    def clearAllEdges(self):
        for edge in self._edges:
            self._canvas.delete(edge)

    def _drawNode(self,name):
        x = self._nodes[name]['x']
        y = self._nodes[name]['y']
        color = self._nodes[name]['color']

        self._nodes[name]['canvasId'] = \
            canvasId = self._canvas.create_rectangle(x-5,
                                                     y-5,
                                                     x+5,
                                                     y+5,
                                                     fill = color,
                                                     tags = (str(name),'node',"node-%s" % name))
        self._nodes[name]['labelId'] = \
            labelId = self._canvas.create_text(x,
                                 y+15,
                                 text=name,
                                 tags = (str(name),'label',"label-%s" % name))


    def _moveNode(self,event):
        if self._selectedNode not in self._nodeIdNameMap:
            return

        name = self._nodeIdNameMap[self._selectedNode]
        x = self._canvas.canvasx(event.x)
        y = self._canvas.canvasy(event.y)

        self._nodes[name]['x'] = x
        self._nodes[name]['y'] = y
        
        self._canvas.coords(self._selectedNode,
                            x-5,
                            y-5,
                            x+5,
                            y+5)

        self._canvas.delete("label-%s" % name)

        
        self._canvas.create_text(x,
                                 y+15,
                                 text=name,
                                 tags = (str(name),'label',"label-%s" % name))

        self._redrawEdges(name)

    def _selectNode(self,event):
        self._selectedNode = self._canvas.find_closest(self._canvas.canvasx(event.x),
                                                       self._canvas.canvasy(event.y))[0]
        
    def _deselectNode(self,event):
        self._selectedNode = None
