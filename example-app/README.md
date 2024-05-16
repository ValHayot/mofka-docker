# Example app

The goal of this example is to demonstrate how Mofka could be used within the AERO applications for data communication within sites where outbound connection is not available on compute nodes.

![AERO-mofka](figures/AERO(DSaaS)_MofKa_Octopus.jpg)

## How to run

### Locally

Start the Bedrock server

`bedrock ofi+tcp -c config.json &`

Create all topics and assign them memory partitions. For this example, we will create three topics,
two for the sources (source_1 and source_2) and another for the output report.

```
mofkactl topic create source_1 --groupfile mofka.ssg
mofkactl partition add source_1 \
	--type memory \
	--rank 0 \
	--groupfile mofka.ssg

mofkactl topic create source_2 --groupfile mofka.ssg
mofkactl partition add source_2 \
	--type memory \
	--rank 0 \
	--groupfile mofka.ssg

mofkactl topic create report --groupfile mofka.ssg
mofkactl partition add report \
	--type memory \
	--rank 0 \
	--groupfile mofka.ssg
```

Fetch the data from AERO and publish as an event. The example app requires two data inputs, therefore this needs to be executed twice for each input.

```
python example-app/mofka-login-producer.py source_1 1
python example-app/mofka-login-producer.py source_2 2
```

On a compute node, consume the events and retrieve associated data inputs, perform computation and publish the report as a event to Mofka

```
python example-app/app.py
```

Back on the login node, consume the report event and publish to DSaaS

```
python example-app/mofka-login-consumer.py
```

### Polaris

For Polaris, sample scripts are provided to assist with execution.

#### Creating the Spack environment

1. Load modules on Polaris
```
module load PrgEnv-gnu gcc-native/12.3 nvhpc-mixed libfabric
```

2. Clone the Spack repositore and checkout the latest version
```
git clone --depth=100 https://github.com/spack/spack.git ~/spack
git switch -c releases/latest origin/releases/latest
```

3. Source the Spack setup script and create environment using the provided yml
```
source ~/spack/share/spack/setup-env.sh
spack env create pymofka example-app/spack.yml
```

4. Activate the newly created environment and install packages
```
spack env activate pymofka -p
spack install
```

#### Running the scripts

This repo contains two helper scripts for running on Polaris, namely: `run-polaris.sh` and `pbs-submit.sh`. The `run-polaris.sh` script:
- loads the Spack environment (assuming that the instructions above were followed exactly)
- starts the Bedrock service using ofi+tcp on the login node
- creates the necessary topics and assigns them memory partitions
- creates a login node producer and submits two events for the data inputs
- starts the app (using `pbs-submit.sh`) on the compute node that will consume the previous data input event and publish the report as an event
- creates a login node consumer that should receive the report from the compute node's producer

The `run-polaris` script takes as input a single argument representing the communication protocol to use.

To run the scripts, from the root folder, execute:
`bash example-app/run-polaris.sh <mofka_communication_protocol>`

e.g.,
`bash example-app/run-polaris.sh "ofi+cxi://"`


**NOTE**: `pbs-submit.sh` needs to be modified to use the correct allocation.
