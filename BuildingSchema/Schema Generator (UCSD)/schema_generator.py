
# coding: utf-8

# In[1]:

import numpy as np
import pandas as pd
import operator
import pickle
import shelve
import re
from collections import Counter, defaultdict, OrderedDict, deque
import csv
import rdflib
from rdflib.namespace import OWL, RDF
from rdflib import URIRef
import os


# In[2]:

#####################################################
################ 0. Initialization ##################
#####################################################


buildingName = 'ebu3b'
uriPrefix = 'http://www.semanticweb.org/jbkoh/ontologies/2016/4/BuildingSchema#'

sensor_dict = shelve.open('metadata/ebu3b_devices.shelve')

labeledFile = 'metadata/' + buildingName + '_sensor_types_location.csv'
with open(labeledFile, 'rb') as fp:
    #truthDF = pd.read_excel(fp)
    truthDF = pd.DataFrame.from_csv(fp)
    truthDF = truthDF.set_index(keys='Unique Identifier')
schemaMapDF = pd.read_csv('metadata/EBU3B_to_BS.csv').set_index('token')


# In[3]:

#####################################################
###### 1. Tokenization (UCSD specific code.) ########
#####################################################

#Parse the data in the dictionary as filtered by device_list
#Gives us a sensor_list with sensor information of a building

def extract_words(sentence, delimiter="re", reExp='(\d+\s?-?\s?\d+)|(\d+)'):
    if delimiter=='re':
        result = re.findall(reExp, sentence)
    else:
        result = sentence.lower().split(delimiter)
    while '' in result:
        result.remove('')
    return [word.lower() for word in result]

def sentence2lower(wordList):
    return [word.lower() for word in wordList]

def tokenize(tokenType, raw):
    raw = raw.replace('_', ' ')
    if tokenType=='Alphanumeric':
        sentence = re.findall("\w+", raw)
    elif tokenType in ['AlphaAndNum', 'NumAsSingleWord']:
        sentence = re.findall("[a-zA-Z]+|\d+", raw)
    elif tokenType=='NoNumber':
        sentence = re.findall("[a-zA-Z]+|\d+", raw)
    else:
        assert(False)
    if tokenType=='NumAsSingleWord':
        sentence = ['NUM' if len(re.findall('\d+',word))>0 else word for word in sentence]
    sentence = sentence2lower(sentence)
    return sentence


naeDict = dict()
naeDict['bonner'] = ["607", "608", "609", "557", "610"]
naeDict['ap_m'] = ['514', '513','604']
naeDict['bsb'] = ['519', '568', '567', '566', '564', '565']
naeDict['ebu3b'] = ["505", "506"]
naeList = naeDict[buildingName]


sensor_list = []
nameList = list()
names_num_list = []
names_str_list = []
names_num_listWithDigits = [] 
sensor_type_namez=[]
descList = []
unitList = []
type_str_list = []
type_list = []
jcinameList = list()
jci_names_str_list = []
srcid_set = set([])
totalList = list()
sentenceList = list()

tokenType = 'AlphaAndNum'
    
for nae in naeList:
    device = sensor_dict[nae]
    h_dev = device['props']
    for sensor in device['objs']:
        h_obj = sensor['props']
        srcid = str(h_dev['device_id']) + '_' + str(h_obj['type']) + '_' + str(h_obj['instance'])
        
        if h_obj['type'] not in (0,1,2,3,4,5,13,14,19):
            continue
        
        if srcid in srcid_set:
            continue
        else:
            srcid_set.add(srcid)
        
        #jciSentence = tokenize(tokenType, sensor['jci_name'])
        jciSentence = extract_words(sensor['jci_name'], 're', '\w+')
        #nameSentence = tokenize(tokenType, sensor['name'])
        nameSentence = extract_words(sensor['name'], 're', "[a-zA-Z]+|\d+")
        #descSentence = tokenize(tokenType, sensor['desc'])
        totalSentence = jciSentence + nameSentence
        label = ' '.join(totalSentence)
        
        unitList.append('unittt'+str(sensor['unit']))
        
        #convert string to dictionary for categorical vectorization
        type_str_list.append({str(h_obj['type_str']):1})
        type_list.append({str(h_obj['type']):1})
        
        totalList.append(totalSentence)
        
        #create a flat list of dictionary to avoid using json file
        equipName = ''
        equipType = truthDF['Equipment Type'][srcid]
        equipRef = truthDF['Equipment Ref'][srcid]
        if type(equipType)==str:
            equipName += equipType
        if type(equipRef)==str:
            equipName += ('_'+equipRef)
            
        try:
            sensor_list.append({'srcid': srcid, 
                            'name': sensor['name'], 
                            'description': sensor['desc'],
                            'unit': sensor['unit'],
                            'type_string': h_obj['type_str'],
                            'type': h_obj['type'],
                            #'device_id': h_obj['device_id'],
                            'jci_name': sensor['jci_name'],
                            #add data related characteristics here
                            'sentence': totalSentence,
                            'point_type': truthDF['Ground Truth Point Type'][srcid],
                            'equip': equipName
                        })
        except:
            print truthDF.loc[srcid]
            assert(False)

sensorDF = pd.DataFrame(sensor_list).set_index('srcid')
#sensorDF = sensorDF.set_index('srcid')
#sensorDF = sensorDF.groupby(sensorDF.index).first()


# In[4]:

#######################################################
#2. Map label<->token<->tag (Semi-UCSD specific code.)#
#######################################################

## - Extract valid tokens and make them a label
## - Make data structures for label<->token<->tag(tagset) 
## Outputs are four data structures: 
## 1. labelList: List of labels
## 2. tokenDict: key=token, value=tag or tagset
## 3. upperTagsetDict: key=named tagset, value=tagset (upper class of the named tagset)
## (4. tagsetList: list of tag and tagsets) -> Obsolete

## WARNING: This part is our building-specific part.

tagsetList = list()
tokenDict = dict()
labelList = list()
upperTagsetDict = dict()

for sentence in totalList:
    tempTokenDict = dict()
    tempTagsetList = list()
    tempUpperTagsetDict = dict()
    for i, word in enumerate(sentence):
        if word in schemaMapDF.index:
            token = word
            origTag = schemaMapDF['bs'][word]
            if schemaMapDF['instance?'][word]:
                #TODO: this is heuristic
                if word=='ebu3b':
                    tag = 'Building-ebu3b'
                    token = 'EBU3B'
                else:
                    token = token+sentence[i+1]
                    tag = origTag+'-'+sentence[i+1]
                tempUpperTagsetDict[tag] = origTag
                token = token.upper()
                tempTokenDict[token] = tag
            else:
                token = token.upper()
                tempTokenDict[token] = origTag
            tempTagsetList.append(tag)
    
    if 'rm' in sentence and 'ebu3b' in sentence and 'vma' in sentence and len(tempTokenDict)>3:
        label = '_'.join(tempTokenDict.keys()).upper()
        labelList.append(label)
        tokenDict.update(tempTokenDict)
        upperTagsetDict.update(tempUpperTagsetDict)
        tagsetList += tempTagsetList

#tagsetList = list(set(tagsetList))
#tokenList = list(set(tokenList))
#labelList = list(set(labelList))


# In[5]:

print tokenDict['ACTHTGSP']
print labelList[0].split('_')


# In[21]:

#####################################################
######## 3. Add triples and serialize them ##########
#####################################################

#### Adding the labels and tags to the ttl file

typeTagList = ['Zone_Temperature_Effective_Cooling_Setpoint',
            'Zone_Temperature_Effective_Heating_Setpoint',
            'Cooling_Command',
            'Heating_Command',
            'Damper_Command',
            'Fan_Command',
            'Cooling_Max_Discharge_Air_Flow',
            'Occupied_Cooling_Min_Discharge_Air_Flow',
            'Occupied_Command',
            'Reheat_Valve',
            'Discharge_Air_Flow_Sensor',
            'Discharge_Air_Flow_Setpoint',
            'Zone_Temperature_Setpoint',
            'Temperature_Adjustment',
            'Zone_Temperature_Setpoint'
           ]

def check_tagset(tagOrTagset):
    return '_' in tagOrTagSet

def make_ref(term):
    return URIRef(uriPrefix+term)

def find_proper_token(tokens, tagName, g):
    baseTagRef = make_ref(tagName)
    for token in tokens:
        tokenRef = make_ref(token)
        tagRef = g.value(tokenRef, make_ref('hasTag'))
        if (tagRef, RDF.type, baseTagRef) in g:
            return token
    return None

#Initiate graph from base ttl file
g = rdflib.Graph()
g.parse('metadata/BuildingSchema.ttl', format='turtle')

typeTagRefList = [make_ref(typeTag) for typeTag in typeTagList]


# Iterate label to generate label and corresponding tagsets
for label in labelList:
    #print label
    # Make an URI for a label. All nodes should have a URI.
    # (TODO: There might be a way to do this without URI.)
    labelRef = URIRef(uriPrefix+label)
    
    # Add the label
    g.add((labelRef, RDF.type, OWL.NamedIndividual))
    #g.add((labelRef, RDF.type, URIRef(uriPrefix+'Label')))
    g.add((labelRef, RDF.type, make_ref('Label')))
    
    tokens = label.split('_')
    
    ### Triples for Label<->Token<->Tag
    # Iterate tokens in a label to generate tags, tagsets, instances of tagsets.
    for token in tokens:
        #tokenRef = URIRef(uriPrefix+token)
        tokenRef = make_ref(token)
        
        # Check if a token is in the graph already or not
        # Add it otherwise.
        if not (tokenRef, None, None) in g:
            # add a triple to isntantiate the token
            g.add((tokenRef, RDF.type, OWL.NamedIndividual)) # Current token is a type of NamedIndividual
            g.add((tokenRef, RDF.type, make_ref('Token'))) # Current token is a type of Token.
            tagOrTagset = tokenDict[token]
            tagRef = make_ref(tagOrTagset)
            if not (tagRef, None, None) in g:
                if tagOrTagset in upperTagsetDict.keys():
                    g.add((tagRef, RDF.type, OWL.NamedIndividual))
                    upperTagRef = make_ref(upperTagsetDict[tagOrTagset])
                    g.add((tagRef, RDF.type, upperTagRef))
                else:
                    print tagRef
                    print("WARNING: The tag %s is not in the base schema.", tag)
                    continue
            g.add((tokenRef, make_ref('hasTag'), tagRef))
        
        if (tokenRef, None, None) in g:
            g.add((labelRef, make_ref('hasToken'), tokenRef))
        else:
            print("Error: token %s is not added", token)
    
    ### Add a triple for VAV<->Room
    roomToken = find_proper_token(tokens, 'Room', g)
    roomTokenRef = make_ref(roomToken) 
    roomTagRef = g.value(roomTokenRef, make_ref('hasTag'))
    vavToken = find_proper_token(tokens, 'Variable_Air_Volume_Box', g)
    vavTokenRef = make_ref(vavToken)
    vavTagRef = g.value(vavTokenRef, make_ref('hasTag'))
    
    if not (vavTagRef, make_ref('feeds'), roomTagRef) in g:
        g.add((vavTagRef, make_ref('feeds'), roomTagRef))
        
    ### Add a triple for VAV<->Point
    for token in tokens:
        tokenRef = make_ref(token)
        tagRef = g.value(tokenRef, make_ref('hasTag'))
        if tagRef in typeTagRefList:
            g.add((vavTagRef, make_ref('hasPoint'), tagRef))
    
# Store as output.ttl
g.serialize(destination='output_'+buildingName+'.ttl', format='turtle')


# In[ ]:



