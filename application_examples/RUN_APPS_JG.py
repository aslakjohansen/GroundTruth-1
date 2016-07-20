#!/usr/bin/env python

import sys
import os
import rdflib

if len(sys.argv) < 2:
    print "Need a turtle file of a building"
    sys.exit(0)

RDF = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = rdflib.Namespace('http://www.w3.org/2000/01/rdf-schema#')
BRICK = rdflib.Namespace('http://buildsys.org/ontologies/brick#')
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
print "Finding Occ sensors in all rooms"
res = g.query("""
SELECT ?sensor ?room
WHERE {
    ?sensor rdf:type brick:Occupancy_Sensor .
    ?room rdf:type brick:Room .
    ?sensor brick:isPointOf ?room .

}""")
print "-> {0} results".format(len(res))

#Why are these three things necessary? Occupancy modeling should only take the occupancy sensor... right? What is all the metering stuff for?
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
    ?meter brick:isPointOf ?equipment .
    ?equipment bf:hasTag btag:HVAC .
    ?equipment bf:feeds ?zone .
    ?zone brick:contains ?room .
}""")
print "-> {0} results".format(len(res))

print "Find all power meters for Lighting equipment"
res = g.query("""
SELECT ?meter ?equipment ?room
WHERE {
    ?meter rdf:type brick:Power_Meter .
    ?equipment rdf:type brick:Lighting_System .
    ?room rdf:type brick:Room .
    ?meter brick:isPointOf ?equipment .
    ?zone brick:contains ?room .
    { ?equipment brick:feeds+ ?zone }
        UNION
    { ?equipment brick:feeds+ ?room }
}""")
print "-> {0} results".format(len(res))

print

print "--- Energy Apportionment App ---"
print "Find Occ sensors in all rooms"
res = g.query("""
SELECT ?sensor ?room
WHERE {
    ?sensor rdf:type brick:Occupancy_Sensor .
    ?room rdf:type brick:Room .
    ?sensor bf:isLocatedIn ?room .
}""")
print "-> {0} results".format(len(res))

print "Find lux sensors in rooms"
res = g.query("""
SELECT ?sensor ?room
WHERE {
    ?sensor rdf:type brick:Luminance_Sensor .
    ?room rdf:type brick:Room .
    ?sensor brick:isLocatedIn ?room .
}""")
print "-> {0} results".format(len(res))

#What's Tags for here?
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
    ?vav brick:hasPoint ?reheat_vlv_cmd .
}
""")
print "-> {0} results".format(len(res))

print "Airflow sensor for all VAVs"
res = g.query("""
SELECT ?airflow_sensor ?room ?vav
WHERE {
    ?airflow_sensor rdf:type brick:Discharge_Air_Flow_Sensor .
    ?vav rdf:type brick:VAV .
    ?room rdf:type brick:Room .
    ?airflow_sensor brick:isLocatedIn ?room .
    ?vav brick:hasPoint ?airflow_sensor .
}""")
print "-> {0} results".format(len(res))

print "Associate VAVs to zones and rooms"
res = g.query("""
SELECT ?vav ?room
WHERE {
    ?vav rdf:type brick:VAV .
    ?room rdf:type brick:Room .
    ?vav brick:feeds ?zone .
    ?room brick:isLocatedIn ?zone .
}""")
print "-> {0} results".format(len(res))

#Can't figure this one out.
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
    ?hvac_zone rdf:type brick:HVAC_Zone .
    ?floor brick:isPartOf ?bldg .
    ?room brick:isPartOf ?floor .
    ?room brick:isLocatedIn ?hvac_zone .
}""")
print "-> {0} results".format(len(res))

#GHC Doesn't have orientiation data
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
    ?hvac_zone rdf:type brick:HVAC_Zone .
    ?vav  bf:feeds ?hvac_zone .
}""")
print "-> {0} results".format(len(res))

print

print "--- Participatory Feedback ---"

#GHC Doesn't have lighting equipment
print "Associate lighting with rooms"
res = g.query("""
SELECT ?light_equip ?light_state ?light_cmd ?room
WHERE {
    ?light_equip rdf:type brick:Lighting_System .
    ?light_equip brick:feeds ?zone .
    ?zone rdf:type brick:Lighting_Zone .
    ?zone brick:contains ?room .
    ?room rdf:type brick:Room .
    ?light_state rdf:type brick:Status .
    ?light_state bf:isPointOf ?light_equip .
    ?light_cmd rdf:type brick:Command .
    ?light_cmd bf:isPointOf ?light_equip .
}""")
print "-> {0} results".format(len(res))

#GHC Can't do this (no low-level power meters)
print "Find all power meters and associate them with room"
res = g.query("""
SELECT ?meter ?room
WHERE {
    ?meter  rdf:type    brick:Sensor .
    ?meter  rdf:type    brick:Power_Meter .
    ?room    rdf:type    brick:Room .
    ?equip   rdf:type   brick:Equipment .
    ?meter brick:isPointOf ?equip .
    ?equip  brick:isLocatedIn ?room .
}""")
print "-> {0} results".format(len(res))

print

print "DO THIS!!! --- Fault Detection Diagnosis ---"

print

#GHC Can't Do this (no low-level power meters)
print "--- Non-Intrusive Load Monitoring App ---"
print "Get equipment, power meters and what room they are in"
res = g.query("""
SELECT ?equip ?meter ?floor ?room
WHERE {
    ?equip  rdf:type    brick:Equipment .
    ?meter  rdf:type    brick:Power_Meter .
    ?room    rdf:type    brick:Room .
    ?meter   brick:isPointOf ?equip .
    ?equip   brick:isLocatedIn ?room .
}
""")
print "-> {0} results".format(len(res))

print

#GHC Can't do this (no low-level power meters)
print "--- Demand Response ---"
print "Find all equipment (inside rooms) and associated power meters and control points"
res = g.query("""
SELECT ?equip ?meter ?cmd
WHERE {
    ?cmd    rdf:type    brick:Command .
    ?equip  rdf:type    brick:Equipment .
    ?meter  rdf:type    brick:Power_Meter .
    ?room   rdf:type    brick:Room .
    ?equip  bf:isLocatedIn ?room .
    ?meter  bf:isPointOf ?equip .
    ?cmd    bf:isPointOf ?equip .
}""")
print "-> {0} results".format(len(res))
