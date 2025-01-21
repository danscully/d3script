# StepChaseGenerator.py


from d3 import *
import d3script


def initCallback():
    d3script.log('StepChaseGenerator','Initialized')

def setupChaseGenerator(prefix):
    op = Undoable('Setup Chase Generator')
    
    if (d3script.D3MAJORVERSION >= 30):
        expLay = d3script.createLayerOfTypeOnCurrentTrack('ExpressionVariables')
        newVars = []
        if expLay == None:
            d3script.log('StepChaseGenerator','Could not Expression module for settings')
            return
    
        sectStart,tag,note = d3script.getSectionTagNoteForTrackAndTime(state.track,state.player.tRender)
        expLay.setExtents(sectStart,sectStart+30.0)
        expLay.name = '[Expr] ' + prefix
        
        # Create variables
        def addExpressionVariable(vName, expType=ExpressionVariable.FloatType):
            ev = ExpressionVariable()
            ev.name = vName
            ev.type = expType
            expLay.moduleConfig.container.variables.append(ev)
            return ev
            
        newVars.append(addExpressionVariable(prefix+'runt'))
        newVars.append(addExpressionVariable(prefix+'steps'))
        newVars.append(addExpressionVariable(prefix+'stept'))
        newVars.append(addExpressionVariable(prefix+'up'))
        newVars.append(addExpressionVariable(prefix+'hold'))
        newVars.append(addExpressionVariable(prefix+'down'))
        newVars.append(addExpressionVariable(prefix+'low'))
        newVars.append(addExpressionVariable(prefix+'high'))
          
        for i in range(0,8):
            stepName = prefix+'step'+str(i+1)
            stepVar = addExpressionVariable(stepName,ExpressionVariable.FunctionType)

  
        markDirty(expLay.moduleConfig)
        
        
        def fieldsChangedCB():
            
            if len(expLay.fields) < 16:
                return
            
            d3script.getFieldFromLayerByName(expLay,prefix+'runt').sequence.keys[0].v = 0.0
            d3script.getFieldFromLayerByName(expLay,prefix+'steps').sequence.keys[0].v = 8.0
            d3script.getFieldFromLayerByName(expLay,prefix+'stept').sequence.keys[0].v = 1.0
            d3script.getFieldFromLayerByName(expLay,prefix+'up').sequence.keys[0].v = 0.1
            d3script.getFieldFromLayerByName(expLay,prefix+'hold').sequence.keys[0].v = 0.8
            d3script.getFieldFromLayerByName(expLay,prefix+'down').sequence.keys[0].v = 0.1
            d3script.getFieldFromLayerByName(expLay,prefix+'low').sequence.keys[0].v = 0.1
            d3script.getFieldFromLayerByName(expLay,prefix+'high').sequence.keys[0].v = 1.0

            d3script.setExpression(expLay,prefix+'runt','uptime')

    
            baseText = """if((PREFIXrunt + STEPINDEX * PREFIXstept)%(PREFIXsteps*PREFIXstept) < PREFIXup,
                            lerp(PREFIXhigh,PREFIXlow,((PREFIXup) - (PREFIXrunt + STEPINDEX * PREFIXstept)%(PREFIXsteps*PREFIXstept))/PREFIXup),
                            if((PREFIXrunt + STEPINDEX * PREFIXstept)%(PREFIXsteps*PREFIXstept) <= (PREFIXup+PREFIXhold),
                                PREFIXhigh,
                                if(PREFIXdown > 0, 
                                    lerp(PREFIXhigh,(PREFIXlow),
                                    clamp(((PREFIXrunt + STEPINDEX * PREFIXstept)%(PREFIXsteps*PREFIXstept) - PREFIXhold - PREFIXup)/PREFIXdown,0,1)), 
                                    PREFIXlow
                                )
                            )
                          )
                """
    
            baseText = baseText.replace(' ','').replace('PREFIX',prefix).replace('\n','').replace(')',')\n')
            if baseText[-1] == '\n':
                baseText = baseText[:-1]
                
            for i in range(0,8):
                stepName = prefix+'step'+str(i+1)
                d3script.getFieldFromLayerByName(expLay,stepName).sequence.keys[0].s = baseText.replace('STEPINDEX',str(i))
            
        expLay.onFieldsChangedAction.add(fieldsChangedCB)
  
def chasePopup():
    """Open a popup menu"""
    
    menu = PopupMenu('Setup Chase:')
    menu.add(TextBox('Chase name must be unique in its section of track'))
    nameStem = "Chase"
    menu.editItem('Chase Name:', nameStem, setupChaseGenerator)
    menu.pos = (d3gui.root.size / 2) - (menu.size/2)
    menu.pos = Vec2(menu.pos[0],menu.pos[1]-100)

    d3gui.root.add(menu)
    menu.contents.findWidgetByName('Setup Chase:').textBox.focus = True
    
          
SCRIPT_OPTIONS = {
    "minimum_version" : 21, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Setup Chase Generator", # Display name of script
            "group" : "Chase Generator", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Setup Chase Generator", #text for help system
            "callback" : chasePopup, # function to call for the script
        }
        ]

    }
