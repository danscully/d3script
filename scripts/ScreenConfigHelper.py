#ScreenConfigHelper
from d3 import *
import d3script

def initCallback():
    d3script.log("ScreenConfigHelper","ScreenConfigHelper Loaded")

def getSceneryMoverLayer(layer):
    sceneryLayer = filter(lambda x:x.name == layer, d3script.getCurrentTrack().layers)
    if (len(sceneryLayer) != 1):
        d3script.log('ScreenConfigHelper','Could not find ' + layer + ' layer.  Create layer with that name to add Screen Config keys automatically')
        return None
    else:
        return sceneryLayer[0]
    

def getConfigForTime(time, layer):
    sceneryLayer = getSceneryMoverLayer(layer)
    if (sceneryLayer == None):
        return None
    
    configSeq = sceneryLayer.findSequence('config')
    keyIndex = configSeq.sequence.find(d3script.getPlayer().tRender)
    
    if keyIndex < 0:
        return None
    else:
        return configSeq.sequence.keys[keyIndex].r


def createOrUpdateScreenConfig(configName,layer,configTemplateName,addToModule=True,moveTime=5):
    template = filter(lambda x: x.description == configTemplateName, resourceManager.allResources(ScreenConfiguration))
    if len(template) != 1:
        d3script.log('ScreenConfigHelper','Could not find template configuration.  Create a config named '+configTemplateName +' with the objects you want tracked')
        return
    
    template = template[0]

    sc = resourceManager.loadOrCreate('objects/screenconfiguration/' + configName,ScreenConfiguration)

    #remove all existing objects
    tempObjs = []
    for obj in sc.objects:
        tempObjs.append(obj)

    for obj in tempObjs:
        sc.removeObject(obj)

    #add each object and the animates value            
    for i in range(len(template.objects)):
        sc.addObject(template.objects[i])
        sc.lock_axes[i] = template.lock_axes[i]
        sc.animates[i] = template.animates[i]

    if (addToModule):
        sceneryLayer = getSceneryMoverLayer(layer)
        if (sceneryLayer == None):
            return

        configSeq = sceneryLayer.findSequence('config')
        if (configSeq.noSequence):
            configSeq.disableSequencing = False
        
        player = d3script.getPlayer()
        curConfig = getConfigForTime(player.tRender, layer)
        if (curConfig == None):
            configSeq.sequence.setResource(player.tRender,sc)
        else:
            configSeq.sequence.setResource(player.tRender,curConfig)
            configSeq.sequence.setResource(player.tRender + float(moveTime), sc)

        nextKeyTime = configSeq.sequence.findNextKeyTime(player.tRender + float(moveTime))
        
        if nextKeyTime > (player.tRender + float(moveTime)):
            configSeq.sequence.setResource(nextKeyTime,sc)

class ScreenConfigHelperWidget(Widget):

    def __init__(self, layer, config):
        Widget.__init__(self)

        self.layer = layer
        self.configTemplate = config
        self.add(TitleButton('Screen Config Helper'))
        self.tRender = d3script.getPlayer().tRender
        self.prevConfig = getConfigForTime(self.tRender, self.layer)
        self.configName = 'New Config'
        vb = ValueBox(self,'prevConfig')
        vb.readOnly = True
        self.add(Field('Config Name',ValueBox(self,'configName')))
        self.add(Field('Previous Config',vb))
        yesNo = ['No', 'Yes']
        self.updatePrevious = 0
        self.transitionTime = 5
        self.add(Field('Update Previous', ValueBox(self,'updatePrevious',yesNo)))
        self.add(Field('Transition Time', ValueBox(self,'transitionTime')))
        bt = Button('Save', self.execute)
        bt.overrideMinSize = (lambda x:Vec2(200,35))
        self.add(bt)
        self.arrangeVertical()
        self.computeAllMinSizes()

    def update(self):
        player = d3script.getPlayer()
        if self.tRender != player.tRender:
            self.tRender = player.tRender
            self.prevConfig = getConfigForTime(self.tRender, self.layer)

    def execute(self):
        if (self.updatePrevious == 1):
            resName = self.prevConfig.userInfoPath
            createOrUpdateScreenConfig(resName,self.layer,self.configTemplate, addToModule = False)
        else:
            resName = self.configName + '.apx'
            createOrUpdateScreenConfig(resName,self.layer, self.configTemplate, addToModule = True,moveTime = self.transitionTime)
        self.close()


def updateCurrentScreenConfig(layer="SCENERYMOVER", config="_sctemplate"):
    config = getConfigForTime(d3script.getPlayer().tRender,layer)
    resName = config.userInfoPath
    createOrUpdateScreenConfig(resName,layer,config.description, addToModule = False)

def openScreenConfigHelperWidget(layer="SCENERYMOVER", config="_sctemplate" ):
    d3gui.root.add(ScreenConfigHelperWidget(layer, config))

SCRIPT_OPTIONS = {
    "minimum_version" : 23, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Create/Update Config", # Display name of script
            "group" : "Screen Config Helper", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Create a Screen Config by name", #text for help system
            "callback" : createOrUpdateScreenConfig, # function to call for the script
        },
        {
            "name" : "Update Config", # Display name of script
            "group" : "Screen Config Helper", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Update current screen config", #text for help system
            "callback" : updateCurrentScreenConfig, # function to call for the script
        },        
        {
            "name" : "Open SC Helper Widget", # Display name of script
            "group" : "Screen Config Helper", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Open Screen Config Helper Widget", #text for help system
            "callback" : openScreenConfigHelperWidget, # function to call for the script
        }
        ]
    }
