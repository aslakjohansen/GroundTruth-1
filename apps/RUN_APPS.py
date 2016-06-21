#!/usr/bin/env python

import sys
import os
import rdflib

try:
    from termcolor import colored
except:
    def f(x,y):
        print x
    colored = f

def printResults(res):
    if len(res) > 0:
        color = 'green'
    else:
        color = 'red'
    print colored("-> {0} results".format(len(res)), color, attrs=['bold'])

def printTuples(res):
    for row in res:
        print map(lambda x: x.split('#')[-1], row)

if len(sys.argv) < 2:
    print "Need a turtle file of a building"
    sys.exit(0)

RDF = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = rdflib.Namespace('http://www.w3.org/2000/01/rdf-schema#')
BRICK = rdflib.Namespace('http://buildsys.org/ontologies/Brick#')
BRICKFRAME = rdflib.Namespace('http://buildsys.org/ontologies/BrickFrame#')
BRICKTAG = rdflib.Namespace('http://buildsys.org/ontologies/BrickTag#')
OWL = rdflib.Namespace('http://www.w3.org/2002/07/owl#')

def new_graph():
    g = rdflib.Graph()
    g.bind( 'rdf', RDF)
    g.bind( 'rdfs', RDFS)
    g.bind( 'brick', BRICK)
    g.bind( 'bf', BRICKFRAME)
    g.bind( 'btag', BRICKTAG)
    g.bind( 'owl', OWL)
    g.parse('../BuildingSchema/Brick.ttl', format='turtle')
    g.parse('../BuildingSchema/BrickFrame.ttl', format='turtle')
    g.parse('../BuildingSchema/BrickTag.ttl', format='turtle')
    return g

g = new_graph()
g.parse(sys.argv[1], format='turtle')

# ADD INVERSE RELATIONSHIPS
res = g.query("SELECT ?a ?b WHERE { ?a bf:hasPart ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.isPartOf, row[0]))

res = g.query("SELECT ?a ?b WHERE {?a bf:hasPoint ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.isPointOf, row[0]))

res = g.query("SELECT ?a ?b WHERE {?a bf:feeds ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.isFedBy, row[0]))

res = g.query("SELECT ?a ?b WHERE {?a bf:contains ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.isLocatedIn, row[0]))

res = g.query("SELECT ?a ?b WHERE {?a bf:controls ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.isControlledBy, row[0]))

res = g.query("SELECT ?a ?b WHERE {?a bf:hasOutput ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.isOutputOf, row[0]))

res = g.query("SELECT ?a ?b WHERE {?a bf:hasInput ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.isInputOf, row[0]))

res = g.query("SELECT ?a ?b WHERE {?a bf:hasTagSet ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.isTagSetOf, row[0]))

res = g.query("SELECT ?a ?b WHERE {?a bf:hasToken ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.isTokenOf, row[0]))

print "--- Occupancy Modeling App ---"      ############################################ Occupancy Modeling
print "Finding Temp, CO2, Occ sensors in all rooms"
res = g.query("""
SELECT ?sensor ?room
WHERE {

    {
      { ?sensor rdf:type ?class .
        ?class rdfs:subClassOf brick:Temperature_Sensor . }
      UNION
      { ?sensor rdf:type brick:Temperature_Sensor }
    }

        UNION

    {
      { ?sensor rdf:type ?class .
        ?class rdfs:subClassOf brick:Occupancy_Sensor . }
      UNION
      { ?sensor rdf:type brick:Occupancy_Sensor }
    }

        UNION

    {
      { ?sensor rdf:type ?class .
        ?class rdfs:subClassOf brick:CO2_Sensor . }
      UNION
      { ?sensor rdf:type brick:CO2_Sensor }
    }

    ?room rdf:type brick:Room .
    ?sensor bf:isPointOf ?room .

}""")
printResults(res)

print "Finding all power meters for equipment in rooms"
res = g.query("""
SELECT ?meter ?equipment ?room
WHERE {

    {
        {?meter rdf:type brick:Power_Meter}
        UNION
        {?meter rdf:type ?class .
         ?class rdfs:subClassOf brick:Power_Meter}
    }

    ?room rdf:type brick:Room .
    ?equipment rdf:type brick:Equipment .
    ?equipment bf:isLocatedIn ?room .
    ?meter bf:isPointOf ?equipment .
}""")
printResults(res)


print "Find all power meters for HVAC equipment"
res = g.query("""
SELECT ?meter ?equipment ?room
WHERE {
    {
        {?meter rdf:type brick:Power_Meter}
        UNION
        {?meter rdf:type ?class .
         ?class rdfs:subClassOf brick:Power_Meter}
    }
    ?equipment rdf:type brick:Equipment .
    ?room rdf:type brick:Room .
    ?meter bf:isPointOf ?equipment .

    ?equipment rdf:type ?class .
    ?class rdfs:subClassOf brick:HVAC .

    ?equipment bf:feeds+ ?zone .
    ?zone bf:hasPart ?room .
}""")
printResults(res)

print "Find all power meters for Lighting equipment"
res = g.query("""
SELECT ?meter ?equipment ?room
WHERE {
    ?meter rdf:type brick:Power_Meter .
    ?equipment rdf:type brick:Equipment .
    ?room rdf:type brick:Room .
    ?meter bf:isPointOf ?equipment .

    ?equipment rdf:type ?class .
    ?class rdfs:subClassOf brick:Lighting .

    ?zone bf:hasPart ?room .
    { ?equipment bf:feeds+ ?zone }
        UNION
    { ?equipment bf:feeds+ ?room }
}""")
printResults(res)

print "...or if that doesn't work, find all power meters"
res = g.query("""
SELECT ?meter ?loc
WHERE {
    {
        {?meter rdf:type brick:Power_Meter}
        UNION
        {?meter rdf:type ?class .
         ?class rdfs:subClassOf brick:Power_Meter}
    }
    ?loc rdf:type ?loc_class .
    ?loc_class rdfs:subClassOf brick:Location .

    ?loc bf:hasPoint ?meter .
}
""")
printResults(res)

print

print "--- Energy Apportionment App ---"      ############################################ Energy Apportionment
print "Find Occ sensors in all rooms"
res = g.query("""
SELECT ?sensor ?room
WHERE {
    {
      { ?sensor rdf:type ?class .
        ?class rdfs:subClassOf brick:Occupancy_Sensor . }
      UNION
      { ?sensor rdf:type brick:Occupancy_Sensor }
    }
    ?room rdf:type brick:Room .
    ?sensor bf:isLocatedIn ?room .
    ?sensor bf:isPointOf ?room .
}""")
printResults(res)

print "Find lux sensors in rooms"
res = g.query("""
SELECT ?sensor ?room
WHERE {
    {
      { ?sensor rdf:type ?class .
        ?class rdfs:subClassOf brick:Luminance_Sensor . }
      UNION
      { ?sensor rdf:type brick:Luminance_Sensor }
    }
    ?room rdf:type brick:Room .
    ?sensor bf:isLocatedIn ?room .
    ?sensor bf:isPointOf ?room .
}""")
printResults(res)

print "Find lighting/hvac equipment (e.g. desk lamps) rooms"
res = g.query("""
SELECT ?equipment ?room
WHERE {
    ?equipment rdf:type brick:Equipment .
    ?room rdf:type brick:Room .

    ?equipment bf:isLocatedIn ?room .

    { ?equipment rdf:type ?class .
      ?class rdfs:subClassOf brick:Lighting .}
    UNION
    { ?equipment rdf:type ?class .
      ?class rdfs:subClassOf brick:HVAC .}
}""")
printResults(res)

print

print "--- Web Displays App ---"  ################################################ Web Displays
print "Reheat valve command for VAVs"
res = g.query("""
SELECT ?reheat_vlv_cmd ?vav
WHERE {
    ?reheat_vlv_cmd rdf:type brick:Reheat_Valve_Command .
    ?vav rdf:type brick:VAV .
    ?vav bf:hasPoint+ ?reheat_vlv_cmd .
}
""")
printResults(res)

print "Airflow sensor for all VAVs"
res = g.query("""
SELECT ?airflow_sensor ?room ?vav
WHERE {
    {
      { ?sensor rdf:type ?class .
        ?class rdfs:subClassOf brick:Discharge_Air_Flow_Sensor . }
      UNION
      { ?sensor rdf:type brick:Discharge_Air_Flow_Sensor }
    }

    ?vav rdf:type brick:VAV .
    ?room rdf:type brick:Room .

    { ?airflow_sensor bf:isPartOf ?vav }
        UNION
    { ?vav bf:feeds+ ?airflow_sensor }
}""")
printResults(res)

print "Associate VAVs to zones and rooms"
res = g.query("""
SELECT ?vav ?room
WHERE {
    ?vav rdf:type brick:VAV .
    ?room rdf:type brick:Room .
    ?vav bf:feeds+ ?zone .
    ?room bf:isPartOf ?zone .
}""")
printResults(res)

print "Find power meters for cooling loop, heating loop"
res = g.query("""
SELECT ?equip ?equip_type ?meter
WHERE {
    ?equip_type rdfs:subClassOf brick:Equipment .
    ?equip rdf:type ?equip_type .
    ?meter rdf:type brick:Power_Meter .

    ?equip rdf:type ?class .
    ?class rdfs:subClassOf brick:Water_System .
    ?meter bf:isPointOf ?equip .
}""")
printResults(res)

print

print "--- Model-Predictive Control App ---"

print "Find all buildings, floors, hvac zones, rooms"
res = g.query("""
SELECT ?bldg ?floor ?room ?zone
WHERE {
    ?bldg rdf:type brick:Building .
    ?floor rdf:type brick:Floor .
    ?room rdf:type brick:Room .
    ?zone rdf:type brick:HVAC_Zone .

    ?floor bf:isPartOf+ ?bldg .
    ?room bf:isPartOf+ ?floor .
    ?room bf:isPartOf+ ?zone .
}""")
printResults(res)

#print "Find windows in the room"
print "Grab the orientation of the room if we have it"
res = g.query("""
SELECT ?room ?orientation
WHERE {
    ?room rdf:type brick:Room .
    ?room rdfs:hasProperty brick:Orientation .
    ?orientation rdf:type brick:Orientation .
}""")
printResults(res)

print "Grab all VAVs and AHUs and zones"
res = g.query("""SELECT ?vav ?ahu ?hvac_zone
WHERE {
    ?vav rdf:type brick:VAV .
    ?ahu rdf:type brick:AHU .
    ?ahu bf:feeds ?vav .
    ?hvac_zone rdf:type brick:HVAC_Zone .
    ?vav  bf:feeds ?hvac_zone .
}""")
printResults(res)

print

print "--- Participatory Feedback ---"

print "Associate lighting with rooms"
res = g.query("""
SELECT ?light_equip ?light_state ?light_cmd ?room
WHERE {

    # OR do we do ?light_equip rdf:type brick:Lighting_System
    ?light_equip rdf:type ?class .
    ?class rdfs:subClassOf brick:Lighting_System .

    ?light_equip bf:feeds ?zone .
    ?zone rdf:type brick:Lighting_Zone .
    ?zone bf:contains ?room .
    ?room rdf:type brick:Room .

    {
      { ?light_state rdf:type ?state_class .
        ?state_class rdfs:subClassOf brick:Luminance_Status . }
      UNION
      { ?light_state rdf:type brick:Luminance_Status }
    }

    {
      { ?light_cmd rdf:type ?cmd_class .
        ?cmd_class rdfs:subClassOf brick:Luminance_Command . }
      UNION
      { ?light_cmd rdf:type brick:Luminance_Command }
    }
}""")
printResults(res)

print "Find all power meters and associate them with floor and room"
g.query("CONSTRUCT {?a bf:isPointOf ?b} WHERE {?b bf:hasPoint ?a}")
res = g.query("""
SELECT ?meter ?loc
WHERE {

    {
        {?meter rdf:type brick:Power_Meter}
        UNION
        {?meter rdf:type ?class .
         ?class rdfs:subClassOf brick:Power_Meter}
    }

    { ?loc    rdf:type    brick:Room }
        UNION
    { ?loc rdf:type brick:Floor }

    ?meter  bf:isPointOf ?loc .
}""")
printResults(res)
#printTuples(res)

print

print "DO THIS!!! --- Fault Detection Diagnosis ---"

print

print "--- Non-Intrusive Load Monitoring App ---"
print "Get equipment, power meters and what floor/room they are in"
res = g.query("""
SELECT ?equip ?meter ?floor ?room
WHERE {
    {
        {?meter rdf:type brick:Power_Meter}
        UNION
        {?meter rdf:type ?class .
         ?class rdfs:subClassOf brick:Power_Meter}
    }

    ?equip  rdf:type    brick:Equipment .
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
printResults(res)

print

print "--- Demand Response ---"
print "Find all equipment (inside rooms) and associated power meters and control points"
res = g.query("""
SELECT ?equip ?meter ?cmd
WHERE {
    {
        {?meter rdf:type brick:Power_Meter}
        UNION
        {?meter rdf:type ?class .
         ?class rdfs:subClassOf brick:Power_Meter}
    }
    ?cmd    rdf:type    brick:Command .
    ?equip  rdf:type    brick:Equipment .
    ?room   rdf:type    brick:Room .
    ?equip  bf:isLocatedIn ?room .
    ?meter  bf:isPointOf ?equip .
    ?cmd    bf:isPointOf ?equip .
}""")
printResults(res)
