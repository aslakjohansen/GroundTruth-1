#!/bin/bash

for building in ../etc/instance_generators/IBM/IBM_B3.ttl ../etc/instance_generators/SODA_UCB/SODA/berkeley.ttl ../etc/instance_generators/EBU3B_UCSD/ebu3b_brick.ttl ../etc/instance_generators/GTC_SDU/gtc_brick.ttl ../etc/instance_generators/GHC_CMU/GHC_brick.ttl ../etc/instance_generators/RICE_UVA/Rice.ttl; do
    echo $building
    python3 RUN_APPS_jp.py $building
done
