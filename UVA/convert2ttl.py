import rdflib
import re
import csv
from rdflib.namespace import OWL, RDF, RDFS
from rdflib import URIRef

BRICK = rdflib.Namespace('http://buildsys.org/ontologies/Brick#')
BRICKFRAME = rdflib.Namespace('http://buildsys.org/ontologies/BrickFrame#')
RICE = rdflib.Namespace('http://virginia.edu/building/ontology/rice#')

building_graph = rdflib.Graph()
building_graph.bind('rice', RICE)
building_graph.bind('brick', BRICK)
building_graph.bind('brickframe', BRICKFRAME)
building_graph.bind('owl', OWL)

brick_graph = rdflib.Graph()
brick_graph.bind('brick', BRICK)
brick_graph.parse('../BuildingSchema/Brick.ttl', format='turtle')

building_graph.add((RICE.RICE, RDF.type, BRICK.Building))
building_graph.add((RICE.Floor_0, RDF.type, BRICK.Floor)) #aka, basememt
building_graph.add((RICE.Floor_1, RDF.type, BRICK.Floor))
building_graph.add((RICE.Floor_2, RDF.type, BRICK.Floor))
building_graph.add((RICE.Floor_3, RDF.type, BRICK.Floor))
building_graph.add((RICE.Floor_4, RDF.type, BRICK.Floor))
building_graph.add((RICE.Floor_5, RDF.type, BRICK.Floor))
building_graph.add((RICE.Floor_0, BRICKFRAME.isPartof, RICE.RICE))
building_graph.add((RICE.Floor_1, BRICKFRAME.isPartof, RICE.RICE))
building_graph.add((RICE.Floor_2, BRICKFRAME.isPartof, RICE.RICE))
building_graph.add((RICE.Floor_3, BRICKFRAME.isPartof, RICE.RICE))
building_graph.add((RICE.Floor_4, BRICKFRAME.isPartof, RICE.RICE))
building_graph.add((RICE.Floor_5, BRICKFRAME.isPartof, RICE.RICE))
building_graph.add((RICE.AHU_1, RDF.type, BRICK.AHU))
building_graph.add((RICE.AHU_2, RDF.type, BRICK.AHU))
building_graph.add((RICE.AHU_3, RDF.type, BRICK.AHU))
building_graph.add((RICE.AHU_4, RDF.type, BRICK.AHU))
building_graph.add((RICE.AHU_1, BRICKFRAME.isPartof, RICE.RICE))
building_graph.add((RICE.AHU_2, BRICKFRAME.isPartof, RICE.RICE))
building_graph.add((RICE.AHU_3, BRICKFRAME.isPartof, RICE.RICE))
building_graph.add((RICE.AHU_4, BRICKFRAME.isPartof, RICE.RICE))

with open('point.csv', 'r') as src:
    ptList = csv.DictReader(src)
    for pt in ptList:
        label = pt['original label']
        pt_type = pt['tagset']
        pt_ahu = pt['ahu']
        pt_zone = pt['hvac_zone']
        pt_floor = pt['floor']
        pt_room = pt['room']
        label = re.sub('\s+','_',label)

        pt_type = re.sub('\s+','_',pt_type)
        # pt_type = BRICK[pt_type]

        building_graph.add((BRICK[pt_type], RDF.type, OWL.NamedIndividual))
        building_graph.add((BRICK[pt_type], RDF.type, BRICK.Point))
        building_graph.add((RICE[label], RDF.type, BRICK[pt_type]))

        if pt_room:
            building_graph.add((RICE["Room" + pt_room], RDF.type, OWL.NamedIndividual))
            building_graph.add((RICE["Room" + pt_room], RDF.type, BRICK.Room))
            building_graph.add((RICE["Room" + pt_room], BRICKFRAME.contains, RICE[label]))
            building_graph.add((RICE["Room" + pt_room], BRICKFRAME.hasPoint, RICE[label]))

            if pt_zone:
                building_graph.add((RICE["HVAC_Zone" + pt_zone], RDF.type, OWL.NamedIndividual))
                building_graph.add((RICE["HVAC_Zone" + pt_zone], RDF.type, BRICK.HVAC_Zone))
                building_graph.add((RICE["HVAC_Zone" + pt_zone], BRICKFRAME.hasPart, RICE["Room" + pt_room]))

                building_graph.add((RICE["VAV" + pt_zone], RDF.type, OWL.NamedIndividual))
                building_graph.add((RICE["VAV" + pt_zone], RDF.type, BRICK.VAV))
                building_graph.add((RICE["VAV" + pt_zone], BRICKFRAME.feeds, RICE["HVAC_Zone" + pt_zone]))
                building_graph.add((RICE["VAV" + pt_zone], BRICKFRAME.hasPoint, RICE[label]))

                building_graph.add((RICE["AHU" + pt_zone], BRICKFRAME.feeds, RICE["VAV" + pt_zone]))
                
            if pt_floor:
                building_graph.add((RICE["Floor" + pt_floor], BRICKFRAME.hasPart, RICE["Room" + pt_room]))

            if len(pt_room) < 3:
                pt_floor = '0'
            else:
                pt_floor = pt_room[0]
            building_graph.add((RICE["Floor" + pt_floor], BRICKFRAME.hasPart, RICE["Room" + pt_room]))

building_graph.serialize(destination='Rice.ttl', format='turtle')
