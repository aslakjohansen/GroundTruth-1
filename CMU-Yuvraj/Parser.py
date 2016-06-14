import pandas as pd
import operator
import pickle
import shelve
import re
from collections import Counter, defaultdict, OrderedDict, deque
import csv
import rdflib
from rdflib.namespace import OWL, RDF, RDFS
from rdflib import URIRef
import os

def main():
	Total = dict()
	Tagsets = dict()
	TagsetsToTags = dict()
	Equipment = dict()
	print "hi"
	BRICK = rdflib.Namespace('http://buildsys.org/ontologies/brick#')
	GHC = rdflib.Namespace('http://cmu.edu/building/ontology/ghc#')
	#RDF, RDFS and OWL have already been imported in the library initializations
	print GHC["test"]
	#Initiate graph from base ttl file
	g = rdflib.Graph()
	g.bind('GHC', GHC)
	g.bind('brick', BRICK)
#	g.parse('../BuildingSchema/Brick.ttl', format='turtle')
	count1 = 0
	count2 = 0
	changeablemapping = dict()
	with open('CMU_GHC.csv', 'rU') as DataFile:
		with open('CMU_AHU_OddBuildingTagSet.csv','rU') as Mapping:
		    with open('TagSets.csv','rU') as GDocs:
			changeable = csv.DictReader(GDocs)
			for row in changeable:
				Value = row['Dimension']
				Key = row['TagSet']
				Key = re.sub(' ','_',Key)
				Values = Value.split('>')
				if (len(Values)>1):
					changeablemapping[Key] = Values
			#	print Values
			reader = csv.DictReader(Mapping)	
			for row in reader:
				#print row['Bas1'], row['TagSet'], row['Tags']
				BasTag = row['Bas1']
				ListBasTag = BasTag.split('/')
				length = len(ListBasTag)
				Key = ListBasTag[length-1]
			#	print Key
				x=row['TagSet']
				NewX = re.sub(' ','_',x)
				Key = re.sub(' ','_',Key)
			#	print NewX	
				Tagsets[Key] = NewX
				Tags = row['Tags']
				listTags = Tags.split(';')
				TagsetsToTags[NewX]=listTags
				if(NewX in changeablemapping.keys()):
			#		print "1"
					pass
				else:
					print "2",NewX
			#	print ListBasTag
			MapReader = csv.reader(Mapping, delimiter=' ',quotechar='|')
		#	for row in MapReader:
		#		print row
		reader = csv.DictReader(DataFile)
		g.add((GHC['GHC_HVAC'],RDF.type,OWL.NamedIndividual))
		g.add((GHC['GHC_HVAC'],RDF.type,BRICK['HVAC']))
		for row in reader:
			New = row['bas_raw']
			ListBasTag = New.split('/')
			length = len(ListBasTag)
			Key = ListBasTag[length-1]
			Key = re.sub(' ','_',Key)
			y=0
			if('Parking' in ListBasTag[2]):
				y=1
			
			NewKey = ListBasTag[1]+'/'+ListBasTag[3+y]+'/'+Key
			NewKey = re.sub(' ','_',NewKey)
			x = GHC[NewKey]
		#	g.add((Key,RDF.type,OWL.NamedIndividual))
		#	g.add((Key,RDF.type,BRICK[Tagsets[key]]))
		#	print Key
			Equip = ""
			BelongsTo = ""
			if Key in Tagsets:
				count1+=1
				g.add((x,RDF.type,OWL.NamedIndividual))
				g.add((x,RDF.type,BRICK[Tagsets[Key]]))
				location = "" 
				for i in range(0,3+y):
					location=location+ListBasTag[i]

				location = re.sub(' ','_',location)
				g.add((GHC[location],RDF.type,OWL.NamedIndividual))
				g.add((GHC[location],RDF.type,BRICK["Location"]))
				g.add((x,BRICK.hasLocation,GHC[location]))
				if 'AHU' in ListBasTag[3+y]:
					Equip="AHU"
				elif 'VAV' in ListBasTag[3+y] or 'FSB' in ListBasTag[3+y]:
				#	print ListBasTag[3+y]
					Equip="VAV"
				elif 'CRAC' in ListBasTag[3+y]:
					Equip="CRAC"
				elif 'FCU' in ListBasTag[3+y]:
				#	print "HELLO"
					Equip="Fan_Coil_Unit"
				else:
					#print ListBasTag[3+y],NewKey
					if('Usage' in NewKey or 'Peak' in NewKey):
						Equip = "Meter"
					else:
						print NewKey
			#	mapping = changeablemapping[Tagsets[Key]]
			#	if(len(mapping) == 4):
			#		Equip = re.sub(' ','_',mapping[3])
			#		BelongsTo =""
			#	if(len(mapping) == 3):
			#		Equip = re.sub(' ','_',mapping[2])
			#		BelongsTo = re.sub(' ','_',mapping[1])
			#	if(len(mapping) > 4):
			#		Equip = re.sub(' ','_',mapping[4])
			#		BelongsTo = re.sub(' ','_',mapping[3])
			
			#	LowestEquip = mapping[len(mapping)-1]
			#	NewEquipment = ListBasTag[1]+'/'+ListBasTag[3+y]+'/'+Equip
			#	NewBelongs =  ListBasTag[1]+'/'+ListBasTag[3+y]+'/'+BelongsTo
			#	NewEquipment = re.sub(' ','_',NewEquipment)
			#	NewBelong = re.sub(' ','_',NewBelongs)

				blank = re.sub(' ','_',ListBasTag[3+y])
			#	print changeablemapping[Tagsets[Key]], Key
		#	#	print blank, ListBasTag[3+y]
			#	NewEquip = NewEquipment
			#	print NewBelong, NewEquip, x
				if not (blank in Equipment) and not 'Interface' in ListBasTag[3+y] and Equip!="":
					
					Equipment[blank] = 1
					g.add((GHC[blank],RDF.type, OWL.NamedIndividual))
					g.add((GHC[blank],RDF.type, BRICK[Equip]))
				#	if not(NewBelong in Equipment):
				#		g.add((GHC[NewBelong],RDF.type, OWL.NamedIndividual))
				#		g.add((GHC[NewBelong],RDF.type,BRICK[BelongsTo]))
				#		Equipment[NewBelong]=1
				#		g.add((GHC[NewEquip],BRICK.hasLocation,GHC[location]))
					#	print NewBelong, NewEquip
					
				#	g.add((GHC[NewEquip],BRICK.isPartOf,GHC[NewBelong]))
				#	g.add((GHC[NewEquip],BRICK.hasLocation, GHC[location]))
				if(Equip !=""):
					g.add((GHC[blank], BRICK.hasPoint, x))
				if Equip == "":
					g.add((GHC['GHC_HVAC'],BRICK.hasPoint,x))
							
					
			else:
				Total[Key]=1
			#	print Key
				count2+=1
			#	print Key
		#	if ('AHU' in ListBasTag[3]):
		#		print "3",ListBasTag[3]
		#	if ('AHU' in ListBasTag[4]):
		#		print "4",ListBasTag[4]	
		for item in TagsetsToTags.keys():
			x = BRICK[item]
			#for value in TagsetsToTags[item]:
			#	g.add((x,BRICK.hasTag,BRICK[value]))
	with open('AHURelations2.csv', 'rU') as relations:
		reader = csv.DictReader(relations)
		for row in reader:
			new = re.sub('_','-',row['First'])
			g.add((GHC[new+'_I'],BRICK.feeds,GHC[row['Third']]))
	
#	g.add((GHC["AHU-1_Zone-Temperature"],RDF.type,OWL.NamedIndividual))
	if((BRICK["Run_Request"],None,None) in g):
		print "Hi"
#	g.add((GHC["AHU-1_Zone-Temperature"],RDF.type,BRICK["Zone_Temp"]))
#	g.add((GHC["VAV1"], BRICK.hasPoint, GHC["AHU-1_Zone-Temperature"]))
	g.serialize(destination='GHCYuvraj_brick.ttl', format='turtle')
	print count1
	print count2
	print len(Total.keys())
	
main();
