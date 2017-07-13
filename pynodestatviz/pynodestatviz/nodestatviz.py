#
# Copyright (c) 2014 - Adjacent Link LLC, Bridgewater, New Jersey
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

from lxml import etree
from Tkinter import *
from textwrap import dedent
from pkg_resources import resource_filename
from nodedisplaycanvas import  NodeDisplayCanvas
from nodepropertyframe import NodePropertyFrame
from . import RenderException
import os
from Location import Location

class NodeStatViz(Frame):
    def __init__(self,location=None,parent=None):
        
        Frame.__init__(self,parent)

        self.master.title("Node Statistic Vizualizer")

        self.master.iconname("nodestatviz")

        self.pack(expand=YES,fill=BOTH,side=BOTTOM)

        self._statusLabel = Label(self,relief=SUNKEN,text="foo", anchor=W)

        self._statusLabel.pack(fill=X,side=BOTTOM)

        panedWindow = PanedWindow(self)
        
        self._nodeDisplayCanvas = NodeDisplayCanvas(panedWindow)

        panedWindow.add(self._nodeDisplayCanvas)

        self._nodePropertyFrame = NodePropertyFrame(panedWindow)

        panedWindow.add(self._nodePropertyFrame)
                
        panedWindow.pack(expand=YES,fill=BOTH,side=RIGHT)
        
        schemaDoc = etree.parse(resource_filename('pynodestatviz',
                                                  'schema/nodestatviz.xsd'))

        self._schema = etree.XMLSchema(etree=schemaDoc,attribute_defaults=True)

        xslt = \
            dedent('''\
                   <xsl:stylesheet version="1.0" 
                                  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
                     <xsl:output method="xml"/>
                     <xsl:template match="node()|@*">
                       <xsl:copy>
                         <xsl:apply-templates select="node()|@*"/>
                       </xsl:copy>
                     </xsl:template>
                     <xsl:template match="/nodestatviz/edges/edge/@src">
                       <xsl:copy>
                         <xsl:apply-templates select="node()|@*"/>
                       </xsl:copy>
                       <xsl:variable name="src" select="."/>
                       <xsl:variable name="nodes" select="/nodestatviz/nodes/node"/>
                       <xsl:if test="not($nodes[@name=$src])">
                         <xsl:message terminate="no">Edge using unknown source node: <xsl:value-of select="$src"/>
                         </xsl:message>
                       </xsl:if>
                     </xsl:template>
                     <xsl:template match="/nodestatviz/edges/edge/@dst">
                       <xsl:copy>
                         <xsl:apply-templates select="node()|@*"/>
                       </xsl:copy>
                       <xsl:variable name="dst" select="."/>
                       <xsl:variable name="nodes" select="/nodestatviz/nodes/node"/>
                       <xsl:if test="not($nodes[@name=$dst])">
                         <xsl:message terminate="no">Edge using unknown source node: <xsl:value-of select="$dst"/>
                         </xsl:message>
                       </xsl:if>
                     </xsl:template>
                     <xsl:template match="/nodestatviz/table/rows/row">
                       <xsl:copy>
                         <xsl:apply-templates select="node()|@*"/>
                       </xsl:copy>
                       <xsl:if test="count(./column)!=count(/nodestatviz/table/header/column)">
                         <xsl:message terminate="no">Rows must have the same number of columns as the header<text/>
                         </xsl:message>
                       </xsl:if>
                     </xsl:template>
                   </xsl:stylesheet>''')

        xsltDoc = etree.XML(xslt)
        
        self._transform = etree.XSLT(xsltDoc)

        (self._pipeRead,self._pipeWrite) = os.pipe()

        self.tk.createfilehandler(self._pipeRead,tkinter.READABLE,self._render)

        self.master.bind('<Control-Key-s>',self._saveLocations)
 
        self.master.bind('<Control-Key-l>',self._clear)

        self._nodes = []
        self._edges = []
        self._locations = {}
        self._locationsFile = location

        print("CHECKING FOR LOCATIONS FILE: ", self._locationsFile)
        if os.path.exists(self._locationsFile):
            print("File Exists")
            locationSchemaXML = dedent('''\
            <xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'>
              <xs:element name='nodestatviz-locations'>
                <xs:complexType>
                  <xs:sequence>
                    <xs:element name='nodes' minOccurs='0' maxOccurs='1'>
                      <xs:complexType>
                        <xs:sequence>
                          <xs:element name='node' minOccurs='0' maxOccurs='unbounded'>
                            <xs:complexType>
                              <xs:attribute name='name' type='xs:string' use='required'/>
                              <xs:attribute name='x' type='xs:float' use='required'/>
                              <xs:attribute name='y' type='xs:float' use='required'/>
                            </xs:complexType>
                          </xs:element>
                        </xs:sequence>
                      </xs:complexType>
                    </xs:element>
                  </xs:sequence>
                </xs:complexType>
              </xs:element>
            </xs:schema>''')

            parser = etree.XMLParser()

            locationsSchemaRoot = etree.XML(locationSchemaXML,parser)

            locationSchema = etree.XMLSchema(etree=locationsSchemaRoot,attribute_defaults=True)
            
            locationRoot = etree.parse(location)

            if not locationSchema(locationRoot):
                message = ""
                for entry in  locationSchema.error_log:
                    message += "%d: %s\n" % (entry.line,entry.message)
                print >> sys.stderr, message
            for node in locationRoot.xpath('/nodestatviz-locations/nodes/node'):
                self._locations[node.get('name')]=(float(node.get('x')),
                                                   float(node.get('y')))
    
            
    def _saveLocations(self,event):

        root = etree.Element("nodestatviz-locations")

        nodes =  etree.SubElement(root, "nodes")

        self._locations = {}
        
        for (name,x,y) in self._nodeDisplayCanvas.getNodeLocations():
            self._locations[name]= (x,y)

            etree.SubElement(nodes, "node",name=name,x=str(x),y=str(y))

        f = open(self._locationsFile, 'w')
        
        print >> f, etree.tostring(root,pretty_print=True)

        f.close()


    def update(self,xml):
        self._nodeDisplayCanvas.clearAllEdges
        os.write(self._pipeWrite,"%05d%s" % (len(xml),xml))

    def _render(self,file,mask):
        length = os.read(file,5)

        xml =  os.read(file,int(length))

        parser = etree.XMLParser()

        root = etree.XML(xml,parser)

        if not self._schema(root):
            message = ""
            for entry in self._schema.error_log:
                message += "%d: %s\n" % (entry.line,entry.message)
                print >> sys.stderr,"\nInvalid update:\n",message.rstrip()
                return

        result_tree = self._transform(root)
        
        if len(self._transform.error_log):
            message = ""
            for entry in self._transform.error_log:
                message += "%s\n" %(entry.message)
            print >> sys.stderr, "\nInvalid update:\n",message.rstrip()
            return

        root = result_tree.getroot()

        if root.get('clear') == 'yes':
             self._clear()
             nodes = []
             edges = []
        else:
            nodes = list(self._nodes)
            edges = list(self._edges)

        self._nodes = []
        self._edges = []
            
        for title in root.xpath('/nodestatviz/title'):
            self._setTitle(title.get('text'))

        hasNodes = False
        for node in root.xpath('/nodestatviz/nodes/node'):
            name = node.get('name')
            
            self._addNode(name,node.get('color'), node.get('x'), node.get('y'))

            self._nodes.append(name)

            if name in nodes:
                nodes.remove(name)

            hasNodes = True

                
        hasEdges = False

        for edge in root.xpath('/nodestatviz/edges/edge'):
            src = edge.get('src')
            dst = edge.get('dst')
            color = edge.get('color')
            color2 = edge.get('color2')

            self._addEdge(src,
                          dst,
                          color,
                          color2,
                          edge.get('style'))

            self._edges.append((src,dst))
            
            if (src,dst) in edges:
                edges.remove((src,dst))

            hasEdges = True

        for (src,dst) in edges:
            self._deleteEdge(src,dst)

        for node in nodes:
            self._deleteNode(node)


        if not hasEdges and not hasNodes:
            self._nodeDisplayCanvas.clear()

        hasTable = False

        for table in root.xpath('/nodestatviz/table'):
            tableHeader = []
            widths = []
            for header in table.xpath('header/column'):
                tableHeader.append(
                    {'text' : header.get('text'),
                     'width': int(header.get('width')),
                     'foreground': header.get('foreground'),
                     'background': header.get('background'),
                     })
                widths.append(int(header.get('width')))
                
            tableBody = []

            for row in table.xpath('rows/row'):
                tableRow = []
                i = 0
                for column in row.xpath('column'):
                    tableRow.append(
                        {'text' :column.get('text'),
                         'foreground': column.get('foreground'),
                         'background': column.get('background'),
                         'width': widths[i],
                         })
                    i += 1
                    
                tableBody.append(tuple(tableRow))
        
            self._setPropertyTable(tableHeader,tableBody)

            self._setPropertyTableTitle(table.get('title'))

            hasTable = True

        if not hasTable:
            self._nodePropertyFrame.clear()

        hasStatus = False

        for status in root.xpath('/nodestatviz/status'):
            self._setStatus(status.get('text'))
            hasStatus = True

        if not hasStatus:
            self._setStatus("")
            
    def _clear(self,event=None):
        self._nodeDisplayCanvas.clear()
        self._nodePropertyFrame.clear()
        self._setStatus("")

    def _addNode(self,name,color, xVal, yVal):
        # a1 = float(self._corners[0].getLat())
        # b1 = float(self._corners[0].getLon())
        # a2 = float(self._corners[1].getLat())
        # b2 = float(self._corners[1].getLon())


        # nodeX = float(xVal)
        # nodeY = float(yVal)
        # x = float(250*(nodeX-a1)/(a2-a1)) + 20
        # y = float(250*(nodeY-b1)/(b2-b1)) + 20


        x = float(xVal)
        y = float(yVal)
        self._nodeDisplayCanvas.addNode(name,x,y,color)

    def _addEdge(self,source,destination,color,color2,style):
        self._nodeDisplayCanvas.addEdge(source,destination,color,color2,style)
        
    def _deleteNode(self,name):
        self._nodeDisplayCanvas.deleteNode(name)

    def _deleteEdge(self,source,destination):
        self._nodeDisplayCanvas.deleteEdge(source,destination)
        
    def _setStatus(self,status):
        self._statusLabel.configure(text="nodes: %-10d %s" % (len(self._nodes),
                                                              status))
    def _setTitle(self,title):
        self.master.title(title)
    
    def _setPropertyTable(self,header,body):
        self._nodePropertyFrame.setPropertyTable(header,body)

    def _setPropertyTableTitle(self,title):
        self._nodePropertyFrame.setTitle(title)

