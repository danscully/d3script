# SearchTrack
from gui.inputmap import *
from d3 import *
from gui.columnlistview import *
import d3script
import json


def initCallback():
    d3script.log("PresetManager3","PresetManager3 Loaded")
    PMPreset.loadPresets()


def applyPreset(preset):
    PMPreset.applyByName(preset)  

class PMPreset():

    presets = []

    @staticmethod
    def savePresets():
        d3script.log("PresetManager3","Saving Presets")
        presetList = []
        for p in PMPreset.presets:
            presetList.append({'name':p.name,'fieldValues':p.fieldValues})
        
        d3script.setPersistentValue('PM3Settings',presetList,'PM3Settings')

    @staticmethod
    def loadPresets():
        d3script.log("PresetManager3","Loading Presets")
        PMPreset.presets = []
        data = d3script.getPersistentValue('PM3Settings','PM3Settings')
        if data != None:
            d3script.log("PresetManager3","Loading Presets")
            for p in data:
                PMPreset(p['name'],p['fieldValues'])

    @staticmethod
    def findByName(presetName):
        for p in PMPreset.presets:
            if (p.name == presetName):
                return p
            
        return None
    
    @staticmethod
    def applyByName(presetName):
        for p in PMPreset.presets:
            if (p.name == presetName):
                p.applyPreset()

    def __init__(self,name, fieldValues):   
        PMPreset.presets.append(self)
        self.update(name, fieldValues)

    def update(self, name, fieldValues):
        self.name = name
        self.fieldValues = fieldValues
        PMPreset.savePresets()

    def delete(self):
        PMPreset.presets.remove(self)
        PMPreset.savePresets()
        
    def applyPreset(self):
        op = Undoable('PresetManager Applying Preset')
        
        curTRender = state.player.tRender
        trk = state.track
        
        for valueSet in self.fieldValues:
            modifyFields = []
            if 'type' in valueSet:
                typeString = valueSet['type']
                if typeString == 'int':
                    setType = int
                elif typeString == 'str':
                    setType = str
                elif typeString == 'float':
                    setType = float
                else:    
                    setType = globals()[typeString.encode('ascii','ignore')]
            else:
                setType = float

            if valueSet['field'] == '<opensequence>':
                oles = d3script.getTrackWidget().layerView.openEditorManager.openLayerEditors
                for ole in oles.values():  
                    modifyFields += [fw.fieldSequence for fw in ole.selectedFieldWrappers if (fw.fieldSequence.type == setType)]

            else:
                for lay in d3script.getSelectedLayers():
                    modifyFields += [f for f in lay.fields if (f.name == valueSet['field']) and (f.type == setType)]

            for fs in modifyFields:
                seq = fs.sequence
                sectStartTime = trk.sections.getT(trk.beatToSection(trk.timeToBeat(curTRender)))
                nextSectIndex = trk.beatToSection(trk.timeToBeat(curTRender)) + 1
                if nextSectIndex < trk.nSections:
                    nextSectStartTime = trk.sections.getT(nextSectIndex)
                else:
                    nextSectStartTime = sectStartTime + 30; 
                curValue = seq.evalString(curTRender)
                prevKeyTime = seq.findCurrentKeyTime(curTRender)
                nextKeyTime = seq.findNextKeyTime(curTRender)
                prevKeyValue = seq.evalString(prevKeyTime)
                nextKeyValue = seq.evalString(nextKeyTime)
                sectValue = seq.evalString(sectStartTime)
                nextSectValue = seq.evalString(nextSectStartTime)

                def parseKeyValue(value):
                    if (isinstance(value,str) or isinstance(value,unicode)):
                        value = value.replace('<currentvalue>', curValue)
                        value = value.replace('<previousvalue>', prevKeyValue)
                        value = value.replace('<nextvalue>', nextKeyValue)
                        value = value.replace('<sectvalue>', sectValue)
                        value = value.replace('<nextsectvalue>', nextSectValue)

                        if setType == float:
                            value = eval(value)
                            return float(value)
                        
                        elif setType == int:
                            value = eval(value)
                            return int(value)

                        elif setType == str:
                            return value

                        else:
                        # set type must be a resource
                            res = resourceManager.allResources(setType)
                            res = filter(lambda r:r.description == value,res)
                            if len(res) != 1:
                                return None
                            else:
                                return res[0]

                    else:
                        return value
                    

                def parseKeyTime(time):
                    if (isinstance(time,str) or isinstance(time,unicode)):
                        if time == '<none>':
                            return None
                        time = time.replace('<sectionstart>', str(sectStartTime))
                        time = time.replace('<nextsectionstart>',str(nextSectStartTime))
                        time = time.replace('<prevkeytime>', str(prevKeyTime))
                        time = time.replace('<nextkeytime>', str(nextKeyTime))
                        time = time.replace('<relativeepsilon>', str(curTRender - Key.tEpsilon))
                        time = time.replace('<epsilon>', str(Key.tEpsilon))
                        return float(eval(time))
                    
                    return float(time) + curTRender
            
                if (len(valueSet['keys']) > 1) and ('!' not in valueSet['flags']):
                    delStartTime = parseKeyTime(valueSet['keys'][0][1])
                    delEndTime = parseKeyTime(valueSet['keys'][-1][1])

                    if (delStartTime != None) and (delEndTime != None):

                        curKeyIndex = seq.find(delStartTime)
                        if (curKeyIndex != -1) and (seq.key(curKeyIndex).localT == delStartTime):
                            seq.remove(curKeyIndex, 1)
                        
                        nextKeyIndex = seq.find(seq.findNextKeyTime(delStartTime))
                        while (nextKeyIndex != -1) and (seq.key(nextKeyIndex).localT >= delStartTime and seq.key(nextKeyIndex).localT <= delEndTime):
                            seq.remove(nextKeyIndex, 1)
                            nextKeyIndex = seq.find(seq.findNextKeyTime(delStartTime))

        
                for key in valueSet['keys']:
                    keyValue = parseKeyValue(key[0])
                    keyTime = parseKeyTime(key[1])

                    def setKey(localSeq,localTime,localValue):
                        if localValue == None:
                            return
                        
                        if setType == int:
                            localSeq.setFloat(localTime,float(math.floor(localValue)))
                        elif setType == float:
                            localSeq.setFloat(localTime,float(localValue))
                        elif setType == str:
                            localSeq.setString(localTime,str(localValue))
                        else:
                            localSeq.setResource(localTime,localValue)

                    if (fs.noSequence == True) and (keyTime != None):
                        fs.disableSequencing = False   
                        if (seq.nKeys() > 0):         
                            seq.remove(0,seq.nKeys())
                        setKey(seq, keyTime, keyValue)
                        seq.key(seq.find(keyTime)).interpolation = key[2]

                    elif (fs.noSequence == True) and (keyTime == None):
                        keyTime = fs.layer.tStart
                        if (seq.nKeys > 0):         
                            seq.remove(0,seq.nKeys())
                        setKey(seq, keyTime, keyValue)

                    elif (fs.noSequence == False) and (keyTime == None) and ('<>' not in valueSet['flags']):
                        keyTime = curTRender
                        setKey(seq, keyTime, keyValue)
                        seq.key(seq.find(curTRender)).interpolation = key[2]

                    elif (fs.noSequence == False) and (keyTime == None) and ('<>' in valueSet['flags']):
                        setKey(seq, prevKeyTime, keyValue)
                        setKey(seq, nextKeyTime, keyValue)

                    elif (fs.noSequence == False) and (keyTime != None):
                        setKey(seq, keyTime, keyValue)
                        seq.key(seq.find(keyTime)).interpolation = key[2]

                d3script.refreshEditorsForLayer(fs.layer)

class PresetEditor(Widget):

    def __init__(self ,preset):
        def onSave():
            d3script.log("PresetManager3",self.editValues)
            self.preset.update(self.editName, json.loads(self.editValues))
            rw = d3gui.root.findWidgetByName('Record Preset')
            if (rw != None):
                rw.parent.generatePresetRows(); 
            self.close()

        def onDelete():
            self.preset.delete()
            rw = d3gui.root.findWidgetByName('Record Preset')
            if (rw != None):
                rw.parent.generatePresetRows(); 
            self.close()

        self.add(TitleButton('Edit Preset'))
        d3script.log("PresetManager3","Preset is: " + str(type(preset).__name__))
        self.preset = preset
        self.editName = preset.name
        self.editValues = json.dumps(preset.fieldValues, indent = 2)
        self.add(Field('Preset Name',ValueBox(self,'editName')))
        vb = ValueBox(self,'editValues')
        vb.textBox.multiline = True
        vb.width = 80.0
        self.add(Field('Preset Values', vb))
        self.add(Button('Save', onSave))
        self.add(Button('Delete', onDelete))
        self.pos = Vec2(gui.cursorPos.x + 64, gui.cursorPos.y)
        self.arrangeVertical()
        self.computeAllMinSizes()
        d3gui.root.add(self)
        



class PresetRecordWidget(Widget):

    def __init__(self):
        Widget.__init__(self)
        PMPreset.loadPresets()
        self.add(TitleButton('Record Preset'))
        self.presetName = 'Preset Name'
        self.add(Field('Preset Name',ValueBox(self,'presetName')))
        yesNo = ['No', 'Yes']
        self.useTimes = 0
        self.add(Field('Save Timings',ValueBox(self,'useTimes',yesNo)))
        bw = Widget()
        bt = Button('Save Col X/Y', lambda: self.addPreset(0))
        bt.overrideMinSize = (lambda x:Vec2(200,35))
        bw.add(bt)
        bt = Button('Save ColorShift', lambda: self.addPreset(1))
        bt.overrideMinSize = (lambda x:Vec2(200,35))
        bw.add(bt)
        bt = Button('Save Translate', lambda: self.addPreset(2))
        bt.overrideMinSize = (lambda x:Vec2(200,35))
        bw.add(bt)
        bt = Button('Save Crop', lambda: self.addPreset(3))
        bt.overrideMinSize = (lambda x:Vec2(200,35))
        bw.add(bt)
        bt = Button('Save Open Seqs', lambda: self.addPreset(4))
        bt.overrideMinSize = (lambda x:Vec2(200,35))
        bw.add(bt)

        bw.arrangeHorizontal()
        self.add(bw)

        columnNames = ['Name', 'Values']
        columns = []
        for column in columnNames:
            columns.append(ColumnListViewColumn(column,column,None))
        
        self.presetWidget = CollapsableWidget('Presets(click to apply)','Presets(click to apply)')
        self.add(self.presetWidget)

        self.listWidget = ColumnListView(columns,maxSize=Vec2(1500, 800) * d3gui.dpiScale)
    
        self.generatePresetRows()

        self.listWidget.itemColumnClickedAction = (lambda item,colIndex: self.handleItemClick(item,colIndex))
        self.listWidget.itemColumnRightClickedAction = (lambda item,colIndex: self.handleItemRightClick(item,colIndex))
        self.presetWidget.add(self.listWidget)
        self.arrangeVertical()
        self.computeAllMinSizes()


    def generatePresetRows(self):


        if (self.listWidget):
            rows = []
            for preset in PMPreset.presets:
                textValues = json.dumps(preset.fieldValues)
                if len(textValues) > 70:
                    textValues = textValues[:67] + '...'
                rows.append([preset.name, textValues])

            items = map(lambda x:ColumnListViewItem(x),rows)

            self.listWidget.items = items
            self.listWidget.recalculateColumnSizes()

    def handleItemClick(self, item, colIndex):
        PMPreset.applyByName(item.values[0])


    def handleItemRightClick(self,item,colIndex):

        PresetEditor(PMPreset.findByName(item.values[0]))

    def addPreset(self,set):

        if (len(filter(lambda x:x.name == self.presetName, PMPreset.presets)) > 0):
            d3.alertInfo('Preset names should be unique.')
            return
        

        values = []
        # only refer to first layer editor
        ole = d3script.getTrackWidget().layerView.openEditorManager.openLayerEditors
        if (len(ole) != 1):
            return
        
        ole = ole.values()[0]

        if (set == 0):
            #Tint
            fields = ['xCol','yCol']
        elif (set == 1):
            #colorshift
            fields = ['brightness (shift)','contrast (scale)','hue shift','red min','red max','red gamma','green min','green max','green gamma','blue min','blue max','blue gamma']
        elif (set == 2):
            #translation
            fields = ['size','scale.x','scale.y','pos.x','pos.y','rotation']
        elif (set == 3):
            #crop
            fields = ['right','left','top','bottom','cropSoftness']
        elif (set == 4):
            #open sequences
            openSequences = ole.selectedFieldWrappers
            fields = map(lambda x:x.fieldSequence.name, openSequences)
        else:
            #something went wrong
            fields = []

        for field in fields:
            m=filter(lambda f:f.fieldSequence.name == field,ole.fieldWrappers)

            for f in m:
                #f.field.parent.expand()
                if self.useTimes == 0:
                    saveVal = f.field.valueBox.getVal()
  
                    if (f.fieldSequence.type == int):
                        saveType = "int"
                        saveInterpolation = Key.select
                    elif (f.fieldSequence.type == float):
                        saveType = "float"
                        saveInterpolation = Key.cubic
                    elif (f.fieldSequence.type == str):
                        saveType = "str"
                        saveInterpolation = Key.select
                    else:
                        #type is a resource
                        saveVal = saveVal.description
                        saveInterpolation = Key.select
                        saveType = globals().keys()[globals().values().index(f.fieldSequence.type)]

                    values.append({'field':f.fieldSequence.name,'flags':'','type':saveType, 'keys':[(saveVal,'<none>',saveInterpolation)]})


                else:
                    trk = state.track
                    keyArray = []
                    curSection = trk.beatToSection(trk.timeToBeat(state.player.tRender))
                    startTime = trk.sections.getT(curSection)

                    if (startTime < f.fieldSequence.layer.tStart):
                        startTime = f.fieldSequence.layer.tStart
                    if (curSection < trk.nSections):
                        endTime = trk.sections.getT(curSection + 1)
                    else:
                        endTime = trk.lengthInSec

                    for key in filter(lambda x: (x.localT >= startTime - Key.tEpsilon) and (x.localT < endTime), f.fieldSequence.sequence.keys):
                        if (f.fieldSequence.type == float) or (f.fieldSequence.type == int):
                            saveVal = key.v
                        elif f.fieldSequence.type == str:
                            saveVal = key.s
                        else:
                            #We are a resource sequence and we save those via the stringname
                            saveVal = key.r.description

                        keyArray.append((saveVal,key.localT - startTime,key.interpolation))

                    if (f.fieldSequence.type == int):
                        saveType = "int"
                    elif (f.fieldSequence.type == float):
                        saveType = "float"
                    elif (f.fieldSequence.type == str):
                        saveType = "str"
                    else:
                        #type is a resource
                        saveType = globals().keys()[globals().values().index(f.fieldSequence.type)]
                    values.append({'field':f.fieldSequence.name,'flags':'','type':saveType,'keys':keyArray})    

        PMPreset(self.presetName,values)
        self.generatePresetRows()

        
def presetPopup():
    """Open a popup menu with rename options"""
    
    widget = PresetRecordWidget()

    d3gui.root.add(widget)
    widget.pos = (d3gui.root.size / 2) - (widget.size/2)
    widget.pos = Vec2(widget.pos[0],widget.pos[1]-100)


SCRIPT_OPTIONS = {
    "minimum_version" : 23, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Preset Manager", # Display name of script
            "group" : "Preset Manager", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Manage Number(float) values as recallable values", #text for help system
            "callback" : presetPopup, # function to call for the script
        },
        {
            "name" : "Apply Preset", # Display name of script
            "group" : "Preset Manager", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Apply a preset by name", #text for help system
            "callback" : applyPreset, # function to call for the script
        }
        ]

    }
