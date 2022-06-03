# d3script
This is the beginnings of a system to manage the loading and UI for external scripts in the d3/disguise media server.  This project is completely unsupported and sure to get support to throw your ticket in the trash.  Good luck!

# How to use it
To use, put d3script.py somewhere on the d3 Python sys.path.  Or, put it at the root of the project and in the Disguise Python Console (Alt-C) type:
sys.path.append('./')
This will add the project root onto the Python search path.

# What is does
- Scans a folder (hardcoded to "./objects/Scripts") for modules (.py files or other more complex modules) and loads what it finds. 

- Processes a required dictionary in each loaded module with the name `SCRIPT_OPTIONS`.  This dictionary specifies min and max compatible versions, and optional initialization and destruction callbacks.  The loader checks for compatible versions and will only proceed if it is compatible.  See the example script `testScript.py` for more info on this dictionary.

- This dictionary also has a "scripts" dictionary which describe available entrypoints.  Each "script" consists of a name, a group (for organizing in the Script Menu widget), a callback function, and an optional binding.  The loader takes each "script", and creates a widget with a collapsible panel for each group, and a button for each script on that panel.  If there is a binding, it also sets up that as well (its a bit of a hack at the moment).  Pressing the button or optional binding triggers the callback function.  That function could either do work or open another widget, depending on the scripter's goals.

- The loader also adds a "Scripts" button to the state bar at the top. That button opens the Scripts Menu widget.  

There is also an option to "Reload Scripts" on the Scripts Menu widget.  Pressing that calls the destructor callback on existing script modules, and rescans the scripts folder for new script modules, and reloads existing script modules.

I've also thrown in a few utility functions but that's really just a gesture towards a useful standard library.

# Todo
- Add a launch_script() function to allow for remote telnet execution of loaded scripts.
- Create a context menu for each script button to allow for inspection of binding, etc.
- Start to think about useful api / gui wrappers that could be standardized.
- Convert my main helpers.py scripts into this format to "eat my own dogfood".

Created by Dan Scully (with copious amounts of copy and paste from others)
dan@danscully.com
