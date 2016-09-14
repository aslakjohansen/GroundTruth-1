
# coding: utf-8

# In[1]:

import sys
import os
import rdflib

try:
    from termcolor import colored
except:
    print("pip install termcolor")
    def f(x,y, attrs=[]):
        print(x)
    colored = f


# The rule-based FDD application requires the following minimal inputs from AHUs in order to run the rules:

# In[2]:

def printResults(res):
    if len(res) > 0:
        color = 'green'
    else:
        color = 'red'
    print(colored("-> {0} results".format(len(res)), color, attrs=['bold']))

def printTuples(res):
    for row in res:
        print(map(lambda x: x.split('#')[-1], row))

if len(sys.argv) < 2:
    print("Need a turtle file of a building")
    sys.exit(0)


# In[3]:

bfile="../etc/instance_generators/GTC_SDU/gtc_brick.ttl"
bfile="../etc/instance_generators/IBM/IBM_B3.ttl"


# In[4]:

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
    g.parse('../Brick/Brick.ttl', format='turtle')
    g.parse('../Brick/BrickFrame.ttl', format='turtle')
    g.parse('../Brick/BrickTag.ttl', format='turtle')
    return(g)

g = new_graph()
g.parse(bfile, format='turtle')


# In[5]:

# ADD INVERSE RELATIONSHIPS
res = g.query("SELECT ?a ?b WHERE { ?a bf:hasPart ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.isPartOf, row[0]))
res = g.query("SELECT ?a ?b WHERE { ?a bf:isPartOf ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.hasPart, row[0]))

res = g.query("SELECT ?a ?b WHERE {?a bf:hasPoint ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.isPointOf, row[0]))
res = g.query("SELECT ?a ?b WHERE {?a bf:isPointOf ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.hasPoint, row[0]))

res = g.query("SELECT ?a ?b WHERE {?a bf:feeds ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.isFedBy, row[0]))
res = g.query("SELECT ?a ?b WHERE {?a bf:isFedBy ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.feeds, row[0]))

res = g.query("SELECT ?a ?b WHERE {?a bf:contains ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.isLocatedIn, row[0]))
res = g.query("SELECT ?a ?b WHERE {?a bf:isLocatedIn ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.contains, row[0]))

res = g.query("SELECT ?a ?b WHERE {?a bf:controls ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.isControlledBy, row[0]))
res = g.query("SELECT ?a ?b WHERE {?a bf:isControlledBy ?b .}")
for row in res:
    g.add((row[1], BRICKFRAME.controls, row[0]))

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

print()


# In[6]:

print("--- Occupancy Modeling App ---")      ############################################ Occupancy Modeling
print("Finding Temp sensors in all rooms")
res = g.query("""
SELECT DISTINCT ?room
WHERE {
    ?room rdf:type/rdfs:subClassOf* brick:Location .

}""")
printResults(res)


# In[7]:

print("--- Occupancy Modeling App ---")      ############################################ Occupancy Modeling
print("Finding Temp sensors in all rooms")
res = g.query("""
SELECT DISTINCT ?sensor ?zone
WHERE {

    { ?sensor rdf:type/rdfs:subClassOf* brick:Zone_Temperature_Sensor . }
    UNION
    { ?sensor rdf:type/rdfs:subClassOf* brick:FCU_Discharge_Air_Temperature_Sensor . }
    UNION
    { ?sensor rdf:type brick:FCU_Supply_Air_Temperature_Sensor . }
    UNION
    { ?sensor rdf:type/rdfs:subClassOf* brick:FCU_Supply_Air_Temperature_Sensor . }
    UNION
    { ?sensor rdf:type/rdfs:subClassOf* brick:Discharge_Air_Temperature_Sensor . }
    UNION
    { ?sensor rdf:type/rdfs:subClassOf* brick:Supply_Air_Temperature_Sensor . }
    UNION
    { ?sensor rdf:type/rdfs:subClassOf* brick:Occupancy_Sensor . }
    UNION
    { ?sensor rdf:type/rdfs:subClassOf* brick:CO2_Sensor . }
    
    ?sensor bf:isPointOf ?vav .
    ?vav bf:feeds ?zone .

    ?vav rdf:type/rdfs:subClassOf* brick:Terminal_Unit .
    ?zone rdf:type/rdfs:subClassOf* brick:Location .
}""")
occN=len(res)
printResults(res)


# In[8]:

print("Finding CO2, Occ sensors")
res = g.query("""
SELECT DISTINCT ?sensor ?vav
WHERE {

    { ?sensor rdf:type/rdfs:subClassOf* brick:Occupancy_Sensor . }
    UNION
    { ?sensor rdf:type/rdfs:subClassOf* brick:CO2_Sensor . }
    
    ?sensor bf:isPointOf ?room .

    ?room rdf:type/rdfs:subClassOf* brick:Location .

}""")
occN+=len(res)
printResults(res)


# In[9]:

print("Finding all power meters for equipment in rooms")
res = g.query("""
SELECT ?meter ?equipment ?room
WHERE {
    ?meter rdf:type/rdfs:subClassOf* brick:Power_Meter .
    ?room rdf:type/rdfs:subClassOf* brick:Location .
    ?equipment rdf:type/rdfs:subClassOf* brick:Equipment .
    ?equipment bf:isLocatedIn ?room .
    ?meter bf:isPointOf ?equipment .
}""")
occN+=len(res)
printResults(res)


# In[10]:

print("Find all power meters for HVAC equipment")
res = g.query("""
SELECT ?meter ?equipment ?room
WHERE {
    ?meter rdf:type/rdfs:subClassOf* brick:Power_Meter .
    ?room rdf:type/rdfs:subClassOf* brick:Location .
    ?meter bf:isPointOf ?equipment .
    ?equipment rdf:type/rdfs:subClassOf* brick:HVAC .

    ?zone rdf:type/rdfs:subClassOf* brick:Location .

    ?equipment bf:feeds+ ?zone .
    ?zone bf:hasPart ?room .
}""")
occN+=len(res)
printResults(res)


# In[11]:

print("Find all power meters for Lighting equipment")
res = g.query("""
SELECT ?meter ?equipment ?room
WHERE {
    ?meter rdf:type/rdfs:subClassOf* brick:Power_Meter .
    ?room rdf:type/rdfs:subClassOf* brick:Location .
    ?meter bf:isPointOf ?equipment .

    ?equipment rdf:type/rdfs:subClassOf* brick:Lighting_System .

    ?zone bf:hasPart ?room .
    { ?equipment bf:feeds+ ?zone }
     UNION
    { ?equipment bf:feeds+ ?room }
}""")
occN+=len(res)
printResults(res)


# In[12]:

print("...or if that doesn't work, find all power meters")
res = g.query("""
SELECT ?meter ?loc
WHERE {
    ?meter rdf:type/rdfs:subClassOf* brick:Power_Meter .
    ?loc bf:hasPoint ?meter .
    ?loc rdf:type/rdfs:subClassOf* brick:Location .
}
""")
occN+=len(res)
printResults(res)


# In[13]:

occN


# In[14]:

print("--- Energy Apportionment App ---")     ############################################ Energy Apportionment
print("Find Occ sensors in all rooms")
res = g.query("""
SELECT ?sensor ?room
WHERE {
    ?sensor rdf:type/rdfs:subClassOf* brick:Occupancy_Sensor . 
    ?sensor bf:isLocatedIn ?room .
    ?sensor bf:isPointOf ?room .
    ?room rdf:type/rdfs:subClassOf* brick:Location .
}""")
egyN=len(res)
printResults(res)


# In[15]:

print("Find lux sensors in rooms")
res = g.query("""
SELECT ?sensor ?room
WHERE {
    ?sensor rdf:type/rdfs:subClassOf* brick:Luminance_Sensor . 
    
    { ?sensor bf:isPointOf ?room .}
    UNION
    { ?sensor bf:isLocatedIn ?room .}
    
    ?room rdf:type/rdfs:subClassOf* brick:Location .
}""")
egyN+=len(res)
printResults(res)


# In[16]:

print("Find lighting/hvac equipment (e.g. desk lamps) rooms")
res = g.query("""
SELECT ?equipment ?room
WHERE {
    ?room rdf:type/rdfs:subClassOf* brick:Location .
    
    { ?sensor bf:feeds ?room .}
    UNION
    { ?sensor bf:isPointOf ?room .}
    UNION
    { ?sensor bf:isLocatedIn ?room .}
    
    { ?sensor rdf:type/rdfs:subClassOf* brick:Lighting_System .}
    UNION
    { ?sensor rdf:type/rdfs:subClassOf* brick:HVAC .}
    
}""")
egyN+=len(res)
printResults(res)


# In[17]:

egyN


# In[18]:

print("--- Web Displays App ---")  ################################################ Web Displays
print("Reheat/cool valve command for VAVs")
res = g.query("""
SELECT ?vlv_cmd ?vav
WHERE {

    ?vav rdf:type/rdfs:subClassOf* brick:Terminal_Unit .
    ?vav bf:hasPoint+ ?vlv_cmd .
    
    { ?vlv_cmd rdf:type brick:AHU_Cooling_Valve_Command }
    UNION
    { ?vlv_cmd rdf:type brick:FCU_Cooling_Valve_Command }
    UNION
    { ?vlv_cmd rdf:type brick:Reheat_Valve_Command }
    UNION
    { ?vlv_cmd rdf:type brick:Cooling_Valve_Command }
    
}
""")
webN=len(res)
printResults(res)


# In[19]:

print("Airflow sensor for all VAVs")
res = g.query("""
SELECT ?airflow_sensor ?room ?vav
WHERE {
    
    ?vav rdf:type/rdfs:subClassOf* brick:Terminal_Unit .
    ?vav bf:feeds+ ?zone .
    ?zone rdf:type/rdfs:subClassOf* brick:Location .
    ?airflow_sensor bf:isPointOf ?vav .
    
    { ?airflow_sensor rdf:type/rdfs:subClassOf* brick:AHU_Return_Fan_Air_Flow_Sensor . }
    UNION
    { ?airflow_sensor rdf:type/rdfs:subClassOf* brick:Discharge_Air_Flow_Sensor . }
    UNION
    { ?airflow_sensor rdf:type/rdfs:subClassOf* brick:Sensor . }

}""")
webN+=len(res)
printResults(res)


# In[20]:

print("Associate VAVs to zones and rooms")
res = g.query("""
SELECT ?vav ?room
WHERE {
    ?vav rdf:type/rdfs:subClassOf* brick:Terminal_Unit .
    ?zone rdf:type/rdfs:subClassOf* brick:Location .
    ?vav bf:feeds+ ?zone .
}""")
webN+=len(res)
printResults(res)


# In[21]:

print("Find power meters for cooling loop, heating loop")
res = g.query("""
SELECT ?equip ?meter
WHERE {
    ?meter rdf:type brick:Power_Meter .
    ?meter bf:isPointOf* ?equip .
    ?equip bf:isPartOf* ?thing .

    {?thing rdf:type/rdfs:subClassOf* brick:Water_System }
    UNION
    {?thing rdf:type/rdfs:subClassOf* brick:HVAC }
}""")
webN+=len(res)
printResults(res)
#printTuples(res)


# In[22]:

webN


# In[23]:

print("--- Model-Predictive Control App ---")
print("Find all floors, hvac zones, rooms")
res = g.query("""
# no more building
SELECT ?floor ?room ?zone
WHERE {
    ?floor rdf:type brick:Floor .
    ?room  rdf:type/rdfs:subClassOf* brick:Location .
    ?zone  rdf:type/rdfs:subClassOf* brick:Location .

    ?zone bf:isPartOf ?floor .
    ?room bf:isPartOf ?zone .
}""")
mpcN=len(res)
printResults(res)


# In[24]:

#print "Find windows in the room"
print("Grab the orientation of the room if we have it")
res = g.query("""
SELECT ?room ?orientation
WHERE {
    ?room rdf:type/rdfs:subClassOf* brick:Location .
    ?room rdfs:hasProperty ?orientation .
    ?orientation rdf:type brick:Orientation .
}""")
mpcN+=len(res)
printResults(res)


# In[25]:

print("Grab all VAVs and AHUs and zones")
res = g.query("""SELECT ?vav ?ahu ?hvac_zone
WHERE {
    ?vav rdf:type/rdfs:subClassOf* brick:Terminal_Unit .
    ?vav  bf:feeds ?zone .
    ?zone rdf:type/rdfs:subClassOf* brick:Location .
    ?ahu rdf:type brick:AHU .

    { ?ahu bf:feeds+ ?vav }
    UNION
    { ?ahu bf:hasPart ?vav }
}""")
mpcN+=len(res)
printResults(res)


# In[37]:

print("Grab all VAVs and AHUs and zones")
res = g.query("""SELECT ?vav ?ahu ?zone
WHERE {
    ?vav rdf:type/rdfs:subClassOf* brick:Terminal_Unit .
    ?vav  bf:feeds ?zone .
    ?ahu rdf:type brick:AHU .

    { ?ahu bf:feeds ?vav }
}""")
mpcN+=len(res)
printResults(res)
#printTuples(res)


# In[27]:

mpcN


# In[ ]:

print("--- Participatory Feedback ---")
print("Associate lighting with rooms")
res = g.query("""
SELECT DISTINCT ?light_equip ?light_state ?light_cmd ?room
WHERE {

    ?light_equip rdf:type/rdfs:subClassOf* brick:Lighting_System .
    ?light_equip bf:feeds ?zone .
    ?zone rdf:type/rdfs:subClassOf* brick:Location .

    {?light_equip bf:hasPoint ?light_state}
    UNION
    {?zone bf:hasPoint ?light_state}

    {?light_equip bf:hasPoint ?light_cmd}
    UNION
    {?zone bf:hasPoint ?light_cmd}
    
    ?light_state rdf:type/rdfs:subClassOf* brick:Luminance_Sensor .
    ?light_cmd rdf:type/rdfs:subClassOf* brick:Luminance_Command .

}""")
pfN=len(res)
printResults(res)


# In[ ]:

print("Find all power meters and associate them with floor and room")
g.query("CONSTRUCT {?a bf:isPointOf ?b} WHERE {?b bf:hasPoint ?a}")
res = g.query("""
SELECT ?meter ?loc
WHERE {
    ?meter rdf:type/rdfs:subClassOf* brick:Power_Meter .
    ?meter  bf:isPointOf ?loc .

    { ?loc rdf:type/rdfs:subClassOf* brick:Location }

}""")
pfN+=len(res)
printResults(res)
#printTuples(res)


# In[ ]:

pfN


# In[62]:

print("DO THIS!!! --- Fault Detection Diagnosis ---")
print("Get sensors for AHU")
res = g.query("""
SELECT ?ahu ?sensor
WHERE {
    ?ahu rdf:type/rdfs:subClassOf* brick:AHU .
    ?ahu (bf:feeds|bf:hasPoint|bf:hasPart|bf:contains)* ?sensor .

    { ?sensor rdf:type/rdfs:subClassOf* brick:Reheat_Valve_Command }
    UNION
    { ?sensor rdf:type/rdfs:subClassOf* brick:Cooling_Valve_Command }
    UNION
    { ?sensor rdf:type/rdfs:subClassOf* brick:Mixed_Air_Temperature_Sensor }
    UNION
    { ?sensor rdf:type/rdfs:subClassOf* brick:Outside_Air_Temperature_Sensor }
    UNION
    { ?sensor rdf:type/rdfs:subClassOf* brick:Return_Air_Temperature_Sensor }
    UNION
    { ?sensor rdf:type/rdfs:subClassOf* brick:Supply_Air_Temperature_Sensor }
    UNION
    { ?sensor rdf:type/rdfs:subClassOf* brick:Outside_Air_Humidity_Sensor }
    UNION
    { ?sensor rdf:type/rdfs:subClassOf* brick:Return_Air_Temperature_Sensor}
    UNION
    { ?sensor rdf:type/rdfs:subClassOf* brick:Outside_Air_Damper_Position_Sensor }
}""")
fddN=len(res)
printResults(res)


# In[63]:

fddN


# In[64]:

print("--- Non-Intrusive Load Monitoring App ---")
print("Get equipment, power meters and what they measure")
res = g.query("""
SELECT ?x ?meter
WHERE {
    ?meter rdf:type/rdfs:subClassOf* brick:Power_Meter .
    ?meter (bf:isPointOf|bf:isPartOf)* ?x .
    {?x rdf:type/rdfs:subClassOf* brick:Equipment .}
    UNION
    {?x rdf:type/rdfs:subClassOf* brick:Location .}
}
""")
nilmN=len(res)
printResults(res)


# In[65]:

nilmN


# In[66]:

print("--- Demand Response ---")
print("Find all equipment (inside rooms) and associated power meters and control points")
res = g.query("""
SELECT DISTINCT ?equip ?cmd ?status
WHERE {
    ?equip  rdf:type/rdfs:subClassOf* brick:Equipment .
    {
    ?cmd rdf:type/rdfs:subClassOf*    brick:Command .
    ?cmd (bf:isPointOf|bf:isPartOf)* ?equip .
    }
    UNION
    {
    ?status rdf:type/rdfs:subClassOf* brick:Status .
    ?status (bf:isPointOf|bf:isPartOf)* ?equip .
    }

}""")
drN=len(res)
printResults(res)


# In[ ]:

drN


# In[ ]:



