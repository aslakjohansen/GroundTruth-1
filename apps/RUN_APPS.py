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
    g.parse('../BuildingSchema/Brick.ttl', format='turtle')
    g.parse('../BuildingSchema/BrickFrame.ttl', format='turtle')
    g.parse('../BuildingSchema/BrickTag.ttl', format='turtle')
    return g

g = new_graph()
g.parse(sys.argv[1], format='turtle')
print "--- Occupancy Modeling App ---"
print "Finding Temp, CO2, Occ sensors in all rooms"
res = g.query("""
SELECT ?sensor ?sensor_type ?room
WHERE {
    ?sensor_type rdfs:subClassOf brick:Sensor .
    { ?sensor_type bf:hasTag btag:Temperature }
        UNION
    { ?sensor_type bf:hasTag btag:CO2 }
        UNION
    { ?sensor_type bf:hasTag btag:Occupancy }
    ?sensor rdf:type ?sensor_type .
    ?room rdf:type brick:Room .
    ?sensor bf:isLocatedIn ?room .
    ?sensor bf:isPointOf ?room .

}""")
print "-> {0} results".format(len(res))

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

print "Find all power meters for HVAC equipment"
res = g.query("""
SELECT ?meter ?equipment ?room
WHERE {
    ?meter rdf:type brick:Power_Meter .
    ?equipment rdf:type brick:Equipment .
    ?room rdf:type brick:Room .
    ?meter bf:isPointOf ?equipment .
    ?equipment bf:hasTag btag:HVAC .
    ?equipment bf:feeds+ ?zone .
    ?zone bf:hasPart ?room .
}""")
print "-> {0} results".format(len(res))

print "Find all power meters for Lighting equipment"
res = g.query("""
SELECT ?meter ?equipment ?room
WHERE {
    ?meter rdf:type brick:Power_Meter .
    ?equipment rdf:type brick:Equipment .
    ?room rdf:type brick:Room .
    ?meter bf:isPointOf ?equipment .
    ?equipment bf:hasTag btag:Lighting .
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
    ?sensor_type bf:hasTag btag:Occupancy .
    ?sensor rdf:type ?sensor_type .
    ?room rdf:type brick:Room .
    ?sensor bf:isLocatedIn ?room .
    ?sensor bf:isPointOf ?room .
}""")
print "-> {0} results".format(len(res))

print "Find lux sensors in rooms"
res = g.query("""
SELECT ?sensor ?room
WHERE {
    ?sensor_type rdfs:subClassOf brick:Sensor .
    ?sensor_type bf:hasTag btag:Illumination .
    ?sensor rdf:type ?sensor_type .
    ?room rdf:type brick:Room .
    ?sensor bf:isLocatedIn ?room .
    ?sensor bf:isPointOf ?room .
}""")
print "-> {0} results".format(len(res))

print "Find lighting/hvac equipment (e.g. desk lamps) rooms"
res = g.query("""
SELECT ?equipment ?room
WHERE {
    ?equipment rdf:type brick:Equipment .
    ?room rdf:type brick:Room .

    ?equipment bf:isLocatedIn ?room .

    { ?equipment bf:hasTag btag:Lighting }
    UNION
    { ?equipment bf:hasTag btag:HVAC }
}""")
print "-> {0} results".format(len(res))

print

print "--- Web Displays App ---"
print "Reheat valve command for VAVs"
res = g.query("""
SELECT ?reheat_vlv_cmd ?vav
WHERE {
    ?reheat_vlv_cmd rdf:type brick:Reheat_Valve_Command .
    ?vav rdf:type brick:VAV .
    ?vav bf:hasPoint+ ?reheat_vlv_cmd .
}
""")
print "-> {0} results".format(len(res))

print "Airflow sensor for all VAVs"
res = g.query("""
SELECT ?airflow_sensor ?room ?vav
WHERE {
    ?airflow_sensor rdf:type brick:Sensor .
    ?airflow_sensor bf:hasTag btag:Air .
    ?airflow_sensor bf:hasTag btag:Flow .
    ?vav rdf:type brick:VAV .
    ?room rdf:type brick:Room .
    { ?airflow_sensor bf:isPartOf ?vav }
        UNION
    { ?vav bf:feeds+ ?airflow_sensor }
}""")
print "-> {0} results".format(len(res))

print "Associate VAVs to zones and rooms"
res = g.query("""
SELECT ?vav ?room
WHERE {
    ?vav rdf:type brick:VAV .
    ?room rdf:type brick:Room .
    ?vav bf:feeds+ ?zone .
    ?room bf:isPartOf ?zone .
}""")
print "-> {0} results".format(len(res))

print "Find power meters for cooling loop, heating loop"
res = g.query("""
SELECT ?equip ?equip_type ?meter
WHERE {
    ?equip_type rdfs:subClassOf brick:Equipment .
    ?equip rdf:type ?equip_type .
    ?meter rdf:type brick:Power_Meter .
    ?equip rdfs:subClassOf brick:Water_System .
    { ?equip bf:hasTag btag:Chilled }
        UNION
    { ?equip bf:hasTag btag:Hot }
    ?meter bf:isPointOf ?equip .
}""")
print "-> {0} results".format(len(res))

print

print "--- Model-Predictive Control App ---"

print "Find all buildings, floors, hvac zones, rooms"
res = g.query("""
SELECT ?bldg ?floor ?hvac_zone ?room
WHERE {
    ?bldg rdf:type brick:Building .
    ?floor rdf:type brick:Floor .
    ?room rdf:type brick:Room .
    ?hvac_zone rdf:type brick:Zone .
    ?hvac_zone bf:hasTag btag:HVAC .
    ?floor bf:isPartOf ?bldg .
    ?room bf:isPartOf ?floor .
    ?room bf:isPartOf ?hvac_zone .
}""")
print "-> {0} results".format(len(res))

#print "Find windows in the room"
print "Grab the orientation of the room if we have it"
res = g.query("""
SELECT ?room ?orientation
WHERE {
    ?room rdf:type brick:Room .
    ?room rdfs:hasProperty brick:Orientation .
    ?orientation rdf:type brick:Orientation .
}""")
print "-> {0} results".format(len(res))

print "Grab all VAVs and AHUs and zones"
res = g.query("""SELECT ?vav ?ahu ?hvac_zone
WHERE {
    ?vav rdf:type brick:VAV .
    ?ahu rdf:type brick:AHU .
    ?ahu bf:feeds ?vav .
    ?hvac_zone rdf:type brick:Zone .
    ?hvac_zone bf:hasTag btag:HVAC .
    ?vav  bf:feeds ?hvac_zone .
}""")
print "-> {0} results".format(len(res))

print

print "--- Participatory Feedback ---"

print "Associate lighting with rooms"
res = g.query("""
SELECT ?light_equip ?light_state ?light_cmd ?room
WHERE {
    ?light_equip rdf:type brick:Equipment .
    ?light_equip bf:hasTag btag:Lighting .
    ?light_equip bf:feeds ?zone .
    ?zone rdf:type brick:Zone .
    ?zone bf:hasTag btag:Lighting .
    ?zone bf:contains ?room .
    ?room rdf:type brick:Room .
    ?light_state rdf:type brick:Status .
    ?light_state bf:isPointOf ?light_equip .
    ?light_state bf:hasTag btag:Luminance .
    ?light_cmd rdf:type brick:Command .
    ?light_cmd bf:isPointOf ?light_equip .
    ?light_cmd bf:hasTag btag:Luminance .
}""")
print "-> {0} results".format(len(res))

print "Find all power meters and associate them with floor and room"
res = g.query("""
SELECT ?meter ?floor ?room
WHERE {
    ?meter  rdf:type    brick:Sensor .
    ?meter  bf:hasTag   btag:Power .
    ?loc    rdf:type    brick:Location .
    { ?room   bf:isLocatedIn ?loc }
    UNION
    { ?room   bf:isPartOf ?loc }
    ?meter  bf:isPointOf+ ?loc
}""")
print "-> {0} results".format(len(res))

print

print "DO THIS!!! --- Fault Detection Diagnosis ---"

print

print "--- Non-Intrusive Load Monitoring App ---"
print "Get equipment, power meters and what floor/room they are in"
res = g.query("""
SELECT ?equip ?meter ?floor ?room
WHERE {
    ?equip  rdf:type    brick:Equipment .
    ?meter  rdf:type    brick:Sensor .
    ?meter  bf:hasTag   btag:Power .
    ?loc    rdf:type    brick:Location .
    { ?room   bf:isLocatedIn ?loc }
    UNION
    { ?room   bf:isPartOf ?loc }
    ?meter  bf:isPointOf+ ?loc
    { ?equip  bf:isLocatedIn+ ?loc }
    UNION
    { ?equip  bf:isPartOf+ ?loc }
}
""")
print "-> {0} results".format(len(res))

print

print "--- Demand Response ---"
print "Find all equipment (inside rooms) and associated power meters and control points"
res = g.query("""
SELECT ?equip ?meter ?cmd
WHERE {
    ?cmd    rdf:type    brick:Command .
    ?equip  rdf:type    brick:Equipment .
    ?meter  rdf:type    brick:Sensor .
    ?meter  bf:hasTag   btag:Power .
    ?room   rdf:type    brick:Room .
    ?equip  bf:isLocatedIn ?room .
    ?meter  bf:isPointOf ?equip .
    ?cmd    bf:isPointOf ?equip .
}""")
print "-> {0} results".format(len(res))
