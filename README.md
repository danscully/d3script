# d3script
<img src="sampleimages/menu.PNG" align="right" width="200px" />
This is an unofficial scripting framework for external scripts in the d3/disguise media server.  Included is a loading mechanism, a menu UI, and a "standard library" of useful calls.  This project is completely unsupported by Disguise and myself and sure to get support to throw your ticket in the trash.  I recommend pairing it with a Streamdeck (or Loupedeck etc) and Bitfocus Companion to give yourself physical buttons to trigger scripts (see included sample Companion config).  I update this repo periodically as I make new scripts and improvements, but there is no formal release schedule or versioning.  There also many assumptions in the scripts provided.  For example, a script may require an existing layer with a specific name, etc.  Its always good to read the code looking for gotchas, and never use in Production unless you are comfortable owning the consequences.  As a rule, I only run these scripts on Editors, leaving the Director "clean" of my interference.
<br clear="right" />

# What d3Script does
- Scans a folder (hardcoded to "./Scripts") for modules (.py files or other more complex modules) and loads what it finds. 

- Processes a required dictionary in each loaded module with the name `SCRIPT_OPTIONS`.  This dictionary specifies min and max compatible versions, and optional initialization and destruction callbacks.  The loader checks for compatible versions and will only proceed if it is compatible.  

- This dictionary also has a "scripts" dictionary which describe available entrypoints.  Each "script" consists of a name, a group (for organizing in the Script Menu widget), a callback function, and an optional binding.  The loader takes each "script", and creates a widget with a collapsible panel for each group, and a button for each script on that panel.  If there is a binding, it also sets up that as well (its a bit of a hack at the moment).  Pressing the button or optional binding triggers the callback function.  That function could either do work or open another widget, depending on the scripter's goals.

- The loader also adds a "Scripts" Widget to the top right of the UI, pinned open by default. There is also an option to "Reload Scripts" on the Scripts Menu widget.  Pressing that calls the destructor callback on existing script modules, and rescans the scripts folder for new script modules, and reloads existing script modules.

- Provides a set of utility functions that are useful in making scripts for D3, such as getting the track widget, returning the selected layers in the timeline, etc.  Also has a useful function "d3script.dumpObject()" which will list out the type of each property on a d3 internal object and also the call signature of any methods on that object.  Read through the code for more info on what functions are available.

# How to use it
To use, put 'd3script.py' at the root of the project and in the Disguise Python Console (Alt-C) type:
"sys.path.append('./');import d3script",and hit enter.  This will add the project root onto the Python search path, and load the d3script standard library module.

<img src="sampleimages/ConsoleLoad.PNG" width="600px" />

For the included scripts, make a folder in the project root called "scripts".  D3Script will automatically load any files in there when it is iniitially imported.  You can also rescan and reload this folder from the "Scripts" menu.


# What the included scripts do
Here is an overview of the scripts included in this release:

## BetterCueList
This script patches the existing Cue List widget so that if a valid cue number is entered in the search box, only exact matches are shown, or if no exact match exists in a track, the immediately preceding cue is shown (like the "Out of Order Sync" behavior in Eos)

## DeFlash
This script will stop the transport control buttons from flashing, and instead have them highlight in a color.

## Dashboard
<img src="sampleimages/Dashboard.PNG" align="right" width="200px" />
Might be best explained as an "Open Module" without time.  Lets you arrow most editor fields into one widget, as well as "newstyle" expression variables (those defined in an expressions device on variable layer module).  Optionally, by right-clicking on the field, you can add a "Green Match" value, which will add a green highlight if it matches the value.  Alternatively, you can specify min/max values and have that highlight show as a bar graph.

<br clear="right" />

## EncoderLink
Provides functions that are useful when combined with an external encoder, like the knobs on a Streamdeck plus.  Look at code and the Companion config for more information.

## EosLink
<img src="sampleimages/EosLink.PNG" align="right" width="200px" />
Ability to interact with an Eos lighting console.  Can create, delete, and retrigger cues in an Eos cuelist.  The create and delete widgets populate with the cue (e.g. tag) and label (e.g. note) for the current section.  Requires an OSC device to be setup for Eos.  The first time you run an EosLink script you should choose the OSC device from the dropdown list, and choose the user and cuelist defaults to use.

<br clear="right" />


## FieldShortcuts
<img src="sampleimages/fieldshortcuts.PNG" align="right" width="400px" />
Creates keyboard shortcuts for the most common layer editor properties.  For example, if you have a layer editor open, pressing Ctrl-Shift-t will put keyboard focus on the Brightness field if the property is not animated, or open the keyframe editor for the field if it is animated.  It will also minimize all other field groups.  It's basically an attempt to recreate After Effects style shortcut keys for layer properties.

<br clear="right" />


## LayerColorManager
<img src="sampleimages/LayerColorManager.PNG"/>
Allows you to control the UI colors of layers on the timeline.  You can set different criteria based on layer name, status, module type, and module category.  Layers are matched based on the order of the criteria, starting at the top option, until a match is found.

<br clear="right" />


## LayerEditorImprovements
<img src="sampleimages/LayerEditorImprovements.PNG" align="right" width="300px" />
Pins the max height of any open layer editor to the distance between the state bar and the top of the timeline track.  Also, pins the layer editor to the left edge of the screen.  Opening multiple layer editors will tile them out side by side from left to right. THIS IS HIGHLY INVASIVE AND EXPERIMENTAL. I HAVE NOT THOROUGHLY TESTED THIS YET.

<br clear="right" />

## Parenting
<img src="sampleimages/Parenting.PNG" align="right" width="400px" />
The Parent Layers script lets you automatically create expressions linking from multiple layers(children) to one primary layer(parent).  With multiple layers selected, run the script, and at the top choose a layer to be a parent.  You can then either check specific fields they have in common, or use the buttons to select groups of common layers.  The parent layer will have "EXPSRC" appended to its name since expressioning is currently based on names and will break if the parent is renamed.

<br clear="right" />


## PresetManager
<img src="sampleimages/PresetManager.PNG" align="right" width="600px" />
The Preset Manager allows for the saving and recall of any layer editor property.  You can either use the buttons to save common sets of properties, or instead save the all the open sequences of the current layer editor.  You can also choose whether to save timing information or not.  Presets with timing information will use that timing info to animate properties, and will turn on sequencing on a property if applied to it.  You can right click on a preset to edit, rename, or delete it.  There are wildcards that can be manually editted into the preset definitions that allow you to reference the current/next section start times, as well as the value of the sequence at the previous/last keyframe, current/next section, and the playhead (see code for more information).  There is also a convenience script to allow you to apply presets by name (by connecting it do a streamdeck button, for example).  Uses include creating buttons to change blend modes or mappings, or recreate a complicated set of keyframes (e.g. a lightning effect).

<br clear="right" />


## ScreenConfigHelper.py
<img src="sampleimages/ScreenConfig.PNG" align="right" width="200px" />
The Screen Config Helper aids in and speeds up the creation of Animate Object presets.  It requires two objects to be created before use: "\_sctemplate" is a animate object preset config that must contain the objects you want recorded when using the Helper, and "SCENERYMOVER" needs to be a layer in your current timeline where configs will be placed.   

<br clear="right" />


## StatusWidget.py
<img src="sampleimages/StatusWidget.PNG" />
Creates a one-stop-shop for status, including Up/Down/Hold status, transport Engaged status, Editor Locked/Independent status, and LTC status.  Also creates keyboard shortcuts and callable functions to manipulate those settings.
<br />
<br />
<img src="sampleimages/statusWidgetShortcuts.PNG" width="600px" />

<br />

## StepChaseGenerator.py
<img src="sampleimages/Stepchase.PNG" align="right" width="400px" />
This script will create two web modules on your timeline to implement simple step-based chases. The first has a series of parameters like "number of steps", "max level", "min level", "up time", "hold time", etc that you can set to control the effect.  The second module contains 8 possible step values that create expression variables you can reference in the layers you wish to step.  Everything is currently based on the "upTime" expression global so the chase is not deterministic (e.g. won't always start in the same place).  But in the settings module you can use the frame counter of another layer as a timer if you wish to make it deterministic to the start of a section. NOTE: SHOULD BE REBUILT TO BEHAVE BETTER WITH THE EXPRESSION CHANGES IN CURRENT D3 RELEASES.

<br clear="right" />

## TimelineImprovements.py
<img src="sampleimages/TimelineImprovements.PNG" align="right" width="600px" />
Partially overrides the drawing of the track/timeline in order to add markers on layers to indicate the location of keyframes (if any) for that layer.  Also changes the "selected layer" drawing to instead be a bright yellow outline because I find the UI conventions between "selected layer" and "layer with editor opened" to be confusing.

<br clear="right" />

## TimeTool.py
The Timetool script can insert time at the current playhead render position. I built this to automate adding a known number of seconds to the timeline repeatedly (I always make new cues 30 seconds long, for example).  Time should be entered into the dialog (or passed as a string to the script if calling it directly) as "seconds.frames".  It only understands seconds and frames - not full timecode values.  WARNING: DOES NOT BEHAVE WELL WITH AUDIO/QUANTIZED TRACKS.  ALSO ASSUMES 30/60FPS BUT THAT WILL HOPEFULLY BE FIXED IN THE NEXT RELEASE.  SUPER EXPERIMENTAL AND TOUCHES EVERY PART OF YOUR TRACK/TIMELINE.  TEST IN YOUR SETUP BEFORE USING.

<br />

## TrackTools.py
<img src="sampleimages/TrackTools.PNG" align="right" width="200px" />
Track tools provide scripts to Duplicate, Split, Trim, and Move selected layers relative to the position of the playhead.  It also provides the ability to note/tag a section with the playhead at any point in that section, as well as the ability to tell you Section Timing Info.  It also provides the ability to import a Layer from the Layer Library by name. Combining this with the d3script.callScript() function lets you, say, create a key on a Streamdeck which will import a specific layer or group of layers onto the timeline.  I use this often when I see patterns of layers being used - such as file sets that always get played together ("There's a channel 1 and 2 to play...", or sometimes I'll have a hotkey that adds a layer with a "blob" that I can use to mask/shape content.  This file also provides a function to de-sequence all fields on selected layers, useful if you are upgrading an older show file where you have fields with 1 or 0 keyframes that you want desequenced.  Additionally, there is a "Smart Merge Section" option that lets you merge the current section and deletes the cue tag and note at the head of the section being merged.  Other scripts in this group include "Find Broken Expressions", "Search Track" (find media/mappings/layers by name), "Show Section Timing Info" (what each layer is doing in a section), and "Show Layer Timing Info" (what a selected layer is doing through a track) - clicking on a result from one of these scripts will open the layer in question at the time referenced.  Also included is a renaming script that is smart about abbreviations and adding mappings to the name.  

<br clear="right" />

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


Created by Dan Scully (with copious amounts of copy and paste from others)
dan@danscully.com
