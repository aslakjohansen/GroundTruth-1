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
building_graph.add((RICE.RICE_Basement, RDF.type, BRICK.Floor))
building_graph.add((RICE.RICE_Floor_1, RDF.type, BRICK.Floor))
building_graph.add((RICE.RICE_Floor_2, RDF.type, BRICK.Floor))
building_graph.add((RICE.RICE_Floor_3, RDF.type, BRICK.Floor))
building_graph.add((RICE.RICE_Floor_4, RDF.type, BRICK.Floor))
building_graph.add((RICE.RICE_Floor_5, RDF.type, BRICK.Floor))
building_graph.add((RICE.RICE_Basement, BRICKFRAME.isPartof, RICE.RICE))
building_graph.add((RICE.RICE_Floor_1, BRICKFRAME.isPartof, RICE.RICE))
building_graph.add((RICE.RICE_Floor_2, BRICKFRAME.isPartof, RICE.RICE))
building_graph.add((RICE.RICE_Floor_3, BRICKFRAME.isPartof, RICE.RICE))
building_graph.add((RICE.RICE_Floor_4, BRICKFRAME.isPartof, RICE.RICE))
building_graph.add((RICE.RICE_Floor_5, BRICKFRAME.isPartof, RICE.RICE))

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
        pt_type = BRICK[pt_type]
        if (pt_type, None, None) in brick_graph:
            building_graph.add((RICE[label], RDF.type, pt_type))
        else:
            building_graph.add((RICE[label], RDF.type, OWL.NamedIndividual))
            building_graph.add((RICE[label], RDF.type, BRICK.Point))

        if pt_room:
            pt_room = BRICK[pt_room]
            building_graph.add((RICE[pt_room], RDF.type, OWL.NamedIndividual))
            building_graph.add((RICE[pt_room], RDF.type, BRICK["Location"]))
            building_graph.add((RICE[label], BRICKFRAME.isLocatedIn, RICE[pt_room]))

            if pt_zone:
                building_graph.add((RICE["HVAC_Zone" + pt_zone], BRICKFRAME.hasPoint, RICE["Room" + pt_room]))
                building_graph.add((RICE["Room" + pt_room], BRICKFRAME.isPointOf, RICE["HVAC_Zone" + pt_zone]))

            if pt_floor:
                building_graph.add((RICE["Floor" + pt_floor], BRICKFRAME.hasPart, RICE["Room" + pt_room]))

building_graph.serialize(destination='Rice.ttl', format='turtle')
