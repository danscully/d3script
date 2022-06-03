import d3script

def init_scripts():
    d3script.log('testScript','init_scripts called')

def scriptfunc():
    d3script.log('testScript','the scriptfunc1')

def scriptfunc2():
    d3script.log('testScript','the scriptfunc2')
    
def scriptfunc3():
    d3script.log('testScript','the scriptfunc3')

def scriptfunc4():
    d3script.log('testScript','the scriptfunc4')

SCRIPT_OPTIONS = {
    "minimum_version": 17,  # Min. compatible version
    "minimum_minor_version": 1.3, # Min. minor version (when combined with major version)
    "maximum_version": None,  # Max. compatible version - or None
    "maximum_minor_version": None,# Max. minor version  (when combined with major version) - or None
    "init_callback": init_scripts,  # Init callback if version check passes
    "scripts": [
        {
            "name": "My Script #1",  # Display name of script         
            "group": "Dan's Scripts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding": "KeyStroke,Ctrl,3",  # Keyboard shortcut
            "bind_globally": True,  # binding should be global
            "help_text": "Tool Tip Text",  # text for help system
            "callback": scriptfunc,  # function to call for the script
        },
        {
            "name": "My Script #2",  # Display name of script         
            "group": "Dan's Scripts", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding": "KeyStroke,Ctrl,4",  # Keyboard shortcut
            "bind_globally": True,  # binding should be global
            "help_text": "Tool Tip Text",  # text for help system
            "callback": scriptfunc2,  # function to call for the script
        },
        {
            "name": "My Script #3",  # Display name of script         
            "group": "AnotherGroup", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding": "KeyStroke,Ctrl,5",  # Keyboard shortcut
            "bind_globally": True,  # binding should be global
            "help_text": "Tool Tip Text",  # text for help system
            "callback": scriptfunc3,  # function to call for the script
        }
    ]
}

