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
	g.parse('../BuildingSchema/Brick.owl', format='turtle')
	count1 = 0
	count2 = 0
	with open('CMU_GHC.csv', 'rU') as DataFile:
		with open('CMU_AHU_OddBuildingTagSet.csv','rU') as Mapping:
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
				print NewX	
				Tagsets[Key] = NewX
				Tags = row['Tags']
				listTags = Tags.split(';')
				TagsetsToTags[NewX]=listTags
			#	print ListBasTag
			MapReader = csv.reader(Mapping, delimiter=' ',quotechar='|')
		#	for row in MapReader:
		#		print row
		reader = csv.DictReader(DataFile)
		
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
				elif 'VAV' in ListBasTag[3+y]:
				#	print ListBasTag[3+y]
					Equip="VAV"
				elif 'CRAC' in ListBasTag[3+y]:
					Equip="CRAC"
				elif 'FCU' in ListBasTag[3+y]:
					print "HELLO"
					Equip="Fan_Coil_Unit"
				blank = re.sub(' ','_',ListBasTag[3+y])
		#		print blank, ListBasTag[3+y]
				if not (blank in Equipment) and not 'Interface' in ListBasTag[3+y] and Equip!="":
					
					Equipment[blank] = 1
					g.add((GHC[blank],RDF.type, OWL.NamedIndividual))
					g.add((GHC[blank],RDF.type, BRICK[Equip]))
					
					g.add((GHC[blank],BRICK.hasLocation, GHC[location]))
				g.add((GHC[blank], BRICK.hasPoint, x))
						
					
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
	with open('relationship.csv', 'rU') as relations:
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
