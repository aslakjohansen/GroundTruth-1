
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

labeledFile = 'metadata/' + buildingName + '_sensor_types_location.csv'
with open(labeledFile, 'rb') as fp:
    #truthDF = pd.read_excel(fp)
    truthDF = pd.DataFrame.from_csv(fp)
    truthDF = truthDF.set_index(keys='Unique Identifier')
schemaMapDF = pd.read_csv('metadata/EBU3B_to_BS.csv').set_index('token')


# In[3]:

#####################################################
######### 0. Load tokenized data structure ##########
#####################################################

with open('metadata/ebu3b_metadata.pkl', 'rb') as fp:
    totalList = pickle.load(fp)


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


# In[6]:

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
    
    ### Triples for VAV<->Room
    roomToken = find_proper_token(tokens, 'Room', g)
    roomTokenRef = make_ref(roomToken) 
    roomTagRef = g.value(roomTokenRef, make_ref('hasTag'))
    vavToken = find_proper_token(tokens, 'Variable_Air_Volume_Box', g)
    vavTokenRef = make_ref(vavToken)
    vavTagRef = g.value(vavTokenRef, make_ref('hasTag'))
    
    if not (vavTagRef, make_ref('feeds'), roomTagRef) in g:
        g.add((vavTagRef, make_ref('feeds'), roomTagRef))
        
    ### Triples for VAV<->Point
    for token in tokens:
        tokenRef = make_ref(token)
        tagRef = g.value(tokenRef, make_ref('hasTag'))
        if tagRef in typeTagRefList:
            g.add((vavTagRef, make_ref('hasPoint'), tagRef))
    
# Store as output.ttl
g.serialize(destination='output_'+buildingName+'.ttl', format='turtle')

