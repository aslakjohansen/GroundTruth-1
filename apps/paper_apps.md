## How to run Queries

Running these queries isn't too bad using the `rdflib` Python library. The gist of the code
is:

```python
import rdflib

g = rdflib.Graph()
g.parse('<your building turtle file>.ttl', format='ttl')

# query goes here
res = g.query("""
SELECT ?vav ?room
WHERE {
    ?vav rdf:type brick:VAV .
    ?room rdf:type brick:Room .

    ?vav bf:feeds+ ?zone .
    ?room bf:isPartOf ?zone .
}
""")
print "Number of results: {0}".format(len(res))
print "Results:"
for subject, predicate, object in res:
    print subject, predicate, object
```

## Occupancy Modeling

- For each room, we want:
  - temperature sensor
  - co2 sensor
  - pir sensor
  - power meter for any equipment in the room

- identify meters for any HVAC equipment
- identify meters for any lighting equipment

```sql
-- find the sensors for all of the rooms
SELECT ?sensor ?sensor_type ?room
WHERE {
    -- get all sensor classes that measure Temperature, CO2 or occupancy
    ?sensor_type rdfs:subClassOf brick:Sensor .
    { ?sensor_type bf:hasTag brick:Temperature }
        UNION
    { ?sensor_type bf:hasTag brick:CO2 }
        UNION
    { ?sensor_type bf:hasTag brick:Occupancy }

    -- get all sensors of those classes
    ?sensor rdf:type ?sensor_type .

    -- restrict sensors such that they are located in a room
    -- and measure that room (should filter out HVAC equipment
    -- sensors that feed into the room)
    ?room rdf:type brick:Room .
    ?sensor bf:isLocatedIn ?room .
    ?sensor bf:measures ?room .

}

-- find all power meters for equipment in any of the rooms
SELECT ?meter ?equipment ?room
WHERE {
    -- define the types that we're looking for
    ?meter rdf:type brick:Power_Meter .
    ?room rdf:type brick:Room .
    ?equipment rdf:type brick:Equipment .

    -- return the meters that measure equipment that is located
    -- in some room
    ?equipment bf:isLocatedIn ?room .
    ?meter bf:measures ?equipment .
}

-- find all power meters for any HVAC equipment
SELECT ?meter ?equipment ?room
WHERE {
    -- define the types that we're looking for
    ?meter rdf:type brick:Power_Meter .
    ?equipment rdf:type brick:Equipment .
    ?room rdf:type brick:Room .

    -- return meter that measures HVAC equipment
    -- upstream of some room
    ?meter bf:measures ?equipment .
    ?equipment bf:hasTag brick:HVAC .
    ?equipment bf:feeds+ ?zone .
    ?zone bf:hasPart ?room .
}

-- find all power meters for any Lighting equipment
SELECT ?meter ?equipment ?room
WHERE {
    ?meter rdf:type brick:Power_Meter .
    ?equipment rdf:type brick:Equipment .
    ?room rdf:type brick:Room .

    ?meter bf:measures ?equipment .
    ?equipment bf:hasTag brick:Lighting .
    ?zone bf:hasPart ?room .

    -- here we aren't sure of the relationship, so
    -- we capture both ways
    { ?equipment bf:feeds+ ?zone }
        UNION
    { ?equipment bf:feeds+ ?room }

}
```


## Energy Apportionment

- presence:
    - PIR sensors in a room, in a cubicle
- lighting:
    - find pairs of illumination sensors with lighting equipment in each room

Otherwise very similar to the above application

## Web Displays

- reheat valve command for all VAVs, and the associated reheat coil
- airflow sensor for all VAVs
- map VAVs to hvac zones and to rooms in hvac zones
- find the schedule for the HVAC system
- find power meters for:
    - cooling loop
    - heating loop
    - hvac system
    - lightign system
    - equipment in rooms


```sql
-- reheat valve command for all VAVs
SELECT ?reheat_vlv_cmd ?vav
WHERE {
    -- declare the types
    ?reheat_vlv_cmd rdf:type brick:Reheat_Valve_Command .
    ?vav rdf:type brick:VAV .

    -- return reheat valve command points associated with some VAV
    ?vav bf:hasPoint+ ?reheat_vlv_cmd .
}

-- airflow sensor for all VAVs
SELECT ?airflow_sensor ?room ?vav
WHERE {
    -- define some generic air flow sensor type
    ?airflow_sensor rdf:type brick:Sensor .
    ?airflow_sensor bf:hasTag brick:Air .
    ?airflow_sensor bf:hasTag brick:Flow .

    ?vav rdf:type brick:VAV .
    ?room rdf:type brick:Room .

    -- return airflow sensors that are associated with some VAV
    -- This may be that it is part of the VAV or it is downstream
    -- of a VAV
    { ?airflow_sensor bf:isPartOf ?vav }
        UNION
    { ?vav bf:feeds+ ?airflow_sensor }

    -- TODO: is this sufficient, or do we need to
    -- only return airflow sensors that are upstream of some room?
}

-- map VAVs to hvac zones and rooms
SELECT ?vav ?room
WHERE {
    ?vav rdf:type brick:VAV .
    ?room rdf:type brick:Room .

    -- VAVs feed some zone, and that zone contains rooms
    ?vav bf:feeds+ ?zone .
    ?room bf:isPartOf ?zone .
}

-- find power meters for cooling loop, heating loop
SELECT ?equip ?equip_type ?meter
WHERE {
    ?equip_type rdfs:subClassOf brick:Equipment .
    ?equip rdf:type ?equip_type .
    ?meter rdf:type brick:Power_Meter .

    ?equip rdfs:subClassOf brick:Water_System .
    { ?equip bf:hasTag brick:Chilled }
        UNION
    { ?equip bf:hasTag brick:Hot }

    ?meter bf:measures ?equip .

}
```

## Model-Predictive Control

```sql
-- find all buildings, floors, hvac zones, rooms
SELECT ?bldg ?floor? ?hvac_zone ?room
WHERE {
    ?bldg rdf:type brick:Building .
    ?floor rdf:type brick:Floor .
    ?room rdf:type brick:Room .
    ?hvac_zone rdf:type brick:Zone .
    ?hvac_zone bf:hasTag brick:HVAC .

    ?floor bf:isPartOf ?bldg .
    ?room bf:isPartOf ?floor .
    ?room bf:isPartOf ?hvac_zone .
}

-- find windows in the room

-- grab the orientation of the room if we have it
SELECT ?room ?orientation
WHERE {
    ?room rdf:type brick:Room .
    ?room rdfs:hasProperty brick:Orientation .
    ?orientation rdf:type brick:Orientation .
}

-- grab all VAVs and AHUs and zones
SELECT ?vav ?ahu ?hvac_zone
WHERE {
    ?vav rdf:type brick:VAV .
    ?ahu rdf:type brick:AHU .
    ?ahu bf:feeds ?vav .
    ?hvac_zone rdf:type brick:Zone .
    ?hvac_zone bf:hasTag brick:HVAC .
    ?vav  bf:feeds ?hvac_zone .
}
```

## Participatory Feedback
```sql
-- associate lighting with rooms
SELECT ?light_equip ?light_state ?light_cmd ?room
WHERE {
    ?light_equip rdf:type brick:Equipment .
    ?light_equip bf:hasTag brick:Lighting .
    ?light_equip bf:feeds brick:?zone .
    ?zone rdf:type brick:Zone .
    ?zone bf:hasTag brick:Lighting .
    ?zone bf:contains ?room .
    ?room rdf:type brick:Room .

    ?light_state rdf:type brick:Status .
    ?light_state bf:isPointOf ?light_equip .
    ?light_state bf:hasTag brick:Luminance .

    ?light_cmd rdf:type brick:Command .
    ?light_cmd bf:isPointOf ?light_equip .
    ?light_cmd bf:hasTag brick:Luminance .
}

-- find all power meters and associate them with floor and room
SELECT ?meter ?floor ?room
WHERE {
    ?meter  rdf:type    brick:Sensor .
    ?meter  bf:hasTag   brick:Power .
    ?loc    rdf:type    brick:Location .

    { ?room   bf:isLocatedIn ?loc }
    UNION
    { ?room   bf:isPartOf ?loc }

    ?meter  bf:isPointOf+ ?loc
}
```
