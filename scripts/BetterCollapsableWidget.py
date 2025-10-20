import d3 import *

originalCW = CollapsableWidget

class BetterCollapsableWidget(originalCW):
    
    def __init__(self):
        originalCW.__init__(self)
        
    @binding(MouseClick, Mouse.Right)
    def onRightClick(self):
        print('Hello')


CollapsableWidget = BetterCollapsableWidget
    
    