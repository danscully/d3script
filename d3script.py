# Helper api for d3/disguise scripting
# Dan Scully, 2022
# No license yet
# Some code clearly copy/pasted from RGM


import importlib
from d3 import *
from gui.columnlistview import ColumnListView, ColumnListViewItem, ColumnListViewColumn
import os
import json
import sys
import math
import time
import struct
import socket
import win32com.client
import win32api
import win32con
from gui.track.layerview import LayerSelection


VK_CODE = {'backspace':0x08, 'tab':0x09, 'clear':0x0C, 'enter':0x0D, 'shift':0x10,'ctrl':0x11,'alt':0x12,'pause':0x13,
            'caps_lock':0x14,'esc':0x1B,'spacebar':0x20,'page_up':0x21,'page_down':0x22,'end':0x23,'home':0x24,'left_arrow':0x25,
            'up_arrow':0x26,'right_arrow':0x27,'down_arrow':0x28,'select':0x29,'print':0x2A,'execute':0x2B,'print_screen':0x2C,
            'ins':0x2D,'del':0x2E,'help':0x2F,
            '0':0x30,'1':0x31,'2':0x32,'3':0x33,'4':0x34,'5':0x35,'6':0x36,'7':0x37,'8':0x38,'9':0x39,
            'a':0x41,'b':0x42,'c':0x43,'d':0x44,'e':0x45,'f':0x46,'g':0x47,'h':0x48,'i':0x49,'j':0x4A,'k':0x4B,'l':0x4C,'m':0x4D,
            'n':0x4E,'o':0x4F,'p':0x50,'q':0x51,'r':0x52,'s':0x53,'t':0x54,'u':0x55,'v':0x56,'w':0x57,'x':0x58,'y':0x59,'z':0x5A,
            'numpad_0':0x60,'numpad_1':0x61,'numpad_2':0x62,'numpad_3':0x63,'numpad_4':0x64,'numpad_5':0x65,'numpad_6':0x66,
            'numpad_7':0x67,'numpad_8':0x68,'numpad_9':0x69,'multiply_key':0x6A,'add_key':0x6B,'separator_key':0x6C,'subtract_key':0x6D,
            'decimal_key':0x6E,'divide_key':0x6F,
            'F1':0x70,'F2':0x71,'F3':0x72,'F4':0x73,'F5':0x74,'F6':0x75,'F7':0x76,'F8':0x77,'F9':0x78,'F10':0x79,'F11':0x7A,
            'F12':0x7B,'F13':0x7C,'F14':0x7D,'F15':0x7E,'F16':0x7F,'F17':0x80,'F18':0x81,'F19':0x82,'F20':0x83,'F21':0x84,
            'F22':0x85,'F23':0x86,'F24':0x87,
            'num_lock':0x90,'scroll_lock':0x91,'left_shift':0xA0,'right_shift ':0xA1,'left_control':0xA2,'right_control':0xA3,
            'left_menu':0xA4,'right_menu':0xA5,'browser_back':0xA6,'browser_forward':0xA7,'browser_refresh':0xA8,'browser_stop':0xA9,
            'browser_search':0xAA,'browser_favorites':0xAB,'browser_start_and_home':0xAC,'volume_mute':0xAD,'volume_Down':0xAE,
            'volume_up':0xAF,'next_track':0xB0,'previous_track':0xB1,'stop_media':0xB2,'play/pause_media':0xB3,'start_mail':0xB4,
            'select_media':0xB5,'start_application_1':0xB6,'start_application_2':0xB7,'attn_key':0xF6,'crsel_key':0xF7,
            'exsel_key':0xF8,'play_key':0xFA,'zoom_key':0xFB,'clear_key':0xFE,
            '+':0xBB,',':0xBC,'-':0xBD,'.':0xBE,'/':0xBF,'`':0xC0,';':0xBA,'[':0xDB,'\\':0xDC,']':0xDD,"'":0xDE,'`':0xC0}

SCRIPTSFOLDER = "./Scripts"
D3MAJORVERSION = ReleaseVersion.versionName
D3MINORVERSION = ReleaseVersion.micro
SCRIPTMENUTITLE = 'Script Menu'
SCRIPTBUTTONTITLE = 'Scripts'
NOTESTORAGENAME = 'd3scriptstoragenote_donottouch'
scripts = []
scriptMods = []
debugmode = False
shell = win32com.client.Dispatch('WScript.Shell')

#utility functions - should these move somewhere else?
def log(sender, msg,debugOnly = False):
    """
    A wrapper for printing to the console.

    ``debugOnly`` is an optional flag for messages only printed when ``d3script.debugMode`` is True
    """
    if (not debugOnly) or (debugMode):
        print (sender + ": " + msg)

def callScript(module,func,param = None):
    """
    Calls a loaded script function directly.  Useful for firing scripts over the telnet console
    """    
    log('d3script','dispatching: ' + module + '.' + func)
    funcCall = getattr(sys.modules[module],func)
    if (param != None):
        funcCall(param)
    else:
        funcCall()

def sendOscMessage(device,msg,param = None):
    """
    Utility for sending OSC Messages.
    Currently only allows one parameter.  Uses the info from a d3 OSC Device, but does not use the builtin functions
    as messages are only supported on Directors and Actors.
    """

    log('d3script','Sending Eos msg: ' + msg + 'with param: ' + str(param))
    
    OSCAddrLength = math.ceil((len(msg)+1) / 4.0) * 4
    packedMsg = struct.pack(">%ds" % (OSCAddrLength), str(msg))

    if type(param) == str:
        OSCTypeLength = math.ceil((len(',s')+1) / 4.0) * 4
        packedType = struct.pack(">%ds" % (OSCTypeLength), str(',s'))
        OSCArgLength = math.ceil((len(param)+1) / 4.0) * 4
        packedParam = struct.pack(">%ds" % (OSCArgLength), str(param))

    elif type(param) == float:
        OSCTypeLength = math.ceil((len(',f')+1) / 4.0) * 4
        packedType = struct.pack(">%ds" % (OSCTypeLength), str(',f'))
        packedParam  = struct.pack(">f", float(param))

    elif type(param) == int:
        OSCTypeLength = math.ceil((len(',f')+1) / 4.0) * 4
        packedType = struct.pack(">%ds" % (OSCTypeLength), str(',i'))
        packedParam  = struct.pack(">i", int(param))

    else:
        packedType = ''
        packedParam = ''

    oscMsg = packedMsg + packedType + packedParam
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(oscMsg, (device.sendIPAddress, device.sendPort))
    time.sleep(0.1)

def getLayersOfTrackAtTime(trk,t):
    """
    Gets layers of a track that are present at time t
    """
    return filter(lambda l:(l.tStart <= t) and (t <= l.tEnd),trk.layers)

def findWidgetByName(name):
    """
    Find a gui widget by name.  
    Note that if you are looking at the widget title in the UI, that's often the name of the title button 
    and you need to get the parent object to get the widget you want.
    """

    return d3gui.root.findWidgetByName(name)

def getPersistentValue(key,domain=None):
    """
    Gets a persistent value.  d3script stores values as JSON in a special note in d3's note system.
    """
    
    domainPath = ""

    if domain != None:
        domainPath = "_" + domain

    note = resourceManager.loadOrCreate('objects/note/'+NOTESTORAGENAME+domainPath+'.apx',Note)
    if len(note.text) > 0:
        localDict = json.loads(note.text)
    else:
        return None

    if localDict.has_key(key):
        return localDict[key]
    else:
        return None


def setPersistentValue(key,value,domain=None):
    """
    Sets a persistent value which will exist across restarts.  d3script stores values as JSON in a special note in d3's note system.
    """

    domainPath = ""

    if domain != None:
        domainPath = "_" + domain

    note = resourceManager.loadOrCreate('objects/note/'+NOTESTORAGENAME+domainPath+'.apx',Note)
    if len(note.text) > 0:
        localDict = json.loads(note.text)
    else:
        localDict = {}
    
    localDict[key] = value

    note.text = json.dumps(localDict,indent=4)


def createLayerOfTypeOnCurrentTrack(moduleType):
    """
    Creates a new on the current Track of the type specified (by module name in New Layer popup).
    Currently fakes UI interactions.
    Returns the layer.
    """

    tw = getTrackWidget()
    bw = tw.barWidget

    bw.newUnnamedLayer()

    cm = d3gui.root.findWidgetByName('Select type of layer')
    if (cm == None):
        log('d3script','Could not find Class Menu for create layer')
    
    #super fragile
    grps = cm.parent.children[2].children[0].children

    bts = []

    for grp in grps:
        for c in grp.children:
            bts.append(c)
    
    bts = filter(lambda bt: type(bt) == Button,bts)

    btn = filter(lambda bt: bt.name == moduleType,bts)
    
    if len(btn) != 1:
        log('d3script','create layer could not find module of type: ' + moduleType)
        return

    # 'Press' the button to make the layer
    btn[0].clickAction.doit()

    # I assume this is super fragile as well
    return state.track.layers[0]


def getFieldFromLayerByName(lay, fieldName):
    """Get the field by name from a layer"""
    flds = filter(lambda x: x.name.lower() == fieldName.lower(),lay.fields)
    if len(flds) == 1:
        return flds[0]
    else:
        log('d3script','Could not find field: ' + fieldName + ' for layer: ' + lay.name)


def setKeyForLayerAtTime(lay, fieldName, val, timeStart):
    """creates a keyframe for value at time.  If key exists, delete key"""
    """passing a string to a resource field will attempt to find the resource by name"""

    def _findResourceByNameAndType(name,rt):
        if type(name) == str:
            vcs = resourceManager.allResources(rt)
            vcs = filter(lambda v: v.description.lower() == name.lower(),r)

            if len(vcs) == 1:
                return vcs[0]
            else:
                return None
                

    timeStart = float(timeStart)

    seq = getFieldFromLayerByName(lay,fieldName).sequence

    # Find out what type of sequence we are dealing with
    if isinstance(seq, ResourceSequence):
        
    # delineate between videos, mappings, and audio mappings
    # and create full path to resource.

        theRes = None
        if fieldName == 'video':
            resType = VideoClip

        elif fieldName == 'mapping':
            resType = Projection

        elif fieldName == 'Output':
            resType = LogicalAudioOutDevice

        else:
            log('d3script','Only resource sequences of "video", "mapping", or "Output" are supported as of now')
            return


        if type(val) == str:
            theRes = _findResourceByNameAndType(val,resType)

        elif isinstance(val,resType):
            theRes = val

        if (theRes) == None:
            log('d3script','Could not find resource of right type with name ' + val)
            return

    # Remove key if it exists already
        for key in range(seq.nKeys()):
            if seq.keys[key].localT == timeStart:
                seq.remove(key, timeStart)

        seq.setResource(timeStart, theRes)

    elif isinstance(seq, FloatSequence):
        seq.setFloat(timeStart, float(val))

    elif isinstance(seq, StringSequence):
        seq.setStringAtT(timeStart, str(val))



def expressionSafeString(text):
    """
    Convert string to be expression safe.
    Replaces all punctuation with underscores
    """

    return text.replace('{','_').replace('}','_').replace('(','_').replace(')','_').replace(' ','_').replace('[','_').replace(']','_').replace('-','_')


def setExpression(layer,fieldName,expression):
    """
    Sets an expression on the layer for the fieldName specified.  
    Checks to make sure field is or type int or float to avoid issues with trying to set expressions on resource-backed fields.
    """
    fs = filter(lambda f:f.name == fieldName,layer.fields)

    if len(fs) == 0:
        log('d3script','Could not find field: '+ fieldName + ' for layer: ' + layer.name)
        return
    else:
        fs = fs[0]

    if (fs.type != int) and (fs.type != float):
        log('d3script','Field is not int or float type.  Cannot set expression.')
        return

    fs.setExpression(expression)



def simulateKeypress(key):
    """
    Simulates key presses by the user
    # For SHIFT prefix with +
    # For CTRL  prefix with ^
    # For ALT   prefix with %
    # ~	{~}	Send a tilde (~)
	# {!}	Send an exclamation point (!)
	# {^}	Send a caret (^)
	# {+}	Send a plus sign (+)
    # Backspace	{BACKSPACE} or {BKSP} or {BS}	Send a Backspace keystroke
    # Break	{BREAK}	Send a Break keystroke
    # Caps Lock	{CAPSLOCK}	Press the Caps Lock Key (toggle on or off)
    # Clear	{CLEAR}	Clear the field
    # Delete	{DELETE} or {DEL}	Send a Delete keystroke
    # Insert	{INSERT} or {INS}	Send an Insert keystroke
    # Cursor control arrows	{LEFT} / {RIGHT} / {UP} / {DOWN}	Send a Left/Right/Up/Down Arrow
    # End	{END}	Send an End keystroke
    # Enter	{ENTER} or ~	Send an Enter keystroke
    # Escape	{ESCAPE}	Send an Esc keystroke
    # F1 through F16	{F1} through {F16}	Send a Function keystroke
    # Help	{HELP}	Send a Help keystroke
    # Home	{HOME}	Send a Home keystroke
    # Numlock	{NUMLOCK}	Send a Num Lock keystroke
    # Page Down {PGDN}
    # Page Up	{PGUP}	Send a Page Down or Page Up keystroke
    # Print Screen	{PRTSC}	Send a Print Screen keystroke
    # Scroll lock	{SCROLLLOCK}	Press the Scroll lock Key (toggle on or off)
    # TAB	{TAB}	Send a TAB keystroke
    """

    shell.SendKeys(key)

def allLayersOfObject(layerSource):
    """
    Returns all nested layers of an object (usually track).
    """
        
    foundLayers = []
    
    for lay in layerSource:
        foundLayers.append(lay)
        if isinstance(lay, GroupLayer):
            foundLayers.extend(allLayersOfObject(lay.layers))

    return foundLayers


def getSectionTagNoteForTrackAndTime(track,time):
    """
    Return the cue tag and the note for a particular time
    """
    beat = track.timeToBeat(time)
    sectIndex = track.beatToSection(beat)
    sectStart = track.sections.getT(sectIndex)

    tagIndex = track.tags.find(sectStart,sectStart)
    if (tagIndex == -1) or (track.tags.getT(tagIndex) != sectStart):
        newTag = ""
    else:
        newTag = track.tags.getV(tagIndex).split()[1]

        
    noteIndex = track.notes.find(sectStart, sectStart)
    if (noteIndex == -1) or (track.notes.getT(noteIndex) != sectStart):
        newNote = ""
    else:
        newNote = track.notes.getV(noteIndex)

    return sectStart, newTag, newNote


def simulateKeydown(key):
    """
    Simulates a keydown event without a keyup event (for pressing SHIFT, CTRL, etc)
    """
    win32api.keybd_event(VK_CODE[key], 0,0,0)

def simulateKeyup(key):
    """
    Simulates a keyup event without a keydown event (for pressing SHIFT, CTRL, etc)
    """
    win32api.keybd_event(VK_CODE[key],0 ,win32con.KEYEVENTF_KEYUP ,0)


def getTrackWidget():
    """
    Return the track widget
    """
    return findWidgetByName('trackwidget')

def getSelectedLayers():
    """
    Get selected layers (if any) in the active track.
    """
    tw = getTrackWidget()
    if tw:
        return  tw.layerView.getSelectedLayers()


def showTimeBasedResultsWidget(title, columnNames, results):
    """
    Opens a table of results which are clickable to jump to a specific result
    result[-2] must be a track, and result[-1] a time in that track
    """
    def handleItemClick(item,colIndex,resultsWidget):
        print('track: '+str(item.values[-2]))
        print('time: '+str(item.values[-1]))
        time = item.values[-1]
        track = item.values[-2]
        fieldName = item.values[-3]
        lay = item.values[-4]

        if (time != None):
            cmd = TransportCMDTrackBeat()
            tm = d3.state.currentTransportManager
            trackTime = track.findBeatOfLastTag(track.timeToBeat(time))
            cmd.init(resultsWidget, tm, track, track.timeToBeat(time), track.transitionInfoAtBeat(trackTime))
            tm.addCommand(cmd)

        if (lay != None):
            oem = getTrackWidget().layerView.openEditorManager
            laySelect = LayerSelection([lay])
            oem.requestLayerEditor(laySelect)

        if (fieldName != None):
            closeAllLayerSequences()
            closeAllLayerSeparators()

            m=filter(lambda f:f.fieldSequence.name == fieldName,oem.openLayerEditors[laySelect].fieldWrappers)
            for f in m:
                f.field.parent.expand()
                f.field.valueBox.selectValue()
                if (f.fieldSequence.noSequence == False):
                    f.openSequence(True)


    columns = []
    for column in columnNames:
        columns.append(ColumnListViewColumn(column,column,None))

    resultWidget = Widget()
    resultWidget.add(TitleButton(title))

    listWidget = ColumnListView(columns,maxSize=Vec2(1500, 800) * d3gui.dpiScale)
    
    rows = map(lambda x:ColumnListViewItem(x),results)

    listWidget.items = rows
    listWidget.recalculateColumnSizes()
    listWidget.itemColumnClickedAction = (lambda item,colIndex: handleItemClick(item,colIndex,resultWidget))

    resultWidget.add(listWidget)
    resultWidget.arrangeVertical()
    resultWidget.computeAllMinSizes()
    d3gui.root.add(resultWidget)
    resultWidget.pos = (d3gui.root.size / 2) - (resultWidget.size/2)
    resultWidget.pos = Vec2(resultWidget.pos[0],resultWidget.pos[1]-100)


def standardModuleAbbreviation(modName):
    """
    Standard shortenings of Module Name types
    """
    if modName == "ColourAdjust":
        modAbbr = "[CAdj]"
    elif modName == "ChannelRouter":
        modAbbr = "[ChRt]"
    elif modName == "Gradient":
        modAbbr = "[Grad]"
    elif modName == "Notch":
        modAbbr = "[Ntch]"
    else:
        modAbbr = modName[0:4]

    return modAbbr

def blendModeToString(mode):
    """
    Converts blendmode to a human readable form
    """
    modes = {
        0.0 : 'Over',
        1.0 : 'Alpha',
        2.0 : 'Add',
        3.0 : 'Mult',
        4.0 : 'Mask',
        5.0 : 'MultF',
        6.0 : 'MultA',
        7.0 : 'PreMultA',
        8.0 : 'Scrn',
        9.0 : 'Ovrly',
        10.0 : 'Hard',
        11.0 : 'Soft',
        12.0 : 'Burn',
        13.0 : 'Dark',
        14.0 : 'Light',
        15.0 : 'Diff',
        16.0 : 'Excl',
        17.0 : 'Dodge',
        18.0 : 'HMix' }

    return modes[mode]

def closeAllLayerSeparators():
    ole = getTrackWidget().layerView.openEditorManager.openLayerEditors
    for x in ole:  
        v = ole[x].findDescendantsByType(CollapsableWidget)
        w = list(v)
        for i in w:
            i.collapse()


def closeAllLayerSequences():
    """Close all sequences in open editors"""
    ole = getTrackWidget().layerView.openEditorManager.openLayerEditors  
    for x in ole:    
        for f in ole[x].fieldWrappers:
            f.closeSequence()


def openLayerSequenceForProperty(p):
    closeAllLayerSequences()
    closeAllLayerSeparators()
    ole = getTrackWidget().layerView.openEditorManager.openLayerEditors

    if len(ole) == 0:
        tw = d3script.getTrackWidget()
        lv = tw.layerView
        lv.openEditorManager.requestLayerEditor(LayerSelection(lv.getSelectedLayers()))
        ole = getTrackWidget().layerView.openEditorManager.openLayerEditors  

    for x in ole: 
        m=filter(lambda f:f.fieldSequence.name == p,ole[x].fieldWrappers)
        for f in m:
            f.field.parent.expand()
            f.field.valueBox.selectValue()
            if (f.fieldSequence.noSequence == False):
                f.openSequence(True)


def openLayerEditorPropertyGroup(group):
    ole = getTrackWidget().layerView.openEditorManager.openLayerEditors
    closeAllLayerSeparators() 
    for x in ole:   
        v = ole[x].findDescendantsByType(CollapsableWidget)
        w = list(v)
        for i in w:
            if i.name == group:
                i.expand()


def guiSpacer(x,y):
    """
    create and return a spacer widget with the given sizes
    """
    spacer = Widget()
    spacer.minSize = Vec2(x * d3gui.dpiScale.x, y * d3gui.dpiScale.y)
    return spacer

def recursive_dir(obj, path):
    #if ((obj!=None) and (not isinstance(obj, (str,float,int,list,dict,set)))):
    if (obj!=None):
        for attr, val in obj.__dict__.iteritems():
            temp_path = path[:]
            temp_path.append(attr)
            recursive_dir(getattr(obj, attr), temp_path)
    else:
        print (path, "--->", obj)
        print("")

def load_scripts():
    """
    Sets up user scripting.  
    """
    global scripts
    global scriptMods

    #Stop d3/python from making pyc files while we load modules
    pycFlag = sys.dont_write_bytecode
    sys.dont_write_bytecode = True

    # We need to remove the keybindings to previous callback functions.  This seems... bad.
    d3gui.root.inputMap.clearMappings()
    
    openScriptMenu = findWidgetByName(SCRIPTMENUTITLE)
    if openScriptMenu:
        openScriptMenu.parent.close()

    scripts = []

    while len(scriptMods) > 0:
        mod = scriptMods.pop()
        try:
            if mod.SCRIPT_OPTIONS.has_key('del_callback'):
                mod.SCRIPT_OPTIONS['del_callback']()

            #Wonder if I should remove this?
        except:
            log('d3script','Error while reloading ' + mod.__name__ + '. Error thrown during deletion/reload.')

    scriptMods = []

    # Make sure scripts path exists
    if not os.path.exists(SCRIPTSFOLDER):
        os.mkdir(SCRIPTSFOLDER)

    # Add objects/pythonFile to the path
    if SCRIPTSFOLDER not in sys.path:
        sys.path.append(SCRIPTSFOLDER)

    possiblescripts = os.listdir(SCRIPTSFOLDER)
    
    for script in possiblescripts:
        scriptname = os.path.splitext(script)[0]
        try:
            foundMods = filter(lambda x: x.__name__ == scriptname,scriptMods)

            if len(foundMods) == 1:
                reload(foundMods[0])
            elif len(foundMods) == 0:
                scriptMods.append(importlib.import_module(scriptname))
            else:
                log('d3script','Found multiple existing ' + scriptname + ' in module cache. Not reloading.')
        except:
            log('d3script','Error while loading ' + scriptname + '. Skipping script.')


    for mod in scriptMods:
        register_script(mod)

    d3gui.root.add(ScriptMenu())

    #reset this pyc flag when we are done in case something relies on it
    sys.dont_write_bytecode = pycFlag



def open_scripts_menu():
    """
    opens a script menu if not already open
    """

    script_gui_menu = findWidgetByName(SCRIPTMENUTITLE)
    if not script_gui_menu:
        ScriptMenu()
    else:
        script_gui_menu.parent.moveToFront()


def register_script(mod):
    """
    This function has two responsiblities:
    - Check for version compatibility.  If that check clears, call the scripts entrypoint
    - If the script wants it, add the script to the Scripts menu

    Each script should define a dict called ``SCRIPT_OPTIONS`` which defines the following:
    ``SCRIPT_OPTIONS = {
        "minimum_version" : 17, # Min. compatible version
        "minimum_minor_version" : 1.3, # Min. minor version (when combined with major version)
        "maximum_version" : 20, # Max. compatible version - or None
        "maximum_minor_version" : 9.9, # Max. minor version  (when combined with major version) - or None
        "init_callback" : callbackfunc, # Init callback if version check passes
        "del_callback"  : delcallbackfunc, # Destructor in case we reload module
        "scripts" : [array of script entry points (see below)]
    }

    script = {
        "name" : "My Script #1", # Display name of script
        "group" : "Dan's Scripts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
        "binding" : "CTRL+SHIFT+P", # Keyboard shortcut
        "bind_globally" : True, # binding should be global
        "help_text" : "Tool Tip Text", #text for help system
        "callback" : callbackfunc, # function to call for the script
    }
    """
    
    global scripts

    #First check versioning
    try:
        script_options = mod.SCRIPT_OPTIONS

        if script_options['minimum_version'] > D3MAJORVERSION:
            log('d3script','Error while registering ' + mod.__name__ + '. Minimum version is newer than current.')
            return
        elif (script_options['minimum_version'] == D3MAJORVERSION) and (script_options['minimum_minor_version'] > D3MINORVERSION):
            log('d3script','Error while registering ' + mod.__name__ + '. Minimum minor version is newer than current.')
            return
        elif (script_options.has_key('maximum_version')) and (not script_options.has_key('maximum_minor_version')) and (script_options['maximum_version'] < D3MAJORVERSION):
            log('d3script','Error while registering ' + mod.__name__ + '. Maximum version is less than current.')
            return       
        elif (script_options.has_key('maximum_version')) and (script_options.has_key('maximum_minor_version')) and (script_options['maximum_version'] == D3MAJORVERSION) and (script_options['maximum_minor_version'] < D3MINORVERSION):
            log('d3script','Error while registering ' + mod.__name__ + '. Maximum minor version is less than current.')
            return        
    except:
            log('d3script','Error while registering ' + mod.__name__ + '. Uknown error during version check.')
            return    

    log('d3script', mod.__name__ + ' passed version check.')

    #Version checks out - call the init script
    try:
        if script_options.has_key('init_callback'):
            script_options['init_callback']()
    except:
        log('d3script','Error while registering ' + mod.__name__ + '. Error thrown during initialization.')
        return  

    log('d3script', mod.__name__ + ' passed initialization.')

    #process script callbacks
    for script in script_options['scripts']:
        if (not script.has_key('name')) or (not script.has_key('group')) or (not script.has_key('callback')):
            log('d3script','Error while registering ' + mod.__name__ + '. script missing parameter.')
            continue 


        if script.has_key('binding'):
            globalScope = script.get('bind_globally', False)
            helptext = script.get('help_text', script['name'])
            try:
                #ignoring global scope for now. FIX FIX FIX - This is ugly
                d3gui.root.inputMap.add(script['callback'], script['binding'], helptext)
            except:
                log('d3script','Error while registering ' + mod.__name__ + '. Could not make script binding.')
            
        if script not in scripts:
            log('d3script','Adding script ' + script['name'] + ' to scripts list.')
            scripts.append(script)
    
    def script_sort(val):
        val['group'] + '.' + val['name']
    
    scripts.sort(key=script_sort)


class ScriptButton(Widget):
    isStickyable = True

    def __init__(self):
        global scripts

        Widget.__init__(self) 
        bt = TitleButton(SCRIPTBUTTONTITLE)
        bt.clickAction.add(open_scripts_menu)
        self.arrangeHorizontal()
        bt.canClose = False
        bt.border = Vec2(6,6)
        self.border = Vec2(6,6)
        self.pos = Vec2(0,50)
        self.add(bt)


class ScriptMenu(Widget):
    isStickyable = True

    def __init__(self):
        global scripts
        
        Widget.__init__(self)   
        self.titleButton = TitleButton(SCRIPTMENUTITLE)
        self.add(self.titleButton)
        bt = Button('Reload Scripts',load_scripts)
        bt.border = Vec2(0,10)

        self.add(bt)
        self.pos = Vec2(d3gui.root.size.x - 300, 50)
        self.arrangeVertical()
        self.minSize = Vec2(1000,800)
        self.scriptsCW = CollapsableWidget('Scripts','Scripts')
        self.add(self.scriptsCW)

        currentGroup = None
        groupWidget = None

        # Add scripts to menu
        for index, script in enumerate(scripts):
            if (currentGroup != script['group']):
                groupWidget = CollapsableWidget(script['group'],script['group'])
                currentGroup = script['group']
                self.scriptsCW.add(groupWidget)

            bt = Button(script['name'],script['callback'])
            bt.border = Vec2(0,12)

            #self.buttons.append(bt)
            groupWidget.add(bt)

        d3gui.root.add(self)
        self.titleButton.toggleSticky()


load_scripts()