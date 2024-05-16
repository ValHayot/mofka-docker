#!/bin/bash

# Script to initiate event communication in mofka between a login and a compute node

# load spack environment
source ~/spack/share/spack/setup-env.sh
spack env activate pymofka -p
spack load py-pip

export MOFKA_PROTOCOL=$1
echo ${MOFKA_PROTOCOL}

# Start bedrock service
bedrock ${MOFKA_PROTOCOL} -c config.json &
bpid=`echo "$!"`
topic_source_1='source_1'
topic_source_2='source_2'
topic_report='report'

create_topic_partition () {
	# Create a topic and add a memory partition
	# to it using the mofkactl cli
	# function args:
	# 	topic (str) : the topic name
	topic=$1
	mofkactl topic create ${topic} --groupfile mofka.ssg
	mofkactl partition add ${topic} \
		--type memory \
		--rank 0 \
		--groupfile mofka.ssg

}

create_topic_partition ${topic_source_1}
create_topic_partition ${topic_source_2}
create_topic_partition ${topic_report}


# Create input data events
python example-app/mofka-login-producer.py ${topic_source_1} 1
python example-app/mofka-login-producer.py ${topic_source_2} 2

# Launch compute script
qsub -V example-app/pbs-submit.sh

# Meanwhile start consumer and wait to receive event 
python example-app/mofka-login-consumer.py

# Kill bedrock server
kill ${bpid}
