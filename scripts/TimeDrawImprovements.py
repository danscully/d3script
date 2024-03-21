from d3 import *
import d3script

def initCallback():
    d3script.log("TimelineDrawImprovements","TimelineDrawImprovements Loaded")

def _renderToDisplayList(view, layer, isSelected):
    view.LAYER_RENDER_HEIGHT = 22 * d3gui.dpiScale.x
    displayList = layer.subdl
    displayList.clear()
    whiteMix = colours('layer_whitemix')
    isEditorOpened = next((editorLayer for editorLayer in view.openEditorManager.openLayerEditors.iterkeys() if editorLayer.contains_uid(layer.id)), None) != None
    layerColour = layer.colour.mix(whiteMix, 0.2) if isEditorOpened else layer.colour
    
    if isSelected:
        displayList.quadRounded(DxMaterial.alpha, Rect(Vec2(0, 0), layer.size), Colour(1,1,0), Rect(3, 3, 3, 3), Rect(0, 0, 1, 1))
        displayList.quadRounded(DxMaterial.alpha, Rect(Vec2(2, 2), layer.size - Vec2(4, 4)), layerColour, Rect(3, 3, 3, 3), Rect(0, 0, 1, 1))
    else:
        displayList.quadRounded(DxMaterial.alpha, Rect(Vec2(0, 0), layer.size), layerColour, Rect(3, 3, 3, 3), Rect(0, 0, 1, 1))

    border = 4
    if layer.isGroup and layer.isExpanded:
        topBorder = view.LAYER_RENDER_HEIGHT
        displayList.quadRounded(DxMaterial.alpha, Rect(Vec2(border, 1 + topBorder - 4), layer.size - Vec2(border * 2, 2 + topBorder + border - 4)), Colour(0.0, 0.0, 0.0, 0.5), Rect(3, 3, 3, 3), Rect(0, 0, 1, 1))
    if layer.locked:
        displayList.quad(view.lockedMaterial, Rect(Vec2(2, 2), layer.size - Vec2(4, 4)), layer.colour * 0.5, Rect(0, 0, layer.size.x / view.lockedTex.size.y, 1))

    def report_intervals(intervals):
        from operator import itemgetter
        sorted_intervals = sorted(intervals, key=itemgetter(0))
        if not sorted_intervals:
            return
        low, high = sorted_intervals[0]
        for iv in sorted_intervals[1:]:
            if iv[0] <= high:
                high = max(high, iv[1])
            else:
                yield (
                    low, high)
                low, high = iv

        yield (
            low, high)

    tEnd = layer.start + layer.length
    bw = view.barWidget
    lx = bw.tToX(layer.start)

    def render_interval(t0, t1, col):
        t0 = max(t0, layer.start)
        t1 = min(t1, tEnd)
        if t0 < t1:
            x0 = bw.tToX(t0) - lx
            x1 = bw.tToX(t1) - lx
            col = col.mix(whiteMix, 0.25)
            col.a = 0.75
            displayList.quadRounded(DxMaterial.alpha, Rect(Vec2(x0 + 2, 5), Vec2(x1 - x0 - 4, view.LAYER_RENDER_HEIGHT - 10)), col, Rect(2, 2, 2, 2), Rect(0, 0, 1, 1))

    for t0, t1 in report_intervals((r.t0, r.t1) for r in layer.resourceReports if r.seriousness == 0):
        render_interval(t0, t1, colours('layer_old'))

    for t0, t1 in report_intervals((r.t0, r.t1) for r in layer.resourceReports if r.seriousness == 1):
        render_interval(t0, t1, colours('layer_bad'))

    for t0, t1 in report_intervals((r.t0, r.t1) for r in layer.expressionReports if r.seriousness == 1):
        render_interval(t0, t1, colours('layer_bad'))

    expandIconOffset = d3gui.dpiScale.x * 4
    textOffset = d3gui.dpiScale.x * 4
    iconCol = colours('layer_endbuttons')
    keyCol = Colour(0.35,0.35,0.35,1)

    realLayer = d3script.getTrackWidget().layerView.presentationModel.getLayerObjectFromID(layer.id)
    keys = []
    if (type(realLayer) == Layer):
        for seq in filter(lambda x: not x.noSequence, realLayer.fields):
            for key in seq.sequence.keys:
                if (key.localT >= realLayer.tStart) and (key.localT < realLayer.tEnd):
                    keys.append(key)
    
    for key in keys:
        displayList.quad(view.endMaterial, Rect(Vec2(bw.tToX(key.localT - layer.start) - view.END_BITMZP_SIZE.x/2 -1,(6 * d3gui.dpiScale.x)), view.END_BITMZP_SIZE*1.3), keyCol, Rect(0, 0, 1, 1))
        displayList.quad(view.endMaterial, Rect(Vec2(bw.tToX(key.localT - layer.start)  - view.END_BITMZP_SIZE.x/2+2,(6 * d3gui.dpiScale.x)), view.END_BITMZP_SIZE*1.3), keyCol, Rect(0, 0, -1, 1))

    if isSelected:
        displayList.quad(view.endMaterial, Rect(Vec2(), view.END_BITMZP_SIZE), iconCol, Rect(0, 0, 1, 1))
        displayList.quad(view.endMaterial, Rect(Vec2(layer.size.x - view.END_BITMZP_SIZE.x, 0), view.END_BITMZP_SIZE), iconCol, Rect(1, 0, -1, 1))
        textOffset += view.END_BITMZP_SIZE.x
        expandIconOffset += view.END_BITMZP_SIZE.x
    if layer.isGroup:
        if layer.isSmart:
            material = view.smartGroupMaterial
        else:
            material = view.contractMaterial if layer.isExpanded else view.expandMaterial
        displayList.quadBounded(material, Rect(Vec2(expandIconOffset, 5), Vec2(view.LAYER_RENDER_HEIGHT - 15 * d3gui.dpiScale.x, view.LAYER_RENDER_HEIGHT - 15 * d3gui.dpiScale.x)), iconCol, Rect(0, 0, 1, 1), expandIconOffset)
        textOffset += view.LAYER_RENDER_HEIGHT - 10 + d3gui.dpiScale.x * 4
    name = layer.name + layer.indicator + (' [LOCKED]' if layer.locked else '')
    displayList.printBounded(d3gui.font, name, Vec2(textOffset, 1), max(0, layer.size.x - textOffset), textOffset, 1, colours('layer_name'))
    controlPatch = layer.controlPatch
    if controlPatch:
        patchText = controlPatch.layerDescriptionSuffix
        ext = d3gui.font.extent(name + '  ')
        labelOffset = textOffset + ext.x
        displayList.printBounded(d3gui.font, patchText, Vec2(labelOffset, 1), max(0, layer.size.x - textOffset), labelOffset, 1, colours('layer_name') * 0.75)
    return

def loadImprovements():

    tw = d3script.getTrackWidget()
    tw.layerView.view.LAYER_RENDER_HEIGHT = 22 * d3gui.dpiScale.x
    tw.layerView.view.__class__._oldRenderToDisplayList = tw.layerView.view.__class__._renderToDisplayList
    tw.layerView.view.__class__._renderToDisplayList = _renderToDisplayList
    tw.layerView.reRenderNeeded = True

def revertImprovements():
    tw = d3script.getTrackWidget()
    tw.layerView.view.LAYER_RENDER_HEIGHT = d3gui.font.maxHeightInPixels + 4.0
    tw.layerView.view.__class__._renderToDisplayList = tw.layerView.view.__class__._oldRenderToDisplayList
    tw.layerView.reRenderNeeded = True


SCRIPT_OPTIONS = {
    "minimum_version" : 23, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Load Improvements", # Display name of script
            "group" : "Timeline Improvements", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Adds keyframes on modules in Track", #text for help system
            "callback" : loadImprovements, # function to call for the script
        },
                {
            "name" : "Revert Imrprovements", # Display name of script
            "group" : "Timeline Improvements", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Reverts timeline view to normal", #text for help system
            "callback" : revertImprovements, # function to call for the script
        }
        ]
    }
