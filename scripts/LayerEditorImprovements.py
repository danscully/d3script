from d3 import *
import d3script

def initCallback():
    d3script.log("LayerEditorImprovements","LayerEditorImprovements Loaded")

def headerLinker(header, forwardActionTo):
    if not forwardActionTo:
        return

    def makeLinkToAction(*args):
        if hasattr(forwardActionTo, 'headerMakeLinkToAction'):
            forwardActionTo.headerMakeLinkToAction(*args)
        return makeLinkToAction

    header.makeLinkToAction.add(makeLinkToAction)




def loadImprovements():
    ole = d3script.getTrackWidget().layerView.openEditorManager.openLayerEditors
    if (len(ole) != 2):
        d3script.log('LayedEditorImprovements','Must have one regular layer and one multiselection open.')
    else:
        for le in ole.values():
            if len(le.layers) == 1:
                leType = type(le)
                oldPopulate = leType.populate

                def populate(layerEd):
                    oldPopulate(layerEd)
                    tw = d3script.getTrackWidget()
                    # 40 is a magic number - height of state bar plus height of title button
                    layerEd.sw.maxSize = Vec2(512 * d3gui.dpiScale.x, tw.pos.y - 40*d3gui.dpiScale.y)

                    def updatePosSize():
                        xPos = 0
                        ole = tw.layerView.openEditorManager.openLayerEditors.values()
                        if (layerEd not in ole):
                            xPos = 0
                        else:
                            for le in ole:
                                if le == layerEd:
                                    break
                                else:
                                    xPos += le.size.x
                        layerEd.sw.maxSize = Vec2(512 * d3gui.dpiScale.x, tw.pos.y - 40*d3gui.dpiScale.y)
                        layerEd.pos = Vec2(xPos,20* d3gui.dpiScale.y)

                    layerEd.updateAction.add(updatePosSize)

                leType.populate = populate

            else:
                leType = type(le)
                oldRefresh = leType.refresh

                def refresh(layerEd):
                    oldRefresh(layerEd)
                    tw = d3script.getTrackWidget()

                    def updatePosSize():
                        xPos = 0
                        ole = tw.layerView.openEditorManager.openLayerEditors.values()
                        if (layerEd not in ole):
                            xPos = 0
                        else:
                            for le in ole:
                                if le == layerEd:
                                    break
                                else:
                                    xPos += le.size.x
                        layerEd.scroll.maxSize = Vec2(512 * d3gui.dpiScale.x, tw.pos.y - 40*d3gui.dpiScale.y)
                        layerEd.pos = Vec2(xPos,20* d3gui.dpiScale.y)

                    layerEd.updateAction.add(updatePosSize)
                
                leType.refresh = refresh
                    

SCRIPT_OPTIONS = {
    "minimum_version" : 23, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Layer Editor Improvements", # Display name of script
            "group" : "Layer Editor Improvements", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Layout Improvements to Layer Editor", #text for help system
            "callback" : loadImprovements, # function to call for the script
        }
        ]
    }
