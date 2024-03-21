# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.8.3 (tags/v3.8.3:6f8c832, May 13 2020, 22:37:02) [MSC v.1924 64 bit (AMD64)]
# Embedded file name: C:\blip\dev\scripts\gui\sockpuppet\editor_bank.py
# Compiled at: 2023-03-03 13:17:06
from gui.separator import Separator
import d3
d3module = d3
from d3 import *
import collections, random, json
from gui.inputmap import *
import PresetManager

BANKSIZE = 1000
THUMBPATH = "objects/dxtexture/objectthumbnails/"
class OBViewStyle():

    def __init__(self, friendlyDisplayName, canAutoPopulate=False, showNamesInListView=True, showFileTypes=True, info=lambda r: ''):
        self.friendlyDisplayName = friendlyDisplayName
        self.canAutoPopulate = canAutoPopulate
        self.showNamesInListView = showNamesInListView
        self.showFileTypes = showFileTypes
        self._info = info

    def info(self, resource):
        if isinstance(resource, Indirection):
            return 'Indirection'
        return self._info(resource)


OBResourceViewStyles = {VideoClip: OBViewStyle(tr('Video Clip'), canAutoPopulate=True), 
   DxTexture: OBViewStyle(tr('Texture'), canAutoPopulate=True), 
   LogicalAudioOutDevice: OBViewStyle(tr('Logical Audio Out Device'), showNamesInListView=False, showFileTypes=False), 
   Projection: OBViewStyle(tr('Mapping'), showNamesInListView=False, showFileTypes=False), 
   DfxFile: OBViewStyle(tr('Notch File')), 
   AudioTrack: OBViewStyle(tr('Audio Track'), canAutoPopulate=True),
   PMPreset: OBViewStyle('PM Preset', canAutoPopulate=True)}


def findChildrenInTree(widget, t):
    if type(widget) == t:
        return [widget]
    result = []
    for c in widget.children:
        cf = findChildrenInTree(c, t)
        result = result + cf

    return result


defaultResourceTypes = [ cls for cls in OBResourceViewStyles.keys() ]

def obViewStyle(cls):
    return OBResourceViewStyles.get(cls, None) or OBViewStyle(cls.__username__)


class OBBankThumbnails(Widget):

    def __init__(self, bankSelector):
        Widget.__init__(self)
        self.bankSelector = bankSelector
        self.style = obViewStyle(self.bankSelector.selectedResourceType)
        self.deferredRenderer = DeferredRenderer()
        self.renderAction.add(self.render)
        self.updateAction.add(self.update)
        #Need to update this bankChange action
        #bankChangeAction = resourceManager.anyResourceChangedAction(DmxBank)
        #bankChangeAction.add(self.markDirty)
        self.closeAction.add(lambda : bankChangeAction.remove(self.markDirty))
        self.closeAction.add(lambda : setattr(self, 'deferredRenderer', None))

    def markDirty(self, resource):
        #if resource is self.bankSelector.bank:
        #    self.deferredRenderer.dirty = True
        self.deferredRenderer.dirty = True

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

    def screenPosToBankSlot(self, pos):
        item = self.deferredRenderer.itemAtPoint(pos - self.absPos, 'slot')
        if item:
            slot = item.data[0]
        else:
            slot = None
        return (
         self.bankSelector.selectedBankIndex, slot)

    def render(self):
        viewMat = Mat()
        viewMat.setTranslation(Vec(self.absPos))
        if self.deferredRenderer.dirty:
            self.deferredRenderer.dirty = False
            self.refresh()
        self.deferredRenderer.render(viewMat)

    def acceptDrop(self, dropped):
        bank, slot = self.screenPosToBankSlot(d3gui.cursorPos)
        if slot is not None:
            widget = dropped['formats'].get('widget', lambda : None)()
            if isinstance(widget, ObjectViewThumbnail):
                if widget.resource is None or isinstance(widget.resource, self.bankSelector.selectedResourceType) or isinstance(widget.resource, ResourceSequence) and issubclass(widget.resource.expectedType, self.bankSelector.selectedResourceType) or isinstance(widget.resource, Indirection):
                    self.bankSelector.bank.setResource(slot, widget.resource)
                    return True
        return False

    def acceptArrow(self, arrowSource):
        bank, slot = self.screenPosToBankSlot(d3gui.cursorPos)
        if slot is None:
            return False
        else:
            return self.bankSelector.acceptObjects(arrowSource, bank, slot)

    @binding(MouseDrag, 'Ctrl', Mouse.Left)
    def dragCopySelection(self, state, startPos, pos):
        """Copy the element in the slot under the cursor to another slot"""
        self.dragSelection(state, startPos, pos, True)

    @binding(MouseDrag, Mouse.Left)
    def dragMoveSelection(self, state, startPos, pos):
        """Move the element in the slot under the cursor to another slot"""
        self.dragSelection(state, startPos, pos, False)

    @binding(MouseClick, Mouse.Right)
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
            elif isinstance(resource,PMPreset):
                    #Add PMPreset editor call here
                    pass
            
    @binding(MouseClick, Mouse.Right)
    def applySelection(self):
        """Edit the resource in the slot under the cursor"""
        item = self.deferredRenderer.itemAtPoint(d3gui.cursorPos - self.absPos, 'slot')
        if item:
            iSlot = item.data[0]
            self.bankSelector.bank.performAction(iSlot)
           
            
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
                    bank.setResource(dropSlot, self.bumnail.resource)
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
    colourDefault = Colour.blackZeroAlpha
    colourHighlight = colours('widget_highlight_background')
    colourError = colours('widget_attention_bg')

    def slotBounds(self, iSlot):
        for slotItem in self.deferredRenderer.allItemsById('slot'):
            if slotItem.data[0] == iSlot:
                return slotItem.bounds

        return Rect()

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
        return self.colourDefault

    def deferSlotContainer(self, iSlot, bounds):
        slotItem = DeferredRendererItem()
        slotItem.renderType = DeferredRendererItem.RenderType_Quad
        slotItem.id = 'slot'
        slotItem.data = (iSlot,)
        slotItem.bounds = bounds
        slotItem.colCallable = lambda : self.slotColour(iSlot)
        self.deferredRenderer.deferItem(slotItem)


class OBBankThumbnails_Grid(OBBankThumbnails):

    THUMBSIZE = 80


    def __init__(self, bankSelector, half=False):
        OBBankThumbnails.__init__(self, bankSelector)
        self.half = half

    def refresh(self):
        self.deferredRenderer.reset()
        #if ThumbnailSystem.supportsThumbnails(self.bankSelector.selectedResourceType):
        #    width = self.bankSelector.bankEditor.constraintSize.x / 1.1
        #    cellsWide = self.bankSelector.bankEditor.nColumns
        #    cellWidth = max(64 * d3gui.dpiScale.x, width / cellsWide)
        #    cellHeight = min(64 * d3gui.dpiScale.x, cellWidth) + d3gui.font.maxHeightInPixels
        #else:
        #    cellWidth = 200 * d3gui.dpiScale.x
        #    cellHeight = d3gui.font.maxHeightInPixels
        #    cellsWide = 4
        width = self.bankSelector.bankEditor.constraintSize.x / 1.1
        cellsWide = self.bankSelector.bankEditor.nColumns
        cellWidth = max(OBBankThumbnails_Grid.THUMBSIZE * d3gui.dpiScale.x, width / cellsWide)
        cellHeight = min(OBBankThumbnails_Grid.THUMBSIZE * d3gui.dpiScale.x, cellWidth) + d3gui.font.maxHeightInPixels

        if self.half:
            cellWidth *= 2
            cellsWide /= 2
            cellsWide = max(cellsWide, 1)
        cellsHigh = int(BANKSIZE / cellsWide)
        cellSize = Vec2(float(cellWidth), float(cellHeight)).round(1)
        cellSizeWithBorder = cellSize * Vec2(1.1, 1.1)
        self.minSize = cellSizeWithBorder * Vec2(cellsWide, cellsHigh)
        bank = self.bankSelector.bank
        cellColour = Colour(0.25, 0.25, 0.25, 0.75)
        dxt = resourceManager.allResources(DxTexture)

        for iSlot in range(BANKSIZE):
            pos = Vec2(int(iSlot % cellsWide), int(iSlot / cellsWide)) * cellSizeWithBorder
            bounds = Rect(pos, cellSize)
            self.deferSlotContainer(iSlot, bounds)
            resource = bank.getResource(iSlot)
            self.deferredRenderer.deferQuad('', None, Rect(pos, cellSize * 1.06), cellColour)
            if (resource) and (isinstance(resource,Resource)) and (ThumbnailSystem.supportsThumbnails(type(resource))):
                self.deferredRenderer.deferThumbnailQuad('', None, bounds, resource)
                text = '%d: %s' % (iSlot, resource.path.filenameAndExtension if self.style.showFileTypes else resource.path.filename)
            elif (resource):
                if isinstance(resource,Resource):
                    matchName = resource.path.filename
                    matchType = type(resource).__name__
                else:
                    matchName = resource.name
                    matchType = 'PMPreset'
                
                texResource = filter(lambda x: x.path == THUMBPATH + matchType + '/' + matchName + '.png')
                if len(texResource > 0): 
                    texResource = texResource[0]
                else:
                    texResource = filter(lambda x: x.path == THUMBPATH + 'defaults' + '/' + matchType + '.png')[0]

                self.deferredRenderer.deferThumbnailQuad('', None, bounds, resource)
                text = '%d: %s' % (iSlot, matchName)

            else:
                text = str(iSlot)
            self.deferredRenderer.deferBoundedText('', None, bounds.bl, SlugFont.AlignLeft, SlugFont.AlignBottom, bounds.size.x, text)

        return


class OBBankThumbnails_List(OBBankThumbnails):

    LISTWIDTH = 300
    LISTHEIGHT = 64

    def refresh(self):
        self.deferredRenderer.reset()
        cellSize = Vec2(OBBankThumbnails_List.LISTWIDTH, OBBankThumbnails_List.LISTHEIGHT) * d3gui.dpiScale
        cellSizeWithBorder = cellSize * Vec2(1.1, 1.1)
        self.minSize = cellSizeWithBorder * Vec2(1, BANKSIZE)
        bank = self.bankSelector.bank
        for iSlot in range(BANKSIZE):
            pos = Vec2(0, iSlot) * cellSizeWithBorder
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

    def __init__(self, bankEditor, initialBankName=None):
        Widget.__init__(self)
        self.arrangeVertical()
        self.bankEditor = bankEditor
        self._selectedBankName = None
        action = resourceManager.resourceChangedAction(self.objectSet)
        action.add(self.onDirty)
        self.closeAction.add(lambda : action.remove(self.onDirty))
        self.populate(initialBankName)
        return

    def onDirty(self, resource):
        self.populate(self.selectedBankName)
        self.arrangeAll()

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

        def onSelect(name):
            self._selectedBankName = name
            self.bankPage.refresh()

        self.selectMenu.selectAction.add(onSelect)
        for bankIndex, button in zip(bankIndices, self.selectMenu.allButtons):
            button.popupMenuAction.clear()
            button.popupMenuAction.add(lambda bankIndex=bankIndex: self.bankContextMenu(bankIndex))
            button.acceptArrowDelegate = lambda arrowSource, bankIndex=bankIndex: self.acceptObjects(arrowSource, bankIndex, 0)

        self.slotScrollContainer = ScrollWidget2(name='slotScrollContainer', renderBack=True, maxSize=Vec2(1, 1))
        self.slotScrollContainer.contents.arrangeVertical()
        self.add(self.slotScrollContainer)
        self.createOBBankThumbnails()
        self.selectMenu.selectByName(initialBankName)
        return

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
    def objectSet(self):
        return self.bankEditor.objectSet

    @property
    def bank(self):
        return self.objectSet.getBank(self.selectedBankIndex)

    @property
    def selectedBankIndex(self):
        return self.bankIndices[self._selectedBankName]

    @selectedBankIndex.setter
    def selectedBankIndex(self, iBank):
        for key, value in self.bankIndices.iteritems():
            if value == iBank:
                self.selectedBankName = key

    @property
    def selectedBankName(self):
        return self._selectedBankName

    @selectedBankName.setter
    def selectedBankName(self, bankName):
        self.selectMenu.selectByName(bankName)

    @property
    def selectedResourceType(self):
        return self.bankEditor.selectedResourceType

    def bankContextMenu(self, bankIndex):

        def wrapBankString(nw):
            nw.textBox.allow('0123456789-*,')
            return nw

        self.contextMenuSelectedBankIndex = bankIndex
        menu = PopupMenu(TFormat('Options (bank {0:d})', bankIndex))
        menu.add(NameWidget('Rename:', self.objectSet.getBank(bankIndex).name, self.onContextMenuBankName))
        menu.add(NameWidget('Duplicate:', '0', self.onContextMenuCopyBankTo))
        menu.add(NameWidget('New Bank:', '0', self.onCreateNewBank))
        if obViewStyle(self.selectedResourceType).canAutoPopulate:
            menu.add(NameWidget('Auto-populate Banks From Directory:', self.objectSet.autoPopulateFolder, self.onContextMenuAutoPopulateBanks))
        menu.item('Save Manifest', self.onContextMenuWriteManifest)
        rangeHelpText = tr('Specify a comma-separated list, range or * for all banks')
        menu.add(wrapBankString(NameWidget('Reset Bank(s):', str(bankIndex), self.onContextMenuResetBank).setHelpText(rangeHelpText)))
        menu.add(wrapBankString(NameWidget('Remove Missing:', str(bankIndex), self.onContextMenuRemoveMissing).setHelpText(rangeHelpText)))
        menu.add(wrapBankString(NameWidget('Delete Bank(s):', str(bankIndex), self.onContextMenuDeleteBank).setHelpText(rangeHelpText)))
        d3gui.root.add(menu)
        menu.pos = d3gui.cursorPos + Vec2(64, -64)

    def onContextMenuBankName(self, name):
        op = Undoable('Rename Bank')
        self.bankIndices[name] = self.contextMenuSelectedBankIndex
        self.objectSet.getBank(self.contextMenuSelectedBankIndex).name = name
        originalBankIndex = self.selectedBankIndex
        self.populate()
        self.selectedBankIndex = originalBankIndex
        self.objectSet.saveOnDelete()

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
                d3.alertError('A bank with that index already exists')
            elif bankIndex < 0 or bankIndex > 255:
                d3.alertError('Bank index must be between 0 and 255')
            else:
                self.objectSet.addBank(bankIndex, bankName)
        except ValueError:
            d3.alertError('Bank index must be numeric')

    def onContextMenuWriteManifest(self):
        type = self.selectedResourceType
        text = 'DMX file manifest for type ' + type.__name__ + ':\n'
        for iBank in range(0, len(self.objectSet.banks)):
            bank = self.objectSet.getBank(iBank)
            if bank:
                text = text + 'bank ' + str(iBank)
                if bank.name != '':
                    text = text + ':' + bank.name
                text = text + ':\n'
                nWritten = 0
                for i in range(0, 256):
                    resource = bank.getResource(i)
                    if resource:
                        nWritten = nWritten + 1
                        path = str(resource.path)
                        if type == VideoClip:
                            path = str(resource.file.path)
                        text = text + '   ' + str(i) + ' : ' + path + '\n'

                if nWritten == 0:
                    text = text + ' *** no files ***\n'
                text = text + '\n'

        import os
        try:
            os.mkdir('output')
        except:
            pass

        pathAndFilename = os.path.join('output\\', 'd3 bank manifest ' + type.__name__ + '.txt')
        out = open(pathAndFilename, 'w')
        out.write(text)
        alertNotificationSystem.overlayMessage('%s manifest written to\n%s' % (type.__name__, os.path.join(d3.projectPaths.folderName(), pathAndFilename)))

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
            d3.alertError('Bank index must be numeric')
            return

        copyFromBankIndex = self.contextMenuSelectedBankIndex
        if self.objectSet.getBank(copyToBankIndex):
            d3.alertError('A bank with that index already exists')
        elif copyToBankIndex < 0 or copyToBankIndex > 255:
            d3.alertError('Bank index must be between 0 and 255')
        else:
            copyFromBank = self.objectSet.getBank(copyFromBankIndex)
            copyToBank = self.objectSet.addBank(copyToBankIndex, copyToBankName)
            for slot in range(256):
                resource = copyFromBank.getResource(slot)
                copyToBank.setResource(slot, resource)

    def onContextMenuAutoPopulateBanks(self, baseFolder):
        op = Undoable('auto-populate banks')
        self.objectSet.autoPopulateFolder = baseFolder
        self.objectSet.autoPopulateAllBanks()

    def onContextMenuResetBank(self, banks):
        op = Undoable('Reset Bank(s)')
        markDirty(self.objectSet)
        for bankIndex in self.banksFromString(banks):
            for slot in range(256):
                self.objectSet.getBank(bankIndex).setResource(slot, None)

        return

    def onContextMenuRemoveMissing(self, banks):
        op = Undoable('Remove Missing from Bank(s)')
        markDirty(self.objectSet)
        for bankIndex in self.banksFromString(banks):
            for slot in range(256):
                bank = self.objectSet.getBank(bankIndex)
                resource = bank.getResource(slot)
                if resource and (resource.isNotFoundLocal or resource.isIncomplete):
                    bank.setResource(slot, None)

        return

    def onContextMenuDeleteBank(self, banks):
        op = Undoable('Delete Bank(s)')
        for bankIndex in self.banksFromString(banks):
            if self.objectSet.getNumberOfBanks() > 1:
                self.objectSet.removeBank(bankIndex)
                if bankIndex == self.selectedBankIndex:
                    self.bankEditor.lastSelectedBankPageNameForResourceType[self.selectedResourceType] = None
                    self.populate()
            else:
                d3.alertError('Cannot remove the last bank')

        return

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

    def ensureSlotVisible(self, iSlot):
        bounds = Rect(self.bankPage.slotBounds(iSlot))
        bounds.pos += self.bankPage.absPos
        self.slotScrollContainer.ensureRectVisible(bounds)


class Bumnail(Thumbnail):

    def __init__(self, resource, sourceSlot):
        Thumbnail.__init__(self, resource, 'None', False)
        self.sourceSlot = sourceSlot
        self.ignoreInput = True


class BankEditor(ResizableWidget):
    isStickyable = True

    def onCloseAction(self):
        self.updateParameterTrackingSubscription(False)
        path = 'internal/%s/gui/%s.state.json' % (d3NetManager.localMachine.hostname, self.__class__.__name__)
        print('save state', path)
        saveData = {}
        saveData['viewType'] = self.viewType
        saveData['selectedResourceType'] = self.selectedResourceType.__name__
        saveData['selectedBankName'] = self.bankSelector.selectedBankName
        saveData['nColumns'] = self.nColumns
        resourceManager.package.write(path, bytearray(json.dumps(saveData)))

    def loadState(self):
        path = 'internal/%s/gui/%s.state.json' % (d3NetManager.localMachine.hostname, self.__class__.__name__)
        try:
            rawLoadData = resourceManager.package.read(path)
            loadData = json.loads(bytearray(rawLoadData).decode('utf-8'))
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

    def _initParams(self):
        return {'resourceType': self.selectedResourceType.__name__, 'view': self.viewType, 'nColumns': self.nColumns, 'initSize': self.initSize}

    def __init__(self, resourceType=None, view=0, nColumns=16, initSize=Vec2()):
        ResizableWidget.__init__(self)
        self.arrangeVertical()
        self.titleButton = TitleButton('Bank Editor')
        self.titleButton.popupMenuAction.add(self.popupMenu)
        self.titleButton.hasOptionButton = True
        self.add(self.titleButton)
        if initSize.x == 0 or initSize.y == 0:
            initSize = d3gui.root.size / 2
        self.initSize = initSize
        self.minConstraint = Vec2(340, 16) * d3gui.dpiScale
        self.objectViewSize = Vec2(initSize.x, 400 * d3gui.dpiScale.y)
        sockPuppet = subsystems.getSystem(SockPuppetSystem)
        reportedResourceTypes = [ t for t in sockPuppet.registry.classes() ]
        objectSetResourceTypes = [ objSet.classType for objSet in resourceManager.allResources(DmxObjectSet) ]
        self.resourceTypes = list(set(reportedResourceTypes + defaultResourceTypes + objectSetResourceTypes))
        self.selectedResourceType = self.nameToResourceType(resourceType)
        self.searchString = ''
        self.optionsWidget = Widget()
        self.optionsWidget.arrangeHorizontal()
        self.typeVB = ValueBox(lambda : self.resourceTypes.index(self.selectedResourceType), lambda index: self.setResourceType(self.resourceTypes[index]))
        sortedNames, sortedIndices = zip(*sorted((obViewStyle(t).friendlyDisplayName, i) for i, t in enumerate(self.resourceTypes)))
        self.typeVB.setOptionsWithValues(sortedNames, sortedIndices)
        self.titleButton.add(self.typeVB)
        self.optionsWidget.add(Field('Search', ValueBox(self, 'searchString')))
        self.add(self.optionsWidget)
        self.bankWidget = Widget()
        self.bankWidget.arrangeVertical()
        self.add(self.bankWidget)
        self._viewType = view
        self.highlightSlot = -1
        self.nColumns = nColumns
        self.oldNColumns = -1
        self.lastSelectedBankPageNameForResourceType = {}
        self.bankSelector = None
        self.objectView = None
        self.objectViewFloating = d3os.DebugOptions.options().defaultDetachedBankEditorResources()
        self.objectViewPos = Vec2(0, 0)
        self.objectViewGroup = CollapsableWidget('Resources', 'Resources')
        self.add(self.objectViewGroup)
        self.onParameterTrackingChanged()
        self.updateAction.add(self.onUpdate)
        self.closeAction.add(self.onCloseAction)
        self.constraintChangedAction.add(self.onConstraintChanged)
        if not self.loadState():
            self.setResourceType(VideoClip, True)
        self.constraintSize = initSize
        self.hasSetConstraint = False
        self.computeAllMinSizes()
        self.arrangeAll()
        self.overrideAssertConstraint = self.customAssertConstraint
        return

    def popupMenu(self):
        menu = PopupMenu('options')
        menu.pos = d3gui.cursorPos + Vec2(32, 0)
        menu.add(Field('View', ValueBox(self, 'viewType', [tr('Grid'), tr('Half-width Grid'), tr('List')])))
        vb = ValueBox(self, 'nColumns')
        vb.changeAction.add(self.onNColumnsChanged)
        sockPuppet = subsystems.getSystem(SockPuppetSystem)
        menu.add(Field('Columns', vb))
        vb = ValueBox(sockPuppet.library, 'parameterTracking', ['Off', 'On'])
        vb.changeAction.add(self.onParameterTrackingChanged)
        menu.add(Field('Parameter tracking', vb))
        menu.add(Field('Auto-Populate', ValueBox(sockPuppet.library, 'enableAutoPopulate', ['Disable', 'Enable'])))
        title = tr('Detach Resource View')
        if self.objectViewFloating:
            title = tr('Attach Resource View')
        menu.add(Button(title, self.toggleFloatingObjectView))
        d3gui.root.add(menu)

    def toggleFloatingObjectView(self):
        self.objectViewFloating = not self.objectViewFloating
        self.setResourceType(self.selectedResourceType, True)

    def onUpdate(self):
        self.typeVB.pos = Vec2(self.titleButton.closeButton.size.x * 1.5, 0)
        if self.hasSetConstraint == False:
            self.onConstraintChanged()
        if self.nColumns != self.oldNColumns:
            self.oldNColumns = self.nColumns
            self.onNColumnsChanged()
        if self.objectViewFloating:
            self.objectViewPos = self.objectView.pos

    def onConstraintChanged(self):
        self.maxSize = self.constraintSize
        scrollers = findChildrenInTree(self, ScrollWidget2)
        if len(scrollers) >= 1:
            self.arrangeAll()
        self.onNColumnsChanged()
        self.initSize = self.constraintSize
        self.hasSetConstraint = True

    def onNColumnsChanged(self):
        self.nColumns = max(self.nColumns, 1)
        self.bankSelector.onDirty(None)
        self.bankSelector.arrangeAll()
        self.objectView.constraintSize = self.objectViewSize
        self.customAssertConstraint()
        return

    def onParameterTrackingChanged(self):
        sockPuppet = subsystems.getSystem(SockPuppetSystem)
        self.updateParameterTrackingSubscription(sockPuppet.library.parameterTracking)

    def updateParameterTrackingSubscription(self, on):
        sockPuppet = subsystems.getSystem(SockPuppetSystem)
        if on:
            sockPuppet.singleChangedPropertyAction.add(self.onParameterChanged)
        else:
            sockPuppet.singleChangedPropertyAction.remove(self.onParameterChanged)
            self.highlightSlot = -1

    def onParameterChanged(self, dmxProperty):
        sockPuppet = subsystems.getSystem(SockPuppetSystem)
        if dmxProperty.type == DmxProperty.DmxBankSlot:
            self.setResourceType(self.nameToResourceType(sockPuppet.singleChangedType))
            self.bankSelector.selectedBankIndex = sockPuppet.singleChangedValue(0)
            self.highlightSlot = sockPuppet.singleChangedValue(1)
            self.bankSelector.ensureSlotVisible(self.highlightSlot)
        else:
            self.highlightSlot = -1

    def nameToResourceType(self, name):
        return ([ type for type in self.resourceTypes if type.__name__ == name ] or [self.resourceTypes[0]])[0]

    def setResourceType(self, resourceType, forceRefresh=False):
        if self.selectedResourceType != resourceType or forceRefresh:
            self.selectedResourceType = resourceType
            sockPuppet = subsystems.getSystem(SockPuppetSystem)
            self.objectSet = sockPuppet.library.findOrAddSet(self.selectedResourceType.__name__)
            if self.bankSelector:
                self.bankSelector.close()
            self.bankSelector = BankSelector(self)
            self.bankWidget.add(self.bankSelector)
            lastSelected = self.lastSelectedBankPageNameForResourceType.get(resourceType, None)
            if lastSelected:
                self.bankSelector.selectedBankName = lastSelected
            else:
                self.bankSelector.selectedBankName = next(k for k, v in self.bankSelector.bankIndices.iteritems())
            self.addObjectView()
            self.onConstraintChanged()
        return

    def addObjectView(self):
        if self.objectView:
            self.objectView.close()
        if self.objectViewGroup:
            self.objectViewGroup.hidden = True
        self.objectView = ObjectView(self.selectedResourceType.__name__).canClose(False).allowNull(True, 'None')
        self.objectView.maxSize.y = self.objectViewSize.y
        self.objectView.contents.maxSize.y = self.objectView.maxSize.y
        self.objectView.titleButton.hidden = not self.objectViewFloating
        if self.objectViewFloating:
            self.objectView.positionNear(self.titleButton)
            self.objectViewPos = self.objectView.pos
            d3gui.root.add(self.objectView)
            self.objectView.pos = self.objectViewPos
        else:
            self.objectViewGroup.hidden = False
            self.objectViewGroup.add(self.objectView)

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
    def viewType(self):
        return self._viewType

    @viewType.setter
    def viewType(self, viewType):
        if self._viewType != viewType:
            self._viewType = viewType
            self.bankSelector.createOBBankThumbnails()
            self.bankSelector.bankPage.refresh()


import core.serialise
core.serialise.registerType(BankEditor)