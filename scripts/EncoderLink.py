# FieldShortcuts.py

from gui.inputmap import *
from d3 import *
import d3script


encoderAction = "_focused"
shiftCtrlMode = True

def setShiftCtrlMode(value):
    global shiftCtrlMode

    if value == "True":
        shiftCtrlMode = True
    else:
        shiftCtrlMode = False


def setEncoderAction(field):
    global encoderAction
    print(encoderAction + ' - Before')
    encoderAction = field
    print(encoderAction + ' - After')
    if encoderAction == "_focused":
        pass
    elif encoderAction == "colXY":
        d3script.openLayerSequenceForProperty('xCol')
    elif encoderAction == "posXY":   
        d3script.openLayerSequenceForProperty('pos.x') 
    elif encoderAction == "redMinMax":   
        d3script.openLayerSequenceForProperty('red min') 
    elif encoderAction == "scaleXY":   
        d3script.openLayerSequenceForProperty('scale.x') 
    elif encoderAction == "cropLR":   
        d3script.openLayerSequenceForProperty('left') 
    elif encoderAction == "cropTB":   
        d3script.openLayerSequenceForProperty('top') 

def initCallback():
    d3script.log("EncoderLink","EncoderLink Loaded")

def scrollXEncoder(scale):
    global encoderAction
    global shiftCtrlMode
    fw = d3gui.root.focusedWidget()
    
    #print(encoderAction + ' - XEnc')
    if encoderAction == "_focused":
        pass
    elif encoderAction == "colXY":
        if fw.parent.parent.name != "xCol":
            d3script.openLayerSequenceForProperty('xCol')
    elif encoderAction == "posXY":   
        if fw.parent.parent.name != "pos.x":
            d3script.openLayerSequenceForProperty('pos.x') 
    elif encoderAction == "redMinMax":   
        if fw.parent.parent.name != "red min":
            d3script.openLayerSequenceForProperty('red min') 
    elif encoderAction == "scaleXY":   
        if fw.parent.parent.name != "scale.x":
            d3script.openLayerSequenceForProperty('scale.x') 
    elif encoderAction == "cropLR":   
        if fw.parent.parent.name != "left":
            d3script.openLayerSequenceForProperty('left') 
    elif encoderAction == "cropTB":   
        if fw.parent.parent.name != "top":
            d3script.openLayerSequenceForProperty('top')

    #if shiftCtrlMode:
    #    d3script.simulateKeydown('shift')
    #    d3script.simulateKeydown('ctrl')

    scrollFocusedSmall(scale)
    
    #if shiftCtrlMode:
    #    d3script.simulateKeyup('shift')
    #    d3script.simulateKeyup('ctrl') 


def scrollYEncoder(scale):
    global encoderAction
    global shiftCtrlMode
    #print(encoderAction + ' - YEnc')
    fw = d3gui.root.focusedWidget()

    if encoderAction == "_focused":
        advancePlayhead(scale)
        return
    elif encoderAction == "colXY":
        if fw.parent.parent.name != "yCol":
            d3script.openLayerSequenceForProperty('yCol')
    elif encoderAction == "posXY":   
        if fw.parent.parent.name != "pos.y":
            d3script.openLayerSequenceForProperty('pos.y')
    elif encoderAction == "redMinMax":   
        if fw.parent.parent.name != "red max":
            d3script.openLayerSequenceForProperty('red max') 
    elif encoderAction == "scaleXY": 
        if fw.parent.parent.name != "scale.y":  
            d3script.openLayerSequenceForProperty('scale.y') 
    elif encoderAction == "cropLR": 
        if fw.parent.parent.name != "right":  
            d3script.openLayerSequenceForProperty('right') 
    elif encoderAction == "cropTB":
        if fw.parent.parent.name != "bottom":   
            d3script.openLayerSequenceForProperty('bottom') 

    #if shiftCtrlMode:
    #    d3script.simulateKeydown('shift')
    #    d3script.simulateKeydown('ctrl')

    scrollFocusedSmall(scale)
    
    #if shiftCtrlMode:
    #    d3script.simulateKeyup('shift')
    #    d3script.simulateKeyup('ctrl') 


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
        },
        {
            "name" : "Scroll Focused Small", # Display name of script
            "group" : "Encoder Link", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "move value by 'small' amount.  'scale' is the direction as an int ", #text for help system
            "callback" : scrollXEncoder, # function to call for the script
        },
        {
            "name" : "Scroll Focused Small", # Display name of script
            "group" : "Encoder Link", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "move value by 'small' amount.  'scale' is the direction as an int ", #text for help system
            "callback" : scrollYEncoder, # function to call for the script
        },
        {
            "name" : "Scroll Focused Small", # Display name of script
            "group" : "Encoder Link", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "move value by 'small' amount.  'scale' is the direction as an int ", #text for help system
            "callback" : setEncoderAction, # function to call for the script
        }
    ]
}
