import rdflib
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
        pt_type = pt['parsed tagset']
        pt_type = BRICK[pt_type]
        if (pt_type, None, None) in brick_graph:
            building_graph.add((RICE[label], RDF.type, pt_type))
        else:
            building_graph.add((RICE[label], RDF.type, BRICK.Equipment))

        #pt_loc = pt['room']
        #building_graph.add((pt['original label'], BRICKFRAME.isLocatedIn, RICE[pt_loc]))

building_graph.serialize(destination='test.ttl', format='turtle')
