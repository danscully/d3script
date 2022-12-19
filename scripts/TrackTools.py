# Track Tools
from operator import truediv
from gui.inputmap import *
from d3 import *
from gui.columnlistview import *
import d3script

def initCallback():
    d3script.log("scullyscripts","ScullyScripts Loaded")

def deSequenceLayers():
    op = Undoable('deSequence Layers')
    lays = d3script.getSelectedLayers()
    for lay in lays:
    
        if isinstance(lay,GroupLayer):
            continue

        flds = lay.fields
        flds = filter(lambda f:((f.noSequence == False) and (f.sequence.nKeys() <= 1)),flds)

        for fld in flds:
            fs = fld.sequence
            fs.stripToFirstKey()
            fld.disableSequencing = True
            

def hardMuteLayers():
    lays = d3script.getSelectedLayers()

    for lay in lays:
        d3script.setExpression(lay,'brightness','0')
        lay.name = 'MUTED ' + lay.name

def hardUnMuteLayers():
    lays = d3script.getSelectedLayers()

    for lay in lays:
        d3script.setExpression(lay,'brightness','self')
        if (lay.name.find('MUTED') == 0):
            lay.name = lay.name[6:]


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
        selectedLayerObjects = d3script.getSelectedLayers()
        t = tw.player.tCurrent
        lv.track.splitLayersAtBeat(selectedLayerObjects, t)


def moveSelectedLayersToPlayhead():
    """Move selected layers to playhead"""
    tw = d3script.getTrackWidget()
    lv = tw.layerView
    if len(lv.selectedLayerIDs) > 0:    
        selectedLayerObjects = d3script.getSelectedLayers()
        t = tw.player.tCurrent
        map(lambda l: tw.barWidget.moveLayer(l,t), selectedLayerObjects) 

def trimSelectedLayersToPlayhead():
    """Trim selected layers to playhead"""
    tw = d3script.getTrackWidget()
    lv = tw.layerView
    if len(lv.selectedLayerIDs) > 0:    
        selectedLayerObjects = d3script.getSelectedLayers()
        t = tw.player.tCurrent
        for l in selectedLayerObjects:
            if l.tStart < t:
                l.setExtents(l.tStart,t)


def addEffectLayersToSelectedLayers(moduleName):
    """Creates and effects layer and then matches it to an existing layer, and arrows and expression links it"""
    lays = d3script.getSelectedLayers()

    for lay in lays:
        newLayer = d3script.createLayerOfTypeOnCurrentTrack(moduleName)

        if newLayer == None:
            d3script.log('TrackTools','Could not create effect layer of type: ' + moduleName)
            continue

        #set extents to match existing layer
        newLayer.setExtents(lay.tStart,lay.tEnd)

        #set the index
        newLayer.tracks[0].moveLayerToIndex(newLayer,newLayer.tracks[0].findLayerIndex(lay) - 1)

        #set the brightness of the effect layer to the expression link to the source layer
        expString = 'module:' + d3script.expressionSafeString(lay.name) + '.brightness'
        d3script.setExpression(newLayer, 'brightness', expString)

        #set the blend mode directly to be the blendmode of the sourceLayer
        layBmodeSeq = d3script.getFieldFromLayerByName(lay,'blendmode').sequence
        bmode = layBmodeSeq.key(0).v

        newLayBmodeSeq = d3script.getFieldFromLayerByName(newLayer,'blendmode').sequence
        d3script.setKeyForLayerAtTime(newLayer,'blendmode',bmode,newLayBmodeSeq.key(0).localT)

        #Set the mapping
        layMappingSeq = d3script.getFieldFromLayerByName(lay,'mapping').sequence
        mapping = layMappingSeq.key(0).r

        newLayMappingSeq = d3script.getFieldFromLayerByName(newLayer,'mapping').sequence
        d3script.setKeyForLayerAtTime(newLayer,'mapping',mapping,newLayMappingSeq.key(0).localT)

        #Arrow the layers together
        newLayer.tracks[0].makeArrow(lay,newLayer)


def layerInSection(lay,scStart,scEnd):
    if ((lay.tStart >= scStart) and (lay.tStart < scEnd) or 
        (lay.tEnd >= scStart) and (lay.tEnd < scEnd) or 
        (lay.tStart < scStart) and (lay.tEnd >= scEnd)):

        return True

    else:
        return False


def showSectionTimingInfo(trustNoSequence = False):

    #get the section times
    sects = state.track.sections
    scIndex = sects.find(state.player.tCurrent)
    scStart = sects.getT(scIndex)
    scEnd = sects.getT(scIndex + 1)

    # get all layers that intersect playhead
    lays = filter(lambda l: layerInSection(l,scStart,scEnd),state.track.layers)

    allLays = lays
    for lay in lays:
        if isinstance(lay, GroupLayer):
            allLays += lay.layers

    timedEvents = []

    for lay in allLays:
        if isinstance(lay,GroupLayer):
            continue

        flds = lay.fields
        flds = filter(lambda f:f.noSequence == False,flds)

        for fld in flds:
            fs = fld.sequence
            activeKeys = filter(lambda k:(k.localT >= scStart) and (k.localT < scEnd),fs.keys)
            keyCount = len(activeKeys)
            totalKeyCount = fs.nKeys()

            #our key checks require at least two key frames.  But if we believe noSequence flag, one keyframe should be enough

            if (trustNoSequence == True):
                keysNeeded = 1
            else:
                keysNeeded = 2

            if (fld.name == 'video') and (keyCount >= keysNeeded):

                animDescription = '[' + str(keyCount) + '/' + str(totalKeyCount) + ']: '

                for k in activeKeys:
                    mediaTransField= d3script.getFieldFromLayerByName(lay,'transition time')
                    t = mediaTransField.sequence.findCurrentKeyTime(k.localT)
                    transKey = filter(lambda k: k.localT == t,mediaTransField.sequence.keys)[0]
                    animDescription += '+' + str(round((k.localT - scStart), 2)) + '@' + k.r.description + '(' + str(transKey.v) + ') '

                timedEvents.append((lay.name,fld.name,animDescription))

            elif (fld.name != 'transition time') and (keyCount >= keysNeeded):

                animDescription = '[' + str(keyCount) + '/' + str(totalKeyCount) + ']: '

                for k in activeKeys:
                    if (type(k) == KeyResource) and (k.r != None):
                        if (k.r != None):
                            val = k.r.description
                        else:
                            val = 'None'
                    elif (type(k) == KeyFloat):
                        val = str(round(k.v,4))
                    else:
                        val = str(k.v)

                    animDescription += '+' + str(round((k.localT - scStart), 2)) + '@' + val + ' '

                timedEvents.append((lay.name,fld.name,animDescription))

    #Show results
    columnNames = ['Layer','field','keys']

    columns = []
    for column in columnNames:
        columns.append(ColumnListViewColumn(column,column,None))

    resultWidget = Widget()
    resultWidget.add(TitleButton('Section Timing Info'))

    listWidget = ColumnListView(columns,maxSize=Vec2(1500, 800) * d3gui.dpiScale)
    
    rows = map(lambda x:ColumnListViewItem(x),timedEvents)

    listWidget.items = rows
    listWidget.recalculateColumnSizes()
    resultWidget.add(listWidget)
    resultWidget.arrangeVertical()
    resultWidget.computeAllMinSizes()
    d3gui.root.add(resultWidget)
    resultWidget.pos = (d3gui.root.size / 2) - (resultWidget.size/2)
    resultWidget.pos = Vec2(resultWidget.pos[0],resultWidget.pos[1]-100)


def importLayerFromLibraryByName(layerName):
    #Move cursor because the import function likes to move the playhead to the cursos
    tw = d3script.getTrackWidget()
    d3gui.cursorPos = Vec2(tw.barWidget.tToX(state.player.tCurrent) - tw.scrollWidget.hScroll.absOffset,d3gui.cursorPos[1])
    
    a = tw.barWidget.popupBarMenu()
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
            "name" : "De-Sequence Layer", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Takes all single keyframe sequences and de-sequences them", #text for help system
            "callback" : deSequenceLayers, # function to call for the script
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
        },
        {
            "name" : "Hard Mute Layers", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Sets brightness expression of layer to 0", #text for help system
            "callback" : hardMuteLayers, # function to call for the script
        },
        {
            "name" : "Hard UnMute Layers", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Sets brightness of layer back to self and removes MUTED label", #text for help system
            "callback" : hardUnMuteLayers, # function to call for the script
        },
        {
            "name" : "Add Effect Layers to Selected Layers", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Sets brightness of layer back to self and removes MUTED label", #text for help system
            "callback" : addEffectLayersToSelectedLayers, # function to call for the script
        },
        {
            "name" : "Show Section Timing Info", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Find animated properties and reports on timing", #text for help system
            "callback" : showSectionTimingInfo, # function to call for the script
        }
        ]

    }
