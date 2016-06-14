# Occupancy Modeling

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
    ?sensor_type rdfs:subClassOf brick:Sensor .
    ?sensor rdf:type ?sensor_type .
    ?room rdf:type brick:Room .
    ?sensor bf:isLocatedIn ?room .
    ?sensor bf:measures ?room .

    { ?sensor_type bf:hasTag brick:Temperature }
        UNION
    { ?sensor_type bf:hasTag brick:CO2 }
        UNION
    { ?sensor_type bf:hasTag brick:Occupancy }
}

-- find all power meters for equipment in any of the rooms
SELECT ?meter ?equipment ?room
WHERE {
    ?meter rdf:type brick:Power_Meter .
    ?room rdf:type brick:Room .
    ?equipment rdf:type brick:Equipment .

    ?equipment bf:isLocatedIn ?room .
    ?meter bf:measures ?equipment .
}

-- find all power meters for any HVAC equipment
SELECT ?meter ?equipment ?room
WHERE {
    ?meter rdf:type brick:Power_Meter .
    ?equipment rdf:type brick:Equipment .
    ?room rdf:type brick:Room .

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

    ?equipment bf:hasTag brick:Lighting .
    ?zone bf:hasPart ?room .

    { ?equipment bf:feeds+ ?zone }
        UNION
    { ?equipment bf:feeds+ ?room }

}
```

