#!/bin/bash

for building in ../UCBerkeley/berkeley.ttl ../UCSD/EBU3B/ebu3b_brick.ttl ../SDU/sdu_gtc_simple.ttl ../CMU-Yuvraj/GHCYuvraj_brick.ttl ../UVA/Rice.ttl; do
    echo $building
    python RUN_APPS.py $building
done
