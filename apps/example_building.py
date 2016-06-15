# import the rdflib
from rdflib import Graph, Namespace, URIRef, Literal
import rdflib

# declare the namespaces. This will pull in the definition of the schema
# if it exists. Else, we need to parse some file to fill in the missing symbols
# is not pulling anything in from the web, I don't think?
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
BRICK = Namespace('http://buildsys.org/ontologies/Brick#')
BRICKFRAME = Namespace('http://buildsys.org/ontologies/BrickFrame#')
BRICKTAG = Namespace('http://buildsys.org/ontologies/BrickTag#')

# This is the graph object that contains all of the schemas. We use this
# graph to pull out classes and relationships, but any *instances* of these
# are going to be stored in another graph.
g = rdflib.Graph()
# "bind()" simply means that we can use 'rdf' instead of the full URI for rdf when
# referring to entities in its namespace. Just shorthand
g.bind( 'rdf', RDF)
g.bind( 'rdfs', RDFS)
g.bind( 'brick', BRICK)
g.bind( 'bf', BRICKFRAME)
g.bind( 'btag', BRICKTAG)
#g.parse('../BuildingSchema/BrickV2.ttl', format='turtle')
#g.parse('../BuildingSchema/BrickFrame.ttl', format='turtle')
#g.parse('../BuildingSchema/BrickTag.ttl', format='turtle')

# We want to add nodes to the graph for our building. The building exists in its
# own namespace, which we are calling EX

EX = Namespace('http://buildsys.org/ontologies/building_example#')
g.bind('ex', EX)

# Once we have our namespace, we can start placing things in it. Lets create
# some entity that will represent our building. We have a "Building" Location in
# the brick schema, so we need to declare that some unique label within the EX
# namespace "is a" building. This is achieved using the builtin RDF.type relationship.
# Here, the label "building_1" is implicitly created when we mention it in the add()
# function. Add()'s 3 arguments are: subject, predicate, object.
g.add((EX.building_1, RDF.type, BRICK.Building))
# we can give it a name too
g.add((EX.building_1, RDFS.label, Literal("Example Building Hall")))
# we can check now if our entity is known to be a location. This should be true because
# we inherited that from BRICK.building, which is a subclass of Location
print "SHOULD be True: ", (BRICK.Building, RDFS.subClassOf, BRICK.Location) in g
# TODO: need a sparql query for this?
res = g.query("""SELECT DISTINCT ?bldg
WHERE {
?bldg rdf:type brick:Building
}
""")
print "All buildings:"
for row in res:
    print "%s" % row

# now that we have a building, lets add 2 floors to it.
# We implicitly create the 2 labels floor_1 and floor_2 that represent
# the floor entities. We use the RDF.type relationship to say that they are
# instances of the Floor class as defined by the BRICK schema.
g.add((EX.floor_1, RDF.type, BRICK.Floor))
g.add((EX.floor_2, RDF.type, BRICK.Floor))

# We then link these floors to our example building by using the BRICKFRAME relationsihp
# "isPartOf".
g.add((EX.floor_1, BRICKFRAME.isPartOf, EX.building_1))
g.add((EX.floor_2, BRICKFRAME.isPartOf, EX.building_1))

# the query for "all floors in this building"
res = g.query("""SELECT DISTINCT ?bldg ?floor
WHERE {
    ?bldg rdf:type brick:Building .
    ?floor rdf:type brick:Floor .
    ?floor bf:isPartOf+ ?bldg .
}
""")
for row in res:
    print "Building %s has floor %s" % row

# now lets do the same for a few rooms. Here, to autogenerate some labels, we're tkaing
# advantage of the fact that EX.floor_1 and EX["floor_1"] are equivalent.
# Remember, each label needs to be *unique* within the namespace.
for floor_num in [1,2]:
    floor = EX["floor_{0}".format(floor_num)]
    for room_num in [1,2,3,4]:
        room = EX["room_{0}_{1}".format(floor_num, room_num)]
        g.add((room, RDF.type, BRICK.Room))
        g.add((room, BRICKFRAME.isPartOf, floor))
# TODO: query to demonstrate that we now know that those rooms are in the building
res = g.query("""SELECT DISTINCT ?bldg ?room
WHERE {
    ?bldg rdf:type brick:Building .
    ?room rdf:type brick:Room .
    ?room bf:isPartOf+ ?bldg .
}
""")
for row in res:
    print "Building %s has room %s" % row

# We have some structure to our building, so lets start adding in some equipment.
# Sensors are straightforward to add. Lets put some CO2 and PIR  and temperature sensors
# in some rooms.
# We *could* do the following:
#     for num in range(1,5):
#         temp_sensor = EX["temp_sensor_{0}".format(num)]
#         co2_sensor = EX["co2_sensor_{0}".format(num)]
#         pir_sensor = EX["pir_sensor_{0}".format(num)]
#         g.add((temp_sensor, RDF.type, BRICK.Sensor))
#         g.add((co2_sensor, RDF.type, BRICK.Sensor))
#         g.add((pir_sensor, RDF.type, BRICK.Sensor))
#
# This successfully identifies all of these labels as being sensors, but it doesn't yet
# tell us what kind of sensor they are. BRICK schema defines a tag Temperature which
# is a subclass of PhysicalProperties, which is a subclass of MeasurementProperty, which
# is a subclass of Tag.
#
# If we wanted to add this tag, we could do so to each of the instances, using a line like:
#   g.add((EX.temp_sensor_1, BRICKFRAME.hasTag, BRICK.Temperature))
#
# However, we'd have to do this for *each* instance of a temperature sensor, co2 sensor, etc.
# What if we forgot to label one? What if we later on want to associate more information
# with what consists a temperature sensor? What we really want here is a subclass for each
# of these sensor types.
#
# We would declare a temperature sensor class like the following:
#   BRICK.Temperature_Sensor RDFS.subClassOf BRICK.Sensor
#   BRICK.Temperature_Sensor BRICKFRAME.hasTag BRICK.Temperature
#
# Then we end up with something like
#
#     for num in range(1,5):
#         temp_sensor = EX["temp_sensor_{0}".format(num)]
#         co2_sensor = EX["co2_sensor_{0}".format(num)]
#         pir_sensor = EX["pir_sensor_{0}".format(num)]
#         g.add((temp_sensor, RDF.type, BRICK.Temperature_Sensor))
#         g.add((co2_sensor, RDF.type, BRICK.CO2_Sensor))
#         g.add((pir_sensor, RDF.type, BRICK.PIR_Sensor))
#
# It could be that in our building, we know slightly more about the temperature sensors: we want
# to indicate that the temperature sensors in our building measure in Fahrenheit. We don't
# want to add that to the *main* BRICK schema, because it isn't true for all temperature
# sensors. However, we can create our own subclass and attach the property there
#
#   EX.Fahrenheit_Temperature_Sensor RDFS.subClassOf BRICK.Temperature_Sensor
#   EX.Fahrenheit_Temperature_Sensor BRICKFRAME.hasUnit BRICK.Fahrenheit
#
# and then declare our instances using
#   g.add((temp_sensor, RDF.type, EX.Fahrenheit_Temperature_Sensor))

# add temperature sensor class
g.add((EX.Fahrenheit_Temperature_Sensor, RDFS.subClassOf, BRICK.Sensor))
g.add((EX.Fahrenheit_Temperature_Sensor, BRICKFRAME.hasTag, BRICK.Temperature))
g.add((EX.Fahrenheit_Temperature_Sensor, BRICKFRAME.hasUnit, BRICK.Fahrenheit))

# add co2 sensor class
g.add((EX.CO2_Sensor, RDFS.subClassOf, BRICK.Sensor))
g.add((EX.CO2_Sensor, BRICKFRAME.hasTag, BRICK.CO2))

# add occupancy sensor class
g.add((EX.PIR_Sensor, RDFS.subClassOf, BRICK.Sensor))
g.add((EX.PIR_Sensor, BRICKFRAME.hasTag, BRICK.Occupancy))
# TODO: how do we indicate that it is PIR?

# create the instances of our sensors
for num in range(1,9):
    temp_sensor = EX["temp_sensor_{0}".format(num)]
    co2_sensor = EX["co2_sensor_{0}".format(num)]
    pir_sensor = EX["pir_sensor_{0}".format(num)]
    # declare sensors
    g.add((temp_sensor, RDF.type, EX.Fahrenheit_Temperature_Sensor))
    g.add((co2_sensor, RDF.type, EX.CO2_Sensor))
    g.add((pir_sensor, RDF.type, EX.PIR_Sensor))

# add sensor to room
g.add((EX.temp_sensor_1, BRICKFRAME.isLocatedIn, EX.room_1_1))
g.add((EX.temp_sensor_2, BRICKFRAME.isLocatedIn, EX.room_1_2))
g.add((EX.temp_sensor_3, BRICKFRAME.isLocatedIn, EX.room_1_3))
g.add((EX.temp_sensor_4, BRICKFRAME.isLocatedIn, EX.room_1_4))
g.add((EX.temp_sensor_5, BRICKFRAME.isLocatedIn, EX.room_2_1))
g.add((EX.temp_sensor_6, BRICKFRAME.isLocatedIn, EX.room_2_2))
g.add((EX.temp_sensor_7, BRICKFRAME.isLocatedIn, EX.room_2_3))
g.add((EX.temp_sensor_8, BRICKFRAME.isLocatedIn, EX.room_2_4))
g.add((EX.temp_sensor_1, BRICKFRAME.measures, EX.room_1_1))
g.add((EX.temp_sensor_2, BRICKFRAME.measures, EX.room_1_2))
g.add((EX.temp_sensor_3, BRICKFRAME.measures, EX.room_1_3))
g.add((EX.temp_sensor_4, BRICKFRAME.measures, EX.room_1_4))
g.add((EX.temp_sensor_5, BRICKFRAME.measures, EX.room_2_1))
g.add((EX.temp_sensor_6, BRICKFRAME.measures, EX.room_2_2))
g.add((EX.temp_sensor_7, BRICKFRAME.measures, EX.room_2_3))
g.add((EX.temp_sensor_8, BRICKFRAME.measures, EX.room_2_4))

g.add((EX.co2_sensor_1, BRICKFRAME.isLocatedIn, EX.room_1_1))
g.add((EX.co2_sensor_2, BRICKFRAME.isLocatedIn, EX.room_1_2))
g.add((EX.co2_sensor_3, BRICKFRAME.isLocatedIn, EX.room_1_3))
g.add((EX.co2_sensor_4, BRICKFRAME.isLocatedIn, EX.room_1_4))
g.add((EX.co2_sensor_5, BRICKFRAME.isLocatedIn, EX.room_2_1))
g.add((EX.co2_sensor_6, BRICKFRAME.isLocatedIn, EX.room_2_2))
g.add((EX.co2_sensor_7, BRICKFRAME.isLocatedIn, EX.room_2_3))
g.add((EX.co2_sensor_8, BRICKFRAME.isLocatedIn, EX.room_2_4))
g.add((EX.co2_sensor_1, BRICKFRAME.measures, EX.room_1_1))
g.add((EX.co2_sensor_2, BRICKFRAME.measures, EX.room_1_2))
g.add((EX.co2_sensor_3, BRICKFRAME.measures, EX.room_1_3))
g.add((EX.co2_sensor_4, BRICKFRAME.measures, EX.room_1_4))
g.add((EX.co2_sensor_5, BRICKFRAME.measures, EX.room_2_1))
g.add((EX.co2_sensor_6, BRICKFRAME.measures, EX.room_2_2))
g.add((EX.co2_sensor_7, BRICKFRAME.measures, EX.room_2_3))
g.add((EX.co2_sensor_8, BRICKFRAME.measures, EX.room_2_4))

g.add((EX.pir_sensor_1, BRICKFRAME.isLocatedIn, EX.room_1_1))
g.add((EX.pir_sensor_2, BRICKFRAME.isLocatedIn, EX.room_1_2))
g.add((EX.pir_sensor_3, BRICKFRAME.isLocatedIn, EX.room_1_3))
g.add((EX.pir_sensor_4, BRICKFRAME.isLocatedIn, EX.room_1_4))
g.add((EX.pir_sensor_5, BRICKFRAME.isLocatedIn, EX.room_2_1))
g.add((EX.pir_sensor_6, BRICKFRAME.isLocatedIn, EX.room_2_2))
g.add((EX.pir_sensor_7, BRICKFRAME.isLocatedIn, EX.room_2_3))
g.add((EX.pir_sensor_8, BRICKFRAME.isLocatedIn, EX.room_2_4))
g.add((EX.pir_sensor_1, BRICKFRAME.measures, EX.room_1_1))
g.add((EX.pir_sensor_2, BRICKFRAME.measures, EX.room_1_2))
g.add((EX.pir_sensor_3, BRICKFRAME.measures, EX.room_1_3))
g.add((EX.pir_sensor_4, BRICKFRAME.measures, EX.room_1_4))
g.add((EX.pir_sensor_5, BRICKFRAME.measures, EX.room_2_1))
g.add((EX.pir_sensor_6, BRICKFRAME.measures, EX.room_2_2))
g.add((EX.pir_sensor_7, BRICKFRAME.measures, EX.room_2_3))
g.add((EX.pir_sensor_8, BRICKFRAME.measures, EX.room_2_4))
#TODO: do we *ALSO* use "hasPoint" here?, or conversely isPointOf?
# these two lines are equivalent
g.add((EX.pir_sensor_8, BRICKFRAME.isPointOf, EX.room_2_4))
g.add((EX.room_2_4, BRICKFRAME.hasPoint, EX.pir_sensor_8))

# now we need a notion of a power meter. The BRICK schema has a Power Meter concept,
# under the hierarchy: Tag -> Point -> Meter -> Power -> Power Meter.
# Let's attach a power meter to each of the floors
g.add((EX.floor_power_meter_1, RDF.type, BRICK.Power_Meter))
g.add((EX.floor_power_meter_2, RDF.type, BRICK.Power_Meter))
g.add((EX.floor_1, BRICKFRAME.hasPoint, EX.floor_power_meter_1))
g.add((EX.floor_2, BRICKFRAME.hasPoint, EX.floor_power_meter_2))

# hasPoint is how we associate some sensor with what it measures?
# TODO: Does the act of associating EX.floor_1 with EX.floor_power_meter_1 using the BRICKFRAME.hasPoint have any recursive qualities?

# In our example building, we don't know a whole lot about the HVAC system. We do 
# know that we have an AHU, and that it has 3 VAVs per floor. 1 VAV serves 2 of the rooms.
# The other 2 rooms are each served by 1 VAV

# instantiate an AHU
g.add((EX.ahu_1, RDF.type, BRICK.AHU))
# associate the AHU with the building
# TODO: is there another, better way of doing this?
g.add((EX.building_1, BRICKFRAME.hasPart, EX.ahu_1))

# instantiate our 6 VAVs
g.add((EX.vav_1_1, RDF.type, BRICK.VAV))
g.add((EX.vav_1_2, RDF.type, BRICK.VAV))
g.add((EX.vav_1_3, RDF.type, BRICK.VAV))
g.add((EX.vav_2_1, RDF.type, BRICK.VAV))
g.add((EX.vav_2_2, RDF.type, BRICK.VAV))
g.add((EX.vav_2_3, RDF.type, BRICK.VAV))

# establish the VAVs as downstream of the AHU
g.add((EX.ahu_1, BRICKFRAME.feeds, EX.vav_1_1))
g.add((EX.ahu_1, BRICKFRAME.feeds, EX.vav_1_2))
g.add((EX.ahu_1, BRICKFRAME.feeds, EX.vav_1_3))
g.add((EX.ahu_1, BRICKFRAME.feeds, EX.vav_2_1))
g.add((EX.ahu_1, BRICKFRAME.feeds, EX.vav_2_2))
g.add((EX.ahu_1, BRICKFRAME.feeds, EX.vav_2_3))

# instantiate 6 HVAC zones; one for each VAV
g.add((EX.hvac_zone_1_1, RDF.type, BRICK.HVAC_Zone))
g.add((EX.hvac_zone_1_2, RDF.type, BRICK.HVAC_Zone))
g.add((EX.hvac_zone_1_3, RDF.type, BRICK.HVAC_Zone))
g.add((EX.hvac_zone_2_1, RDF.type, BRICK.HVAC_Zone))
g.add((EX.hvac_zone_2_2, RDF.type, BRICK.HVAC_Zone))
g.add((EX.hvac_zone_2_3, RDF.type, BRICK.HVAC_Zone))

# declare which rooms are in which HVAC Zone
g.add((EX.hvac_zone_1_1, BRICKFRAME.hasPart, EX.room_1_1))
g.add((EX.hvac_zone_1_1, BRICKFRAME.hasPart, EX.room_1_2))
g.add((EX.hvac_zone_1_2, BRICKFRAME.hasPart, EX.room_1_3))
g.add((EX.hvac_zone_1_3, BRICKFRAME.hasPart, EX.room_1_4))

g.add((EX.hvac_zone_2_1, BRICKFRAME.hasPart, EX.room_1_1))
g.add((EX.hvac_zone_2_1, BRICKFRAME.hasPart, EX.room_1_2))
g.add((EX.hvac_zone_2_2, BRICKFRAME.hasPart, EX.room_1_3))
g.add((EX.hvac_zone_2_3, BRICKFRAME.hasPart, EX.room_1_4))

# declare that the VAVs feed the HVAC Zones
g.add((EX.vav_1_1, BRICKFRAME.feeds, EX.hvac_zone_1_1))
g.add((EX.vav_1_2, BRICKFRAME.feeds, EX.hvac_zone_1_2))
g.add((EX.vav_1_3, BRICKFRAME.feeds, EX.hvac_zone_1_3))

g.add((EX.vav_2_1, BRICKFRAME.feeds, EX.hvac_zone_2_1))
g.add((EX.vav_2_2, BRICKFRAME.feeds, EX.hvac_zone_2_2))
g.add((EX.vav_2_3, BRICKFRAME.feeds, EX.hvac_zone_2_3))

# all temperature sensors in rooms downstream of an AHU
res = g.query("""SELECT ?sensor ?room
WHERE {
    ?sensor_type rdfs:subClassOf brick:Sensor .
    ?sensor_type bf:hasTag brick:Temperature .
    ?sensor rdf:type ?sensor_type .
    ?ahu rdf:type brick:AHU .
    ?ahu bf:feeds+ ?zone .
    ?zone bf:hasPart ?room .
    ?sensor bf:measures ?room .
}
""")
print "AHU has %d downstream temperature sensors" % len(res)
for row in res:
    print row

res = g.query("""
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
""")
print len(res)

# TODO: add Lighting

# how to save our results to a Turtle file, which Protege can read
g.serialize(destination='example_building.ttl', format='turtle')
print len(g)
