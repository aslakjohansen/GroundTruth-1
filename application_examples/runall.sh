#!/bin/bash

for building in ../building_instances/ebu3b_brick.ttl  ../building_instances/ghc_brick.ttl  ../building_instances/gtc_brick.ttl  ../building_instances/rice_brick.ttl  ../building_instances/soda_brick.ttl; do
    echo $building
    python RUN_APPS.py $building
done
