from d3 import *
import d3script

def initCallback():
    d3script.log("LayerColorManager","LayerColorManager Loaded")

MODULE_NAME_CATEGORIES = [
    ( "AudioModule", "Audio","Content"),
    ( "RenderStreamModule", "RenderStream","Content"),
    ( "StageRenderModule", "StageRender","Content"),
    ( "VariableVideoModule", "Video","Content"),
    ( "VideoTriggerModule", "VideoTrigger","Content"),
    ( "VirtualLineupModule", "VirtualLineup","Content"),
    ( "WebModule", "Web","Content"),
    ( "CameraControlModule", "CameraControl","Control"),
    ( "CameraCutControl", "CameraCutControl","Control"),
    ( "ControlModule", "Control","Control"),
    ( "DmxControlModule", "DmxLightsControl","Control"),
    ( "DmxShareModule", "DmxShare","Control"),
    ( "HttpControlModule", "HttpControl","Control"),
    ( "IndirectionControl", "IndirectionControl","Control"),
    ( "MDCModule", "MDC","Control"),
    ( "MTCModule", "MTC","Control"),
    ( "MasterModule", "MasterBrightness","Control"),
    ( "DVIMatrixControlModule", "MatrixControl","Control"),
    ( "MidiNoteModule", "MidiNote","Control"),
    ( "OpenModule", "Open","Control"),
    ( "OscControlModule", "OscControl","Control"),
    ( "PlayModeModule", "PlayMode","Control"),
    ( "ProjectorControlModule", "ProjectorControl","Control"),
    ( "TargetObjectModule", "TargetObject","Control"),
    ( "IgnoreTimecodeModule", "TimecodeMode","Control"),
    ( "TrackJumpModule", "TrackJump","Control"),
    ( "TransportBrightnessLocalModule", "TransportBrightnessLocal","Control"),
    ( "TransportControlModule", "TransportControl","Control"),
    ( "TransportVolumeLocalModule", "TransportVolumeLocal","Control"),
    ( "BlurModule", "Blur","Effect"),
    ( "CDLModule", "CDL","Effect"),
    ( "ChannelRouterModule", "ChannelRouter","Effect"),
    ( "ColourAdjustModule", "ColourAdjust","Effect"),
    ( "ComposeModule", "Compose","Effect"),
    ( "EdgeFilterModule", "EdgeFilter","Effect"),
    ( "FadeModule", "Fade","Effect"),
    ( "FilmicGrainModule", "FilmicGrain","Effect"),
    ( "KaleidoscopeModule", "Kaleidoscope","Effect"),
    ( "LutModule", "Lut","Effect"),
    ( "MotionBlurModule", "MotionBlur","Effect"),
    ( "NoiseModule", "Noise","Effect"),
    ( "PixelMapModule", "PixelMap","Effect"),
    ( "PixelateModule", "Pixelate","Effect"),
    ( "ScrollModule", "Scroll","Effect"),
    ( "SpinBitmap", "SpinBitmap","Effect"),
    ( "TriggerModule", "Trigger","Effect"),
    ( "UVLookupModule", "UVLookup","Effect"),
    ( "VariableVideoTransitionModule", "VideoTransition","Effect"),
    ( "BugsModule", "Bugs","Generative"),
    ( "ChevronModule", "Chevron","Generative"),
    ( "ColourModule", "Colour","Generative"),
    ( "GradientModule", "Gradient","Generative"),
    ( "NotchModule", "Notch","Generative"),
    ( "RGBColourModule", "RGBColour","Generative"),
    ( "RadarModule", "Radar","Generative"),
    ( "TimecodeReadoutModule", "Readout","Generative"),
    ( "ScanModule", "Scan","Generative"),
    ( "StrobeModule", "Strobe","Generative"),
    ( "PongModule", "Tennis","Generative"),
    ( "TestPatternModule", "TestPattern","Generative"),
    ( "TextModule", "Text","Generative"),
    ( "TrackingMarkerModule", "TrackingMarker","Generative"),
    ( "BitmapModule", "Bitmap","Legacy"),
    ( "VideoModule", "LegacyVideo","Legacy"),
    ( "VideoTransitionModule", "LegacyVideoTransition","Legacy"),
    ( "AnimateCamera", "AnimateCameraControl","Previsualization"),
    ( "AnimateCameraPreset", "AnimateCameraPreset","Previsualization"),
    ( "ScreenPositionModule", "AnimateObjectPreset","Previsualization"),
    ( "TargetModule", "TargetControl","Previsualization"),
    ( "Target2Module", "TargetPreset","Previsualization")
]

class ColorSettings():
        
    matchCriteria = [
        'name.equals',
        'name.startsWith',
        'name.contains',
        'type.equals',
        'category.equals',
        'status.bad',
        'status.muted',
        'status.smartGroup',
        'status.group',
        'status.containedInGroup',
        'status.suppressed',
        'status.externalControl',
        'status.hasExpression',
        'status.brokenExpression',
        'none'
    ]
            
    def __init__(self,data=None):

        if (data == None):
            self.crit1 = self.matchCriteria.index('status.bad')
            self.val1 = ''
            self.color1 = Colour(0.5, 0.0, 0.0)
            self.crit2 = self.matchCriteria.index('status.muted')
            self.val2 =  ''
            self.color2 = Colour(0.125, 0.125, 0.125)
            self.crit3 = self.matchCriteria.index('status.smartGroup')
            self.val3 = ''
            self.color3 = Colour(0.392, 0.4549, 0.5)
            self.crit4 = self.matchCriteria.index('status.group')
            self.val4 = ''
            self.color4 = Colour(0.5, 0.4549, 0.392)
            self.crit5 = self.matchCriteria.index('status.externalControl')
            self.val5 =  ''
            self.color5 = Colour(0.188, 0.4392, 0.25)
            self.crit6 = self.matchCriteria.index('none')
            self.val6 = ''
            self.color6 = Colour(0.0, 0.0, 0.0)
            self.crit7 = self.matchCriteria.index('none')
            self.val7 =  ''
            self.color7 = Colour(0.0, 0.0, 0.0)
            self.crit8 = self.matchCriteria.index('none')
            self.val8 = ''
            self.color8 = Colour(0.0, 0.0, 0.0)
            self.crit9 = self.matchCriteria.index('none')
            self.val9 = ''
            self.color9 = Colour(0.0, 0.0, 0.0)
            self.crit10 = self.matchCriteria.index('none')
            self.val10 =  ''
            self.color10 = Colour(0.0, 0.0, 0.0)
            self.defaultColor = Colour(0.375,0.375,0.375)
        else:
            self.crit1 = data['crit1']
            self.val1 = data['val1']
            self.color1 = Colour(*data['color1'])
            self.crit2 = data['crit2']
            self.val2 =  data['val2']
            self.color2 = Colour(*data['color2'])
            self.crit3 = data['crit3']
            self.val3 = data['val3']
            self.color3 = Colour(*data['color3'])
            self.crit4 = data['crit4']
            self.val4 = data['val4']
            self.color4 = Colour(*data['color4'])
            self.crit5 = data['crit5']
            self.val5 =  data['val5']
            self.color5 = Colour(*data['color5'])
            self.crit6 = data['crit6']
            self.val6 = data['val6']
            self.color6 = Colour(*data['color6'])
            self.crit7 = data['crit7']
            self.val7 =  data['val7']
            self.color7 = Colour(*data['color7'])
            self.crit8 = data['crit8']
            self.val8 = data['val8']
            self.color8 = Colour(*data['color8'])
            self.crit9 = data['crit9']
            self.val9 = data['val9']
            self.color9 = Colour(*data['color9'])
            self.crit10 = data['crit10']
            self.val10 =  data['val10']
            self.color10 = Colour(*data['color10'])
            self.defaultColor = Colour(*data['defaultColor'])

    def dataRepresentation(self):
            return {
                'crit1' : self.crit1,
                'val1' : self.val1,
                'color1' : list(self.color1.toVec()),
                'crit2' : self.crit2,
                'val2' :  self.val2,
                'color2' : list(self.color2.toVec()),
                'crit3' : self.crit3,
                'val3' : self.val3,
                'color3' : list(self.color3.toVec()),
                'crit4' : self.crit4,
                'val4' : self.val4,
                'color4' : list(self.color4.toVec()),
                'crit5' : self.crit5,
                'val5' :  self.val5,
                'color5' : list(self.color5.toVec()),
                'crit6' : self.crit6,
                'val6' : self.val6,
                'color6' : list(self.color6.toVec()),
                'crit7' : self.crit7,
                'val7' :  self.val7,
                'color7' : list(self.color7.toVec()),
                'crit8' : self.crit8,
                'val8' : self.val8,
                'color8' : list(self.color8.toVec()),
                'crit9' : self.crit9,
                'val9' : self.val9,
                'color9' : list(self.color9.toVec()),
                'crit10' : self.crit10,
                'val10' :  self.val10,
                'color10' : list(self.color10.toVec()),
                'defaultColor' : list(self.defaultColor.toVec()) 
            }

def patchCalcColor(data):
    #first save settings
    d3script.setPersistentValue('LayerColorManager',data.dataRepresentation())

    def replacementCalcColor(pm,layer):
        for i in range(1,11):
            crit = ColorSettings.matchCriteria[getattr(data,'crit'+str(i))]
            
            val = getattr(data,'val'+str(i))
            color = getattr(data,'color'+str(i))
            defaultColor = getattr(data,'defaultColor')
            #print(layer.name + ':' + crit + ' defcol: ' + str(defaultColor))
            
            if crit == 'none':
                continue
            if crit == 'status.bad':
                if layer.crashed:
                    return color
                continue
            if crit == 'status.muted':
                if not layer.renderEnable:
                    return color
                continue
            if crit == 'status.smartGroup':
                if isinstance(layer,SmartGroupLayer):
                    return color
                continue
            if crit == 'status.group':
                if isinstance(layer,GroupLayer):
                    return color
                continue
            if crit == 'status.containedInGroup':
                if (layer.container != None):
                    return color
                continue
            if crit == 'status.externalControl':
                 if layer.isExternallyControlled():
                      return color
                 continue
            if crit == 'status.hasExpression':
                if type(layer) != Layer:
                   continue
                if (len(filter(lambda x: x.expression,layer.fields)) > 0):
                    return color
                continue
            if crit == 'status.brokenExpression':
                if type(layer) != Layer:
                   continue
                if (len(layer.expressionReports) > 0):
                    return color
                continue
            if crit == 'status.suppressed':
                if type(layer) != Layer:
                   continue
                brightnessField = layer.findSequence('brightness')
                if (brightnessField) and (brightnessField.expression) and (brightnessField.expression.expression == '0'):
                    return color
                continue
            if crit == 'name.equals':
                if layer.name == val:
                    return color
                continue
            if crit == 'name.startsWith':
                if layer.name.startswith(val):
                    return color
                continue
            if crit == 'name.contains':
                if val in layer.name:
                    return color
                continue
            if crit == 'type.equals':
                translatedModName = filter(lambda x: x[1] == val, MODULE_NAME_CATEGORIES)
                if len(translatedModName) == 1:
                    translatedModName = translatedModName[0][0]
                else:
                    translatedModName == None
                typeAsString = str(layer.moduleType)[11:-2]
                if (type(layer) == Layer) and ((typeAsString == val) or (typeAsString == translatedModName)):
                    return color
                continue
            if crit == 'category.equals':
                if (type(layer) != Layer):
                    continue
                typeAsString = str(layer.moduleType)[11:-2]
                category = filter(lambda x: x[0] == typeAsString, MODULE_NAME_CATEGORIES)
                if len(category) == 1:
                    category = category[0][2]
                else:
                    category = 'Misc'
                if val == category:
                    return color
                continue


        return defaultColor

    tw = d3script.getTrackWidget()
    pm = tw.layerView.presentationModel
    pm.__class__._calculateColour = replacementCalcColor
    pm.rebuildModel()
    tw.layerView.reRenderNeeded = True

class LayerColorManager(Widget):

    def __init__(self):
        Widget.__init__(self)

        colorData = d3script.getPersistentValue('LayerColorManager')

        #if no values use default
        if (not colorData):
            self.colorSettings = ColorSettings()
        else:
            self.colorSettings = ColorSettings(colorData)

        
        self.add(TitleButton('Layer Color Manager'))

        critWidget = Widget()
        valWidget = Widget()
        colorWidget = Widget()

        critWidget.add(TextLabel('Criteria'))
        valWidget.add(TextLabel('Value'))
        colorWidget.add(TextLabel('Color'))

        def minSize(size):
            return Vec2(max(300,size.x),32)
        
        def minColorSize(size):
            return Vec2(100,32)
        
        
        for i in range(1,11):
            vb = ValueBox(self.colorSettings,'crit'+str(i),self.colorSettings.matchCriteria)
            vb.overrideMinSize = minSize
            critWidget.add(vb)
            vb = ValueBox(self.colorSettings,'val'+str(i))
            vb.overrideMinSize = minSize
            valWidget.add(vb)
            vb = ValueBox(self.colorSettings,'color'+str(i))
            vb.overrideMinSize = minColorSize
            colorWidget.add(vb)

        critWidget.arrangeVertical()
        valWidget.arrangeVertical()
        colorWidget.arrangeVertical()
        
        columns = Widget()
        columns.add(critWidget)
        columns.add(valWidget)
        columns.add(colorWidget)
        columns.arrangeHorizontal()

        self.add(columns)
        self.add(Button('Save',lambda : patchCalcColor(self.colorSettings)))
        self.arrangeVertical()
        self.computeAllMinSizes()

def openManager():
    """Open a popup menu with rename options"""
    
    widget = LayerColorManager()

    d3gui.root.add(widget)
    widget.pos = (d3gui.root.size / 2) - (widget.size/2)
    widget.pos = Vec2(widget.pos[0],widget.pos[1]-100)


SCRIPT_OPTIONS = {
    "minimum_version" : 23, # Min. compatible version
    "init_callback" : initCallback, # Init callback if version check passes
    "scripts" : [
        {
            "name" : "Open Layer Color Manager", # Display name of script
            "group" : "Layer Color Manager", # Group to organize scripts menu.  Scripts menu is sorted a separated by group
            "help_text" : "Set Layer Colors", #text for help system
            "callback" : openManager, # function to call for the script
        }
        ]
    }