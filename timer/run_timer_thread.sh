#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
PYTHONLIB=${PWD}/../lib/lib-py/python3.6/site-packages/ # folder with python library
REPERTORY_LIB_NEST=${PWD}/../lib/nest_run/lib/python3.6/site-packages/ # folder with py-nest
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST
export PATH=$PATH:${PWD}/../../../co_simulation/co-simulation-tvb-nest/venv/

for i in {1..10}
do
  for trail in {0..10}
  do
    python3 ./run_co-sim_thread.py './test_file/paper_time_thread/' $trail 0.0 1000.0 $i
  done
done