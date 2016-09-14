#!/bin/bash

for building in `ls ../building_instances/*.ttl`; do
    echo $building
    python RUN_APPS.py $building
done
