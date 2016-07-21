# The GreenTech House / Center

This directory targets [GTH](http://greentechcenter.dk)

The [Makefile](Makefile) uses a [generator script](gtc_brickgenerator.py) to generate the Brick TTL file. This script uses three JSON files listing equipment and their relations:

1. [gtc.json](gtc.json)
   List of all exposed points.
2. [gtc_vavs.json](gtc_vavs.json)
   List of the equivalent of VAVs and how they are connected to the rooms and the equivalent of an AHU.
3. [rooms.json](rooms.json)
   List of rooms, including configuration and internal point names.

