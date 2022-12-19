from gui.inputmap import *
from d3 import *
import d3script


class StaggerWidget(Widget):
    _staggerAmount = 0.0
    _indexLayer = 0

    def __init__(self):
        Widget.__init__(self)
        self.add(TitleButton('Stagger'))
        self.add(Field('Amount',ValueBox(self,'staggerAmount')))
        self.add(Field('IndexLayer',ValueBox(self,'indexLayer')))
        d3gui.root.add(self) 
        self.pos = Vec2(500,500)
        self.arrangeVertical()


    def doStagger(self):
        
        lays = d3script.getSelectedLayers()
        if len(lays) > 1:
            layIndex = self._indexLayer % len(lays)
            
            tStart = lays[layIndex].tStart

            for idx,lay in enumerate(lays):
                offset = abs(idx-layIndex) * self._staggerAmount / 30
                lay.tStart = tStart + offset

    @property
    def staggerAmount(self):
        #print('Setting....')
        return self._staggerAmount

    @staggerAmount.setter
    def staggerAmount(self, value):
        #print('Getting...')
        if (value != self._staggerAmount):
            self._staggerAmount = value
            self.doStagger()

    @property
    def indexLayer(self):
        #print('Setting....')
        return self._indexLayer

    @indexLayer.setter
    def indexLayer(self, value):
        #print('Getting...')
        if (value != self._indexLayer):
            self._indexLayer = value
            self.doStagger()
