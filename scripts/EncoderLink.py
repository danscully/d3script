# FieldShortcuts.py

from gui.inputmap import *
from d3 import *
import d3script

def initCallback():
    d3script.log("EncoderLink","EncoderLink Loaded")


def scrollFocusedSmall(scale):
    scaleNumber = int(scale)
    fw = d3gui.root.focusedWidget()
    if hasattr(fw,'mouseScrollSmall'):
        fw.mouseScrollSmall(scaleNumber)

def advancePlayhead(step):
    stepInt = int(step)
    if (abs(stepInt) == 1):
        time = state.player.tCurrent + 1 * stepInt
    else:
        grr = state.globalRefreshRate
        time = ((state.player.tCurrent * grr.numerator/float(grr.denominator)) + 2.0 * (stepInt/abs(stepInt))) * (grr.denominator / float(grr.numerator)) 

    cmd = TransportCMDTrackBeat()
    tm = state.currentTransportManager
    trk = state.track 
    cmd.init(d3gui.root, tm, trk, trk.timeToBeat(time), trk.transitionInfoAtBeat(0))
    tm.addCommand(cmd)


SCRIPT_OPTIONS = {
    "minimum_version" : 23, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Scroll Focused Small", # Display name of script
            "group" : "Encoder Link", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "move value by 'small' amount.  'scale' is the direction as an int ", #text for help system
            "callback" : scrollFocusedSmall, # function to call for the script
        }
    ]
}
