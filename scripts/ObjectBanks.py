from gui.separator import Separator
from d3 import *
import collections, random, json
from gui.inputmap import *
from PresetManager3 import PMPreset, PresetEditor
import d3script
import functools
import math
from gui.listview import ListView,ListViewItem

def trace(func):
    @functools.wraps(func)

    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result
    return wrapper


def presetPopup():
    openBank('PMPreset')

    
def openBankForObjectViews():
    ovs = d3gui.root.childrenOfType(ObjectView)
    
    for ov in ovs:
        be = BankEditor(ov.className,[globals()[ov.className.encode('ascii','ignore')]])
        ovCallback = ov.onSet
        def callback(res):
            ovCallback(res)
            be.close()
            ov.close()
            
        be.selectionFunc = callback
        d3gui.root.add(be)
        #ov.close()


def openBank(resType=None):
    if (resType):
        be = BankEditor(resType,[globals()[resType]])
    else:
        be = BankEditor()
    
    be.selectionFunc = applyPresetForResource
    d3gui.root.add(be)


def applyPresetForPath(path):
    presetPath = -1
    try:
        presetPath = path.index('pmpreset')
    except:
        pass

    if (presetPath == 0):
        resource = PMPreset.loadFromPath(path)
    else:
        resource = resourceManager.load(path)

    if resource:
        applyPresetForResource(resource)


        
def applyPresetForResource(resource):
    if isinstance(resource,PMPreset):
        resource.applyPreset()
        
    elif isinstance(resource,SuperLayer):
        d3script.copyLayerToTime(resource,state.player.tRender)
        
    else:
        if isinstance(resource,Projection):
            field = 'mapping'
        elif isinstance(resource,VideoClip):
            field = 'video'
        elif isinstance(resource,DxTexture):
            field = 'video'
        else:
            return
        
        PMPreset.applyResourceToField(resource,field)    
    
def printHelper(item):
    d3script.log('OB',item)


def getThumbnailResourceAndTextForResource(resource):
    

    if (isinstance(resource,Resource)) and (ThumbnailSystem.supportsThumbnails(type(resource))):
        text = resource.path.filenameAndExtension
        return (resource,text)

    if isinstance(resource,Resource):
        matchName = resource.path.filename.lower()
        matchType = type(resource).__name__.lower()
    else:
        matchName = resource.name.lower()
        matchType = 'pmpreset'

    dxt = resourceManager.allResources(DxTexture)       
    texResource = filter(lambda x: x.path == THUMBPATH + matchType + '/' + matchName + '.png',dxt)

    if len(texResource) > 0: 
        texResource = texResource[0]
    else:
        if (issubclass(type(resource),Projection)):
            matchType = "projection"
            
        texResource = filter(lambda x: x.path == THUMBPATH + 'defaults' + '/' + matchType + '.png',dxt)
        if len(texResource) > 0:
            texResource = texResource[0]
        else:
            texResource = filter(lambda x: x.path == THUMBPATH + 'default.png',dxt)[0]


    text = matchName

    return (texResource,text)



BANKSIZE = 100
THUMBPATH = "objects/dxtexture/objectthumbnails/"

class PresetObjectView(ListView):
    
    def __init__(self):
        ListView.__init__(self)
        for p in PMPreset.presets:
            if (not p.hidden):
                self.items.append(ListViewItem(p.name))
                
        self.arrangeVertical()
        self.contents.arrangeVertical()
        self.makeItemsDraggable(printHelper)
        self.computeAllMinSizes()
        self.bankSelector = None

        #self.overrideMinSize = (lambda given: Vec2(given.x, 400 * d3gui.dpiScale.y))
        #self.sw.overrideMinSize = (lambda given: Vec2(given.x, 400 * d3gui.dpiScale.y))

    def makeItemsDraggable(self, onMoveComplete):
        """Extend the input bindings on the list view to include the ability to drag items"""

        def drag(state, start, pos):
            if state == 1:
                drag.startIndex = self.indexUnderCursor(start)
                drag.dragItem = self.items[drag.startIndex]
            destIndex = self.indexUnderCursor(pos)
            if state == 2:
                drag.dragItem.pos = pos
            if state == 3:
                    if (self.bankSelector):
                        self.bankSelector.bankPage.acceptDrop(drag.dragItem)

        self.contents.inputMap.add(drag, 'MouseDrag,None,Left', tr('Reorder items in the list'), False)

class ScriptObjectView(ListView):
    
    def __init__(self):
        ListView.__init__(self)
        for s in d3script.scripts:
            self.items.append(ListViewItem(s['group'] + ' :: ' + s['name']))
        self.arrangeVertical()
        self.contents.arrangeVertical()
        self.makeItemsDraggable(printHelper)
        self.computeAllMinSizes()
        self.bankSelector = None

        #self.overrideMinSize = (lambda given: Vec2(given.x, 400 * d3gui.dpiScale.y))
        #self.sw.overrideMinSize = (lambda given: Vec2(given.x, 400 * d3gui.dpiScale.y))

    def makeItemsDraggable(self, onMoveComplete):
        """Extend the input bindings on the list view to include the ability to drag items"""

        def drag(state, start, pos):
            if state == 1:
                drag.startIndex = self.indexUnderCursor(start)
                drag.dragItem = self.items[drag.startIndex]
            destIndex = self.indexUnderCursor(pos)
            if state == 2:
                drag.dragItem.pos = pos
            if state == 3:
                    if (self.bankSelector):
                        self.bankSelector.bankPage.acceptDrop(drag.dragItem)

        self.contents.inputMap.add(drag, 'MouseDrag,None,Left', tr('Reorder items in the list'), False)


class OBViewStyle():

    # @trace
    def __init__(self, friendlyDisplayName, canAutoPopulate=False, showNamesInListView=True, showFileTypes=True, info=lambda r: ''):
        self.friendlyDisplayName = friendlyDisplayName
        self.canAutoPopulate = canAutoPopulate
        self.showNamesInListView = showNamesInListView
        self.showFileTypes = showFileTypes
        self._info = info

    # @trace
    def info(self, resource):
        if isinstance(resource, Indirection):
            return 'Indirection'
        return self._info(resource)


class OBBank():

    changeAction = None

    @staticmethod
    def setChangeAction(func):
        OBBank.changeAction = func
    

    # @trace
    def __init__(self, parent, name="bank"):
        #init stuff
        #bank.slots is a thing.  Seems to be a set of resources - code to the effect of "if resource in bank.slots"
        #bank.name is the name of bank
        self.name = name
        self.slots = []
        for i in range(BANKSIZE):
            self.slots.append(None)
        self.parent = parent
        if (OBBank.changeAction):
            OBBank.changeAction(self)

    # @trace
    def getResource(self, slot):
        #return resource for slot
        return self.slots[slot]
    
    # @trace
    def setResource(self, slot, resource):
        #set the resource for the slot
        self.slots[slot] = resource

        self.parent.saveOnDelete()

        if (OBBank.changeAction):
            OBBank.changeAction(self)
        
        
class OBObjectSet():

    changeAction = None
    @staticmethod
    def setChangeAction(func):
        OBObjectSet.changeAction = func

    @staticmethod
    # @trace
    def findOrAddSet(resourceType):
    #return a set for the resourceType

        obSet = OBObjectSet(resourceType)
        storedValues = d3script.getPersistentValue(resourceType,"ObjectBanks")

        if storedValues == None:
            obSet.addBank(0,"Bank 1")
            return obSet 

        else:
            #NEED TO HANDLE PMPresets
            for idx,bank in storedValues.items():
                newBank = obSet.addBank(int(idx),bank["name"])
                for slotIdx, slot in bank["slots"].items():
                    try:
                        if ("pmpreset/" in slot):
                            resource = PMPreset.loadFromPath(slot)

                        else:
                            resource = resourceManager.load(slot)

                    except:
                            resource = None
                            d3script.log('ObjectBanks','Could not load resource by name: ' + slot)
                            
                    newBank.setResource(int(slotIdx),resource)
            
            return obSet

    # @trace
    def __init__(self,resourceType):
        self.banks = []

        for i in range(BANKSIZE):
            self.banks.append(None)

        self.resourceType = resourceType
        if(OBObjectSet.changeAction):
            OBObjectSet.changeAction(self)

    # @trace
    def getBank(self, index):
        return self.banks[index]
    
    # @trace
    def saveOnDelete(self):
        storedValues = {}

        for idx, bank in enumerate(self.banks):
            storeSlots = {}

            if bank != None:
                for slotIndex, slot in enumerate(bank.slots):
                    if slot != None:
                        storeSlots[slotIndex] = str(slot.path)

                storedValues[idx] = {"name":bank.name, "slots":storeSlots}
        d3script.setPersistentValue(self.resourceType,storedValues,"ObjectBanks")

    # @trace
    def addBank(self, bankIndex, bankName):
        
        self.banks[bankIndex] = OBBank(self,bankName)
        self.saveOnDelete()
        if (OBBank.changeAction):
            OBBank.changeAction(self.banks[bankIndex])
        if(OBObjectSet.changeAction):
            OBObjectSet.changeAction(self)

        return self.banks[bankIndex]

    # @trace
    def getNumberOfBanks(self):
        return len(self.banks)
    
    # @trace
    def removeBank(self, bankIndex):
        if (OBBank.changeAction):
            OBBank.changeAction(self.banks[bankIndex])
        if(OBObjectSet.changeAction):
            OBObjectSet.changeAction(self)
        self.banks[bankIndex] = None
        

    
OBResourceViewStyles = {VideoClip: OBViewStyle(tr('Video Clip'), canAutoPopulate=True), 
   SuperLayer: OBViewStyle('Layer Library', canAutoPopulate=True),
   DxTexture: OBViewStyle(tr('Texture'), canAutoPopulate=True), 
   Projection: OBViewStyle(tr('Mapping'), canAutoPopulate=True), 
   PMPreset: OBViewStyle('PM Preset', canAutoPopulate=True)}


# @trace
def findChildrenInTree(widget, t):
    if type(widget) == t:
        return [widget]
    result = []
    for c in widget.children:
        cf = findChildrenInTree(c, t)
        result = result + cf

    return result


defaultResourceTypes = [ cls for cls in OBResourceViewStyles.keys() ]

# @trace
def obViewStyle(cls):
    return OBResourceViewStyles.get(cls, None) or OBViewStyle(cls.__username__)


class OBBankThumbnails(Widget):

    # @trace
    def __init__(self, bankSelector):
        Widget.__init__(self)
        self.bankSelector = bankSelector
        self.style = obViewStyle(self.bankSelector.selectedResourceType)
        self.deferredRenderer = DeferredRenderer()
        self.renderAction.add(self.render)
        self.updateAction.add(self.update)
        OBBank.setChangeAction(self.markDirty)
        self.closeAction.add(lambda : OBBank.setChangeAction(None))
        self.closeAction.add(lambda : setattr(self, 'deferredRenderer', None))

    # @trace
    def markDirty(self, resource):
        if resource is self.bankSelector.bank:
            self.deferredRenderer.dirty = True
            self.update()
        #self.deferredRenderer.dirty = True

    # @trace
    def update(self):
        self.setSuggestion('')
        if d3gui.widgetUnderCursor is self and self.deferredRenderer:
            bank, slot = self.screenPosToBankSlot(d3gui.cursorPos)
            if slot is not None:
                resource = self.bankSelector.bank.getResource(slot)
                if isinstance(resource,Resource):
                    if resource.isInError:
                        if resource.isBad:
                            status = resource.status()
                        elif resource.isNotFoundLocal:
                            status = 'Not found'
                        else:
                            status = 'In Error'
                        self.setSuggestion('%s\n%s' % (resource.userInfoPath, status))
                    else:
                        self.setSuggestion(resource.descriptionExtended)
        return

    # @trace
    def screenPosToBankSlot(self, pos):
        item = self.deferredRenderer.itemAtPoint(pos - self.absPos, 'slot')
        if item:
            slot = item.data[0]
        else:
            slot = None
        return (
         self.bankSelector.selectedBankIndex, slot)

    # @trace
    def render(self):
        viewMat = Mat()
        viewMat.setTranslation(Vec(self.absPos))
        if self.deferredRenderer.dirty:
            self.deferredRenderer.dirty = False
            self.refresh()
        self.deferredRenderer.render(viewMat)

    # @trace
    def acceptDrop(self, dropped):
        bank, slot = self.screenPosToBankSlot(d3gui.cursorPos)
        if slot is not None:
            if (isinstance(dropped,ListViewItem)):
                self.bankSelector.bank.setResource(slot, PMPreset.findByName(dropped.text))
            else:
                widget = dropped['formats'].get('widget', lambda : None)()
                if isinstance(widget, ObjectViewThumbnail):
                    if widget.resource is None or isinstance(widget.resource, self.bankSelector.selectedResourceType) or isinstance(widget.resource, ResourceSequence) and issubclass(widget.resource.expectedType, self.bankSelector.selectedResourceType) or isinstance(widget.resource, Indirection):
                        self.bankSelector.bank.setResource(slot, widget.resource)
                        return True
        return False

    # @trace
    def acceptArrow(self, arrowSource):
        bank, slot = self.screenPosToBankSlot(d3gui.cursorPos)
        if slot is None:
            return False
        else:
            return self.bankSelector.acceptObjects(arrowSource, bank, slot)

    @binding(MouseDrag, 'Ctrl', Mouse.Left)
    # @trace
    def dragCopySelection(self, state, startPos, pos):
        """Copy the element in the slot under the cursor to another slot"""
        self.dragSelection(state, startPos, pos, True)

    @binding(MouseDrag, Mouse.Left)
    # @trace
    def dragMoveSelection(self, state, startPos, pos):
        """Move the element in the slot under the cursor to another slot"""
        self.dragSelection(state, startPos, pos, False)

    @binding(MouseClick, Mouse.Right)
    # @trace
    def editSelection(self):
        """Edit the resource in the slot under the cursor"""
        item = self.deferredRenderer.itemAtPoint(d3gui.cursorPos - self.absPos, 'slot')
        if item:
            iSlot = item.data[0]
            resource = self.bankSelector.bank.getResource(iSlot)
            if isinstance(resource,Resource):
                existing = d3gui.findEditor(resource)
                if not existing:
                    ed = guisystem.makeEditor(resource)
                    ed.pos = d3gui.cursorPos + Vec2(32, 0) * d3gui.dpiScale
                    d3gui.root.add(ed)
            elif isinstance(resource, PMPreset):
                    #Add PMPreset editor call here
                    PresetEditor(resource)
                    pass
            
    @binding(MouseClick, Mouse.Left)
    # @trace
    def applySelection(self):
        """Edit the resource in the slot under the cursor"""
        item = self.deferredRenderer.itemAtPoint(d3gui.cursorPos - self.absPos, 'slot')
        if item:
            iSlot = item.data[0]
            self.bankSelector.bankEditor.applySelection(self.bankSelector.bank.getResource(iSlot))

                      
    # @trace
    def dragSelection(self, state, startPos, pos, copy):
        op = Undoable('Drag thumbnail')
        if state == 1:
            item = self.deferredRenderer.itemAtPoint(startPos - self.absPos, 'slot')
            self.bumnail = None
            if item:
                iSlot = item.data[0]
                resource = self.bankSelector.bank.getResource(iSlot)
                if resource:
                    self.bumnail = Bumnail(resource, iSlot)
                    d3gui.root.add(self.bumnail)
        elif self.bumnail and state == 3:
            self.bumnail.close()
            bank = self.bankSelector.bank
            dropLocation = d3gui.root.widgetUnderPoint(pos)
            removeSource = not copy
            if isinstance(dropLocation, OBBankThumbnails):
                _, dropSlot = dropLocation.screenPosToBankSlot(pos)
                if dropSlot is not None and self.bumnail.sourceSlot != dropSlot:
                    bank.setResource(dropSlot, self.bumnail.slotResource)
                else:
                    removeSource = False
            if removeSource:
                bank.setResource(self.bumnail.sourceSlot, None)
            self.bumnail = None
        if self.bumnail:
            self.bumnail.moveToFront()
            self.bumnail.pos = pos - self.bumnail.minSize / 2
        return

    colourFound = colours('widget_pulse')
    colourdefault = Colour.blackZeroAlpha
    colourHighlight = colours('widget_highlight_background')
    colourError = colours('widget_attention_bg')


    def slotHidden(self, iSlot):
        
        searchString = self.bankSelector.bankEditor.searchString
        resource = self.bankSelector.bank.getResource(iSlot)

        if (resource) and (searchString) and (searchString in str(resource.path)):
            return False
        
        if (searchString == ""):
            return False
        
        return True
    
    # @trace
    def slotBounds(self, iSlot):
        for slotItem in self.deferredRenderer.allItemsById('slot'):
            if slotItem.data[0] == iSlot:
                return slotItem.bounds

        return Rect()

    # @trace
    def slotColour(self, iSlot):
        searchString = self.bankSelector.bankEditor.searchString
        resource = self.bankSelector.bank.getResource(iSlot)
        if resource and isinstance(resource,Resource):
            if resource.isInError:
                return self.colourError
        if resource and searchString and isinstance(resource,Resource):
            searchName = resource.path.filenameAndExtension if self.style.showFileTypes else resource.path.filename
            if searchString in searchName:
                return self.colourFound
        if resource and searchString and isinstance(resource,PMPreset):
            searchName = resource.name
            if searchString in searchName:
                return self.colourFound           
        if self.bankSelector.bankEditor.highlightSlot == iSlot:
            return self.colourHighlight
        return self.colourdefault

    # @trace
    def deferSlotContainer(self, iSlot, bounds):
        slotItem = DeferredRendererItem()
        slotItem.renderType = DeferredRendererItem.RenderType_Quad
        slotItem.id = 'slot'
        slotItem.data = (iSlot,)
        slotItem.bounds = bounds
        slotItem.colCallable = lambda : self.slotColour(iSlot)
        self.deferredRenderer.deferItem(slotItem)


class OBBankThumbnails_Grid(OBBankThumbnails):

    THUMBSIZE = 110


    # @trace
    def __init__(self, bankSelector, half=False):
        OBBankThumbnails.__init__(self, bankSelector)
        self.half = half

    # @trace
    def refresh(self):
        self.deferredRenderer.reset()
        width = self.bankSelector.bankEditor.constraintSize.x / 1.1
        cellsWide = self.bankSelector.bankEditor.nColumns
        cellWidth = max(OBBankThumbnails_Grid.THUMBSIZE * d3gui.dpiScale.x, width / cellsWide)
        cellHeight = min(OBBankThumbnails_Grid.THUMBSIZE * d3gui.dpiScale.x, cellWidth) + d3gui.font.maxHeightInPixels

        if self.half:
            cellWidth *= 2
            cellsWide /= 2
            cellsWide = max(cellsWide, 1)
        cellsHigh = int(BANKSIZE / cellsWide)
        cellTopMargin = 5.0
        cellSize = Vec2(float(cellWidth), float(cellHeight)).round(1)
        cellSizeWithBorder = cellSize * Vec2(1.1, 1.1)
        self.minSize = cellSizeWithBorder * Vec2(cellsWide, cellsHigh)
        bank = self.bankSelector.bank
        cellColour = Colour(0.25, 0.25, 0.25, 0.75)

        skipCount = 0
        for iSlot in range(BANKSIZE):
            if self.slotHidden(iSlot):
                skipCount += 1
                continue
            
            displaySlot = iSlot - skipCount    
            pos = Vec2(int(displaySlot % cellsWide), int(displaySlot / cellsWide)) * cellSizeWithBorder + Vec2(0,5.0)
            bounds = Rect(pos, cellSize)
            #Give a top margin for the thumbnail
            texbounds = Rect(pos + Vec2(0,25), cellSize)
            self.deferSlotContainer(iSlot, bounds)
            resource = bank.getResource(iSlot)
            self.deferredRenderer.deferQuad('', None, Rect(pos, cellSize * 1.06), cellColour)
            if (resource):
                texResource,text = getThumbnailResourceAndTextForResource(resource)
                self.deferredRenderer.deferThumbnailQuad('', None, texbounds, texResource)
                text = str(iSlot) + ': ' + text
            else:
                text = str(iSlot)
            if d3gui.font.extent(text) > OBBankThumbnails_Grid.THUMBSIZE * d3gui.dpiScale.x:
                textLength = len(text)
                slices = math.ceil(float(textLength) / 15.0)
                slicedText = ""
                for i in range(int(slices)):
                    if slicedText == "":
                        joiner = ""
                    else:
                        joiner = "\n    "
                    slicedText = slicedText + joiner + text[i*15:(i+1)*15]
                text = slicedText
                
            self.deferredRenderer.deferBoundedText('', None, bounds.bl, SlugFont.AlignLeft, SlugFont.AlignBottom, bounds.size.x, text)

        return


class OBBankThumbnails_List(OBBankThumbnails):

    LISTWIDTH = 300
    LISTHEIGHT = 64

    # @trace
    def refresh(self):
        self.deferredRenderer.reset()
        cellSize = Vec2(OBBankThumbnails_List.LISTWIDTH, OBBankThumbnails_List.LISTHEIGHT) * d3gui.dpiScale
        cellSizeWithBorder = cellSize * Vec2(1.1, 1.1)
        self.minSize = cellSizeWithBorder * Vec2(1, BANKSIZE)
        bank = self.bankSelector.bank
        skipCount = 0
        for iSlot in range(BANKSIZE):
            if math.random() > 0.5:
                skipCount += 1
                continue
            
            pos = Vec2(0, iSlot-skipCount) * cellSizeWithBorder
            bounds = Rect(pos, cellSize)
            self.deferSlotContainer(iSlot, bounds)
            resource = bank.getResource(iSlot)
            self.deferredRenderer.deferText('', None, bounds.tl, SlugFont.AlignLeft, SlugFont.AlignTop, str(iSlot))
            if resource:
                self.deferredRenderer.deferThumbnailQuad('', None, Rect(bounds.tl + Vec2(32, 0) * d3gui.dpiScale, Vec2(64, 64) * d3gui.dpiScale), resource)
                if self.style.showNamesInListView:
                    text = '%s\n%s' % (resource.path, self.style.info(resource))
                else:
                    text = self.style.info(resource)
                self.deferredRenderer.deferText('', None, bounds.tl + Vec2(106, 0) * d3gui.dpiScale, SlugFont.AlignLeft, SlugFont.AlignTop, text)

        return


class BankSelector(Widget):

    # @trace
    def __init__(self, bankEditor, initialBankName=None):
        Widget.__init__(self)
        self.arrangeVertical()
        self.bankEditor = bankEditor
        self._selectedBankName = None
        self.slotScrollContainer = None
        # WE AREN'T GOING TO STORE OBJECT SETS AS RESOURCES SO WE SHOULDN'T WATCH THEM FOR BEING DIRTY
        OBObjectSet.setChangeAction(self.onDirty)
        self.closeAction.add(lambda : OBObjectSet.setChangeAction(None))
        self.populate(initialBankName)
        return

    # @trace
    def onDirty(self, resource):
        self.populate(self.selectedBankName)
        self.arrangeAll()

    # @trace
    def populate(self, initialBankName=None):
        self.clear()
        self.bankIndices = {}
        self.bankPage = None
        bankNames = []
        bankIndices = []


        for iBank, bank in enumerate(self.objectSet.banks):
            if bank:
                name = '%d:%s' % (iBank, bank.name)
                self.bankIndices[name] = iBank
                bankNames.append(name)
                bankIndices.append(iBank)
                if initialBankName is None:
                    initialBankName = name

        self.selectMenu = SelectMenu(bankNames)
        self.add(self.selectMenu)

        # @trace
        def onSelect(name):
            self._selectedBankName = name
            self.bankPage.refresh()

        self.selectMenu.selectAction.add(onSelect)
        for bankIndex, button in zip(bankIndices, self.selectMenu.allButtons):
            button.popupMenuAction.clear()
            button.popupMenuAction.add(lambda bankIndex=bankIndex: self.bankContextMenu(bankIndex))
            button.acceptArrowDelegate = lambda arrowSource, bankIndex=bankIndex: self.acceptObjects(arrowSource, bankIndex, 0)

        if self.slotScrollContainer:
            maxSize = self.slotScrollContainer.maxSize
        else:
            maxSize = Vec2(1024,1024)

        self.slotScrollContainer = ScrollWidget2(name='slotScrollContainer', renderBack=True, maxSize=maxSize)
        self.slotScrollContainer.contents.arrangeVertical()
        self.add(self.slotScrollContainer)
        self.createOBBankThumbnails()
        self.selectMenu.selectByName(initialBankName)
        return

    # @trace
    def createOBBankThumbnails(self):
        if self.bankPage:
            self.bankPage.close()
            self.bankPage = None
        if self.bankEditor.viewType == 0:
            self.bankPage = OBBankThumbnails_Grid(self, False)
        elif self.bankEditor.viewType == 1:
            self.bankPage = OBBankThumbnails_Grid(self, True)
        elif self.bankEditor.viewType == 2:
            self.bankPage = OBBankThumbnails_List(self)
        else:
            raise ValueError('Unknown view type %d' % self.bankEditor.viewType)
        self.slotScrollContainer.contents.add(self.bankPage)
        return

    @property
    # @trace
    def objectSet(self):
        return self.bankEditor.objectSet

    @property
    # @trace
    def bank(self):
        return self.objectSet.getBank(self.selectedBankIndex)

    @property
    # @trace
    def selectedBankIndex(self):
        return self.bankIndices[self._selectedBankName]

    @selectedBankIndex.setter
    # @trace
    def selectedBankIndex(self, iBank):
        for key, value in self.bankIndices.iteritems():
            if value == iBank:
                self.selectedBankName = key

    @property
    # @trace
    def selectedBankName(self):
        return self._selectedBankName

    @selectedBankName.setter
    # @trace
    def selectedBankName(self, bankName):
        if bankName != None:
            self.selectMenu.selectByName(bankName)
        else:
            self.selectMenu.selectByNumber(0)

    @property
    # @trace
    def selectedResourceType(self):
        return self.bankEditor.selectedResourceType

    # @trace
    def bankContextMenu(self, bankIndex):

        # @trace
        def wrapBankString(nw):
            nw.textBox.allow('0123456789-*,')
            return nw

        self.contextMenuSelectedBankIndex = bankIndex
        menu = PopupMenu(TFormat('Options (bank {0:d})', bankIndex))
        menu.add(NameWidget('Rename:', self.objectSet.getBank(bankIndex).name, self.onContextMenuBankName))
        menu.add(NameWidget('Duplicate:', '0', self.onContextMenuCopyBankTo))
        menu.add(NameWidget('New Bank:', '0', self.onCreateNewBank))
        rangeHelpText = tr('Specify a comma-separated list, range or * for all banks')
        menu.add(wrapBankString(NameWidget('Reset Bank(s):', str(bankIndex), self.onContextMenuResetBank).setHelpText(rangeHelpText)))
        menu.add(wrapBankString(NameWidget('Remove Missing:', str(bankIndex), self.onContextMenuRemoveMissing).setHelpText(rangeHelpText)))
        menu.add(wrapBankString(NameWidget('Delete Bank(s):', str(bankIndex), self.onContextMenuDeleteBank).setHelpText(rangeHelpText)))
        d3gui.root.add(menu)
        menu.pos = d3gui.cursorPos + Vec2(64, -64)

    # @trace
    def onContextMenuBankName(self, name):
        op = Undoable('Rename Bank')
        self.bankIndices[name] = self.contextMenuSelectedBankIndex
        self.objectSet.getBank(self.contextMenuSelectedBankIndex).name = name
        originalBankIndex = self.selectedBankIndex
        self.populate()
        self.selectedBankIndex = originalBankIndex
        self.objectSet.saveOnDelete()

    # @trace
    def onCreateNewBank(self, bankIndexString):
        op = Undoable('Create Bank')
        try:
            if ':' in bankIndexString:
                bankIndexStr, bankName = bankIndexString.split(':')
                bankIndex = int(bankIndexStr)
            else:
                bankIndex = int(bankIndexString)
                bankName = ''
            if self.objectSet.getBank(bankIndex):
                alertError('A bank with that index already exists')
            elif bankIndex < 0 or bankIndex >= BANKSIZE:
                alertError('Bank index must be between 0 and 255')
            else:
                self.objectSet.addBank(bankIndex, bankName)
        except ValueError:
            alertError('Bank index must be numeric')


    # @trace
    def onContextMenuCopyBankTo(self, bankIndexString):
        op = Undoable('Copy Bank')
        try:
            if ':' in bankIndexString:
                copyToBankIndexStr, copyToBankName = bankIndexString.split(':')
                copyToBankIndex = int(copyToBankIndexStr)
            else:
                copyToBankIndex = int(bankIndexString)
                copyToBankName = ''
        except ValueError:
            alertError('Bank index must be numeric')
            return

        copyFromBankIndex = self.contextMenuSelectedBankIndex
        if self.objectSet.getBank(copyToBankIndex):
            alertError('A bank with that index already exists')
        elif copyToBankIndex < 0 or copyToBankIndex > 255:
            alertError('Bank index must be between 0 and 255')
        else:
            copyFromBank = self.objectSet.getBank(copyFromBankIndex)
            copyToBank = self.objectSet.addBank(copyToBankIndex, copyToBankName)
            for slot in range(256):
                resource = copyFromBank.getResource(slot)
                copyToBank.setResource(slot, resource)


    # @trace
    def onContextMenuResetBank(self, banks):
        op = Undoable('Reset Bank(s)')
        
        for bankIndex in self.banksFromString(banks):
            markDirty(objectSet.getBank(bankIndex))
            for slot in range(256):
                self.objectSet.getBank(bankIndex).setResource(slot, None)

        return

    # @trace
    def onContextMenuRemoveMissing(self, banks):
        op = Undoable('Remove Missing from Bank(s)')
        for bankIndex in self.banksFromString(banks):
            markDirty(objectSet.getBank(bankIndex))
            for slot in range(256):
                bank = self.objectSet.getBank(bankIndex)
                resource = bank.getResource(slot)
                if resource and (resource.isNotFoundLocal or resource.isIncomplete):
                    bank.setResource(slot, None)

        return

    # @trace
    def onContextMenuDeleteBank(self, banks):
        op = Undoable('Delete Bank(s)')
        for bankIndex in self.banksFromString(banks):
            if self.objectSet.getNumberOfBanks() > 1:
                self.objectSet.removeBank(bankIndex)
                if bankIndex == self.selectedBankIndex:
                    self.bankEditor.lastSelectedBankPageNameForResourceType[self.selectedResourceType] = None
                    self.populate()
            else:
                alertError('Cannot remove the last bank')

        return

    # @trace
    def banksFromString(self, str):
        if '*' in str:
            return [ iBank for iBank, bank in enumerate(self.objectSet.banks) if bank is not None ]
        else:
            banks = []
            splits = str.split(',')
            for sub in splits:
                r = sub.split('-', 2)
                if len(r) == 2:
                    start = int(r[0])
                    end = int(r[1]) + 1
                    for i in range(start, end):
                        if self.objectSet.getBank(i) is not None:
                            banks.append(i)

                else:
                    banks.append(int(sub))

            return banks

    # @trace
    def acceptObjects(self, arrowSource, bankNumber, slot):
        op = Undoable('Populate Bank From Folder')
        if arrowSource.format == 'Resources':
            bank = self.objectSet.getBank(bankNumber)
            for resource in arrowSource.dataGetter():
                if not resource or not isinstance(resource, self.selectedResourceType) or resource in bank.slots:
                    continue
                while bank.getResource(slot):
                    if slot > 255:
                        return True
                    slot = slot + 1

                bank.setResource(slot, resource)

            self.selectedBankIndex = bankNumber
            self.objectSet.saveOnDelete()
            return True
        return False

    # @trace
    def ensureSlotVisible(self, iSlot):
        bounds = Rect(self.bankPage.slotBounds(iSlot))
        bounds.pos += self.bankPage.absPos
        self.slotScrollContainer.ensureRectVisible(bounds)


class Bumnail(Thumbnail):

    # @trace
    def __init__(self, resource, sourceSlot):
        self.slotResource = resource
        texResource, _ = getThumbnailResourceAndTextForResource(resource)
        Thumbnail.__init__(self, texResource, 'None', False)
        self.sourceSlot = sourceSlot
        self.ignoreInput = True


class BankEditor(ResizableWidget):
    isStickyable = True

    # @trace
    def onCloseAction(self):
        saveData = {}
        saveData['viewType'] = self.viewType
        saveData['selectedResourceType'] = self.selectedResourceType.__name__
        saveData['selectedBankName'] = self.bankSelector.selectedBankName
        saveData['nColumns'] = self.nColumns
        d3script.setPersistentValue("state",saveData,"ObjectBanks")

    # @trace
    def loadState(self):
        try:
            loadData = d3script.getPersistentValue("state","ObjectBanks")
            self.viewType = loadData['viewType']
            selectedTypeName = loadData['selectedResourceType'].encode('utf-8')
            self.setResourceType(self.nameToResourceType(selectedTypeName), True)
            sel = loadData.get('selectedBankName', None)
            if sel:
                self.bankSelector.selectedBankName = sel
            if 'nColumns' in loadData:
                self.nColumns = loadData['nColumns']
            return True
        except:
            return False

        return

    # @trace
    def _initParams(self):
        return {'resourceType': self.selectedResourceType.__name__, 'view': self.viewType, 'nColumns': self.nColumns, 'initSize': self.initSize}

    # @trace
    def __init__(self, resourceType=None,resourceTypes=None, selectionFunc=None, startBank = 0, view=0, nColumns=0, initSize=Vec2()):
        ResizableWidget.__init__(self)
        self.arrangeVertical()
        if resourceTypes:
            self.resourceTypes = resourceTypes
        else:
            self.resourceTypes = defaultResourceTypes

        self.titleButton = TitleButton('Object Bank Editor')
        self.titleButton.popupMenuAction.add(self.popupMenu)
        self.titleButton.hasOptionButton = True
        self.add(self.titleButton)
        if initSize.x == 0 or initSize.y == 0:
            initSize = d3gui.root.size / 2
        self.initSize = initSize
        self.minConstraint = Vec2(340, 16) * d3gui.dpiScale
        self.objectViewSize = Vec2(initSize.x, 400 * d3gui.dpiScale.y)
        self.selectedResourceType = self.nameToResourceType(resourceType)
        self.searchString = ''
        self.optionsWidget = Widget()
        self.optionsWidget.arrangeHorizontal()
        self.typeVB = ValueBox(lambda : self.resourceTypes.index(self.selectedResourceType), lambda index: self.setResourceType(self.resourceTypes[index]))
        sortedNames, sortedIndices = zip(*sorted((obViewStyle(t).friendlyDisplayName, i) for i, t in enumerate(self.resourceTypes)))
        self.typeVB.setOptionsWithValues(sortedNames, sortedIndices)
        self.titleButton.add(self.typeVB)
        vb = ValueBox(self, 'searchString')
        vb.changeAction.add(self.searchValueChanged)
        self.optionsWidget.add(Field('Search',vb))
        self.add(self.optionsWidget)
        self.bankWidget = Widget()
        self.bankWidget.arrangeVertical()
        self.add(self.bankWidget)
        self._viewType = view
        self.highlightSlot = -1
        self.nColumns = 10
        self.oldNColumns = -1
        self.lastSelectedBankPageNameForResourceType = {}
        self.bankSelector = None
        self.objectView = None
        self.pos = Vec2(d3gui.root.size.x,0)
        self.selectionFunc = selectionFunc
        self.objectViewPos = Vec2(0, 0)
        self.objectViewGroup = CollapsableWidget('Resources', 'Resources')
        self.add(self.objectViewGroup)
        self.updateAction.add(self.onUpdate)
        self.closeAction.add(self.onCloseAction)
        self.constraintChangedAction.add(self.onConstraintChanged)
        if not self.loadState():
            self.setResourceType(VideoClip, True)
        if resourceType:
           self.setResourceType(self.nameToResourceType(resourceType), True)
        if nColumns > 0:
            self.nColumns = nColumns
        self.bankSelector.selectedBankIndex = startBank
        self.constraintSize = initSize
        self.hasSetConstraint = False
        self.computeAllMinSizes()
        self.arrangeAll()
        self.overrideAssertConstraint = self.customAssertConstraint
        return


    def searchValueChanged(self):
        bankWidgets = self.childrenOfTypeRecursive(OBBankThumbnails)
        if len(bankWidgets) > 0:
            bankWidgets[0].deferredRenderer.dirty = True
        
    # @trace
    def popupMenu(self):
        menu = PopupMenu('options')
        menu.pos = d3gui.cursorPos + Vec2(32, 0)
        menu.add(Field('View', ValueBox(self, 'viewType', [tr('Grid'), tr('Half-width Grid'), tr('List')])))
        vb = ValueBox(self, 'nColumns')
        vb.changeAction.add(self.onNColumnsChanged)
        menu.add(Field('Columns', vb))
        d3gui.root.add(menu)


    def applySelection(self, item):
        if self.selectionFunc != None:
            self.selectionFunc(item)

    # @trace
    def onUpdate(self):
        self.typeVB.pos = Vec2(self.titleButton.closeButton.size.x * 1.5, 0)
        if self.hasSetConstraint == False:
            self.onConstraintChanged()
        if self.nColumns != self.oldNColumns:
            self.oldNColumns = self.nColumns
            self.onNColumnsChanged()
        #if self.objectViewFloating:
        #    self.objectViewPos = self.objectView.pos

    # @trace
    def onConstraintChanged(self):
        self.maxSize = self.constraintSize
        scrollers = findChildrenInTree(self, ScrollWidget2)
        if len(scrollers) >= 1:
            self.arrangeAll()
        self.onNColumnsChanged()
        self.initSize = self.constraintSize
        self.hasSetConstraint = True

    # @trace
    def onNColumnsChanged(self):
        self.nColumns = max(self.nColumns, 1)
        self.bankSelector.onDirty(None)
        self.bankSelector.arrangeAll()
        self.objectView.constraintSize = self.objectViewSize
        self.customAssertConstraint()
        return

    # @trace
    def nameToResourceType(self, name):
        return ([ type for type in self.resourceTypes if type.__name__ == name ] or [self.resourceTypes[0]])[0]



    # @trace
    def setResourceType(self, resourceType, forceRefresh=False):
        if self.selectedResourceType != resourceType or forceRefresh:
            self.selectedResourceType = resourceType
            self.objectSet = OBObjectSet.findOrAddSet(self.selectedResourceType.__name__)
            if self.bankSelector:
                self.bankSelector.close()
            self.bankSelector = BankSelector(self)
            self.bankWidget.add(self.bankSelector)
            lastSelected = self.lastSelectedBankPageNameForResourceType.get(resourceType, None)
            if lastSelected:
                self.bankSelector.selectedBankName = lastSelected
            else:
                self.bankSelector.selectedBankName = None
            self.addObjectView()
            self.onConstraintChanged()
        return

    # @trace
    def addObjectView(self):
        if self.objectView:
            self.objectView.close()

        if self.objectViewGroup:
            self.objectViewGroup.hidden = True


        if issubclass(self.selectedResourceType,Resource):
            self.objectView = ObjectView(self.selectedResourceType.__name__).canClose(False).allowNull(True, 'None')
            
            if issubclass(self.selectedResourceType,SuperLayer):
                pass
                #self.objectView.setFilter((lambda lay: (lay.container == None) and (lay.track == None) and (len(lay.owners) > 0)))
             
        else:
            #need to make an "objectView" for presets
            self.objectView = PresetObjectView()
            self.objectView.bankSelector = self.bankSelector
            self.objectView.maxSize.y = self.objectViewSize.y
        

        self.objectViewGroup.hidden = False
        self.objectViewGroup.add(self.objectView)

    # @trace
    def customAssertConstraint(self):
        """ Override default behaviour from resizableWidget so we can fit the various widgets to the editor better """
        self.computeAllMinSizes()
        self.arrangeAll()
        if self.objectView.contents.maxSize.y > self.objectView.maxSize.y:
            self.objectView.contents.maxSize.y = self.objectView.maxSize.y
        limitedConstraint = self.constraintSize
        if limitedConstraint.y > d3gui.root.size.y:
            limitedConstraint.y = d3gui.root.size.y
        if limitedConstraint.x > d3gui.root.size.x:
            limitedConstraint.x = d3gui.root.size.x
        bankPageHeight = limitedConstraint.y - (self.size.y - self.bankSelector.slotScrollContainer.size.y)
        absMinHeight = 10 * d3gui.dpiScale.y
        if bankPageHeight < absMinHeight:
            bankPageHeight = absMinHeight
        if bankPageHeight != self.bankSelector.slotScrollContainer.size.y:
            self.bankSelector.slotScrollContainer.maxSize.y = bankPageHeight
        self.bankSelector.slotScrollContainer.maxSize.x = limitedConstraint.x
        self.bankSelector.selectMenu.minSize.x = limitedConstraint.x
        self.bankSelector.selectMenu.maxSize.x = limitedConstraint.x
        self.objectViewSize.x = limitedConstraint.x
        self.objectViewSize.y = self.objectView.maxSize.y

    @property
    # @trace
    def viewType(self):
        return self._viewType

    @viewType.setter
    # @trace
    def viewType(self, viewType):
        if self._viewType != viewType:
            self._viewType = viewType
            self.bankSelector.createOBBankThumbnails()
            self.bankSelector.bankPage.refresh()

def initCallback():
    d3script.log("ObjectBanks","ObjectBanks Loaded")

SCRIPT_OPTIONS = {
    "minimum_version" : 23, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Preset Bank", # Display name of script
            "group" : "Object Banks", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Open an PMPreset bank", #text for help system
            "callback" : presetPopup, # function to call for the script
        },
        {
            "name" : "Bank For View", # Display name of script
            "group" : "Object Banks", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "binding" : "KeyPress,Alt,Z", # Keyboard shortcut
            "bind_globally" : True, # binding should be global
            "help_text" : "Open a bank for a current open Object View", #text for help system
            "callback" : openBankForObjectViews, # function to call for the script
        },
        {
            "name" : "Open Bank Editor", # Display name of script
            "group" : "Object Banks", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Open editor for banks", #text for help system
            "callback" : openBank, # function to call for the script
        },
        {
            "name" : "Apply Preset for Path", # Display name of script
            "group" : "Object Banks", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Apply an adhoc preset for a resource - requires a path", #text for help system
            "callback" : applyPresetForPath, # function to call for the script
        }
        ]

    }