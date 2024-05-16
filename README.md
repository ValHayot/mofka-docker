# pyMofka example

PyMofka DockerFile and example code. This repo provides a dockerfile that configures a spack environment with mofka installed as well as example functions for starting a producer and a consumer.

PyMofka code mostly borrowed from [MofkaDask](https://github.com/GueroudjiAmal/MofkaDask/)

## Docker

### Clone the repo
Prior to building the docker image and following the rest of the instructions, it is necessary to clone the repository:

```
git clone git@github.com:ValHayot/mofka-docker.git
```

### Build
Build dockerfile using the following command:

```
docker build -t mofka .
```

### Running the container
To run the container, the following command may be used. The current working directory (root of the repo) is mounted to be able to access `mofka_producer.py` and `mofka_client.py` scripts.

```
docker run --rm -it -v $PWD:$PWD -w $PWD mofka
```

### Running the scripts
One in the container with the environment set up, it is possible to start running the produce and consumer scripts. However, it is first necessary to start the Bedrock server, which in turn will generate the `mofka.ssg` file:

```
bedrock ofi+tcp -c config.json &
```

Then, the producer can be started:
```
python mofka_producer.py
```

and finally, the consumer can be started:
```
python mofka_consumer.py
```

Example output of running from start to finish should look like this:

```
[mofka] root@5abf41a46da4:/Users/valeriehayot-sasson/postdoc/mofka-docker# bedrock ofi+tcp -c config.json &
[5] 1043
[mofka] root@5abf41a46da4:/Users/valeriehayot-sasson/postdoc/mofka-docker# [2024-04-28 15:30:31.473] [info] [yokan] YOKAN provider registration done
[2024-04-28 15:30:31.473] [info] Bedrock daemon now running at ofi+tcp://172.17.0.2:37027

[mofka] root@5abf41a46da4:/Users/valeriehayot-sasson/postdoc/mofka-docker# python mofka_producer.py
69PQDSNPVH
GV0ZAD3V40
Y303PPXTT9
6XGC369CRV
2Y0VVQMULE
A9RD64L6RG
ALH2R8WJE5
OLH40RCLJR
U5JVOWGMX8
726HNBZN7X
[mofka] root@5abf41a46da4:/Users/valeriehayot-sasson/postdoc/mofka-docker# python mofka_consumer.py 
data='69PQDSNPVH', metadata={'action': 'get_result'}
data='GV0ZAD3V40', metadata={'action': 'get_result'}
data='Y303PPXTT9', metadata={'action': 'get_result'}
data='6XGC369CRV', metadata={'action': 'get_result'}
data='2Y0VVQMULE', metadata={'action': 'get_result'}
data='A9RD64L6RG', metadata={'action': 'get_result'}
data='ALH2R8WJE5', metadata={'action': 'get_result'}
data='OLH40RCLJR', metadata={'action': 'get_result'}
data='U5JVOWGMX8', metadata={'action': 'get_result'}
data='726HNBZN7X', metadata={'action': 'get_result'}
```
