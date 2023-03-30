# d3script
<img src="sampleimages/menu.PNG" align="right" width="200px" />
This is an unofficial scripting framework for external scripts in the d3/disguise media server.  Included is a loading mechanism, a menu UI, and a "standard library" of useful calls.  This project is completely unsupported by Disguise and myself and sure to get support to throw your ticket in the trash.  I recommend pairing it with a Streamdeck (or Loupedeck etc) and Bitfocus Companion to give yourself physical buttons to trigger scripts (see included sample Companion config).  I update this repo periodically as I make new scripts and improvements, but there is no formal release schedule or versioning.  There also many assumptions in the scripts provided.  For example, a script may require an existing layer with a specific name, etc.  Its always good to read the code looking for gotchas, and never use in Production unless you are comfortable owning the consequences.  As a rule, I only run these scripts on Editors, leaving the Director "clean" of my interference.

# What d3Script does
- Scans a folder (hardcoded to "./Scripts") for modules (.py files or other more complex modules) and loads what it finds. 

- Processes a required dictionary in each loaded module with the name `SCRIPT_OPTIONS`.  This dictionary specifies min and max compatible versions, and optional initialization and destruction callbacks.  The loader checks for compatible versions and will only proceed if it is compatible.  

- This dictionary also has a "scripts" dictionary which describe available entrypoints.  Each "script" consists of a name, a group (for organizing in the Script Menu widget), a callback function, and an optional binding.  The loader takes each "script", and creates a widget with a collapsible panel for each group, and a button for each script on that panel.  If there is a binding, it also sets up that as well (its a bit of a hack at the moment).  Pressing the button or optional binding triggers the callback function.  That function could either do work or open another widget, depending on the scripter's goals.

- The loader also adds a "Scripts" Widget to the top right of the UI, pinned open by default. There is also an option to "Reload Scripts" on the Scripts Menu widget.  Pressing that calls the destructor callback on existing script modules, and rescans the scripts folder for new script modules, and reloads existing script modules.

- Provides a set of utility functions that are useful in making scripts for D3, such as getting the track widget, returning the selected layers in the timeline, etc.

# How to use it
To use, put 'd3script.py' at the root of the project and in the Disguise Python Console (Alt-C) type:
"sys.path.append('./');import d3script",and hit enter.  This will add the project root onto the Python search path, and load the d3script standard library module.

<img src="sampleimages/ConsoleLoad.PNG" width="600px" />

For the included scripts, make a folder in the project root called "scripts".  D3Script will automatically load any files in there when it is iniitially imported.  You can also rescan and reload this folder from the "Scripts" menu.


# What the included scripts do
There are currently four groups of scripts (gathered into four files) included in this release:

- FieldShortcuts.py
Creates keyboard shortcuts for the most common layer editor properties.  For example, if you have a layer editor open, pressing Ctrl-Shift-t will put keyboard focus on the Brightness field if the property is not animated, or open the keyframe editor for the field if it is animated.  It will also minimize all other field groups.  It's basically an attempt to recreate After Effects style shortcut keys for layer properties.  You can see all the keyboard shortcuts at the end of the file.

- SmartRename.py
Smart Rename will let you rename a file based on the filename of the media, and also appends the module, blendmode, and mapping ("Alpha" as a blendmode and "Video" as a module are not added because I assume them as a default).  This script assumes anything from the first occurance of "[" onward is automatically updated data and will overwrite that in a name.  This script also will not touch layers with "EXPSRC" in the name as it assumes that layer is the source of an expression link and will be broken by renaming it.

- ParentLayers.py
This script provides a dialog to quickly expression link multiple layers.  Select two or more layers, run this script, and you will get a dialog allowing you to choose the parent layer, and toggle which fields should be linked.  There are also buttons to select all Color, Transform(e.g. scale/position/rotation), and Crop fields, respectively.  The parent layers gets renamed with a "EXPSRC" appended.  You can change that in the code, but I use it to know I shouldn't rename the layer or else I'll break the expression links which are name based. I built this because I often want to expression link two or more layers for all transform properties.  This lets me do it in three keystrokes.

- EosLink.py
If you are using an ETC Eos based console, and need to manipulate a cue list for triggering d3, this script allows you to create and delete cues from Disguise.  Basically, running the "Create Cue..." script will let you create a cue in your cue list with the cue number and section note for the section at the current playhead position.  "Delete Cue..." will do the same, but delete a cue.  To use, you must set up an OSC device, and select it in the Create/Delete dialogs.  It also requires specifying the Eos User and Cuelist.  Those choices are remembered. 

- TrackTools.py
Track tools provide scripts to Duplicate, Split, Trim, and Move selected layers relative to the position of the playhead.  It also provides the ability to note/tag a section with the playhead at any point in that section, as well as the ability to tell you Section Timing Info.  It also provides the ability to import a Layer from the Layer Library by name. Combining this with the d3script.callScript() function lets you, say, create a key on a Streamdeck which will import a specific layer or group of layers onto the timeline.  I use this often when I see patterns of layers being used - such as file sets that always get played together ("There's a channel 1 and 2 to play...", or sometimes I'll have a hotkey that adds a layer with a "blob" that I can use to mask/shape content.  This file also provides a function to de-sequence all fields on selected layers, useful if you are upgrading an older show file where you have fields with 1 or 0 keyframes that you want desequenced.

- StatusWidget.py
Creates a one-stop-shop for status, including Up/Down/Hold status, transport Engaged status, Editor Locked/Independent status, and LTC status.  Also creates keyboard shortcuts and callable functions to manipulate those settings.

- PresetManager.py
Creates a preset system.  You can record a value(s) or keyframes as a preset and apply it with a button click, or with a script function call.  See code for "special" values.

- EncoderLink.py
Provides functions that are useful when combined with an external encoder, like the knobs on a Streamdeck plus.  

# Combining with a control surface
You can use these scripts either by the keyboard shortcuts they define, or by clicking on a button in the scripts menu.  You can also call them remotely.  To do that, set a "telnetConsolePort" in Machine Settings.  This will allow you to connect via TCP/telnet. From there, call the following to trigger a script.
> d3script.callScript(*filenameinquoteswithoutpy*,*functionnameinquotes*,*optionalstringparameterinquotes*)

That function also supports an optional string parameter if the function requires a value to be passed to it, like 
> d3script.callScript('TrackTools','importLayerByName','MyLayer')

I use a streamdeck with Bitfocus Companion, which can send string commands over telnet.




# Warnings and Known Issues
- You'd be crazy to use these in production.  But I do, so......
- Like I said above, you will probably get the stink eye from support if you are using these.  I only ever load themn onto an editor machine to reduce the surface area of possible problems.  Generally, the things that manipulate the gui (like the fieldshortcuts) are safer than scripts that manipulate data (like the renamer or track tools).  
- The interface, functions, and methods that make up 'd3script' are not stable and may change from release to release.  I also don't have a release schedule or versioning system yet, so good luck with that.
- Sometimes to get the keyboard shortcuts to work after an initial load, I need to click into the background of the gui.  Need to fix that.
- SOmetimes the "Scripts" menu button disappears.  Typing "d3script.load_scripts()" into the console will restore it.


# Todo
- Create a context menu for each script button to allow for inspection of binding, etc.
- Solve binding issue
- Move OSC functions into library
- Remove unnecessary imports from scripts
- Implement real version controls and release process


Created by Dan Scully (with copious amounts of copy and paste from others)
dan@danscully.com
