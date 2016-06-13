#!/usr/bin/env python

from rdflib import Graph, Namespace, URIRef, Literal
import rdflib
import json

RDF   = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS  = Namespace('http://www.w3.org/2000/01/rdf-schema#')
BF    = rdflib.Namespace('http://buildsys.org/ontologies/BrickFrame#')
TAGS  = rdflib.Namespace('http://buildsys.org/ontologies/BrickTag#')
BRICK = rdflib.Namespace('http://buildsys.org/ontologies/Brick#')

g = rdflib.Graph()
g.bind('rdf' , RDF)
g.bind('rdfs', RDFS)
g.bind('bf'  , BF)
g.bind('tag' , TAGS)
g.bind('ts'  , BRICK)
result = g.parse('../BrickFrame.ttl', format='n3')
result = g.parse('../BrickTag.ttl', format='n3')
result = g.parse('../Brick.ttl', format='n3')

# building
BUILDING = Namespace('http://buildsys.org/ontologies/building_example#')
g.bind('building', BUILDING)

# actors
entity_vav                = BUILDING['/vav']
entity_supply_damper      = BUILDING['/supply_damper']
entity_return_damper      = BUILDING['/return_damper']
entity_supply_pressure    = BUILDING['/supply_pressure']
entity_cooling_coil       = BUILDING['/cooling_coil']
entity_supply_temperature = BUILDING['/supply_temperature']
rooms = map(lambda name: BUILDING['/rooms/'+name], ['room1', 'room2'])
all_entities = [
    entity_vav,
    entity_supply_damper,
    entity_return_damper,
    entity_supply_pressure,
    entity_cooling_coil,
    entity_supply_temperature,
]
entity_supply_air = BUILDING['/media/supply_air']
entity_return_air = BUILDING['/media/return_air']

# types
g.add( (entity_vav               , RDF.type, BRICK['VAV']) )
g.add( (entity_supply_damper     , RDF.type, BRICK['Damper']) )
g.add( (entity_return_damper     , RDF.type, BRICK['Damper']) )
g.add( (entity_supply_pressure   , RDF.type, BRICK['Air_Pressure_Sensor']) )
g.add( (entity_cooling_coil      , RDF.type, BRICK['Cooling_Coil']) )
g.add( (entity_supply_temperature, RDF.type, BRICK['Temperature_Sensor']) )
for room in rooms:
    g.add( (room, RDF.type, BRICK['Room']) )
g.add( (entity_supply_air        , RDF.type, BRICK['Supply_Air']) )
g.add( (entity_return_air        , RDF.type, BRICK['Return_Air']) )

# isPartOf relationships
for entity in filter(lambda entity: entity!=entity_vav, all_entities):
    g.add( (entity, BRICK['isPartOf'], entity_vav) )

# media
g.add( (entity_supply_damper     , BRICK['hasTagSet'], entity_supply_air) )
g.add( (entity_return_damper     , BRICK['hasTagSet'], entity_return_air) )
g.add( (entity_supply_pressure   , BRICK['hasTagSet'], entity_supply_air) )
g.add( (entity_cooling_coil      , BRICK['hasTagSet'], entity_supply_air) )
g.add( (entity_supply_temperature, BRICK['hasTagSet'], entity_supply_air) )

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

