# D3 Helpers
from __future__ import print_function
from gui.inputmap import *
from d3 import *
from gui.track.layerview import LayerView
from gui.track import TrackWidget
import d3script
import re
import gui.widget


def initCallback():
    d3script.log("FieldShortcuts","FieldShortcuts Loaded")

def closeSeparators():
    ole = d3script.getTrackWidget().layerView.openEditorManager.openLayerEditors
    for x in ole:  
        v = ole[x].findDescendantsByType(CollapsableWidget)
        w = list(v)
        for i in w:
            i.collapse()


def openSequenceForProperty(p):
    closeSeparators()
    ole = d3script.getTrackWidget().layerView.openEditorManager.openLayerEditors  
    for x in ole: 
        m=filter(lambda f:f.fieldSequence.name == p,ole[x].fieldWrappers)
        for f in m:
            f.field.parent.expand()
            if (f.fieldSequence.noSequence == True):
                f.field.valueBox.selectValue()
            else:
                f.openSequence(True)

#Main Functions

def openAnimatedSequences():
    """Open all Sequences with > 1 Keyframe"""
    closeSeparators()
    ole = d3script.getTrackWidget().layerView.openEditorManager.openLayerEditors 
    for x in ole:    
        m=filter(lambda f:f.fieldSequence.sequence.nKeys() > 1,ole[x].fieldWrappers)
        for f in m:
            f.field.parent.expand()
            f.openSequence(False)             

def closeAllSequences():
    """Close all sequences in open editors"""
    ole = d3script.getTrackWidget().layerView.openEditorManager.openLayerEditors  
    for x in ole:    
        for f in ole[x].fieldWrappers:
            f.closeSequence()

def openVideo():
    """Open Media Sequence for Open Editors"""
    openSequenceForProperty('video')

def toggleTransport():
    """Toggle transport engaged/disengaged"""
    state.currentTransportManager.engaged ^= 1

def duplicateSelectedLayers():
    """Duplicate Selected Layers"""
    lv = d3script.getTrackWidget().layerView
    if len(lv.selectedLayerIDs) > 0:
        lv._duplicateSelected()

def splitSelectedLayers():
    """Split selected layers"""
    tw = d3script.getTrackWidget()
    lv = tw.layerView
    if len(lv.selectedLayerIDs) > 0:
        selectedLayerObjects = lv.d3script.getSelectedLayers()
        t = tw.player.tCurrent
        lv.track.splitLayersAtBeat(selectedLayerObjects, t)

def doCloseAll():
    closeAllSequences()
    closeSeparators()

def openOpacity():
    openSequenceForProperty('brightness')

def openPosX():
    openSequenceForProperty('pos.x')

def openPosY():
    openSequenceForProperty('pos.y')

def openSize():
    openSequenceForProperty('size')

def openBlend():
    openSequenceForProperty('blendMode')

def openColourX():
    openSequenceForProperty('xCol')

def openRot():
    openSequenceForProperty('rotation')

def openMapping():
     openSequenceForProperty('mapping')

def openColourShift():
    lays = d3script.getSelectedLayers()
    ed = d3gui.findEditor(lays[0])
    v = ed.findDescendantsByType(CollapsableWidget)
    w = list(v)
    for i in w:
        i.collapse()
        if i.name == 'Colour Shift':
            i.expand()

def openCrop():
    lays = d3script.getSelectedLayers()
    ed = d3gui.findEditor(lays[0])
    v = ed.findDescendantsByType(CollapsableWidget)
    w = list(v)
    for i in w:
        i.collapse()
        if i.name == 'Crop':
            i.expand()   


SCRIPT_OPTIONS = {
    "minimum_version" : 21, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Open Animated Sequences", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor for animated props", #text for help system
            "callback" : openAnimatedSequences, # function to call for the script
        },
        {
            "name" : "Open Video Propery", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,v", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor video property", #text for help system
            "callback" : openVideo, # function to call for the script
        },
        {
            "name" : "Open Opacity Propery", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,t", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor brightness(opacity) property", #text for help system
            "callback" : openOpacity, # function to call for the script
        },
        {
            "name" : "Open PosX Propery", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,p", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor position X property", #text for help system
            "callback" : openPosX, # function to call for the script
        },
        {
            "name" : "Open PosY Propery", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,y", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor position Y property", #text for help system
            "callback" : openPosY, # function to call for the script
        },
        {
            "name" : "Open Size Propery", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,e", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor size property", #text for help system
            "callback" : openSize, # function to call for the script
        },
        {
            "name" : "Open Blend Propery", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,b", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor blend property", #text for help system
            "callback" : openBlend, # function to call for the script
        },
        {
            "name" : "Open ColourX Propery", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,h", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor ColourX property", #text for help system
            "callback" : openColourX, # function to call for the script
        },
        {
            "name" : "Open Rot Propery", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,r", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor Rotation property", #text for help system
            "callback" : openRot, # function to call for the script
        },
        {
            "name" : "Open Mapping Propery", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,m", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor Mapping property", #text for help system
            "callback" : openMapping, # function to call for the script
        },
        {
            "name" : "Open Colour Shift Propery", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,c", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor Colour Shift property", #text for help system
            "callback" : openColourShift, # function to call for the script
        },
        {
            "name" : "Open Crop Propery", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,o", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor Crop property", #text for help system
            "callback" : openCrop, # function to call for the script
        }
        ]

    }
