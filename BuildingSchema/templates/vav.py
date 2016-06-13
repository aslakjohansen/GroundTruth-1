#!/usr/bin/env python

from rdflib import Graph, Namespace, URIRef, Literal
import rdflib
import json

BRICK = Namespace(rdflib.term.URIRef('http://www.semanticweb.org/jbkoh/ontologies/2016/4/untitled-ontology-27#'))
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')

g = Graph()
s = g.parse('../Brick.ttl', format='turtle', publicID='brick')
g.bind('rdf', RDF)
g.bind('brick', BRICK)

# actors
entity_vav                = URIRef('/vav')
entity_supply_damper      = URIRef('/supply_damper')
entity_return_damper      = URIRef('/return_damper')
entity_supply_pressure    = URIRef('/supply_pressure')
entity_cooling_coil       = URIRef('/cooling_coil')
entity_supply_temperature = URIRef('/supply_temperature')
rooms = map(lambda name: URIRef('/rooms/'+name), ['room1', 'room2'])
all_entities = [
    entity_vav,
    entity_supply_damper,
    entity_return_damper,
    entity_supply_pressure,
    entity_cooling_coil,
    entity_supply_temperature,
]

# types
g.add( (entity_vav               , RDF.type, BRICK['VAV']) )
g.add( (entity_supply_damper     , RDF.type, BRICK['Damper']) )
g.add( (entity_return_damper     , RDF.type, BRICK['Damper']) )
g.add( (entity_supply_pressure   , RDF.type, BRICK['Air_Pressure_Sensor']) )
g.add( (entity_cooling_coil      , RDF.type, BRICK['Cooling_Coil']) )
g.add( (entity_supply_temperature, RDF.type, BRICK['Temperature_Sensor']) )
for room in rooms:
    g.add( (room, RDF.type, BRICK['Room']) )

# isPartOf relationships
for entity in filter(lambda entity: entity!=entity_vav, all_entities):
    g.add( (entity, BRICK['isPartOf'], entity_vav) )

# media
g.add( (entity_supply_damper     , BRICK['hasTagSet'], BRICK['Supply_Air']) )
g.add( (entity_return_damper     , BRICK['hasTagSet'], BRICK['Return_Air']) )
g.add( (entity_supply_pressure   , BRICK['hasTagSet'], BRICK['Supply_Air']) )
g.add( (entity_cooling_coil      , BRICK['hasTagSet'], BRICK['Supply_Air']) )
g.add( (entity_supply_temperature, BRICK['hasTagSet'], BRICK['Supply_Air']) )

# feeds relationships (note: no AHU has been connected yet)
g.add( (entity_supply_damper  , BRICK['feeds'], entity_supply_pressure) )
g.add( (entity_supply_pressure, BRICK['feeds'], entity_cooling_coil) )
g.add( (entity_cooling_coil   , BRICK['feeds'], entity_supply_temperature) )
for room in rooms:
    g.add( (entity_supply_temperature, BRICK['feeds'], room) )
for room in rooms:
    g.add( (room, BRICK['feeds'], entity_return_damper) )

# controls relationships
g.add( (entity_supply_pressure   , BRICK['controls'], entity_supply_damper) )
g.add( (entity_supply_temperature, BRICK['controls'], entity_cooling_coil) )

# hasUnit relationships
g.add( (entity_supply_temperature, BRICK['hasUnit'], BRICK['Celcius']) )

# export
g.serialize('vav.ttl', 'turtle')

