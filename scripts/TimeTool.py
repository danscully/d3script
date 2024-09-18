import d3script
import time
from d3 import *
from math import floor

DEFAULT_FPS = 30.0
DEFAULT_AMT = 30

def insertTime(time):
    op = Undoable('Timetool Insert Time')

    #timeAmount is in seconds
    #TODO: Get Real FPS for the track rather than the guess above
    timeBase = 1 / DEFAULT_FPS

    #Check format and parse time
    timeMatch = re.search('^([1-9][0-9]*)(?:\.([1-9][0-9]*))?',time)
    if not timeMatch:
        alertInfo('Time in wrong format.  Should be in seconds or seconds.frames (e.g. "54" or "30.12").  No changes made.')
        return
    else:
        timeAmount = float(timeMatch.group(1))

        if len(timeMatch.groups()) > 1:
            timeAmount += float(timeMatch.group(2)) * timeBase

    #grab the tRender time as the insertion point 
    timeInsert = state.player.tRender

    #If audio track or quantized, bail   
    if (len(state.track.audio_sections) > 1):
        alertInfo('Audio Tracks not supported. No changes made.')
        return
    
    #Store output status and Hold onstage
    outputState = state.localOrDirectorState().directorState().output 
    state.localOrDirectorState().directorState().output = LocalState.Hold

    #Extend length of track
    state.track.lengthInBeats = state.track.timeToBeat(timeAmount)

    #get the barWidget to help us move stuff
    bw = d3script.getTrackWidget().barWidget

    for lay in state.track.layers:

        if lay.tEnd <= timeInsert:
            #layer is before the insertion point
            continue
        
        if lay.tStart >= timeInsert:
            bw.moveLayer(lay,lay.tStart + timeAmount)  

        else:
            #Extend Layer
            lay.setExtents(lay.tStart,lay.tEnd + timeAmount)

            #Move all the keyframes that need to move
            for fs in lay.fields:
              seq = fs.sequence
              for k in seq.keys:
                  k.localT += timeAmount



        #Move the annots
        def moveAnnots(timeSequence):
            numAnnots = timeSequence.n()
            for i in range(numAnnots-1, -1):
                annotTime = timeSequence.getT(i)
                if annotTime < timeInsert:
                    #we are iterating backwards, so lets bail 
                    break
                else:
                    annotValue = timeSequence.getV(i)
                    timeSequence.removeIndex(i)
                    timeSequence.set(annotTime,annotValue)

        moveAnnots(state.track.tags)
        moveAnnots(state.track.notes)
        moveAnnots(state.track.sections)

        state.localOrDirectorState().directorState().output = outputState


class TimeAddingWidget(Widget):
    isStickyable = False

    def __init__(self):

        Widget.__init__(self)
        self.arrangeVertical()

        titleButton = TitleButton("Insert Time:")
        self.add(titleButton)
        self.tsw = TimecodeSubmitWidget()
        self.add(self.tsw)
        self.arrangeVertical()

        self.pos = (d3gui.root.size / 2) - (self.size/2)


def insertTimePopup():
    time = str(DEFAULT_AMT)
    menu = PopupMenu('Insert Time')
    menu.editItem('Seconds:', time, insertTime)
    menu.pos = (d3gui.root.size / 2) - (menu.size/2)
    menu.pos = Vec2(menu.pos[0],menu.pos[1]-100)

    d3gui.root.add(menu)
    menu.contents.findWidgetByName('Seconds:').textBox.focus = True

def initCallback():
    d3script.log("Time Tool","Time Tool Loaded")

SCRIPT_OPTIONS = {
    "minimum_version" : 21, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Insert Time", # Display name of script
            "group" : "Time Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Insert seconds on the current track at the playhead ", #text for help system
            "callback" : insertTimePopup, # function to call for the script
        }
        ]
    }