# FieldShortcuts.py

from gui.inputmap import *
from d3 import *
import d3script
from gui.track.layerview import LayerSelection

def initCallback():
    d3script.log("FieldShortcuts","FieldShortcuts Loaded")


def openAnimatedSequences():

    ole = d3script.getTrackWidget().layerView.openEditorManager.openLayerEditors 

    if len(ole) == 0:
        tw = d3script.getTrackWidget()
        lv = tw.layerView
        lv.openEditorManager.requestLayerEditor(LayerSelection(lv.getSelectedLayers()))

    d3script.closeAllLayerSeparators()
    for x in ole:    
        m=filter(lambda f:f.fieldSequence.sequence.nKeys() > 1,ole[x].fieldWrappers)
        for f in m:
            f.field.parent.expand()
            f.openSequence(False)             



def doCloseAll():
    d3script.closeAllLayerSequences()
    d3script.closeAllLayerSeparators()

def openVideo():
    d3script.openLayerSequenceForProperty('video')

def openOpacity():
    d3script.openLayerSequenceForProperty('brightness')

def openPosX():
    d3script.openLayerSequenceForProperty('pos.x')

def openPosY():
    d3script.openLayerSequenceForProperty('pos.y')

def openScaleX():
    d3script.openLayerSequenceForProperty('scale.x')

def openScaleY():
    d3script.openLayerSequenceForProperty('scale.y')

def openSize():
    d3script.openLayerSequenceForProperty('size')

def openBlend():
    d3script.openLayerSequenceForProperty('blendMode')

def openColourX():
    d3script.openLayerSequenceForProperty('xCol')

def openColourY():
    d3script.openLayerSequenceForProperty('yCol')

def openRot():
    d3script.openLayerSequenceForProperty('rotation')

def openMapping():
    d3script.openLayerSequenceForProperty('mapping')

def openColourShift():
    d3script.openLayerEditorPropertyGroup('Colour Shift')

def openCrop():
    d3script.openLayerEditorPropertyGroup('Crop')  


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
