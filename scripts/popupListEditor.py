# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.8 (main, Nov  6 2022, 02:23:43) [MSC v.1929 64 bit (AMD64)]
# Embedded file name: C:\blip\dev\scripts\gui\PopupListEditor.py
# Compiled at: 2024-02-01 12:01:16
from d3 import *
from functools import partial
from gui.inputmap import *
from gui.separator import Separator
import d3script

def initCallback():
        d3script.log("Popup List Editor","Popup List Editor Loaded")

    
def gotoPopupListEditor():
    popupListEditor = d3gui.root.childOfType(PopupListEditor)
    if not popupListEditor:
        popupListEditor = PopupListEditor()
        d3gui.root.add(popupListEditor)
    popupListEditor.focus = True


def __del__():
    w = d3gui.root.childOfType(PopupListEditor)
    if w:
        w.close()


def __reload__():
    gotoPopupListEditor()


class PopupListEditor(Widget):
    isStickyable = True

    def _initParams(self):
        return {}

    def __init__(self):
        Widget.__init__(self)
        self.name = 'PopupListEditor'
        self.arrangeVertical()
        self.titleButton = TitleButton('Popup List Editor')
        self.add(self.titleButton)
        self.maxSize = Vec2(3400, 700)
        self.typeButton = Button('Select Resource Type', (lambda : self.onChooseTypeButtonPressed()))
        self.add(self.typeButton)
        self.add(Separator())
        self.listEditor = None
        return

    def onChooseTypeButtonPressed(self):
        classMenu = ClassMenu()
        classMenu.set('Resource', self.selectType, False, False)
        d3gui.root.add(classMenu.positionNear(self))

    def selectType(self, type):
        self.dataSource = ListEditorDataSource_ResourceType()
        self.dataSource.set(type)
        if self.listEditor:
            self.listEditor.removeFromParent()
            self.listEditor = None
        self.listEditor = ListEditor(self.dataSource)
        self.add(self.listEditor)
        self.typeButton.name = 'Selected Resource Type: ' + type
        return


import core.serialise
core.serialise.registerType(PopupListEditor)

SCRIPT_OPTIONS = {
    "minimum_version" : 21, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Open List Editor", # Display name of script
            "group" : "Popup List Editor", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "Keypress,Alt,`",
            "bind_globally" : True, # binding should be global
            "help_text" : "Open List Editor", #text for help system
            "callback" : gotoPopupListEditor, # function to call for the script
        }
        ]

    }
