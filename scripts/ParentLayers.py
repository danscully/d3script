# Parent Layers
from gui.inputmap import *
from d3 import *
import d3script
import gui.widget
import gui.alertbox
import d3script



class LayerParentPopup(Widget):
    parentLayer = 0

    def __init__(self):
        

        Widget.__init__(self)   
        self.titleButton = TitleButton("Parent Layers")
        self.add(self.titleButton)
        self.layers = d3script.getSelectedLayers()

        if len(self.layers) < 2:
            gui.alertbox.AlertBox('Parent Layers: Must select more than one layer')
            return

        layerNames = map(lambda l: l.name,self.layers)

        self.parentLayerBox = ValueBox(self, 'parentLayer', layerNames)
        self.add(Field('Parent Layer: ',self.parentLayerBox))

        #generate list of fields in common, that are linkable
        commonFields = set(map(lambda f:f.name,self.layers[0].fields))
        d3script.log('parentLayer',str(commonFields))

        for lay in self.layers:
            layerFields = map(lambda f:f.name,lay.fields)
            sameFields = []
            for field in layerFields:
                if field in commonFields:
                    sameFields.append(field)
            commonFields = sameFields

        #d3script.log('parentLayer',str(commonFields))
        self.fieldWrapperWidget = CollapsableWidget('Fields to link','Fields to link')
        self.fieldWrapperWidget.arrangeVertical()
        self.add(self.fieldWrapperWidget)
        self.fieldSectionWidget = Widget()
        self.fieldSectionWidget.arrangeHorizontal()
        self.fieldWrapperWidget.add(self.fieldSectionWidget)
        self.labelWidget = Widget()
        self.checkWidget = Widget()
        self.checkWidget.minSize = Vec2(50,0)

        for fieldName in commonFields:
            #d3script.log('parentLayer','adding field: ' + fieldName)

            field = filter(lambda f:f.name == fieldName,self.layers[0].fields)[0]

            if (field.type == float) or (field.type == int):
                #d3script.log('parentLayer','added field: ' + fieldName)
                tickbox = TickBoxWidget()
                tickbox.border = Vec2(50,50)
                self.checkWidget.add(tickbox)
                self.labelWidget.add(TextLabel(field.name).justify()) 

        self.labelWidget.arrangeVertical()
        self.checkWidget.arrangeVertical()
        
        self.fieldSectionWidget.add(self.labelWidget)
        self.fieldSectionWidget.add(self.checkWidget)
        self.computeAllMinSizes()
        self.arrangeVertical()

        allColorButton = Button('Check All Color',self.checkColor)
        allColorButton.border = Vec2(0,10)
        self.add(allColorButton)

        allTranslateButton = Button('Check All Translate',self.checkTranslate)
        allTranslateButton.border = Vec2(0,10)
        self.add(allTranslateButton)

        allCropButton = Button('Check All Crop',self.checkCrop)
        allCropButton.border = Vec2(0,10)  
        self.add(allCropButton)     

        toggleAllButton = Button('Toggle All',self.toggleAll)
        toggleAllButton.border = Vec2(0,10)  
        self.add(toggleAllButton) 

        doButton = Button('Parent Layers',self.doParent)
        doButton.border = Vec2(0,10)
        self.add(doButton)
        self.pos = (d3gui.root.size / 2) - (self.size/2)
        d3gui.root.add(self)

    def doParent(self):
        op = Undoable('Parent Layers')
        #first rename the parent layer so it has a label
        parent = self.layers[self.parentLayer]
        if parent.name.find('EXPSRC') == -1:
            parent.name = parent.name + ' EXPSRC'


        #then slice the selected layers so we don't have the parent layer
        self.layers.pop(self.parentLayer)

        #then iterate the layers
        #for each layer, for each ticked box, setExpression
        for lay in self.layers:
            for index,item in enumerate(self.checkWidget.children):
                if item.ticked == True:
                    fieldName = self.labelWidget.children[index].name
                    expression = 'module:' + parent.name + '.' + fieldName
                    d3script.setExpression(lay,fieldName,d3script.expressionSafeString(expression))

        self.close()
    
    def checkSet(self,fields):
        for index,item in enumerate(self.labelWidget.children):
            if item.name in fields:
                self.checkWidget.children[index].ticked = True

    def checkColor(self):
        self.checkSet(['xCol','yCol','brightness (shift)','contrast (scale)','hue shift','red min','red max','red gamma','green min','green max','green gamma','blue min','blue max','blue gamma'])

    def checkCrop(self):
        self.checkSet(['right','left','top','bottom','cropSoftness'])
    
    def checkTranslate(self):
        self.checkSet(['size','scale.x','scale.y','pos.x','pos.y','rotation'])

    def toggleAll(self):
        if len(self.checkWidget.children) > 0:
            value = not self.checkWidget.children[0].ticked

            for tick in self.checkWidget.children:
                tick.ticked = value

def openPopup():
    LayerParentPopup()

def initCallback():
    d3script.log('parentLayers','Initialized')

SCRIPT_OPTIONS = {
    "minimum_version" : 21, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Parent Selected Layers", # Display name of script
            "group" : "Parenting", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binging" : "Keypress,Alt,e",
            "bind_globally" : True, # binding should be global
            "help_text" : "Open Layer Parenting Popup", #text for help system
            "callback" : openPopup, # function to call for the script
        }
        ]

    }
