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

class NodePropertyFrame(Pmw.ScrolledFrame):
    def __init__(self,parent=None):
        Pmw.ScrolledFrame.__init__(self,
                                   parent,
                                   labelpos = 'n', 
                                   label_text = '',
                                   )
        
        self._rowNameIndexMap= {}
        self._headerEntries = []
        self._columnEntries = []
        self._headerFrame = None
        self._rowFrames = []

    def clear(self):
        self.setPropertyTable([],[])
        self.setTitle('')

    def setTitle(self,title):
        self.configure(label_text=title)
        
    def setPropertyTable(self,header,body):

        if self._headerFrame:
            if len(header) != len(self._headerEntries):
                for entry in self._headerEntries:
                    entry['entry'].pack_forget()
                    del entry['var']

                self._headerFrame.pack_forget()

                self._headerFrame = None
                self._headerEntries = []
            else:
                for i in range(0,len(self._headerEntries)):
                    if header[i]['text'] != self._headerEntries[i]['text']:
                        self._headerEntries[i]['text'] = header[i]['text']
                        self._headerEntries[i]['var'].set(header[i]['text'])

                    if self._headerEntries[i]['width'] != \
                            header[i]['width']:

                        self._headerEntries[i]['width'] = \
                            header[i]['width']

                        self._headerEntries[i]['entry'].configure(width = header[i]['width'])

                
                    if self._headerEntries[i]['foreground'] != \
                            header[i]['foreground']:

                        self._headerEntries[i]['foreground'] = \
                            header[i]['foreground']

                        self._headerEntries[i]['entry'].configure(disabledforeground = header[i]['foreground'])

                    if self._headerEntries[i]['background'] != \
                            header[i]['background']:

                        self._headerEntries[i]['background'] = \
                            header[i]['background']

                        self._headerEntries[i]['entry'].configure(disabledbackground = header[i]['background'])


        if not self._headerFrame:
            self._headerFrame = Frame(self.interior())
            self._headerFrame.pack(fill=X)

            for title in header:
                var = StringVar()
                width = title['width']
                foreground = title['foreground']
                background = title['background']
                text = title['text']

                entry = Entry(self._headerFrame,
                              relief=FLAT,
                              textvariable=var,
                              state=DISABLED,
                              disabledforeground=foreground,
                              disabledbackground=background,
                              width=width)

                entry.pack(side=LEFT,fill=X)

                var.set(text)

                item = {'var'   : var,
                        'entry' : entry,
                        'width' : width,
                        'foreground' : foreground,
                        'background' : background,
                        'text' : text,
                        }

                self._headerEntries.append(item)


        framesToAdd = 0
        framesToDelete = 0

        if len(self._rowFrames):
            if len(self._rowFrames) < len(body):
                framesToAdd = len(body) - len(self._rowFrames)

            elif len(self._rowFrames) > len(body):
                framesToDelete = len(self._rowFrames) - len(body)

                for i in range(0,framesToDelete):
                    entry = self._columnEntries.pop()
                    for item in entry:
                        item['entry'].pack_forget()
                        del item['var']

                    frame = self._rowFrames.pop()
                    frame.pack_forget()

        else:
            framesToAdd = len(body)

        # validate existing body entries
        for i in range(0,len(self._columnEntries)):
            for j in range(0,len(self._columnEntries[i])):
                if self._columnEntries[i][j]['text'] != \
                        body[i][j]['text']:

                    self._columnEntries[i][j]['text'] = \
                        body[i][j]['text']

                    self._columnEntries[i][j]['var'].set(body[i][j]['text'])


                if self._columnEntries[i][j]['width'] != \
                        body[i][j]['width']:

                    self._columnEntries[i][j]['width'] = \
                        body[i][j]['width']

                    self._columnEntries[i][j]['entry'].configure(width = body[i][j]['width'])

                
                if self._columnEntries[i][j]['foreground'] != \
                        body[i][j]['foreground']:

                    self._columnEntries[i][j]['foreground'] = \
                        body[i][j]['foreground']

                    self._columnEntries[i][j]['entry'].configure(disabledforeground = body[i][j]['foreground'])

                if self._columnEntries[i][j]['background'] != \
                        body[i][j]['background']:

                    self._columnEntries[i][j]['background'] = \
                        body[i][j]['background']

                    self._columnEntries[i][j]['entry'].configure(disabledbackground = body[i][j]['background'])

        if framesToAdd:
            # add required rows, if necessary
            bodyStartIndex = len(body)-framesToAdd

            for row in body[bodyStartIndex:]:
                frame = Frame(self.interior())
                frame.pack(fill=X)
                self._rowFrames.append(frame)

                entries = []

                for item in row:
                    var = StringVar()
                    width = item['width']
                    foreground = item['foreground']
                    background = item['background']
                    text = item['text']

                    entry = Entry(frame,
                                  relief=FLAT,
                                  textvariable=var,
                                  state=DISABLED,
                                  disabledforeground=foreground,
                                  disabledbackground=background,
                                  width=width)
                    entry.pack(side=LEFT,fill=X)

                    var.set(text)

                    item = {'var'   : var,
                            'entry' : entry,
                            'width' : width,
                            'foreground' : foreground,
                            'background' : background,
                            'text' : text,
                            }

                    entries.append(item)

                    bodyStartIndex += 1

                self._columnEntries.append(entries)
