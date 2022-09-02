# D3 Helpers
from __future__ import print_function
from gui.inputmap import *
from d3 import *
from gui.track.layerview import LayerView
from gui.track import TrackWidget
import d3script
import re
import gui.widget


def initCallback():
    d3script.log("smartName","SmartName Loaded")


def doComboRename(newNameStem):
    op = Undoable('ScullyRename')
    selLay = d3script.getSelectedLayers()

    for i in selLay:

        if (newNameStem[0] == '!'):
            i.name = newNameStem[1:]

        elif (i.name.find('EXPSRC') != -1):
            continue

        elif (i.description == 'GroupLayer'):
            if (newNameStem.find('*') == -1):
                i.name = newNameStem

        else:
            
            keyResource =  i.findSequence('Mapping').sequence.key(0).r
            if hasattr(keyResource,'description'):
                mapName = ' [' + i.findSequence('Mapping').sequence.key(0).r.description + ']'
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

            existingName = i.name.replace('(','[')
            splitNames = existingName.split('[')
            if len(splitNames) > 1:
                existingNameStem = splitNames[0].rstrip()
            else:
                existingNameStem = ''

            moduleName = type(i.module).__name__
            moduleName = moduleName.replace('Module','')
            if moduleName == 'VariableVideo':
                moduleName = ''
            else:
                moduleName = ' [' + moduleName + ']'


            blendMode = d3script.blendModeToString(i.findSequence('BlendMode').sequence.key(0).v)
            if blendMode == 'Alpha':
                blendMode = ''
            else:
                blendMode = ' [' + blendMode + ']'

            if (newNameStem == '@'):
                i.name = existingNameStem + moduleName + mapName + blendMode

            elif (newNameStem == '$'):
                i.name = mediaName + moduleName + mapName + blendMode

            else:
                i.name = newNameStem + moduleName + mapName + blendMode


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
    menu.add(TextBox('$ for filename, @ to autoupdate, !name... to force exact name'))
    menu.editItem('Rename:', nameStem, doComboRename)
    menu.pos = (d3gui.root.size / 2) - (menu.size/2)
    self.pos = Vec2(menu.pos[0],menu.pos[1]-100)

    d3gui.root.add(menu)
    menu.contents.findWidgetByName('Rename:').textBox.focus = True

       

SCRIPT_OPTIONS = {
    "minimum_version" : 21, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Module Smart Name", # Display name of script
            "group" : "Smart Rename", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binging" : "Keypress,Alt,r",
            "bind_globally" : True, # binding should be global
            "help_text" : "Rename module based on properties", #text for help system
            "callback" : renamePopup, # function to call for the script
        }
        ]

    }
