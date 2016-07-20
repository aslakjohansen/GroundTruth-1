# import the rdflib
from rdflib import Graph, Namespace, URIRef, Literal
import rdflib
import re
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
# own namespace, which we are calling soda

EX = Namespace('http://buildsys.org/ontologies/building_example#')
g.bind('soda_hall', EX)

tags = {}
def readKeys(filename="SodaParseKey"):
	lines = open(filename).readlines()
	for line in lines:
		line = line.strip()
		if line == "":
			continue
		metadataTag = line.split("=>")[0].strip()
		tags[metadataTag] = {}
		parts = line.split("=>")[-1].strip().split(";")
		for part in parts:
			part = part.strip()
			if part == "":
				continue
			key = part.split("->")[-1].strip()
			if " " in key:
				key = re.sub(" ", "_", key)
			value = part.split("->")[0].strip() 
			tags[metadataTag][key] = value

# adding building
g.add((EX.building_1, RDF.type, BRICK.Building))
g.add((EX.building_1, RDFS.label, Literal("Soda Hall")))
# we inherited that from BRICK.building, which is a subclass of Location
print "SHOULD be True: ", (BRICK.Building, RDFS.subClassOf, BRICK.Location) in g
readKeys()

# now that we have a building, lets add 2 floors to it.
# We implicitly create the 2 labels floor_1 and floor_2 that represent
# the floor entities. We use the RDF.type relationship to say that they are
# instances of the Floor class as defined by the BRICK schema.
for floor_num in [ 1, 2, 3, 4, 5, 6, 7 ]:
	floor = EX["floor_{0}".format(floor_num)]
	g.add((floor, RDF.type, BRICK.Floor))
	g.add((floor, BRICKFRAME.isPartOf, EX.building_1)) 

# adding hvac zones and rooms ( since in Soda Hall there is a one<-> one
# mapping between zones and rooms and floors
# Also each zone is associated with a VAV, and the AHU serving it is 
# on the same tag name
to_delete = []
for tag in tags:
	if "zone" in tags[tag]:
		#print tag, tags[tag]
		zone = "hvac_zone_{0}".format(tags[tag]["zone"])
		room = "room_{0}".format(tags[tag]["zone"])
		floor = "floor_{0}".format(tags[tag]["zone"][1])
		vav = "vav_{0}".format(tags[tag]["zone"])
		if (EX[zone], RDF.type, BRICK.HVAC_Zone) not in g:
			g.add((EX[zone], RDF.type, BRICK.HVAC_Zone))
			g.add((EX[room], RDF.type, BRICK.Room))  
			g.add((EX[vav], RDF.type, BRICK.VAV))
			g.add((EX[vav], BRICKFRAME.feeds, EX[zone]))
			g.add((EX[room], BRICKFRAME.isPartOf, EX[floor])) 
			g.add((EX[zone], BRICKFRAME.hasPart, EX[room]))
			#g.add((EX[zone], BRICKFRAME.contains, EX[room]))
		if "ahu" in tags[tag]:
			ahu = "ahu_{0}".format(tags[tag]["ahu"])
			if (EX[ahu], RDF.type, BRICK.AHU) not in g:
				g.add((EX[ahu], RDF.type, BRICK.AHU))
			if (EX[ahu], BRICKFRAME.feeds, EX[vav]) not in g:
				g.add((EX[ahu], BRICKFRAME.feeds, EX[vav])) 
		if "zone_temp_sensor" in tags[tag]:
			sensor = "temp_sensor_{0}".format(zone)	
			g.add((EX[sensor], RDF.type, BRICK.Zone_Temperature_Sensor))
			g.add((EX[vav], BRICKFRAME.hasPoint, EX[sensor]))
			#g.add((EX[sensor], BRICKFRAME.isLocatedIn, EX.room))
			#g.add((EX[sensor], BRICKFRAME.isPointOf, EX.room))	
		elif "zone_temp_setpoint" in tags[tag]:
			sensor = "temp_setpoint_{0}".format(zone)
			g.add((EX[sensor], RDF.type, BRICK.Zone_Temperature_Setpoint))
			g.add((EX[vav], BRICKFRAME.hasPoint, EX[sensor]))
			#g.add((EX[sensor], BRICKFRAME.isLocatedIn, EX.room))
			#g.add((EX[sensor], BRICKFRAME.isPointOf, EX.room))	
		elif "vav_reheat_discharge_air_pressure_sensor" in tags[tag]:
			sensor_flow = "flow_sensor_{0}".format(zone)
			sensor_reheat = "reheat_sensor_{0}".format(zone)
			g.add((EX[sensor_flow], RDF.type, BRICK.Supply_Air_Flow_Sensor))
			g.add((EX[sensor_reheat], RDF.type, BRICK.Reheat_Valve_Command))
			g.add((EX[vav], BRICKFRAME.hasPoint, EX[sensor_flow]))
			g.add((EX[vav], BRICKFRAME.hasPoint, EX[sensor_reheat]))
			g.add((EX[vav], RDF.hasTag, BRICK.Reheat))
		elif "discharge_air_pressure_sensor" in tags[tag]:
			sensor_flow = "flow_sensor_{0}".format(zone)
			g.add((EX[sensor_flow], RDF.type, BRICK.Supply_Air_Flow_Sensor))
			g.add((EX[vav], BRICKFRAME.hasPoint, EX[sensor_flow]))
			
		to_delete.append(tag)


for tag in to_delete:
	del tags[tag]

to_delete = []
for tag in sorted(tags):
	if "ahu" not in tags[tag]:
		to_delete.append(tag)

nonahutags = {}
for tag in to_delete:
	nonahutags[tag] = tags[tag]
	del tags[tag]

to_delete = []
for tag in tags:
	if "ahu" in tags[tag] and "supply_fan" in tags[tag]:
		supply_fan = "supply_fan_{0}".format(tags[tag]["supply_fan"])
		ahu = "ahu_{0}".format(tags[tag]["ahu"])
		if (EX[supply_fan], RDF.type, BRICK.Supply_Fan) not in g:
			g.add((EX[supply_fan], RDF.type, BRICK.Supply_Fan))
			g.add((EX[ahu], RDF.contains, EX[supply_fan]))
		if "pid_loop_P_variable" in tags[tag]:
			sensor = "pid_p_{0}".format(supply_fan)
			g.add((EX[sensor], RDF.type ,BRICK.Supply_Air_Proportional_Gain_Factor))
			g.add((EX[supply_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "pid_loop_I_variable" in tags[tag]:
			sensor = "pid_i_{0}".format(supply_fan)
			g.add((EX[sensor], RDF.type ,BRICK.Supply_Air_Integrative_Gain_Factor))
			g.add((EX[supply_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "static_pressure_setpoint" in tags[tag]:
			sensor = "static_pressure_setpoint_{0}".format(supply_fan)
			g.add((EX[sensor], RDF.type, BRICK.Static_Pressure_Setpoint))
			g.add((EX[supply_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "static_pressure_sensor" in tags[tag]:
			sensor = "static_pressure_sensor_{0}".format(supply_fan)
			g.add((EX[sensor], RDF.type, BRICK.Static_Pressure_Sensor))
			g.add((EX[supply_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "supply_air_temp_setpoint" in tags[tag]:
			sensor = "supply_air_setpoint_{0}".format(supply_fan)
			g.add((EX[sensor], RDF.type, BRICK.Discharge_Air_Temperature_Setpoint))
			g.add((EX[supply_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "supply_air_temp" in tags[tag]:
			sensor = "supply_air_temp_{0}".format(supply_fan)
			g.add((EX[sensor], RDF.type, BRICK.Discharge_Air_Temperature_Sensor))
			g.add((EX[supply_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "fan_speed_reset" in tags[tag]:
			sensor = "fan_speed_reset_{0}".format(supply_fan)
			g.add((EX[sensor], RDF.type, BRICK.Fan_Speed_Reset))
			g.add((EX[supply_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "fan_speed" in tags[tag]:
			sensor = "fan_speed_{0}".format(supply_fan)
			g.add((EX[sensor], RDF.type, BRICK.Fan_Speed_Setpoint))
			g.add((EX[supply_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "smoke_alarm" in tags[tag]:
			sensor = "smoke_alarm_{0}".format(supply_fan)
			g.add((EX[sensor], RDF.type, BRICK.Smoke_Detected_Alarm)) 
			g.add((EX[supply_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "differential_pressure_status" in tags[tag]:
			sensor = "diff_pressure_status_{0}".format(supply_fan)
			g.add((EX[sensor], RDF.type, BRICK.Differential_Pressure_Status)) 
			g.add((EX[supply_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "mixed_air_temp" in tags[tag]:
			sensor = "mixed_air_temp_{0}".format(supply_fan)
			g.add((EX[sensor], RDF.type, BRICK.Mixed_Air_Temperature_Sensor)) 
			g.add((EX[supply_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "fault_sensor" in tags[tag]:
			sensor = "fault_status_{0}".format(supply_fan)
			g.add((EX[sensor], RDF.type, BRICK.Fault_Status))
			g.add((EX[supply_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "chilled_water_valve_pressure" in tags[tag]:
			sensor = "c_water_vlv_press_{0}".format(supply_fan)
			g.add((EX[sensor], RDF.type, BRICK.Cooling_Coil_Valve_Pressure))
			g.add((EX[supply_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "mixed_air_damper" in tags[tag]:
			sensor = "mixed_air_dmp_{0}".format(supply_fan)
			g.add((EX[sensor], RDF.type, BRICK.Mixed_Air_Damper_Position_Sensor))
			g.add((EX[supply_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "start_stop_sensor" in tags[tag]:
			sensor = "s_s_{0}".format(supply_fan)
			g.add((EX[sensor], RDF.type, BRICK.Start_Stop_Status))
			g.add((EX[supply_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "air_volume" in tags[tag] or "filtered_air_volume" in tags[tag]:
			sensor = "supply_fan_cfm_{0}".format(supply_fan)
			g.add((EX[sensor], RDF.type, BRICK.Supply_Fan_Air_Flow_Sensor))
			g.add((EX[supply_fan], BRICKFRAME.hasPoint, EX[sensor]))
		to_delete.append(tag)	
	if "ahu" in tags[tag] and "exhaust_fan" in tags[tag]: 
		exhaust_fan = "exhaust_fan_{0}".format(tags[tag]["exhaust_fan"])
		ahu = "ahu_{0}".format(tags[tag]["ahu"])
		if (EX[exhaust_fan], RDF.type, BRICK.Exhaust_Fan) not in g:
			g.add((EX[exhaust_fan], RDF.type, BRICK.Exhaust_Fan))
			g.add((EX.ahu, RDF.contains, EX[exhaust_fan]))
		if "air_volume" in tags[tag] or "filtered_air_volume" in tags[tag]:
			sensor = "exhaust_fan_cfm_{0}".format(exhaust_fan)
			g.add((EX[sensor], RDF.type, BRICK.Exhaust_Air_Flow_Sensor))
			g.add((EX[exhaust_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "differential_pressure_status" in tags[tag]:
			sensor = "diff_pressure_status_{0}".format(exhaust_fan)
			g.add((EX[sensor], RDF.type, BRICK.Differential_Pressure_Status)) 
			g.add((EX[exhaust_fan], BRICKFRAME.hasPoint, EX[sensor]))
		elif "fan_speed_reset" in tags[tag]:
			sensor = "fan_speed_reset_{0}".format(exhaust_fan)
			g.add((EX[sensor], RDF.type, BRICK.Fan_Speed_Reset))
			g.add((EX[exhaust_fan], BRICKFRAME.hasPoint, EX[sensor]))
		to_delete.append(tag)

for tag in tags:
	if "ALL" in tag:
		to_delete.append(tag)

for tag in to_delete:
	del tags[tag]


to_delete = []
for tag in tags:
	if "VAV_" in tag:
		ahu = "ahu_{0}".format(tags[tag]["ahu"])
		floor = "floor_{0}".format(tags[tag]["floor"][1])
		sensor_flow = "flow_sensor_{0}".format(tag)
		g.add((EX[sensor_flow], RDF.type, BRICK.Supply_Air_Flow_Sensor))
		g.add((EX[sensor_flow], BRICKFRAME.isLocatedIn, EX[floor]))
		if "_MX" in tag:	
			g.add((EX[sensor_flow], BRICKFRAME.hasTag, BRICK.Max))
		elif "_AV" in tag: 
			g.add((EX[sensor_flow], BRICKFRAME.hasTag, BRICK.Average))
		elif "_MN" in tag:
			g.add((EX[sensor_flow], BRICKFRAME.hasTag, BRICK.Min))
		to_delete.append(tag)
	elif "LOW_RAT" in tag:
		ahu = "ahu_{0}".format(tags[tag]["ahu"])
		sensor = "rat_{0}".format(tag)
		g.add((EX[sensor], RDF.type, BRICK.Return_Air_Temperature_Low_Limit_Alarm))
		g.add((EX[ahu], RDF.hasPoint, EX[sensor]))
		to_delete.append(tag)
	elif "SMK_ALM" in tag:
		ahu = "ahu_{0}".format(tags[tag]["ahu"])
		sensor = "smoke_alarm_{0}".format(tag)
		g.add((EX[sensor], RDF.type, BRICK.Smoke_Detected_Alarm)) 
		g.add((EX[ahu], BRICKFRAME.hasPoint, EX[sensor]))
		to_delete.append(tag)
	elif "CURTL" in tag:
		ahu = "ahu_{0}".format(tags[tag]["ahu"]) 
		sensor = "curtl_{0}".format(tag)
		g.add((EX[sensor], RDF.type, BRICK.Curtailment_Override))
		g.add((EX[ahu], BRICKFRAME.hasPoint, EX[sensor])) 
		to_delete.append(tag)
	elif "EVENT" in tag:
		ahu = "ahu_{0}".format(tags[tag]["ahu"])
		sensor = "override_event_{0}".format(tag)
		g.add((EX[sensor], RDF.type, BRICK.AHU_Overriden_On_Status))
		g.add((EX[ahu], BRICKFRAME.hasPoint, EX[sensor]))
		to_delete.append(tag)
 	elif "_OCCPY" in tag:
		ahu = "ahu_{0}".format(tags[tag]["ahu"])
		sensor = "ahu_occpy_{0}".format(tag)
		g.add((EX[sensor], RDF.type, BRICK.Occupancy_Command))
		g.add((EX[ahu], BRICKFRAME.hasPoint, EX[sensor]))
		to_delete.append(tag)
 	elif "___S_S" in tag:
		ahu = "ahu_{0}".format(tags[tag]["ahu"])
		sensor = "ahu_start_stop_{0}".format(tag)
		g.add((EX[sensor], RDF.type, BRICK.Start_Stop_Command))
		g.add((EX[ahu], BRICKFRAME.hasPoint, EX[sensor]))
		to_delete.append(tag)
	elif "OAT" in tag:
 		ahu = "ahu_{0}".format(tags[tag]["ahu"])
		sensor = "oat_{0}".format(tag)
		g.add((EX[sensor], RDF.type, BRICK.Outside_Air_Temperature))
		g.add((EX[ahu], BRICKFRAME.hasPoint, EX[sensor]))
		to_delete.append(tag)


for tag in to_delete:
	del tags[tag]

tags = nonahutags
tagnames = [ (tag, tag[::-1]) for tag in tags ]
for tag in sorted(tagnames, key=lambda k:k[1]):
	print tag[0]
#for tag in sorted(tags):
#	print tag, tags[tag]

for tag in tags:
	if tag == "SOD__BLD_1_KWH":
		sensor = "energy_meter_building_{0}".format(tag)
		g.add((EX[sensor], RDF.type, BRICK.Energy_Meter))
	elif tag == "SOD__BLD_1_KWD":
		sensor = "energy_demand_building_{0}".format(tag)
		g.add((EX[sensor], RDF.type, BRICK.Energy_Demand))

del tags["SOD__BLD_1_KWH"]
del tags["SOD__BLD_1_KWD"]

print "Number of tags remaining : ", len(nonahutags)
g.serialize(destination='soda_hall_berkeley.ttl', format='turtle')
print len(g)
		
