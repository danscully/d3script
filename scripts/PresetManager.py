# SearchTrack
from gui.inputmap import *
from d3 import *
from gui.columnlistview import *
import d3script
import json


def initCallback():
    d3script.log("PresetManager2","PresetManager2 Loaded")

def applyPreset(presetName):
    op = Undoable('PresetManager Applying Preset')
    shift = os.keyboard.down(Keyboard.SHIFT)
    ctrl = os.keyboard.down(Keyboard.CTRL)
    presets = d3script.getPersistentValue('PresetManager2Settings')
    lays = d3script.getSelectedLayers()
    
    preset = filter(lambda x: x['name'] == presetName, presets)
    if (len(preset) != 1):
        d3script.log("PresetManager2","Found multiple presets with name.  Not applying.")
        return

    else:
        preset = preset[0]

        curTRender = state.player.tRender
        trk = state.track
        sectStartTime = trk.sections.getT(trk.beatToSection(trk.timeToBeat(curTRender)))

        modifyFields = []
        for valueSet in preset['values']: 
            if valueSet['field'] == '<opensequence>':
                oles = d3script.getTrackWidget().layerView.openEditorManager.openLayerEditors
                for ole in oles.values():  
                    for fw in ole.selectedFieldWrappers:
                        if (fw.fieldSequence.type == float):
                            modifyFields.append(fw.fieldSequence)
            else:
                for lay in d3script.getSelectedLayers():
                    modifyFields += filter(lambda x: (x.name == valueSet['field']) and (x.type == float),lay.fields)

        for fs in modifyFields:
            seq = fs.sequence
            curValue = float(seq.evalString(curTRender))
            prevValue = float(seq.evalString(seq.findCurrentKeyTime(curTRender))) 
            nextValue = float(seq.evalString(seq.findNextKeyTime(curTRender))) 

            def parseKeyValue(value):
                if value == '@':
                    return curValue
                elif value == '-':
                    return prevValue
                elif value == '+':
                    return nextValue
                else:
                    return float(value)

            def parseKeyTime(time):
                if time == '<none>':
                    return None
                elif time == '<sectstart>':
                    return sectStartTime
                else:
                    return float(time) + curTRender
       	
            if (len(valueSet['keys']) > 1) and ('!' not in valueSet['flags']):
                print('Cleaning up keys')
                delStartTime = parseKeyTime(valueSet['keys'][0][1])
                delEndTime = parseKeyTime(valueSet['keys'][-1][1])

                if (delStartTime != None) and (delEndTime != None):
                    keyIndex = seq.find(delEndTime)

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

                if (fs.noSequence == True) and (keyTime != None):
                    fs.disableSequencing = False   
                    if (seq.nKeys() > 0):         
                        seq.remove(0,seq.nKeys())
                    seq.setFloat(keyTime, float(keyValue))
                    seq.key(seq.find(keyTime)).interpolation = key[2]

                elif (fs.noSequence == True) and (keyTime == None):
                    if (seq.nKeys > 0):         
                        seq.remove(0,seq.nKeys())
                    seq.setFloat(fs.layer.tStart, float(keyValue))

                elif (fs.noSequence == False) and (keyTime == None):
                    seq.setFloat(curTRender, float(keyValue))
                    seq.key(seq.find(curTRender)).interpolation = key[2]
            
                elif (fs.noSequence == False) and (keyTime != None):
                    seq.setFloat(keyTime, float(keyValue))
                    seq.key(seq.find(keyTime)).interpolation = key[2]
                

class PresetManager2Widget(Widget):

    def __init__(self):
        #get any stored values
        self.presets = d3script.getPersistentValue('PresetManager2Settings')
        if (self.presets == None):
            self.presets = []

        Widget.__init__(self)

        self.add(TitleButton('Preset Manager'))
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
            for preset in self.presets:
                textValues = json.dumps(preset['values'])
                if len(textValues) > 70:
                    textValues = textValues[:67] + '...'
                rows.append([preset['name'], textValues])

            items = map(lambda x:ColumnListViewItem(x),rows)

            self.listWidget.items = items
            self.listWidget.recalculateColumnSizes()

    def handleItemClick(self, item, colIndex):
        d3script.log('PresetManager','item has been clicked')
        applyPreset(item.values[0])


    def handleItemRightClick(self,item,colIndex):

        def onSave():
            if (self.editName != self.oldEditName) and (len(filter(lambda x:x['name'] == self.editName, self.presets)) > 0):
                d3.alertInfo('Preset names should be unique.')
                return

            presetValues = json.loads(self.editValues)
            presetName = self.editName
            
            self.presets = filter(lambda x:x['name'] != self.oldEditName,self.presets)
            
            self.presets.append({'name':presetName,'flags':self.editFlags, 'values': presetValues})
            d3script.setPersistentValue('PresetManager2Settings',self.presets)
            self.generatePresetRows()
            self.popup.close()


        def onDelete():
            self.presets = filter(lambda x:x['name'] != self.oldEditName,self.presets)
            d3script.setPersistentValue('PresetManager2Settings',self.presets)
            self.generatePresetRows()
            self.popup.close()


        self.popup = Widget()
        self.popup.add(TitleButton('Edit Preset'))
        self.editName = item.values[0]
        self.oldEditName = item.values[0]
        self.editFlags = item.values[1]
        self.editValues = json.dumps(filter(lambda x: x['name'] == self.editName,self.presets)[0]['values'],indent = 2)
        self.popup.add(Field('Preset Name',ValueBox(self,'editName')))
        self.popup.add(Field('Flags',ValueBox(self,'editFlags')))
        vb = ValueBox(self,'editValues')
        vb.textBox.multiline = True
        vb.width = 80.0
        self.popup.add(Field('Preset Values', vb))
        self.popup.add(Button('Save', onSave))
        self.popup.add(Button('Delete', onDelete))
        parent = self.floatingParent
        self.popup.pos = Vec2(parent.absPos.x + parent.size.x + 8, gui.cursorPos.y)
        self.popup.follows(parent)
        self.popup.arrangeVertical()
        self.popup.computeAllMinSizes()
        d3gui.root.add(self.popup)

    def addPreset(self,set):

        if (len(filter(lambda x:x['name'] == self.presetName, self.presets)) > 0):
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
                f.field.parent.expand()
                if self.useTimes == 0:
                    values.append({'field':f.fieldSequence.name,'flags':'','keys':[(f.field.valueBox.getVal(),'<none>',Key.cubic)]})
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
                        keyArray.append((key.v,key.localT - startTime,key.interpolation))

                    values.append({'field':f.fieldSequence.name,'flags':'','keys':keyArray})    

        self.presets.append({'name':self.presetName,'values':values})
        d3script.setPersistentValue('PresetManager2Settings',self.presets)
        self.generatePresetRows()

        
def presetPopup():
    """Open a popup menu with rename options"""
    
    widget = PresetManager2Widget()

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
