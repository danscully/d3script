# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.8.2 (v3.8.2:7b3ab5921f, Feb 24 2020, 17:52:18) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: C:\blip\dev\scripts\gui\editor_transportmanager.py
# Compiled at: 2022-08-24 05:53:19
from d3 import *
from gui.inputmap import *
import d3script

def toggleDirectorEngaged():
    tm = state.localOrDirectorState().transport

    if (type(tm) == MultiTransportManager):
        curState = all(stm.engaged for stm in tm.transportManagers)
        for stm in tm.transportManagers:
            stm.engaged = not curState
    
    else:
        state.currentTransportManager.engaged ^= 1


def toggleLtcEngaged():

    if (state.currentTransportManager.timecode == None):
        ltc = filter(lambda x:x.description == 'ltc_main',resourceManager.allResources(TimecodeTransportLtc))
        
        if (len(ltc) == 1):
            state.currentTransportManager.timecode = ltc[0]
    
    else:
        state.currentTransportManager.timecode = None


def switchToLtcVor():

    ltcVor = filter(lambda x:x.description == 'ltc_vor',resourceManager.allResources(TimecodeTransportLtc))
        
    if (len(ltcVor) == 1):
        state.currentTransportManager.timecode = ltcVor[0]


def toggleLockToNetwork(goToLocal = False):
    d3.state.lockedToDirector = not d3.state.lockedToDirector

    if goToLocal:
        localTrack = state.track
        localTime = state.player.tCurrent

    if not d3.state.lockedToDirector:
        #Stop playing
        tw = d3script.getTrackWidget()
        tw.children[2].children[0].children[4].clickAction.doit()
    
    if goToLocal:
        cmd = TransportCMDTrackBeat()
        tm = d3.state.currentTransportManager
        beat = localTrack.timeToBeat(localTime)
        #this is hack-y to use root for the parent of the command
        cmd.init(d3gui.root, tm, localTrack, beat, localTrack.transitionInfoAtBeat(beat))
        tm.addCommand(cmd)


def BringDirectorToEditorPlayhead():
    toggleLockToNetwork(goToLocal = True)


class StatusWidget(Widget):
    isStickyable = True

    def __init__(self):

        #define colors
        self.redColor = Colour(0.8, 0.0, 0.0)
        self.greenColor = Colour(0.0, 0.8, 0.0)
        self.purpleColor = Colour(0.5, 0.0, 0.5)
        self.orangeColor = Colour(0.6, 0.4, 0.0)
        self.defaultSize = Vec2(125 * d3gui.dpiScale.x,35 * d3gui.dpiScale.x)

        Widget.__init__(self)

        self.resource = state.currentTransportManager
        self.ltcResource = state.currentTransportManager.timecode
        self.arrangeHorizontal()
        self.updateAction.add(self.onUpdate)

        titleButton = TitleButton("Status:")
        self.add(titleButton)
        

        def makeStatusItem(label,val,size = self.defaultSize):
            wd = Widget()
            wd.arrangeVertical()
            wd.overrideMinSize = lambda x: size
            wd.add(TextLabel(label))
            wd.add(val)
            return wd

        #self.currentCue = self.getTagForCurrentTime(state.localOrDirectorState().directorState())
        #vb = ValueBox(self, 'currentCue', readonly=True)
        #vb.textBox.fontSize(14)
        #self.add(makeStatusItem('Director Cue:',vb))

        self.localCue = self.getTagForCurrentTime(state.localOrDirectorState().localState())
        vb = ValueBox(self, 'localCue', readonly=True)
        vb.textBox.fontSize(14)
        self.add(makeStatusItem('Local Cue:',vb))

        #self.lastEvent = 'MIDI 753'
        #vb = ValueBox(self, 'lastEvent', readonly=True)
        #vb.textBox.fontSize(14)
        #self.add(makeStatusItem('Last TP Event:',vb))

        tcWidget = Widget()
        tcWidget.arrangeHorizontal()
        vb = ValueBox(self.resource, 'monitorString', readonly=True)
        vb.textBox.fontSize(14)
        tcWidget.add(vb)
        tcWidget.add(ValueBox(self.resource, 'statusString', readonly=True))
        self.add(makeStatusItem('Timecode:',tcWidget,size=Vec2(200 * d3gui.dpiScale.x,35 * d3gui.dpiScale.x)))
        
        self.directorEngagedButton = Button('', toggleDirectorEngaged)
        self.directorEngagedButton.overrideMinSize = lambda x: self.defaultSize
        self.add(self.directorEngagedButton)
        self.updateDirectorEngagedButtonState()

        self.ltcEngagedButton = Button('', toggleLtcEngaged)
        self.ltcEngagedButton.overrideMinSize = lambda x: self.defaultSize
        self.add(self.ltcEngagedButton)
        self.updateLtcEngagedButtonState()

        self.lockToDirectorButton = Button('', toggleLockToNetwork)
        self.lockToDirectorButton.overrideMinSize = lambda x: self.defaultSize
        self.add(self.lockToDirectorButton)
        self.updateNetworkLockedButtonState()

        modes = [tr('  Fade down  '), tr('  Fade up  '), tr('  Hold  ')]
        self.outputField = ValueBox(self, 'outputMode', modes).setHelpText('Controls fade up/down, hold, and visualiser mode')
        self.add(self.outputField)
        self.maxSize.x = 1920    


    def onUpdate(self):
        self.updateDirectorEngagedButtonState()
        self.updateLtcEngagedButtonState()
        self.updateNetworkLockedButtonState()

        self.localCue = self.getTagForCurrentTime(state.localOrDirectorState().localState())
        self.currentCue = self.getTagForCurrentTime(state.localOrDirectorState().directorState())

        output = state.localOrDirectorState().directorState().output
        if output == LocalState.FadeUp:
            self.outputField.backCol  = self.greenColor
        elif output == LocalState.FadeDown: 
            self.outputField.backCol  = self.purpleColor
        else:
            self.outputField.backCol  = self.redColor


    def getTagForCurrentTime(self, stateContext):
        trk = stateContext.track
        ply = stateContext.currentTransport.player
        return trk.tagAtBeat(trk.findBeatOfLastTag(trk.timeToBeat(ply.tCurrent)))


    def onResourceChanged(self, resource):
        self.updateDirectorEngagedButtonState()


    def updateDirectorEngagedButtonState(self):
        if hasattr(self, 'directorEngagedButton'):
            self.directorEngagedButton.name = 'Engaged' if self.resource.engaged else 'Disengaged'
            if self.resource.engaged:
                self.directorEngagedButton.backCol = self.greenColor
            else:
                self.directorEngagedButton.backCol = self.redColor


    def updateLtcEngagedButtonState(self):
        if hasattr(self, 'ltcEngagedButton'):
            self.ltcEngagedButton.name = 'Ltc On' if self.resource.timecode != None else 'Ltc Off'
            if self.resource.timecode != None:
                self.ltcEngagedButton.backCol = self.greenColor
            else:
                self.ltcEngagedButton.backCol = self.redColor


    def updateNetworkLockedButtonState(self):
        if d3NetManager.mobileEditorMode:
            self.lockToDirectorButton.hidden = False
            self.lockToDirectorButton.name = tr('Locked To Director') if d3.state.lockedToDirector else tr('Independent')
            self.lockToDirectorButton.setSuggestion('Timeline is locked to director' if d3.state.lockedToDirector else tr('Timeline is not locked to director'))
            
            if d3.state.lockedToDirector:
                self.lockToDirectorButton.backCol = self.greenColor
            else:
                self.lockToDirectorButton.backCol = self.orangeColor
        else:
            #self.lockToDirectorButton.hidden = True
            self.lockToDirectorButton.name = tr('Locked To Director')
            self.lockToDirectorButton.backCol = self.greenColor 


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
            "group" : "Status Widget", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Transport Controls without config", #text for help system
            "callback" : openStatusWidget, # function to call for the script
        },
        {
            "name" : "Toggle Transport", # Display name of script
            "group" : "Status Widget", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Alt,e", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Toggle Transport State", #text for help system
            "callback" : toggleDirectorEngaged, # function to call for the script
        },
        {
            "name" : "Toggle Ltc Transport", # Display name of script
            "group" : "Status Widget", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Alt,t", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Toggle Ltc Transport", #text for help system
            "callback" : toggleLtcEngaged, # function to call for the script
        },
        {
            "name" : "Switch LTC to VOR", # Display name of script
            "group" : "Status Widget", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Toggle Ltc Transport", #text for help system
            "callback" : switchToLtcVor, # function to call for the script
        },
        {
            "name" : "Toggle Locked to network", # Display name of script
            "group" : "Status Widget", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Alt,l", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Toggle Locked to network", #text for help system
            "callback" : toggleLockToNetwork, # function to call for the script
        },
        {
            "name" : "Bring Director To Editor Playhead", # Display name of script
            "group" : "Status Widget", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Alt,g", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Bring Director To Editor Playhead", #text for help system
            "callback" : BringDirectorToEditorPlayhead, # function to call for the script
        },
        {
            "name" : "Hold the Director", # Display name of script
            "group" : "Status Widget", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Alt,h", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Hold output on the director", #text for help system
            "callback" : holdDirector, # function to call for the script
        },
        {
            "name" : "Fade Up the Director", # Display name of script
            "group" : "Status Widget", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Alt,u", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Fade up output on the director", #text for help system
            "callback" : fadeUpDirector, # function to call for the script
        },
        {
            "name" : "Fade Down the Director", # Display name of script
            "group" : "Status Widget", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Alt,d", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Fade down output on the director", #text for help system
            "callback" : fadeDownDirector, # function to call for the script
        }
    ]
}