import rdflib
from rdflib.namespace import OWL, RDF, RDFS
from rdflib import URIRef

src = [i.strip().split(',')[0] for i in open('Rice_Type').readlines()]

BRICK = rdflib.Namespace('http://buildsys.org/ontologies/Brick#')
RICE = rdflib.Namespace('http://virginia.edu/building/ontology/rice#')
building_graph = rdflib.Graph()
brick_graph = rdflib.Graph()
building_graph.bind('rice', RICE)
building_graph.bind('brick', BRICK)
building_graph.bind('owl', OWL)
brick_graph.bind('brick', BRICK)
brick_graph.parse('../BuildingSchema/BrickV2.ttl', format='turtle')

print RICE
