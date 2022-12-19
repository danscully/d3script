# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.8.2 (v3.8.2:7b3ab5921f, Feb 24 2020, 17:52:18) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: C:\blip\dev\scripts\gui\editor_transportmanager.py
# Compiled at: 2022-08-24 05:53:19
from d3 import *
from functools import partial
from gui.inputmap import *
import d3script
import re

def toggleDirectorEngaged():
    tm = state.localOrDirectorState().transport

    if (type(tm) == MultiTransportManager):
        curState = all(stm.engaged for stm in tm.transportManagers)
        for stm in tm.transportManagers:
            stm.engaged = not curState
    
    else:
        state.currentTransportManager.engaged ^= 1

def toggleLockToNetwork():
    d3.state.lockedToDirector = not d3.state.lockedToDirector

    if not d3.state.lockedToDirector:
        #Stop playing
        tw = d3script.getTrackWidget()
        tw.children[2].children[0].children[4].clickAction.doit()
    

class StatusWidget(Widget):
    isStickyable = True

    def __init__(self):
        Widget.__init__(self)
        rowHeight = 20
        self.resource = state.currentTransportManager
        self.arrangeHorizontal()
        self.updateAction.add(self.onUpdate)

        titleButton = TitleButton("Status:")
        self.add(titleButton)
        vb = ValueBox(self.resource, 'monitorString', readonly=True)
        vb.textBox.fontSize(14)
        vb.minSize = Vec2(200,rowHeight)
        self.add(vb)
        vb2 = ValueBox(self.resource, 'statusString', readonly=True)
        vb2.minSize = Vec2(200,rowHeight)
        self.add(vb2)
        
        self.directorEngagedButton = Button('', toggleDirectorEngaged)
        self.directorEngagedButton.minSize = Vec2(200,rowHeight)
        self.add(self.directorEngagedButton)
        self.updateDirectorEngagedButtonState()
        self.lockToDirectorButton = Button('', toggleLockToNetwork)
        self.add(self.lockToDirectorButton)
        self.updateNetworkLockedButtonState()
        modes = [tr('  Fade down  '), tr('  Fade up  '), tr('  Hold  ')]
        self.outputField = ValueBox(self, 'outputMode', modes).setHelpText('Controls fade up/down, hold, and visualiser mode')
        self.add(self.outputField)
        #self.computeAllMinSizes()
        self.minSize.x = 400
        

    def onUpdate(self):
        self.updateDirectorEngagedButtonState()
        self.updateNetworkLockedButtonState()
        output = state.localOrDirectorState().directorState().output
        if output == LocalState.FadeUp:
            self.outputField.backCol  = Colour(0.0, 0.8, 0.0)
        elif output == LocalState.FadeDown: 
            self.outputField.backCol  = Colour(0.5, 0.0, 0.5)
        else:
            self.outputField.backCol  = Colour(0.8, 0.0, 0.0)


    def onResourceChanged(self, resource):
        self.updateDirectorEngagedButtonState()

    def updateDirectorEngagedButtonState(self):
        if hasattr(self, 'directorEngagedButton'):
            self.directorEngagedButton.name = 'Engaged' if self.resource.engaged else 'Disengaged'
            if self.resource.engaged:
                self.directorEngagedButton.backCol = Colour(0.0, 0.8, 0.0)
            else:
                self.directorEngagedButton.backCol = Colour(8.0, 0.0, 0.0)

    def updateNetworkLockedButtonState(self):
        if d3NetManager.mobileEditorMode:
            self.lockToDirectorButton.hidden = False
            self.lockToDirectorButton.name = tr('Locked To Director') if d3.state.lockedToDirector else tr('Independent')
            self.lockToDirectorButton.setSuggestion('Timeline is locked to director' if d3.state.lockedToDirector else tr('Timeline is not locked to director'))
            
            if d3.state.lockedToDirector:
                self.lockToDirectorButton.backCol = Colour(0.0, 0.8, 0.0)
            else:
                self.lockToDirectorButton.backCol = Colour(0.6, 0.4, 0.0)
        else:
            self.lockToDirectorButton.hidden = True

    @property
    def outputMode(self):
        return state.localOrDirectorState().directorState().output

    @outputMode.setter
    def outputMode(self, v):
        state.localOrDirectorState().directorState().output = v


def openStatusWidget():
    widget = StatusWidget()
    widget.pos = (d3gui.root.size / 2) - (widget.size/2)
    widget.pos = Vec2(widget.pos[0],widget.pos[1]-100)

    d3gui.root.add(widget)


def holdDirector():
        state.localOrDirectorState().directorState().output = LocalState.Hold

def fadeUpDirector():
        state.localOrDirectorState().directorState().output = LocalState.FadeUp

def fadeDownDirector():
        state.localOrDirectorState().directorState().output = LocalState.FadeDown


def initCallback():
    d3script.log("statusWidget","statusWidget Loaded")

SCRIPT_OPTIONS = {
    "minimum_version" : 21, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Status Widget", # Display name of script
            "group" : "Status widget", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Transport Controls without config", #text for help system
            "callback" : openStatusWidget, # function to call for the script
        },
        {
            "name" : "Toggle Transport", # Display name of script
            "group" : "Status Widsget", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Alt,e", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Toggle Transport State", #text for help system
            "callback" : toggleDirectorEngaged, # function to call for the script
        },
        {
            "name" : "Toggle Locked to network", # Display name of script
            "group" : "Status Widsget", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Alt,l", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Toggle Locked to network", #text for help system
            "callback" : toggleLockToNetwork, # function to call for the script
        },
        {
            "name" : "Hold the Director", # Display name of script
            "group" : "Status Widsget", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Alt,h", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Hold output on the director", #text for help system
            "callback" : holdDirector, # function to call for the script
        },
        {
            "name" : "Fade Up the Director", # Display name of script
            "group" : "Status Widsget", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Alt,u", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Fade up output on the director", #text for help system
            "callback" : fadeUpDirector, # function to call for the script
        },
        {
            "name" : "Fade Down the Director", # Display name of script
            "group" : "Status Widsget", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Alt,d", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Fade down output on the director", #text for help system
            "callback" : fadeDownDirector, # function to call for the script
        }
    ]
}