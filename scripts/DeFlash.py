import d3script
from d3 import *



def deFlasher(newTrack=None):
    tm = state.currentTransportManager
    tm.player.onChangedTrack.add(deFlasher)
    tm.player.onSwitchPlayMode.add(changeTransportFirstRun)

    
    def patchedupdateNetworkLockedButtonState(self):
        if d3NetManager.mobileEditorMode:
            self.lockToDirectorButton.hidden = False
            if d3.state.lockedToDirector:
                self.lockToDirectorButton.name = tr('Locked To Director')
                self.lockToDirectorButton.setSuggestion('Timeline is locked to director')
                #self.lockToDirectorButton.flash(d3.state.lockedToDirector, 0.5, Colour(0.375, 0.5, 0.375))
                self.lockToDirectorButton.backCol = Colour(0.0,0.5,0.5)
            
            else:
                self.lockToDirectorButton.name = tr('Independent')
                self.lockToDirectorButton.setSuggestion(tr('Timeline is not locked to director'))
                self.lockToDirectorButton.backCol = Colour(0.0,0.0,0.0,0.0)
            self.connectionStatusButton.hidden = False
        

        else:
            self.lockToDirectorButton.hidden = True
            self.connectionStatusButton.hidden = True

    #Monkey patch the track widget
    tw = d3script.getTrackWidget()
    tw.__class__.oldupdateNetworkLockedButtonState = tw.__class__.updateNetworkLockedButtonState
    tw.__class__.updateNetworkLockedButtonState = patchedupdateNetworkLockedButtonState

def changeTransportFirstRun(action):
    tm = state.currentTransportManager
    tm.player.onSwitchPlayMode.remove(changeTransportButtons)
    tm.player.onSwitchPlayMode.remove(changeTransportFirstRun)
    tm.player.onSwitchPlayMode.add(changeTransportButtons)
    changeTransportButtons(action)
    
def changeTransportButtons(action):
        
    mode = action.state
    transControls = d3gui.root.findWidgetByName('buttons')
    activeTint = Colour(0.0,1.0,1.0)
    offTint = Colour(0.0,0.0,0.0,0.0)
    stopTint = Colour(1.0,0.5,0.0)

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