#!/bin/bash

# Script to initiate event communication in mofka between a login and a compute node

# load spack environment
source ~/spack/share/spack/setup-env.sh
spack env activate pymofka -p
spack load py-pip

# Start bedrock service
bedrock ofi+tcp -c config.json &
bpid=`echo "$!"`

mofkactl topic create source_1 --groupfile mofka.ssg
mofkactl topic create source_2 --groupfile mofka.ssg
mofkactl topic create report  --groupfile mofka.ssg

# Create input data events
python example-app/mofka-login-producer.py source_1 1
python example-app/mofka-login-producer.py source_2 2

# Launch compute script
qsub example-app/pbs-submit.sh

# Meanwhile start consumer and wait to receive event 
python example-app/mofka-login-consumer.py

# Kill bedrock server
kill ${bpid}
