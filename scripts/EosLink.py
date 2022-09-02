# D3 Helpers
from __future__ import print_function
from gui.inputmap import *
from d3 import *
from gui.track.layerview import LayerView
from gui.track import TrackWidget
import d3script
import re
import struct
import math
import time
import gui.widget
import gui.alertbox
from gui.tickbox import SimpleTickBoxWidget
import d3script
import socket



def sendMessage(caller,msg,param = None):

    OSCAddrLength = math.ceil((len(msg)+1) / 4.0) * 4
    packedMsg = struct.pack(">%ds" % (OSCAddrLength), str(msg))

    if param != None:
        OSCTypeLength = math.ceil((len(',s')+1) / 4.0) * 4
        packedType = struct.pack(">%ds" % (OSCTypeLength), str(',s'))
        OSCArgLength = math.ceil((len(param)+1) / 4.0) * 4
        packedParam = struct.pack(">%ds" % (OSCArgLength), str(param))

    else:
        OSCTypeLength = 0
        packedType = ''
        OSCArgLength = 0
        packedParam = ''

    oscMsg = packedMsg + packedType + packedParam

    dev = caller.oscDevices[caller.oscDeviceIndex]
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(oscMsg, (dev.sendIPAddress, dev.sendPort))
    time.sleep(0.1)

class EosCueDelete(Widget):
    cue = ''
    user = ''
    cuelist = ''

    def __init__(self):
        
        param = d3script.getPersistentValue('EosLinkUser')
        if param:
            self.user = param
        else:
            self.user = ''
        
        param = d3script.getPersistentValue('EosLinkList')
        if param:
            self.cuelist = param
        else:
            self.cuelist = ''

        param = d3script.getPersistentValue('EosOscDevice')
        if param:
            self.oscDeviceName = param
        else:
            self.oscDeviceName = ''
        
        self.oscDevices = resourceManager.allResources(OscDevice)
        self.oscDeviceIndex = 0
        for idx,item in enumerate(self.oscDevices):
            if item.description == self.oscDeviceName:
                self.oscDeviceIndex = idx
                break
        
        trk = state.track
        lastTagBeat = trk.findBeatOfLastTag(trk.timeToBeat(state.player.tCurrent))
        tag = trk.tagAtBeat(lastTagBeat)

        tagParts = tag.split(' ')
        if (len(tagParts) != 2) or (tagParts[0] != 'CUE'):
            self.cue = ''
        else:
            self.cue = tagParts[1]

        Widget.__init__(self)   
        self.titleButton = TitleButton("EosLink: DELETE Cue")
        self.add(self.titleButton)

        oscDeviceNames = map(lambda l: l.description, self.oscDevices)
        self.oscDeviceBox = ValueBox(self, 'oscDeviceIndex', oscDeviceNames)
        self.add(Field('OSC Device: ',self.oscDeviceBox))

        self.fieldWrapperWidget = CollapsableWidget('Cue Data','Cue Data')
        self.fieldWrapperWidget.arrangeVertical()
        self.add(self.fieldWrapperWidget)
        self.fieldSectionWidget = Widget()
        self.fieldSectionWidget.arrangeHorizontal()
        self.fieldWrapperWidget.add(self.fieldSectionWidget)
        self.labelWidget = Widget()
        self.valuesWidget = Widget()
        self.valuesWidget.minSize = Vec2(50,0)

        self.userEditBox = ValueBox(self,'user')
        self.listEditBox = ValueBox(self,'cuelist')
        self.cueEditBox = ValueBox(self,'cue')

        self.valuesWidget.add(self.userEditBox)
        self.valuesWidget.add(self.listEditBox)
        self.valuesWidget.add(self.cueEditBox)

        self.labelWidget.add(TextLabel('Eos User:').justify()) 
        self.labelWidget.add(TextLabel('Eos List:').justify())
        self.labelWidget.add(TextLabel('Cue Number:').justify()) 

        self.labelWidget.arrangeVertical()
        self.valuesWidget.arrangeVertical()
        
        self.fieldSectionWidget.add(self.labelWidget)
        self.fieldSectionWidget.add(self.valuesWidget)
        self.computeAllMinSizes()
        self.arrangeVertical()

        doButton = Button('Delete Cue',self.doCueDeletion)
        doButton.border = Vec2(0,10)
        self.add(doButton)
        self.pos = (d3gui.root.size / 2) - (self.size/2)
        self.pos = Vec2(self.pos[0],self.pos[1]-100)
        d3gui.root.add(self)

    def doCueDeletion(self):

        if (self.cuelist == '') or (self.cue == '') or (self.user == ''):
            d3script.log('EosLink','Missing list, cue, or user number.  Not sending a message.')
            self.close()
            return

        #Store Values for next time
        d3script.setPersistentValue('EosLinkUser',self.user)
        d3script.setPersistentValue('EosLinkList',self.cuelist)        
        d3script.setPersistentValue('EosOscDevice',self.oscDevices[self.oscDeviceIndex].description)

        prefix = '/eos/user/'+self.user

        #clear the cmd line
        msg = prefix + '/key/clear_cmdline'
        sendMessage(self, msg)

        #go into blind
        msg = prefix + '/key/delete'
        sendMessage(self, msg)

        #create the cue
        msg = prefix + '/set/cue/'+self.cuelist+'/'+self.cue
        sendMessage(self, msg)
        
        #We send enter twice to confirm new cue creation.  If cue exists it has no effect.
        msg = prefix + '/key/enter'
        sendMessage(self, msg)
        sendMessage(self, msg) 

        msg = prefix + '/key/clear_cmdline'
        sendMessage(self, msg)

        self.close()

class EosCueCreator(Widget):
    cue = ''
    user = ''
    cuelist = ''
    label = ''

    def __init__(self):
        
        param = d3script.getPersistentValue('EosLinkUser')
        if param:
            self.user = param
        else:
            self.user = ''
        
        param = d3script.getPersistentValue('EosLinkList')
        if param:
            self.cuelist = param
        else:
            self.cuelist = ''

        param = d3script.getPersistentValue('EosOscDevice')
        if param:
            self.oscDeviceName = param
        else:
            self.oscDeviceName = ''
        
        self.oscDevices = resourceManager.allResources(OscDevice)
        self.oscDeviceIndex = 0
        for idx,item in enumerate(self.oscDevices):
            if item.description == self.oscDeviceName:
                self.oscDeviceIndex = idx
                break
        



        trk = state.track
        lastTagBeat = trk.findBeatOfLastTag(trk.timeToBeat(state.player.tCurrent))
        tag = trk.tagAtBeat(lastTagBeat)
        self.label = trk.noteAtBeat(lastTagBeat)


        tagParts = tag.split(' ')
        if (len(tagParts) != 2) or (tagParts[0] != 'CUE'):
            self.cue = ''
        else:
            self.cue = tagParts[1]

        Widget.__init__(self)   
        self.titleButton = TitleButton("EosLink: Create Cue")
        self.add(self.titleButton)

        oscDeviceNames = map(lambda l: l.description, self.oscDevices)
        self.oscDeviceBox = ValueBox(self, 'oscDeviceIndex', oscDeviceNames)
        self.add(Field('OSC Device: ',self.oscDeviceBox))

        #d3script.log('parentLayer',str(commonFields))
        self.fieldWrapperWidget = CollapsableWidget('Cue Data','Cue Data')
        self.fieldWrapperWidget.arrangeVertical()
        self.add(self.fieldWrapperWidget)
        self.fieldSectionWidget = Widget()
        self.fieldSectionWidget.arrangeHorizontal()
        self.fieldWrapperWidget.add(self.fieldSectionWidget)
        self.labelWidget = Widget()
        self.valuesWidget = Widget()
        self.valuesWidget.minSize = Vec2(50,0)

        self.userEditBox = ValueBox(self,'user')
        self.listEditBox = ValueBox(self,'cuelist')
        self.cueEditBox = ValueBox(self,'cue')
        self.labelEditBox = ValueBox(self,'label')

        self.valuesWidget.add(self.userEditBox)
        self.valuesWidget.add(self.listEditBox)
        self.valuesWidget.add(self.cueEditBox)
        self.valuesWidget.add(self.labelEditBox)

        self.labelWidget.add(TextLabel('Eos User:').justify()) 
        self.labelWidget.add(TextLabel('Eos List:').justify())
        self.labelWidget.add(TextLabel('Cue Number:').justify()) 
        self.labelWidget.add(TextLabel('Cue Label:').justify()) 

        self.labelWidget.arrangeVertical()
        self.valuesWidget.arrangeVertical()
        
        self.fieldSectionWidget.add(self.labelWidget)
        self.fieldSectionWidget.add(self.valuesWidget)
        self.computeAllMinSizes()
        self.arrangeVertical()

        doButton = Button('Create Cue',self.doCueCreation)
        doButton.border = Vec2(0,10)
        self.add(doButton)
        self.pos = (d3gui.root.size / 2) - (self.size/2)
        
        self.pos = Vec2(self.pos[0],self.pos[1]-100)

        d3gui.root.add(self)

    def doCueCreation(self):

        if (self.cuelist == '') or (self.cue == '') or (self.user == ''):
            d3script.log('EosLink','Missing list, cue, or user number.  Not sending a message.')
            self.close()
            return

        #Store Values for next time
        d3script.setPersistentValue('EosLinkUser',self.user)
        d3script.setPersistentValue('EosLinkList',self.cuelist)        
        d3script.setPersistentValue('EosOscDevice',self.oscDevices[self.oscDeviceIndex].description)

        prefix = '/eos/user/'+self.user

        #clear the cmd line
        msg = prefix + '/key/clear_cmdline'
        sendMessage(self, msg)

        #go into blind
        msg = prefix + '/key/blind'
        sendMessage(self, msg)

        #create the cue
        msg = prefix + '/set/cue/'+self.cuelist+'/'+self.cue
        sendMessage(self, msg)
        
        #We send enter twice to confirm new cue creation.  If cue exists it has no effect.
        msg = prefix + '/key/enter'
        sendMessage(self, msg)
        sendMessage(self, msg) 

        msg = '/eos/set/cue/'+self.cuelist+'/'+self.cue+'/label'   
        sendMessage(self, msg,self.label)

        #go live
        msg = prefix + '/key/live'
        sendMessage(self, msg)

        self.close()
    
def createCueForCurrentSection():
    EosCueCreator()

def deleteCueForCurrentSection():
    EosCueDelete()

def initCallback():
    d3script.log('EosLink','Initialized')

SCRIPT_OPTIONS = {
    "minimum_version" : 21, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Create Cue for Current Section", # Display name of script
            "group" : "EosLink", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Creates a cue for the current section Tag", #text for help system
            "callback" : createCueForCurrentSection, # function to call for the script
        },
        {
            "name" : "Delete Cue", # Display name of script
            "group" : "EosLink", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Delete's an Eos cue - assumes current section Tag", #text for help system
            "callback" : deleteCueForCurrentSection, # function to call for the script
        }
        ]

    }
