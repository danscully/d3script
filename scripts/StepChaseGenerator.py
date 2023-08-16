# EosLink.py


from d3 import *
import d3script


def initCallback():
    d3script.log('StepChaseGenerator','Initialized')

def setupChaseGenerator():
    op = Undoable('Setup Chase Generator')
    
    settingsLayer = d3script.createLayerOfTypeOnCurrentTrack('Web')
    if settingsLayer == None:
        d3script.log('StepChaseGenerator','Could not Web module for settings')
        return
    
    sectStart,tag,note =  d3script.getSectionTagNoteForTrackAndTime(state.track,state.player.tRender)

    settingsLayer.setExtents(sectStart,sectStart+30.0)
    settingsLayer.name = '[StpC] Settings'

    outputLayer = d3script.createLayerOfTypeOnCurrentTrack('Web')
    if settingsLayer == None:
        d3script.log('StepChaseGenerator','Could not Web module for output')
        return
    
    outputLayer.setExtents(sectStart,sectStart+30.0)
    outputLayer.name = '[StpC] Outputs'

    # Setup settings layer labels and expressions
    d3script.getFieldFromLayerByName(settingsLayer, 'Name 1').sequence.setString(0,'runt')
    d3script.getFieldFromLayerByName(settingsLayer, 'Name 2').sequence.setString(0,'numsteps')
    d3script.getFieldFromLayerByName(settingsLayer, 'Name 3').sequence.setString(0,'stept')
    d3script.getFieldFromLayerByName(settingsLayer, 'Name 4').sequence.setString(0,'upt')
    d3script.getFieldFromLayerByName(settingsLayer, 'Name 5').sequence.setString(0,'holdt')
    d3script.getFieldFromLayerByName(settingsLayer, 'Name 6').sequence.setString(0,'downt')
    d3script.getFieldFromLayerByName(settingsLayer, 'Name 7').sequence.setString(0,'lowv')
    d3script.getFieldFromLayerByName(settingsLayer, 'Name 8').sequence.setString(0,'highv')

    d3script.getFieldFromLayerByName(settingsLayer, 'Value 1').sequence.keys[0].v = 0.0
    d3script.getFieldFromLayerByName(settingsLayer, 'Value 2').sequence.keys[0].v = 8.0
    d3script.getFieldFromLayerByName(settingsLayer, 'Value 3').sequence.keys[0].v = 1.0
    d3script.getFieldFromLayerByName(settingsLayer, 'Value 4').sequence.keys[0].v = 0.1
    d3script.getFieldFromLayerByName(settingsLayer, 'Value 5').sequence.keys[0].v = 0.8
    d3script.getFieldFromLayerByName(settingsLayer, 'Value 6').sequence.keys[0].v = 0.1
    d3script.getFieldFromLayerByName(settingsLayer, 'Value 7').sequence.keys[0].v = 0.1
    d3script.getFieldFromLayerByName(settingsLayer, 'Value 8').sequence.keys[0].v = 1.0

    d3script.setExpression(settingsLayer,'Value 1','runt=uptime')
    d3script.setExpression(settingsLayer,'Value 2','numsteps=self')
    d3script.setExpression(settingsLayer,'Value 3','stept=self')
    d3script.setExpression(settingsLayer,'Value 4','upt=self')
    d3script.setExpression(settingsLayer,'Value 5','holdt=self')
    d3script.setExpression(settingsLayer,'Value 6','downt=self')
    d3script.setExpression(settingsLayer,'Value 7','lowv=self')
    d3script.setExpression(settingsLayer,'Value 8','highv=self')
    
    # Setup output layer labels and expressions
    d3script.getFieldFromLayerByName(outputLayer, 'Name 1').sequence.setString(0,'step1value')
    d3script.getFieldFromLayerByName(outputLayer, 'Name 2').sequence.setString(0,'step2value')
    d3script.getFieldFromLayerByName(outputLayer, 'Name 3').sequence.setString(0,'step3value')
    d3script.getFieldFromLayerByName(outputLayer, 'Name 4').sequence.setString(0,'step4value')
    d3script.getFieldFromLayerByName(outputLayer, 'Name 5').sequence.setString(0,'step5value')
    d3script.getFieldFromLayerByName(outputLayer, 'Name 6').sequence.setString(0,'step6value')
    d3script.getFieldFromLayerByName(outputLayer, 'Name 7').sequence.setString(0,'step7value')
    d3script.getFieldFromLayerByName(outputLayer, 'Name 8').sequence.setString(0,'step8value')
    
    baseText = """stepSTEPINDEXvalue = if(
                    (runt + STEPINDEX * stept)%(numsteps*stept) < upt,
                    lerp(highv,lowv,(upt - (runt + STEPINDEX * stept)%(numsteps*stept))/upt),
                    if(
                       (runt + STEPINDEX * stept)%(numsteps*stept) <= (upt+holdt),
                       highv,
                       if(downt > 0, lerp(highv,lowv,clamp(((runt + STEPINDEX * stept)%(numsteps*stept) - holdt - upt)/downt,0,1)), lowv)
                    )
                )"""
    

    d3script.setExpression(outputLayer,'Value 1',baseText.replace('STEPINDEX','1'))
    d3script.setExpression(outputLayer,'Value 2',baseText.replace('STEPINDEX','2'))
    d3script.setExpression(outputLayer,'Value 3',baseText.replace('STEPINDEX','3'))
    d3script.setExpression(outputLayer,'Value 4',baseText.replace('STEPINDEX','4'))
    d3script.setExpression(outputLayer,'Value 5',baseText.replace('STEPINDEX','5'))
    d3script.setExpression(outputLayer,'Value 6',baseText.replace('STEPINDEX','6'))
    d3script.setExpression(outputLayer,'Value 7',baseText.replace('STEPINDEX','7'))
    d3script.setExpression(outputLayer,'Value 8',baseText.replace('STEPINDEX','8'))


SCRIPT_OPTIONS = {
    "minimum_version" : 21, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Setup Chase Generator", # Display name of script
            "group" : "Chase Generator", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Setup Chase Generator", #text for help system
            "callback" : setupChaseGenerator, # function to call for the script
        }
        ]

    }
