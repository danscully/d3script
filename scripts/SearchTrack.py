# SearchTrack
from gui.inputmap import *
from d3 import *
from gui.columnlistview import *
import d3script



def initCallback():
    d3script.log("SearchTrak","SearchTrack Loaded")



def handleItemClick(item,colIndex):
    d3script.log('SearchTrack','item has been clicked')
    lay = item.values[6]
    if (type(lay) == Layer) and (len(lay.tracks) == 1):
        d3script.log('SearchTrack','click handler - layer found')
        cmd = TransportCMDTrackBeat()
        tm = d3.state.currentTransportManager
        trk = lay.tracks[0]
        trkTime = trk.findBeatOfLastTag(trk.timeToBeat(lay.tStart))
        cmd.init(None, tm, trk, trk.timeToBeat(trkTime), trk.transitionInfoAtBeat(trkTime))
        tm.addCommand(cmd)


def showResults(results):
    columnNames = ['Track','Cue','Label','Layer','Resource','Type']

    columns = []
    for column in columnNames:
        columns.append(ColumnListViewColumn(column,column,None))

    resultWidget = Widget()
    resultWidget.add(TitleButton('Track Search Results'))

    listWidget = ColumnListView(columns,maxSize=Vec2(1500, 800) * d3gui.dpiScale)
    
    rows = map(lambda x:ColumnListViewItem(x),results)

    listWidget.items = rows
    listWidget.recalculateColumnSizes()
    listWidget.itemColumnClickedAction = handleItemClick

    resultWidget.add(listWidget)
    resultWidget.arrangeVertical()
    resultWidget.computeAllMinSizes()
    d3gui.root.add(resultWidget)
    resultWidget.pos = (d3gui.root.size / 2) - (resultWidget.size/2)
    resultWidget.pos = Vec2(resultWidget.pos[0],resultWidget.pos[1]-100)


def doSearch(searchString):

    typeFilter = Resource
    searchString = searchString.lower()
    searchSplit = searchString.split(':',1)
    if len(searchSplit) > 1:
        if searchSplit[0] == 'm':
            typeFilter = Projection
            searchString = searchSplit[1]

        elif searchSplit[0] == 'v':
            typeFilter = VideoClip
            searchString = searchSplit[1]
    
        elif searchSplit[0] == 'l':
            typeFilter = Layer
            searchString = searchSplit[1]

    res = resourceManager.allResources(typeFilter)

    res = filter(lambda r:r.description.lower().find(searchString) != -1,res)

    lays = set()

    for resource in res:
        if type(resource) == Layer:
            lays.add((resource,resource))
        else:    
            points = resource.findResourcesPointingToThis(Layer)
            for  lay in points:
                lays.add((lay,resource))

    lays = list(lays)

    lays.sort(key = (lambda x: x[0].tStart))

    outputRows = []
    for l in lays:
        lay = l[0]
        if (len(lay.tracks) < 1):
            continue
        
        trk = lay.tracks[0]
        trackName = trk.description
        cueTag = trk.tagAtBeat(trk.findBeatOfLastTag(trk.timeToBeat(lay.tStart)))
        cueLabel = trk.noteAtBeat(trk.findBeatOfLastTag(trk.timeToBeat(lay.tStart)))
        layName = lay.description
        resName = l[1].description
        typeName = str(type(l[1]))
        outputRows.append((trackName,cueTag,cueLabel,layName,resName,typeName,lay))

    d3script.log('searchTrack','Opening Results Window')
    showResults(outputRows)

    
def trackSearchPopup():
    """Open a popup menu with rename options"""
    
    menu = PopupMenu('Search Track')
    menu.add(TextBox('Prefix searchstring with m: for mappings only, v: for videos only, and l: for layers only'))
    menu.editItem('Search String:', '', doSearch)
    menu.computeAllMinSizes()

    d3gui.root.add(menu)
    menu.pos = (d3gui.root.size / 2) - (menu.size/2)
    menu.pos = Vec2(menu.pos[0],menu.pos[1]-100)
    menu.contents.findWidgetByName('Search String:').textBox.focus = True



       

SCRIPT_OPTIONS = {
    "minimum_version" : 21, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Track Search", # Display name of script
            "group" : "Track Search", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "bind_globally" : True, # binding should be global
            "help_text" : "Search tracks for resources by name", #text for help system
            "callback" : trackSearchPopup, # function to call for the script
        }
        ]

    }
