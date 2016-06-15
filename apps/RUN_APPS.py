#!/usr/bin/env python

import sys
import os
import rdflib

if len(sys.argv) < 2:
    print "Need a turtle file of a building"
    sys.exit(0)

RDF = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = rdflib.Namespace('http://www.w3.org/2000/01/rdf-schema#')
BRICK = rdflib.Namespace('http://buildsys.org/ontologies/Brick#')
BRICKFRAME = rdflib.Namespace('http://buildsys.org/ontologies/BrickFrame#')
BRICKTAG = rdflib.Namespace('http://buildsys.org/ontologies/BrickTag#')

def new_graph():
    g = rdflib.Graph()
    g.bind( 'rdf', RDF)
    g.bind( 'rdfs', RDFS)
    g.bind( 'brick', BRICK)
    g.bind( 'bf', BRICKFRAME)
    g.bind( 'btag', BRICKTAG)
    return g

g = new_graph()
g.parse(sys.argv[1], format='turtle')
print "--- Occupancy Modeling App ---"
print "Finding Temp, CO2, Occ sensors in all rooms"
res = g.query("""
SELECT ?sensor ?sensor_type ?room
WHERE {
    ?sensor_type rdfs:subClassOf brick:Sensor .
    { ?sensor_type bf:hasTag brick:Temperature }
        UNION
    { ?sensor_type bf:hasTag brick:CO2 }
        UNION
    { ?sensor_type bf:hasTag brick:Occupancy }
    ?sensor rdf:type ?sensor_type .
    ?room rdf:type brick:Room .
    ?sensor bf:isLocatedIn ?room .
    ?sensor bf:isPointOf ?room .

}""")
print "-> {0} results".format(len(res))
print

print "Finding all power meters for equipment in rooms"
res = g.query("""
SELECT ?meter ?equipment ?room
WHERE {
    ?meter rdf:type brick:Power_Meter .
    ?room rdf:type brick:Room .
    ?equipment rdf:type brick:Equipment .
    ?equipment bf:isLocatedIn ?room .
    ?meter bf:isPointOf ?equipment .
}""")
print "-> {0} results".format(len(res))
print

print "Find all power meters for HVAC equipment"
res = g.query("""
SELECT ?meter ?equipment ?room
WHERE {
    ?meter rdf:type brick:Power_Meter .
    ?equipment rdf:type brick:Equipment .
    ?room rdf:type brick:Room .
    ?meter bf:isPointOf ?equipment .
    ?equipment bf:hasTag brick:HVAC .
    ?equipment bf:feeds+ ?zone .
    ?zone bf:hasPart ?room .
}""")
print "-> {0} results".format(len(res))
print

print "Find all power meters for Lighting equipment"
res = g.query("""
SELECT ?meter ?equipment ?room
WHERE {
    ?meter rdf:type brick:Power_Meter .
    ?equipment rdf:type brick:Equipment .
    ?room rdf:type brick:Room .
    ?meter bf:isPointOf ?equipment .
    ?equipment bf:hasTag brick:Lighting .
    ?zone bf:hasPart ?room .
    { ?equipment bf:feeds+ ?zone }
        UNION
    { ?equipment bf:feeds+ ?room }
}""")
print "-> {0} results".format(len(res))
print

print "--- Energy Apportionment App ---"
print "Find Occ sensors in all rooms"
res = g.query("""
SELECT ?sensor ?room
WHERE {
    ?sensor_type rdfs:subClassOf brick:Sensor .
    ?sensor_type bf:hasTag brick:Occupancy .
    ?sensor rdf:type ?sensor_type .
    ?room rdf:type brick:Room .
    ?sensor bf:isLocatedIn ?room .
    ?sensor bf:isPointOf ?room .
}""")
print "-> {0} results".format(len(res))
print

print "Find lux sensors in rooms"
res = g.query("""
SELECT ?sensor ?room
WHERE {
    ?sensor_type rdfs:subClassOf brick:Sensor .
    ?sensor_type bf:hasTag brick:Illumination .
    ?sensor rdf:type ?sensor_type .
    ?room rdf:type brick:Room .
    ?sensor bf:isLocatedIn ?room .
    ?sensor bf:isPointOf ?room .
}""")
print "-> {0} results".format(len(res))
print

print "Find lighting/hvac equipment (e.g. desk lamps) rooms"
res = g.query("""
SELECT ?equipment ?room
WHERE {
    ?equipment rdf:type brick:Equipment .
    ?room rdf:type brick:Room .

    ?equipment bf:isLocatedIn ?room .

    { ?equipment bf:hasTag brick:Lighting }
    UNION
    { ?equipment bf:hasTag brick:HVAC }
}""")
print "-> {0} results".format(len(res))
print
