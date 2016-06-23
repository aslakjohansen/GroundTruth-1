import rdflib
from rdflib.namespace import OWL, RDF, RDFS
from rdflib import URIRef

src = [i.strip().split(',')[0] for i in open('Rice_Type').readlines()]

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

building_graph.serialize(destination='test.ttl', format='turtle')
