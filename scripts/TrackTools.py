# Track Tools
from operator import truediv
from gui.inputmap import *
from d3 import *
from gui.columnlistview import *
from gui.track.layerview import LayerSelection
import d3script
import re

def initCallback():
    d3script.log("Track Tools","Track Tools Loaded")


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

        d3script.refreshEditorsForLayer(lay)


def switchToTrack(track):
    lds = state.localOrDirectorState()
    currentTM = lds.transport

    #multitransport
    if isinstance(currentTM,MultiTransportManager):
        tps = currentTM.transportManagers
        for tp in tps:
            if (tp.description == track):
                lds.currentTransport = tp
                break
    
    else:
        tks = d3script.getCurrentSetList.tracks
        for tk in tks:
            if (tk.description == track):
                cmd = TransportCMDTrackBeat()
                #this is hack-y to use root for the parent of the command
                cmd.init(d3gui.root, currentTM, tk, 0, tk.transitionInfoAtBeat(0))
                currentTM.addCommand(cmd)
                break
  

def hardMuteLayers():
    op = Undoable('hard mute layers')
    lays = d3script.getSelectedLayers()

    for lay in lays:
        d3script.setExpression(lay,'brightness','0')
        lay.name = 'SUPPRESSED ' + lay.name


def hardUnMuteLayers():
    op = Undoable('hard unmute layers')
    lays = d3script.getSelectedLayers()

    for lay in lays:
        d3script.setExpression(lay,'brightness','self')
        if (lay.name.find('SUPPRESSED ') == 0):
            lay.name = lay.name[11:]


def duplicateSelectedLayers():
    """Duplicate Selected Layers"""
    op = Undoable('duplicate selected layers')
    lv = d3script.getTrackWidget().layerView
    if len(lv.selectedLayerIDs) > 0:
        lv._duplicateSelected()


def splitSelectedLayers():
    """Split selected layers"""
    op = Undoable('split selected layers')
    tw = d3script.getTrackWidget()
    lv = tw.layerView
    if len(lv.selectedLayerIDs) > 0:
        selectedLayerObjects = d3script.getSelectedLayers()
        t = tw.player.tCurrent
        lv.track.splitLayersAtBeat(selectedLayerObjects, t)


def moveSelectedLayersToPlayhead():
    """Move selected layers to playhead"""
    op = Undoable('move selected layers to playhead')
    tw = d3script.getTrackWidget()
    lv = tw.layerView
    if len(lv.selectedLayerIDs) > 0:    
        selectedLayerObjects = d3script.getSelectedLayers()
        t = tw.player.tCurrent
        map(lambda l: tw.barWidget.moveLayer(l,t), selectedLayerObjects) 


def trimSelectedLayersToPlayhead():
    """Trim selected layers to playhead"""
    op = Undoable('trim selected layers to playhead')
    tw = d3script.getTrackWidget()
    lv = tw.layerView
    if len(lv.selectedLayerIDs) > 0:    
        selectedLayerObjects = d3script.getSelectedLayers()
        t = tw.player.tCurrent
        for l in selectedLayerObjects:
            if l.tStart < t:
                l.setExtents(l.tStart,t)


def findBrokenExpressionsInCurrentTrack():
    # get all layers that intersect playhead

    track = d3script.getCurrentTrack()
    allLays = d3script.allLayersOfObject(track.layers)
    foundErrors = []

    for lay in allLays:
        if hasattr(lay,'fields'):
            for f in lay.fields:
                if (f.expression != None) and (not f.expression.isOK):
                    foundErrors.append((track.description, str(lay.tStart), lay.name, f.name, f.expression.expression, lay, f.name, track, lay.tStart))

    d3script.showTimeBasedResultsWidget('Broken Expressions',['Track','Time','Layer','Field', 'ExpText'], foundErrors)


def addEffectLayersToSelectedLayers(moduleName):
    """Creates and effects layer and then matches it to an existing layer, and arrows and expression links it"""
    op = Undoable('add Effects Layers')
    lays = d3script.getSelectedLayers()

    for lay in lays:
        newLayer = d3script.createLayerOfTypeOnCurrentTrack(moduleName)
        trk = d3script.getCurrentTrack()
        if newLayer == None:
            d3script.log('TrackTools','Could not create effect layer of type: ' + moduleName)
            continue

        #set extents to match existing layer
        newLayer.setExtents(lay.tStart,lay.tEnd)

        #if layer is in a group, add fx layer to group
        if lay.container != None:
            trk.addLayerToGroup(newLayer, lay.container)
            trk.moveLayerToIndexInGroup(newLayer,lay.container.layers.index(lay))

        else:    
            #set the index
            trk.moveLayerToIndex(newLayer,trk.findLayerIndex(lay) - 1)

        newLayer.name = d3script.standardModuleAbbreviation(moduleName) + " " + lay.name
        
        #rename the source layer with an EXPSRC flag
        if "EXPSRC" not in lay.name:
            lay.name += ' EXPSRC'

        #set the brightness of the effect layer to the expression link to the source layer        
        expString = 'getByUID(' + hex(lay.uid)[:-1] + ').brightness'
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
        trk.makeArrow(lay,newLayer)


def layerInSection(lay,scStart,scEnd):
    if ((lay.tStart >= scStart) and (lay.tStart < scEnd) or 
        (lay.tEnd >= scStart) and (lay.tEnd < scEnd) or 
        (lay.tStart < scStart) and (lay.tEnd >= scEnd)):

        return True

    else:
        return False


def showLayerTimingInfo(trustNoSequence = True):

    #get selected layers
    lays = d3script.getSelectedLayers()

    timedEvents = []
    
    allLays = lays
    for lay in lays:
        if isinstance(lay, GroupLayer):
            allLays += d3script.allLayersOfObject(lay.layers)

    for lay in allLays:
        if isinstance(lay,GroupLayer):
            continue

        flds = lay.fields
        flds = filter(lambda f:f.noSequence == False,flds)

        for fld in flds:
            fs = fld.sequence
            activeKeys = fs.keys
            keyCount = fs.nKeys()

            if (trustNoSequence == True):
                keysNeeded = 1
            else:
                keysNeeded = 2

            if (fld.name == 'video') and (keyCount >= keysNeeded):

                for k in activeKeys:
                    track = d3script.getCurrentTrack()
                    sectStart, tag, note = d3script.getSectionTagNoteForTrackAndTime(track, k.localT)
                    mediaTransField= d3script.getFieldFromLayerByName(lay,'transition time')
                    t = mediaTransField.sequence.findCurrentKeyTime(k.localT)
                    transKey = filter(lambda k: k.localT == t,mediaTransField.sequence.keys)[0]
                    cueDescription = tag + ' (' + note + ')' 
                    animDescription = str(round((k.localT - sectStart), 2)) + '@' + k.r.description + '(' + str(transKey.v) + ')'
                    timedEvents.append((lay.name, fld.name, cueDescription, animDescription, lay, fld.name, track, k.localT))

            elif (fld.name != 'transition time') and (keyCount >= keysNeeded):

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

                    interpolationFlag = ''
                    if (k.interpolation == k.linear):
                        interpolationFlag = '[L]'
                    elif (k.interpolation == k.select):
                        interpolationFlag = '[S]'

                    track = d3script.getCurrentTrack()
                    sectStart, tag, note = d3script.getSectionTagNoteForTrackAndTime(track, k.localT)
                    cueDescription = tag + ' (' + note + ')' 
                    animDescription = str(round((k.localT - sectStart), 2)) + interpolationFlag + '@' + val
                    timedEvents.append((lay.name,fld.name,cueDescription,animDescription, lay, fld.name,track, k.localT))

    #Show results
    columnNames = ['Layer','field','cue','key']
    d3script.showTimeBasedResultsWidget('Layer Timing Info', columnNames, timedEvents)


def showSectionTimingInfo(trustNoSequence = True):

    track = d3script.getCurrentTrack()
    player = d3script.getPlayer()
    #get the section times

    if (d3script.is31_or_newer()):
        scStart = track.beatToTime(track.findBeatOfLastSection(track.timeToBeat(player.tCurrent))) - Key.tEpsilon
        scEnd = track.beatToTime(track.findBeatOfNextSection(track.timeToBeat(player.tCurrent)))
    else:
    #We subtract Key.tEpsilon for snap cues
        sects = track.sections
        scIndex = d3script.getSectionIndexForTrackAndTime(track, player.tCurrent)
        scStart = sects.getT(scIndex) - Key.tEpsilon
        scEnd = sects.getT(scIndex + 1)

    # get all layers that intersect playhead
    lays = filter(lambda l: layerInSection(l,scStart,scEnd), track.layers)

    allLays = lays
    for lay in lays:
        if isinstance(lay, GroupLayer):
            allLays += d3script.allLayersOfObject(lay.layers)

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

                timedEvents.append((lay.name, fld.name, animDescription, lay, fld.name, track, None))

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

                    interpolationFlag = ''
                    if (k.interpolation == k.linear):
                        interpolationFlag = '[L]'
                    elif (k.interpolation == k.select):
                        interpolationFlag = '[S]'

                    animDescription += '+' + str(round((k.localT - scStart), 2)) + interpolationFlag + '@' + val + ' '

                timedEvents.append((lay.name, fld.name, animDescription, lay, fld.name, track, None))

    #Show results
    columnNames = ['Layer','field','keys']
    d3script.showTimeBasedResultsWidget('Section Timing Info', columnNames, timedEvents)


def importLayerFromLibraryByName(layerName):
    #Move cursor because the import function likes to move the playhead to the cursos
    tw = d3script.getTrackWidget()
    player = d3script.getPlayer()
    d3gui.cursorPos = Vec2(tw.barWidget.tToX(player.tCurrent) - tw.scrollWidget.hScroll.absOffset,d3gui.cursorPos[1])
    
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
        #clear the search history 
        wd.children[2].children[0].valueBox.setVal("")

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


class UpdateSectionTagAndNote(Widget):
    """A Widget to change the section tag and note from anywhere in the section"""

    def __init__(self):
        
        self.trk = d3script.getCurrentTrack()
        self.time = d3script.getPlayer().tCurrent
        self.sectStart, self.newTag, self.newNote = d3script.getSectionTagNoteForTrackAndTime(self.trk, self.time)

        Widget.__init__(self)

        self.arrangeVertical()
        self.add(TitleButton("Update Section Tag / Note"))

        gw = Widget()
        gw.arrangeHorizontal()
        gw.add(TextLabel('Cue / TC:'))
        cueVB = ValueBox(self,'newTag')
        cueVB.textBox.returnAction.add(self.updateTagAndNote)
        gw.add(cueVB)
        self.add(gw)
        
        gw2 = Widget()
        gw2.arrangeHorizontal()
        gw2.add(TextLabel('Note:'))
        noteVB = ValueBox(self,'newNote')
        noteVB.textBox.returnAction.add(self.updateTagAndNote)
        gw2.add(noteVB)
        self.add(gw2)
        self.add(Button('OK', self.updateTagAndNote))

        self.pos = (d3gui.root.size / 2) - (self.size/2)
        d3gui.root.add(self)
        cueVB.focus = True

    def updateTagAndNote(self):
        op = Undoable('Update Tag and Note for Section')

        if d3script.is31_or_newer():
            self.trk.removeTags(self.sectStart,0)
            self.trk.removeTags(self.sectStart,1)
            self.trk.removeTags(self.sectStart,2)
            if ":" in self.newTag:
                self.trk.setTagAtBeat(self.trk.timeToBeat(self.sectStart),Tag(0,self.newTag))    
            else:
                self.trk.setTagAtBeat(self.trk.timeToBeat(self.sectStart),Tag(1,self.newTag))

        else:
            if (self.newTag != ''):
                if ":" in self.newTag:
                    self.newTag = "TC " + self.newTag
                else:
                    self.newTag = "CUE " + self.newTag
           
            self.trk.setTagAtBeat(self.trk.timeToBeat(self.sectStart),self.newTag)

        self.trk.setNoteAtBeat(self.trk.timeToBeat(self.sectStart), self.newNote)
        self.close()


def openTagAndNotePopup():
    temp = UpdateSectionTagAndNote()


def smartMergeCurrentSection():
    op = Undoable('Smart Merge Current Section')
    trk = d3script.getCurrentTrack()
    time = d3script.getPlayer().tCurrent
    if (d3script.is31_or_newer()):
        sectStart = track.findBeatOfLastSection(track.timetoBeat(time))
    else:
        sectStart = trk.sections.getT(trk.sections.find(time,time))

    if d3script.is31_or_newer():
        trk.removeTags(trk.timeToBeat(time),Key.tEpsilon)
        trk.mergeSectionAtBeat(trk.timeToBeat(time))
        trk.removeNoteAtBeat(trk.timeToBeat(time))
    else:
        trk.sections.removeAtTime(sectStart)
        trk.notes.removeAtTime(sectStart)
        trk.tags.removeAtTime(sectStart)


def trackSearch(searchString):
    """Perform the track search"""
    typeFilter = Resource
    searchString = searchString.lower()
    searchSplit = searchString.split(':',1)
    if len(searchSplit) > 1:
        if searchSplit[0] == 'm':
            typeFilter = Projection
            searchString = searchSplit[1]

        elif searchSplit[0] == 'v':
            typeFilter = VideoClip
            searchString = searchSplit[1]
    
        elif searchSplit[0] == 'l':
            typeFilter = Layer
            searchString = searchSplit[1]

    res = resourceManager.allResources(typeFilter)

    res = filter(lambda r:r.description.lower().find(searchString) != -1,res)

    lays = set()

    for resource in res:
        if type(resource) == Layer:
            lays.add((resource,resource))
        else:    
            points = filter(lambda l:type(l) == Layer, resource.findResourcesPointingToThis(Layer))
            for  lay in points:
                lays.add((lay,resource))

    lays = list(lays)

    lays.sort(key = (lambda x: x[0].tStart))

    outputRows = []
    for l in lays:
        lay = l[0]

        trk = d3script.getTrackForLayer(lay)
        if (trk == None):
            continue
        
        trackName = trk.description
        trkTime = trk.findBeatOfLastTag(trk.timeToBeat(lay.tStart))
        if d3script.is31_or_newer():
            cueTag = ''
            tags = trk.tagsAtBeat(trkTime)
            if len(tags) > 0:
                cueTag = tags[0].text
        else:     
            cueTag = trk.tagAtBeat(trkTime)

        cueLabel = trk.noteAtBeat(trkTime)
        layName = lay.description
        resName = l[1].description
        typeName = str(type(l[1]))
        outputRows.append((trackName, cueTag, cueLabel, layName, resName, typeName, lay, None, trk, trkTime))

    d3script.showTimeBasedResultsWidget('Search Results', ['Track','Cue','Label','Layer','Resource','Type'], outputRows)


def trackSearchPopup():
    """Open the track search widget"""
    
    menu = PopupMenu('Search Track')
    menu.add(TextBox('Prefix searchstring with m: for mappings only, v: for videos only, and l: for layers only'))
    menu.editItem('Search String:', '', trackSearch)
    menu.computeAllMinSizes()

    d3gui.root.add(menu)
    menu.pos = (d3gui.root.size / 2) - (menu.size/2)
    menu.pos = Vec2(menu.pos[0],menu.pos[1]-100)
    menu.contents.findWidgetByName('Search String:').textBox.focus = True


def doGroup(groupName):
    op = Undoable('group selected layers')
    tw = d3script.getTrackWidget()
    tw.layerView._groupSelected(groupName)


def ungroupSelectedLayers():
    op = Undoable('Ungroup selected layers')
    lays = d3script.getSelectedLayers()

    for lay in lays:
        if not isinstance(lay,GroupLayer):
            continue
        d3script.getCurrentTrack().ungroupLayer(lay)


def groupPopup():
    """Open a popup menu to group """
    selectedLayerObjects = d3script.getSelectedLayers()
    if not selectedLayerObjects:
        return

    menu = PopupMenu('Group Selected Layers')
    menu.editItem('Group Name:', 'Group', doGroup)
    menu.pos = (d3gui.root.size / 2) - (menu.size/2)
    menu.pos = Vec2(menu.pos[0],menu.pos[1]-100)

    d3gui.root.add(menu)
    menu.contents.findWidgetByName('Group Name:').textBox.focus = True    


def doComboRename(newNameStem):
    op = Undoable('ScullyRename')
    selLay = d3script.getSelectedLayers()

    for i in selLay:

        if (newNameStem[0] == '!'):
            i.name = newNameStem[1:]

        #Now that we exp link via UID I'm not checking this anymore
        #elif (i.name.find('EXPSRC') != -1):
            #We don't rename layers with EXPSRC in their name
            #continue

        else:
            keyResource = None
            
            if (i.findSequence('Mapping') != None):
                keyResource =  i.findSequence('Mapping').sequence.key(0).r

            if (keyResource != None) and (hasattr(keyResource,'description')):
                mapNameMatch = re.search('^(\[.+\]).*',i.findSequence('Mapping').sequence.key(0).r.description)
                if (mapNameMatch != None):
                    mapName = mapNameMatch.group(1) + ' '
                else:
                    mapName = i.findSequence('Mapping').sequence.key(0).r.description + ' '
            else:
                mapName = ''

            mediaName = ''
            if hasattr(i.module, 'video'):
                keyResource =  i.findSequence('video').sequence.key(0).r
                if hasattr(keyResource,'description'):
                    loseExt = re.search('(.*)(.mov|.jpg|.png)', keyResource.description)
                    if loseExt:
                        mediaName = loseExt.group(1)
                else:
                    mediaName = ''

            existingNameMatch = re.search('(\[.+\])*[\s]*(.+)', i.name)
            if ((existingNameMatch != None) and (existingNameMatch.group(2) != None)):
                existingName = existingNameMatch.group(2)
            else:
                existingName = ''

            moduleName = type(i.module).__name__
            moduleName = moduleName.replace('Module','')
            if moduleName == 'VariableVideo':
                moduleName = ''
            else:
                moduleName = d3script.standardModuleAbbreviation(moduleName) + ' '

            localNameStem = newNameStem.replace('$',mediaName).replace('@',existingName)

            i.name = moduleName + mapName + localNameStem


def cleanupTrailingNumbersInName():
    selectedLayers = d3script.getSelectedLayers()

    for lay in selectedLayers:
        lay.name = re.sub(r'\s\d+$', '', lay.name)


def gradientSelfLink():
    selectedLayers = d3script.getSelectedLayers()
    if not selectedLayers:
        return
    
    for lay in selectedLayers:
        if type(lay.module).__name__ != 'GradientModule':
            print ('skipping ' + lay.name)
            continue
        
        #2nd_xCol
        #2nd_yCol
        colXString = 'getByUID(' + hex(lay.uid)[:-1] + ').xCol'
        colYString = 'getByUID(' + hex(lay.uid)[:-1] + ').yCol'

        d3script.setExpression(lay,'2nd xCol',colXString)
        d3script.setExpression(lay,'2nd yCol',colYString)


def renamePopup():
    """Open a popup menu with rename options"""
    selectedLayerObjects = d3script.getSelectedLayers()
    if not selectedLayerObjects:
        return
    isSingleSelection = len(selectedLayerObjects) == 1

    if isSingleSelection:
        heading = selectedLayerObjects[0].name

    else:
        heading = 'Multiple layers'


    mediaName = ''
    if hasattr(selectedLayerObjects[0].module, 'video'):
            keyResource =  selectedLayerObjects[0].findSequence('video').sequence.key(0).r
            if hasattr(keyResource,'description'):
                loseExt = re.search('(.*)(.mov|.jpg|.png)', keyResource.description)
                if loseExt:
                    mediaName = loseExt.group(1)
    
    splitNames = selectedLayerObjects[0].name.split('[')
    if len(splitNames) > 1:
        nameStem = splitNames[0].rstrip()
    else:
        nameStem = mediaName

    menu = PopupMenu('Rename %s' % heading)
    menu.add(TextBox('$ replaced by filename,@ replaced by existing name, !name... to force exact name'))
    menu.editItem('Rename:', nameStem, doComboRename)
    menu.pos = (d3gui.root.size / 2) - (menu.size/2)
    menu.pos = Vec2(menu.pos[0],menu.pos[1]-100)

    d3gui.root.add(menu)
    menu.contents.findWidgetByName('Rename:').textBox.focus = True


def doJumpToNearestCue(target):
    track = d3script.getCurrentTrack()
    jumpTime = None

    try:
        targetNumber = float(target)
    except:
        alert('The cue is not a valid format.')
        return


    tags = track.tags    
    if tags.n < 1:
        alert('There are no cue tags to search through.')
        return
    

    if d3script.is31_or_newer():
        cueBeats = track.cueBeats()
        for beat in cueBeats:
            tag = trk.cueAtBeat(beat).getTag(1)
            if (tag == None):
                continue
            
            if tag.text == target:
                jumpTime = track.beatToTime(beat)
                break
            else:
                try:
                    cueNumber = float(tag.text)
                except:
                    continue
                if (cueNumber < targetNumber):
                    jumpTime = track.beatToTime(beat)
            
    else:    
        for i in range(0,tags.n()):
            tagText = tags.getV(i)
            if (tagText == "CUE " + target):
                jumpTime = tags.getT(i)
                break

            elif ("CUE " in tagText):
                try:
                    cueNumber = float(tagText[4:])
                except:
                    continue
                if (cueNumber < targetNumber):
                    jumpTime = tags.getT(i)
                else:
                    break
    
    if (jumpTime == None):
        d3.alertInfo('Did not find a good cue match.')
        
    cmd = TransportCMDTrackBeat()
    tm = d3script.getCurrentTransportManager()
    trackTime = track.findBeatOfLastTag(track.timeToBeat(jumpTime))
    cmd.init(d3gui.root, tm, track, track.timeToBeat(jumpTime), track.transitionInfoAtBeat(trackTime))
    tm.addCommand(cmd)


    

def nearestCuePopup():
    """Open a popup menu with ability to jump to the nearest cue"""

    currentValue = "0"
    menu = PopupMenu('Goto Nearest Cue')
    menu.editItem('Cue Number:', currentValue, doJumpToNearestCue)
    menu.pos = (d3gui.root.size / 2) - (menu.size/2)
    menu.pos = Vec2(menu.pos[0],menu.pos[1]-100)

    d3gui.root.add(menu)
    menu.contents.findWidgetByName('Cue Number:').textBox.focus = True



SCRIPT_OPTIONS = {
    "minimum_version" : 21, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Change Track", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Change track to passed name", #text for help system
            "callback" : switchToTrack, # function to call for the script
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
            "name" : "Self Link Gradient", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Links the 2nd Col X/Y to the main X/Y of the grad layer", #text for help system
            "callback" : gradientSelfLink, # function to call for the script
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
        },
        {
            "name" : "Show Layer Timing Info", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Find animated properties and reports on timing", #text for help system
            "callback" : showLayerTimingInfo, # function to call for the script
        },
        {
            "name" : "Update Section Tag and Note", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Allows note and tag to be set for current section", #text for help system
            "callback" : openTagAndNotePopup, # function to call for the script
        },
        {
            "name" : "Smart Merge Section", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Merges current section and removes tag/notes", #text for help system
            "callback" : smartMergeCurrentSection, # function to call for the script
        },
        {
            "name" : "Group Selected Layers", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "group selected layers", #text for help system
            "callback" : groupPopup, # function to call for the script
        },
        {
            "name" : "Find Broken Expressions", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "find broken expressions in current track", #text for help system
            "callback" : findBrokenExpressionsInCurrentTrack, # function to call for the script
        },
        {
            "name" : "UnGroup Selected Layers", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Ungroup selectd layers", #text for help system
            "callback" : ungroupSelectedLayers, # function to call for the script
        },
        {
            "name" : "Track Search", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Search tracks for resources by name", #text for help system
            "callback" : trackSearchPopup, # function to call for the script
        },
        {
            "name" : "Module ReName", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Alt,r",
            "bind_globally" : True, # binding should be global
            "help_text" : "Rename module based on properties", #text for help system
            "callback" : renamePopup, # function to call for the script
        },
        {
            "name" : "Goto Nearest Cue", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Ctrl,q",
            "bind_globally" : True, # binding should be global
            "help_text" : "Find the nearest cue and go to it", #text for help system
            "callback" : nearestCuePopup, # function to call for the script
        },
        {
            "name" : "Cleanup Trailing Numbers in Name", # Display name of script
            "group" : "Track Tools", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Removes the trailing additional numbers appended to copied/duped layers", #text for help system
            "callback" : cleanupTrailingNumbersInName, # function to call for the script
        }
        ]

    }


