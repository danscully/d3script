import xml.etree.ElementTree as etree
from parameter import * 
from d3 import *
import uuid
from xml.dom import minidom
import zipfile


pers = resourceManager.allResources(DmxPersonality)

def test():
    print(generateGDTF('VariableVideoModule'))



def exportToDisk(personalityName, personalityText):
    import os
    try:
        os.mkdir('output')
    except:
        pass


    gdtfPathAndFilename = os.path.join('output\\', 'Disguise_Technologies@' + personalityName + '.gdtf')
    pathAndFilename = os.path.join('output\\', 'description.xml')
    pathAndFilename = pathAndFilename.replace('/', '_')
    # out = open(pathAndFilename, 'w')
    # out.write(personalityText)
    # out.close()
    
    with zipfile.ZipFile(gdtfPathAndFilename, 'w', zipfile.ZIP_STORED) as zipf:
            zipf.writestr("description.xml",personalityText)
            
    alertNotificationSystem.overlayMessage('%s personality written to\n%s' % (personalityName, os.path.join(d3.projectPaths.folderName(), gdtfPathAndFilename)))



def generateGDTF(className):

    personalities = filter(lambda x: x.className == className,resourceManager.allResources(DmxPersonality))
    
    #Should have some error handling here, but if we haven't found any personalities we return
    if len(personalities) == 0:
        print('No DMX Personalities found for class: ' + className)
    
    #we use the the first personality as the default for naming etc
    pers = personalities[0]
    
    # Setup XML
    root = etree.Element('GDTF', DataVersion="1.2")
    name = "Disguise Layer: " + pers.classUserName
    shortName = "D3:" + pers.className
    manufacturer = "Disguise Technologies"
    description = "Control for " + pers.classUserName + " module in Disguise media server."

    #Usings uuid3, which creates a UUID from a namespace UUID (which I generated randomly) and a string 
    namespace = uuid.UUID('{308EA87D-7164-42DE-8106-A6D273F57A51}')
    fixtureUUID = str(uuid.uuid3(namespace,className.encode()))

    #Create top level fixture type and child nodes
    fixType = etree.SubElement(root, 'FixtureType', Name=name, ShortName=shortName, LongName=name, Manufacturer=manufacturer, Description=description, FixtureTypeID=fixtureUUID, CanHaveChildren="No")
    attributeDefinitions = etree.SubElement(fixType,'AttributeDefinitions')    
    activationGroups = etree.SubElement(attributeDefinitions, 'ActivationGroups')
    featureGroups = etree.SubElement(attributeDefinitions, 'FeatureGroups')
    attributes = etree.SubElement(attributeDefinitions, 'Attributes')   
     
    geometries = etree.SubElement(fixType, 'Geometries')
    dmxModes = etree.SubElement(fixType, 'DMXModes')

    #Create Geometry
    msl = etree.SubElement(geometries, 'MediaServerLayer')
    msl.set('Name','D3ServerLayer')
    msl.set('Position','{1.000000,0.000000,0.000000,0.000000}{0.000000,1.000000,0.000000,0.000000}{0.000000,0.000000,1.000000,0.000000}{0,0,0,1}')
    
    
    #Dicts to create a unique set of Activation Groups, Feature Groups, and Features
    foundActivationGroups = {}
    foundFeatureGroups = {}
    foundFeatures = {}
    foundAttributes = {}
    
    # We define this function inline to capture above values and let us call it recursively for a Bank/Slot type property since those are diff channels
    def processProperty(p,dmxChannels,slotFlag=False):

        name = p.name
        channelOffset = p.channelOffset
        # Bank/Slot properties get tagged with .bank or .slot
        if p.typeAsInt == DmxProperty.DmxBankSlot:
            if slotFlag:
                name = p.name + '.slot'
                channelOffset = p.channelOffset + 1
            else:
                name = p.name + '.bank'

        # set defaults in case our lookup into the standard attribute types fail
        # FeatureGroup/feature may or may not want to be "Video"    
        featureGroup = 'Video'
        feature = p.group
        activationGroup = None
        attName = name
        attPrettyName = name
        physicalUnit = None
        highlight = None

        # look for a typematch, and if found, use those values
        typeMatches = filter(lambda x: x['_match'] == name,parameterTypes)        
        if len(typeMatches) > 0:
            featureGroup = typeMatches[0].get('_feature').split('.')[0] 
            feature = typeMatches[0].get('_feature').split('.')[1]
            activationGroup = typeMatches[0].get('_ActivationGroup')
            attName = typeMatches[0].get('_name')
            attPrettyName = typeMatches[0].get('_prettyName')
            physicalUnit = typeMatches[0].get('_physicalUnit')
            highlight = typeMatches[0].get('_highlight')

        
        # if the ActivationGroup, FeatureGroup, or Feature is new, add it to the proper nodes
        if (activationGroup) and (activationGroup not in foundActivationGroups):
            foundActivationGroups[activationGroup] = etree.SubElement(activationGroups,'ActivationGroup',Name=activationGroup)
            # print(activationGroup)
        
        if (featureGroup not in foundFeatureGroups):
            foundFeatureGroups[featureGroup] = etree.SubElement(featureGroups,'FeatureGroup',Name=featureGroup,Pretty=featureGroup)
            # print(featureGroup)
            
        if (feature not in foundFeatures):
            # print(feature)
            # print(foundFeatureGroups[featureGroup])
            foundFeatures[feature] = etree.SubElement(foundFeatureGroups[featureGroup],'Feature', Name=feature)
        
        # Create a new Attribute Node and populate it
        if (attName not in foundAttributes):
            att = etree.SubElement(attributes,'Attribute')            
            att.set('Name', attName)
            att.set('Pretty', attPrettyName)
            att.set('Feature',featureGroup + '.' + feature)
            
            if (physicalUnit):
                att.set('PhysicalUnit',physicalUnit)
            else:
                att.set('PhysicalUnit','None')
                
            if (activationGroup):
                att.set('ActivationGroup', activationGroup)
        
            foundAttributes[attName] = att
        
        # Create a new DMX Channel for the property
        dmxChannel = etree.SubElement(dmxChannels,'DMXChannel',DMXBreak='1',Geometry='D3ServerLayer')
        
        # DMX Offset (1-indexed).  16bit fields have a list of indices e.g. "1,2"
        if p.typeAsInt == DmxProperty.Dmx16BigEndian:
            dmxChannel.set('Offset',str(channelOffset + 1) + ',' + str(channelOffset + 2))
        else:
            dmxChannel.set('Offset',str(channelOffset + 1))

        # Highlight fields should have a highlight value.  I think this will be brightness and the rgb color tints
        if (highlight):
            dmxChannel.set('Highlight',highlight)
        else:
            dmxChannel.set('Highlight','None')

        # Create a link to the initial function
        dmxChannel.set('InitialFunction','D3ServerLayer_' + attName + '.' + attName + '.' + attName)
        
        # Create the logical channel under the DMX Channel
        logicalChannel = etree.SubElement(dmxChannel,'LogicalChannel')
        logicalChannel.set('Attribute',attName)
        
        # Options properties SNAP
        if p.typeAsInt == DmxProperty.DmxOptions:
            logicalChannel.set('Snap','Yes')  
        else:
            logicalChannel.set('Snap','No')
            
        if attName == 'Dimmer':
            logicalChannel.set('Master','Grand')
        else:
            logicalChannel.set('Master','None')  
            
        logicalChannel.set('MibFade','0')
        logicalChannel.set('DMXChangeTimeLimit','0')
        
          
        # Create ChannelFunction Node under the LogicalChannel Node
        channelFunction = etree.SubElement(logicalChannel,'ChannelFunction',Name = attName)
        channelFunction.set('Attribute',attName)

        # Our Channel Functions always start a dmx value 0, and Min/Max are 0 to 1 (which only has to do with DMX Profiles aka curves)
        channelFunction.set('DMXFrom','0/1')
        channelFunction.set('Min','0')
        channelFunction.set('Max','1')
        channelFunction.set('PhysicalFrom',str(p.min))
        channelFunction.set('PhysicalTo',str(p.max))
        
        # Some more attributes to try to figure out the parse issue with GrandMA
        channelFunction.set('OriginalAttribute','')
        channelFunction.set('CustomName','')
        channelFunction.set('RealAcceleration','0')
        channelFunction.set('RealFade','0')
        
        # Set Default correctly for 8bit or 16bit fields
        # Need to confirm property defaults for slot/bank
        # For options fields, we just pass on the default as a 8bit value
        
        normalizedDefault = (p.default - p.min) / (p.max - p.min)
        # print(p.name+':'+str(p.default)+':'+str(p.min)+':'+str(p.max))
        
        if p.typeAsInt == DmxProperty.Dmx16BigEndian:
            channelFunction.set('Default',str(int(normalizedDefault*65535.0)) + '/2')
            # print('16bitdef: ' + str(int(normalizedDefault*65535.0)))
            
        elif p.typeAsInt == DmxProperty.DmxOptions:
            channelFunction.set('Default',str(int(p.default)) + '/1')
            
        else:
            channelFunction.set('Default',str(int(normalizedDefault*255.0)) + '/1')
            # print('16bitdef: ' + str(int(normalizedDefault*255.0)))
        
        # Options-Type properties get ChannelSet nodes to define the select options
        if p.typeAsInt == DmxProperty.DmxOptions:     
            for opt in p.options:
                channelSet = etree.SubElement(channelFunction,'ChannelSet',Name=opt.name)
                channelSet.set('DMXFrom',str(opt.min) + '/1')
        
        # If we have just processed a Bank/Slot property for its bank attribute, run this again for the slot attribute
        if (p.typeAsInt == DmxProperty.DmxBankSlot) and (slotFlag == False):
            processProperty(p,dmxChannels,True)
    
    # Process all properties on the personality
    
    modeNames = []
    
    for personality in personalities:
        #Create a default DMX Mode Node and a DMXChannels node
        modeName = (personality.variantName + '_v' + str(personality.vmapVersion)).replace('.','_')
        if (modeName in modeNames):
            modeName = modeName + "+"
        
        modeNames.append(modeName)
        
        dmxMode = etree.SubElement(dmxModes, 'DMXMode', Name = modeName, Description = '', Geometry='D3ServerLayer')
        dmxChannels = etree.SubElement(dmxMode,'DMXChannels')
        
        for p in personality.properties:
            processProperty(p,dmxChannels)

    
    # Pretty format the XML
    rough_string = etree.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    exportToDisk(className + '_Personality',reparsed.toprettyxml(indent='  ', encoding='utf-8'))


