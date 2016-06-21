#!/bin/bash

for building in ../UCSD/EBU3B/ebu3b_brick.ttl ../SDU/sdu_gtc.ttl ../CMU-Yuvraj/GHCYuvraj_brick.ttl ../IBM/IBM_B3.ttl; do
    echo $building
    python RUN_APPS.py $building
done
