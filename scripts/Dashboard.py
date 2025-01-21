# Dashboard
from d3 import *
import d3script
from functools import partial

redColour = Colour(200 / 255.0, 0 / 255.0, 0 / 255.0) 
greenColour = Colour(0 / 255.0, 200 / 255.0, 0 / 255.0)
orangeColour = Colour(210 / 255.0, 160 / 255.0, 0 / 255.0)
dkGreenColour = Colour(0 / 255.0, 100 / 255.0, 0 / 255.0)
dkOrangeColour = Colour(105 / 255.0, 80 / 255.0, 0 / 255.0)
blackColour = Colour(0/ 255.0, 0 / 255.0, 0 / 255.0)

class DividerLine(Widget):
    
    def __init__(self):
        Widget.__init__(self)
        self.overrideMinSize = self.dividerSizeOverride
        self.renderAction.add(self.dividerRender)
        
    def dividerSizeOverride(self,size):
        return Vec2(size.x,2)
        
    def dividerRender(self):
        rect = Rect(self.absPos, self.size)
        self.quad(DxMaterial.alphaMtl, rect, Colour(90 / 255.0, 90 / 255.0, 90 / 255.0))
            
                 
        
class DashItem:
    def __init__(self, res,field,readOnly):
        self.resource = res
        self.name = res.description + ':' + field
        self.field = field
        self.readOnly = readOnly
        self.minGraph = 0
        self.maxGraph = 0
        self.showGraph = False
        self.greenMatch = ""

  
class Dashboard(Widget):
    isStickyable = True
    
    def __init__(self):
        Widget.__init__(self)
        self.closeAction.add(self.onClose)
        self.dashItems = []
        self.titleButton = TitleButton('Dashboard')
        self.startLinkFromDelegate = self._startLinkDelegate
        self.titleButton.startLinkFromDelegate = self._startLinkDelegate
        self.titleButton.contents.startLinkFromDelegate = self._startLinkDelegate
        self.titleButton.contents.makeLinkToAction.add(self.onMakeLink)
        self.fieldWidget = Widget()
        self.minSize = Vec2(1000,200)
        self.fieldWidget.minSize = Vec2(1000,200)
        self.fieldWidget.startLinkFromDelegate = self._startLinkDelegate
        self.makeLinkDelegate = self.onMakeLink
        self.fieldWidget.makeLinkDelegate = self.onMakeLink
        self.titleButton.makeLinkDelegate = self.onMakeLink
        self.add(self.titleButton)
        self.add(self.fieldWidget)
        
        self.varButton = Button('Add Expression Variable',self.addVariablePopup)
        self.varButton.border = Vec2(25,10)
        self.add(self.varButton)
        
        storedValues = d3script.getPersistentValue('dashitems',"Dashboard")
        if (storedValues):
            uidMgr = UidManager.get()
            for value in storedValues:
                res = uidMgr.getResource(value['uid'])
                if res:
                    if type(res) == Layer:
                        res = res.module
                    newItem = DashItem(res,str(value['field']),value['readOnly'])
                    newItem.minGraph = value['minGraph']
                    newItem.maxGraph = value['maxGraph']
                    newItem.showGraph = value['showGraph']
                    newItem.name = value['name']
                    newItem.greenMatch = value['greenMatch']
                    self.dashItems.append(newItem)
        
        self.updateFields()          
        self.pos = Vec2(1820.0,41.0)
        d3gui.root.add(self)
        self.titleButton.toggleSticky()
        
   
    def addVariableExecute(self,varName):
        expVariable = None
        expVariableDevice = None
        
        varDevices = resourceManager.allResources(ExpressionVariablesDevice)
        for device in varDevices:
            for expVar in device.container.variables:
                if expVar.name == varName:
                    expVariable = expVar
                    expVariableDevice = device
                    self.dashItems.append(DashItem(expVariableDevice,varName,False))
                    self.updateFields()
                    return
        
        #Look through Modules
        lays = filter(lambda x: x.moduleType == ExpressionVariablesModule,state.track.layers)
        for lay in lays:
            for f in lay.module.fields:
                if f.variable.name == varName:
                    self.dashItems.append(DashItem(lay.module,varName,True))
                    self.updateFields() 

        d3script.log('Dashboard','Could not find Expression Variable')
   
            
        
    def addVariablePopup(self):
        varName = 'Variable Name'
        menu = PopupMenu('Add Dashboard Expression Variable')
        menu.editItem('Variable Name:', varName, self.addVariableExecute)
        menu.pos = (d3gui.root.size / 2) - (menu.size/2)
        menu.pos = Vec2(menu.pos[0],menu.pos[1]-100)

        d3gui.root.add(menu)
        menu.contents.findWidgetByName('Variable Name:').textBox.focus = True
    
    def onClose(self):
        pass

    def _startLinkDelegate(self, dragStart):
        return True
    
    def populate(self):
        self.updateFields()

    def updateFields(self):
        # remove all children and repopulate
        while len(self.fieldWidget.children) > 0:
            self.fieldWidget.children[0].removeFromParent()
            
        for item in self.dashItems:
            self.createField(item)
        
        self.fieldWidget.arrangeVertical()
        self.arrangeVertical()
        self.computeAllMinSizes()
            
        #store values
        values = []
        for item in self.dashItems:
            res = item.resource
            if issubclass(type(item.resource),Module):
                res = item.resource.layer
            value = {"name":item.name, "uid":res.uid, "field":item.field, 
                     "readOnly":item.readOnly, "maxGraph": item.maxGraph, "minGraph": item.minGraph, 
                     "showGraph": item.showGraph, "greenMatch": item.greenMatch}
            values.append(value)
        
        d3script.setPersistentValue('dashitems',values,'Dashboard')

    def removeField(self,item):
        self.dashItems.remove(item)
        self.updateFields()

    def createField(self, item):
        vb = None
        if (type(item.resource) == ExpressionVariablesDevice):
            expVar = filter(lambda x: x.name == item.field,item.resource.container.variables)[0]
            if expVar.type == ExpressionVariable.StringType:
                vb = ValueBox(expVar,"defaultString",readonly=item.readOnly)
            else:
                vb = ValueBox(expVar,"defaultFloat",readonly=item.readOnly)
                
        elif (type(item.resource) == ExpressionVariablesModule):
            fields = filter(lambda x: x.variable.name == item.field,item.resource.fields)
            if len(fields) > 0:
                vb = ValueBox(fields[0],'value',readonly=True)
        else:
            vb = ValueBox(item.resource,item.field,readonly=item.readOnly)

        def genPopulatePopup(item):

            def removeCb(popup):
                self.removeField(item)
                popup.close()
                
            def readonlyCb(popup):
                vb.readonly = not vb.readonly
                item.readOnly = not item.readOnly
                popup.close()
                
            def toggleBarGraphCb(popup):
                item.barGraph = not item.barGraph
                popup.close()
            
            def onClose():
                self.updateFields()
                   
            def popCb(popup):
                
                popup.add(Field("Name:",ValueBox(item,'name')))
                popup.add(Field("Green value match:",ValueBox(item,'greenMatch')))
                popup.add(Field("Show Bar Graph:",ValueBox(item,'showGraph', unitType=UnitTypeAttribute.Boolean)))
                popup.add(Field("Bar graph min:",ValueBox(item,'minGraph')))
                popup.add(Field("Bar graph max:",ValueBox(item,'maxGraph')))
                popup.add(Field("Read only:",ValueBox(item,'readOnly', unitType=UnitTypeAttribute.Boolean)))

                popup.add(Button('Remove field', (lambda popup=popup: removeCb(popup))))
                
                popup.closeAction.add(onClose)

            return popCb

        if (type(item.resource) == ExpressionVariablesModule) or (type(item.resource) == ExpressionVariablesDevice):
            def ovOverride():
                pu = PopupMenu('Options')
                d3gui.root.add(pu.positionNear(self))
                vb.openValueOptionsAction.doit(pu)
            
            vb.openValueOptionsOverride = ovOverride
                
        vb.openValueOptionsAction.add(genPopulatePopup(item))
        self.fieldWidget.add(Field(item.name,vb))

                
        if (item.showGraph) or (item.greenMatch):
            def sizeOverride(size):
                return Vec2(size.x, 30)
            
            bar = Widget()
            bar.overrideMinSize = sizeOverride
            
            def drawGraph():
                val = vb.getVal()
                normVal = 1
                backColour = blackColour
                alertColour = blackColour
                
                if (type(val) == float) and (item.showGraph):
                    normVal = (val - item.minGraph)/(item.maxGraph - item.minGraph)
                    alertColour = orangeColour
                    
                    if normVal <= 0:
                        normVal = 0
                        alertColour = redColour
                    elif normVal > 1:
                        normVal = 1
                        alertColour = greenColour                    

                elif item.greenMatch:
                    if (issubclass(type(val),Resource)):
                        strVal = val.description
                    else:
                        strVal = vb.textBox.text
                    
                    if (item.greenMatch == strVal):
                        alertColour = greenColour
                    else:
                        alertColour = orangeColour  
                        
                startRect = Rect(Vec2(bar.absPos.x + 10,bar.absPos.y+5), Vec2(10, 10))  
                backRect = Rect(Vec2(bar.absPos.x + 20,bar.absPos.y+5), Vec2(bar.size.x - 30, 10))
                frontRect = Rect(Vec2(bar.absPos.x + 20,bar.absPos.y+5), Vec2((bar.size.x - 30) * normVal, 10)) 
                bar.quad(DxMaterial.alphaMtl, backRect, backColour)
                bar.quad(DxMaterial.alphaMtl, frontRect, alertColour)
                bar.quad(DxMaterial.alphaMtl, startRect, alertColour)
        
            bar.renderAction.add(drawGraph)
            self.fieldWidget.add(bar)
            
        self.fieldWidget.add(DividerLine())
                        
     
    def onMakeLink(self, targetWidget):
        err = self.innerMakeLink(targetWidget)
        if err is not None:
            d3.alertError(TFormat('Could not make link: {0:s}', err))
            return
        else:
            return

    def innerMakeLink(self, targetWidget):
        targetField = targetWidget if isinstance(targetWidget, Field) else targetWidget.parentOfType(Field)
        if not targetField:
            return Translator.translateToString('please link to a field in another editor')
        vb = targetField.valueBox
        resource = vb.containingResource
        if not resource:
            return Translator.translateToString("can't find a resource to link to")

        field = vb.property.field()
        if not field:
            return Translator.translateToString("can't find the real field here - could be a computed value based on something else")
        #object = vb.property.object()
        dashItem = DashItem(resource,str(field.name),False)
        self.dashItems.append(dashItem)
        self.updateFields()
        

def initCallback():
    d3script.log('Dashboard','Initialized')
            
def openDashboard():
    db = Dashboard()
    
SCRIPT_OPTIONS = {
    "minimum_version" : 30, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Open Dashboard", # Display name of script
            "group" : "Dashboard", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Open Dash Board", #text for help system
            "callback" : openDashboard, # function to call for the script
        }
        ]

    }
