import d3script
from d3 import *

def deFlasher(newTrack=None):
    tm = state.currentTransportManager
    tm.player.onChangedTrack.add(deFlasher)
    tm.player.onSwitchPlayMode.add(changeTransportButtons)

def changeTransportButtons(action):
    mode = action.state
    transControls = d3gui.root.findWidgetByName('buttons')
    activeTint = Colour(0,255,255)
    offTint = Colour(100,100,100,0.0)
    stopTint = Colour(2,1,0)

    if transControls:
        for bt in transControls.children:
            if hasattr(bt,'flash'):
                bt.flash(False)
                bt.tint = offTint

    if (mode == 4):
        #Means hold at section, means we are in play > section mode
        mode = 1
    
    if (mode < 3):
        transControls.children[mode+1].tint = activeTint
    else:
        transControls.children[mode+1].tint = stopTint


def initCallback():
    d3script.log("De Flash","De Flash")

SCRIPT_OPTIONS = {
    "minimum_version" : 21, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "DeFlash", # Display name of script
            "group" : "DeFlash", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Stop Flashing UI elements", #text for help system
            "callback" : deFlasher, # function to call for the script
        }
        ]
    }