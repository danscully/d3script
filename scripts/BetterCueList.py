import sys
import d3script
from gui.track.cuelist import * 

def init_callback():
    d3script.log('BetterCueList','BetterCueList loaded.')
    
def refresh_patch(widget):
    oldScrollPos = None
    if widget.view.items:
        oldScrollPos = widget.view.listView.vScroll.ratio
    items = []
    setList = state.currentTransportManager.setList
    widget._setList = setList
    for track in setList.tracks:
        beats = [ CueItem(track, beat, widget.view) for beat in track.noteTagSectionBeats() if widget.filter_cue(track, beat) ]

        try:
            
            #handle SACN cues
            searchStringSplits = widget.searchString.split('.')
            if (len(searchStringSplits) == 3):
                searchString = searchStringSplits[0] + searchStringSplits[1] + '.' + searchStringSplits[2]
            else:
                searchString = widget.searchString
                
            targetNumber = float(searchString)
            prevMatchTime = None

            for i in range(0,track.tags.n()):
                tagText = track.tags.getV(i)
                if ("CUE " in tagText):
                    cueText = tagText[4:]
                    
                    #Deal with sACN Cues
                    cueTextSplits = cueText.split('.')
                    if (len(cueTextSplits) == 3):
                        cueText = cueTextSplits[0] + cueTextSplits[1] + '.' + cueTextSplits[2]
                        
                    cueNumber = float(cueText)
                    
                    if (cueNumber <= targetNumber):
                        prevMatchTime = track.tags.getT(i)
                    elif (cueNumber == targetNumber):
                        prevMatchTime = None
                    else:
                        break
            
            if (prevMatchTime):
                beats = [CueItem(track,prevMatchTime,widget.view)]

        except:
            pass
                        
        if beats or widget.filter_track(track):
            items.append(TrackItem(track, 0.0, widget.view))
            items.extend(beats)

    widget.view.items = items
    widget.hideTrackField()
    widget.update()
    if oldScrollPos:
        widget.view.listView.vScroll.ratio = oldScrollPos
    return

def loadImprovements():
    clm = sys.modules['gui.track.cuelist']
    clm.CueList.refresh = refresh_patch
    
    
SCRIPT_OPTIONS = {
    "minimum_version" : 23, # Min. compatible version
    "init_callback" : init_callback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Load Better Cue List", # Display name of script
            "group" : "Better Cue List", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Load Improvements to the Cue List Widget", #text for help system
            "callback" : loadImprovements, # function to call for the script
        }
        ]
    }