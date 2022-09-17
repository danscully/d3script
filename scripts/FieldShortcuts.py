# FieldShortcuts.py

from gui.inputmap import *
from d3 import *
import d3script

def initCallback():
    d3script.log("FieldShortcuts","FieldShortcuts Loaded")


def closeSeparators():
    ole = d3script.getTrackWidget().layerView.openEditorManager.openLayerEditors
    for x in ole:  
        v = ole[x].findDescendantsByType(CollapsableWidget)
        w = list(v)
        for i in w:
            i.collapse()


def closeAllSequences():
    """Close all sequences in open editors"""
    ole = d3script.getTrackWidget().layerView.openEditorManager.openLayerEditors  
    for x in ole:    
        for f in ole[x].fieldWrappers:
            f.closeSequence()


def openSequenceForProperty(p):
    closeAllSequences()
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


def openAnimatedSequences():
    closeSeparators()
    ole = d3script.getTrackWidget().layerView.openEditorManager.openLayerEditors 
    for x in ole:    
        m=filter(lambda f:f.fieldSequence.sequence.nKeys() > 1,ole[x].fieldWrappers)
        for f in m:
            f.field.parent.expand()
            f.openSequence(False)             


def openLayerEditorPropertyGroup(group):
    ole = d3script.getTrackWidget().layerView.openEditorManager.openLayerEditors 
    for x in ole:   
        v = ole[x].findDescendantsByType(CollapsableWidget)
        w = list(v)
        for i in w:
            i.collapse()
            if i.name == group:
                i.expand()


def doCloseAll():
    closeAllSequences()
    closeSeparators()

def openVideo():
    openSequenceForProperty('video')

def openOpacity():
    openSequenceForProperty('brightness')

def openPosX():
    openSequenceForProperty('pos.x')

def openPosY():
    openSequenceForProperty('pos.y')

def openScaleX():
    openSequenceForProperty('scale.x')

def openScaleY():
    openSequenceForProperty('scale.y')

def openSize():
    openSequenceForProperty('size')

def openBlend():
    openSequenceForProperty('blendMode')

def openColourX():
    openSequenceForProperty('xCol')

def openColourY():
    openSequenceForProperty('yCol')

def openRot():
    openSequenceForProperty('rotation')

def openMapping():
     openSequenceForProperty('mapping')

def openColourShift():
    openLayerEditorPropertyGroup('Colour Shift')

def openCrop():
    openLayerEditorPropertyGroup('Crop')  


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
            "name" : "Open Video Property", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,v", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor video property", #text for help system
            "callback" : openVideo, # function to call for the script
        },
        {
            "name" : "Open Opacity Property", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,t", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor brightness(opacity) property", #text for help system
            "callback" : openOpacity, # function to call for the script
        },
        {
            "name" : "Open PosX Property", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,x", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor position X property", #text for help system
            "callback" : openPosX, # function to call for the script
        },
        {
            "name" : "Open PosY Property", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,y", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor position Y property", #text for help system
            "callback" : openPosY, # function to call for the script
        },
        {
            "name" : "Open ScaleX Property", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,q", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor scale X property", #text for help system
            "callback" : openScaleX, # function to call for the script
        },
        {
            "name" : "Open ScaleY Property", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,w", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor scale Y property", #text for help system
            "callback" : openScaleY, # function to call for the script
        },
        {
            "name" : "Open Size Property", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,e", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor size property", #text for help system
            "callback" : openSize, # function to call for the script
        },
        {
            "name" : "Open Blend Property", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,b", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor blend property", #text for help system
            "callback" : openBlend, # function to call for the script
        },
        {
            "name" : "Open ColourX Property", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,h", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor ColourX property", #text for help system
            "callback" : openColourX, # function to call for the script
        },
        {
            "name" : "Open ColourY Property", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,j", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor ColourX property", #text for help system
            "callback" : openColourY, # function to call for the script
        },
        {
            "name" : "Open Rot Property", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,r", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor Rotation property", #text for help system
            "callback" : openRot, # function to call for the script
        },
        {
            "name" : "Open Mapping Property", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,m", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor Mapping property", #text for help system
            "callback" : openMapping, # function to call for the script
        },
        {
            "name" : "Open Colour Shift Property", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,c", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor Colour Shift property", #text for help system
            "callback" : openColourShift, # function to call for the script
        },
        {
            "name" : "Open Crop Property", # Display name of script
            "group" : "Field Shortcuts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl+Shift,o", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open layer editor Crop property", #text for help system
            "callback" : openCrop, # function to call for the script
        }
    ]
}
