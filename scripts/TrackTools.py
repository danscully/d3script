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
    d3script.log("scullyscripts","ScullyScripts Loaded")


def toggleTransport():
    """Toggle transport engaged/disengaged"""
    tm = state.localOrDirectorState().transport

    if (type(tm) == MultiTransportManager):
        curState = all(stm.engaged for stm in tm.transportManagers)
        for stm in tm.transportManagers:
            stm.engaged = not curState
    
    else:
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


def moveSelectedLayersToPlayhead():
    """Move selected layers to playhead"""
    tw = d3script.getTrackWidget()
    lv = tw.layerView
    if len(lv.selectedLayerIDs) > 0:    
        selectedLayerObjects = lv.d3script.getSelectedLayers()
        t = tw.player.tCurrent
        map(lambda l: tw.barWidget.moveLayer(l,t), selectedLayerObjects) 

def trimSelectedLayersToPlayhead():
    """Trim selected layers to playhead"""
    tw = d3script.getTrackWidget()
    lv = tw.layerView
    if len(lv.selectedLayerIDs) > 0:    
        selectedLayerObjects = lv.d3script.getSelectedLayers()
        t = tw.player.tCurrent
        for l in selectedLayerObjects:
            if l.tStart < t:
                l.setExtents(l.tStart,t)

def importLayerFromLibraryByName(layerName):
    a = d3script.getTrackWidget().barWidget.popupBarMenu()
    widgets = d3gui.root.children

    popup = None
    for wd in widgets:
        if type(wd) == PopupMenu:
            popup = wd

    if (popup != None):
        ilButton = popup.children[1].children[0].children[1]
    
    ilButton.clickAction.doit()

    popup = None
    widgets = d3gui.root.children
    for wd in widgets:
        if (type(wd) == ObjectView) and (wd.children[0].name == "Layer Library"):
            popup = wd

    if (wd):
        widgets = wd.children[3].children[0].children
        for wd in widgets:
            if wd.name == layerName:
                wd.selectResource()

def resetTrackZoom():
    tw = d3script.getTrackWidget()
    for i in range(9):
        tw.barWidget.zoomIn()
    
    tw.barWidget.zoomOut()
    tw.focusMe()

def frameTrackZoom():
    tw = d3script.getTrackWidget()
    for i in range(9):
        tw.barWidget.zoomIn()

    tw.focusMe()

        
SCRIPT_OPTIONS = {
    "minimum_version" : 21, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Toggle Transport", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Alt,e", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Toggle Transport State", #text for help system
            "callback" : toggleTransport, # function to call for the script
        },
        {
            "name" : "Split Selected Layers", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Split Selected layers", #text for help system
            "callback" : splitSelectedLayers, # function to call for the script
        },
        {
            "name" : "Move Selected Layers To Playhead", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Move Selected layers to Playhead", #text for help system
            "callback" : moveSelectedLayersToPlayhead, # function to call for the script
        },
        {
            "name" : "Trim Selected Layers To Playhead", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Trim Selected layers to Playhead", #text for help system
            "callback" : trimSelectedLayersToPlayhead, # function to call for the script
        },
        {
            "name" : "Import Layer from Library By Name", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Import Layer from Library By Name", #text for help system
            "callback" : importLayerFromLibraryByName, # function to call for the script
        },
        {
            "name" : "Reset Track Zoom", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Reset Track Zoom to Normal", #text for help system
            "callback" : resetTrackZoom, # function to call for the script
        },
        {
            "name" : "Zoom Track to Frame Level", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Zoom Track to Frame Level", #text for help system
            "callback" : frameTrackZoom, # function to call for the script
        }
        ]

    }
