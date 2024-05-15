# Example app

The goal of this example is to demonstrate how Mofka could be used within the AERO applications for data communication within sites where outbound connection is not available on compute nodes.

![AERO-mofka](figures/AERO(DSaaS)_MofKa_Octopus.jpg)

## How to run

### Locally

The DSaaS client must be installed to run this code. To download:

`pip install git+https://github.com/nsf-resume/dsaas-client.git`

Start the Bedrock server

`bedrock ofi+tcp -c config.json &`

On a login node, fetch data from DSaaS and publish as an event. The example app requires two data inputs, therefore this needs to be executed twice for each input.

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
- creates a login node producer and submits two events for the data inputs
- starts the app (using `pbs-submit.sh`) on the compute node that will consume the previous data input event and publish the report as an event
- creates a login node consumer that should receive the report from the compute node's producer

To run the scripts, from the root folder, execute:
`bash example-app/run-polaris.sh`

**NOTE**: `pbs-submit.sh` needs to be modified to use the correct allocation.

**NOTE 2**: Communication protocol currently hardcoded (to be fixed). To change communication protocol, edit `run-polaris.sh` and `helpers.py`




