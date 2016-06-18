How to Lay a BRICK
==================

A key concept is that few relations are needed to provide value, but for each added relation that value increases. In these guidelines we differentiate between a simple model and an extended model. The simple model represents a sensible minimum.

Constructing a simple VAV
-------------------------

A VAV needs to be instantiated.

    VAV_1 a VAV

A VAV has a set of potential parts. Instances of such parts should be associated using the *hasPart* relationship.

    Supply_Damper_1 a Supply_Damper
    Return_Damper_1 a Return_Damper
    Cooling_Coil_1  a Cooling_Coil
    
    VAV_1 hasPart Supply_Damper_1
    VAV_1 hasPart Return_Damper_1
    VAV_1 hasPart Cooling_Coil_1

If one knows about sensors then they should be fully described through tags and *pointOf* the VAV instance.

	Supply_Air_Temperature_1 a Supply_Air_Temperature
	Supply_Air_Temperature_1 pointOf VAV_1

Here, Supply_Air_Temperature implies the tags Supply (the role), Air (the media) and Temperature (the modality). 

Extending the VAV
-----------------

If one has visibility into the internals of the VAV then the _feeds_ relationship may be used.

    Supply_Damper_1 feeds Cooling_Coil_1
    Cooling_Coil_1  feeds Supply_Air_Temperature_1

The equipment class is relative to the output of its context. Due to its *partOf* relation to VAV_1 Supply_Air_Temperature_1 thus measures the *temperature* of the *airflow* in the *supply* direction on the output side of VAV_1.

If existing tagsets do not offer enough specificity then a subclass may be constructed. Imagine a temperature sensor -- within VAV_1 -- measuring the same the same the same (role,media,modality), but at the input side of the VAV. This sensor is on the output side of whatever is feeding VAV_1. For the sake of this example, lets call this an AHU.

    AHU_Supply_Air_Temperature isSubClassOf Supply_Air_Temperature
    AHU_Supply_Air_Temperature_1 a AHU_Supply_Air_Temperature
	AHU_Supply_Air_Temperature_1 pointOf VAV_1

For convenience, we can alias this to:

    Input_Supply_Air_Temperature  aliasOf AHU_Supply_Air_Temperature
    Output_Supply_Air_Temperature aliasOf Supply_Air_Temperature
