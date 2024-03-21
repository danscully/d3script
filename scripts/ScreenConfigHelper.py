#ScreenConfigHelper
from d3 import *
import d3script

def initCallback():
    d3script.log("ScreenConfigHelper","ScreenConfigHelper Loaded")

def getSceneryMoverLayer():
    sceneryLayer = filter(lambda x:x.name == 'SCENERYMOVER', state.track.layers)
    if (len(sceneryLayer) != 1):
        d3script.log('ScreenConfigHelper','Could not find SCENERYMOVER layer.  Create layer with that name to add Screen Config keys automatically')
        return None
    else:
        return sceneryLayer[0]
    

def getConfigForTime(time):
    sceneryLayer = getSceneryMoverLayer()
    if (sceneryLayer == None):
        return None
    
    configSeq = sceneryLayer.findSequence('config')
    keyIndex = configSeq.sequence.find(state.player.tRender)
    
    if keyIndex < 0:
        return None
    else:
        return configSeq.sequence.keys[keyIndex].r


def createOrUpdateScreenConfig(configName,addToModule=True,moveTime=5):
    template = filter(lambda x: x.description == '_sctemplate', resourceManager.allResources(ScreenConfiguration))
    if len(template) != 1:
        d3script.log('ScreenConfigHelper','Could not find template configuration.  Create a config named "_sctemplate" with the objects you want tracked')
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
        sceneryLayer = getSceneryMoverLayer()
        if (sceneryLayer == None):
            return

        configSeq = sceneryLayer.findSequence('config')
        if (configSeq.noSequence):
            configSeq.disableSequencing = False
        
        curConfig = getConfigForTime(state.player.tRender)
        if (curConfig == None):
            configSeq.sequence.setResource(state.player.tRender,sc)
        else:
            configSeq.sequence.setResource(state.player.tRender,curConfig)
            configSeq.sequence.setResource(state.player.tRender + float(moveTime), sc)

        nextKeyTime = configSeq.sequence.findNextKeyTime(state.player.tRender + float(moveTime))
        
        if nextKeyTime > (state.player.tRender + float(moveTime)):
            configSeq.sequence.setResource(nextKeyTime,sc)

class ScreenConfigHelperWidget(Widget):

    def __init__(self):
        Widget.__init__(self)

        self.add(TitleButton('Screen Config Helper'))
        self.tRender = state.player.tRender
        self.prevConfig = getConfigForTime(self.tRender)
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
        if self.tRender != state.player.tRender:
            self.tRender = state.player.tRender
            self.prevConfig = getConfigForTime(self.tRender)

    def execute(self):
        if (self.updatePrevious == 1):
            resName = self.prevConfig.userInfoPath
            createOrUpdateScreenConfig(resName,addToModule = False)
        else:
            resName = self.configName + '.apx'
            createOrUpdateScreenConfig(resName,addToModule = True,moveTime = self.transitionTime)
        self.close()


def updateCurrentScreenConfig():
    config = getConfigForTime(state.player.tRender)
    resName = config.userInfoPath
    createOrUpdateScreenConfig(resName,addToModule = False)

def openScreenConfigHelperWidget():
    d3gui.root.add(ScreenConfigHelperWidget())

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
