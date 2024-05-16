FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt -y update

RUN apt-get install -y vim g++ gfortran git vim cmake libtool \
    wget build-essential libncursesw5-dev libssl-dev \
    libsqlite3-dev tk-dev libgdbm-dev libc6-dev autoconf automake \
    libbz2-dev libffi-dev zlib1g-dev unzip software-properties-common

RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt -y install python3.11

RUN git clone --depth=100 https://github.com/spack/spack.git ~/spack
RUN git clone https://github.com/mochi-hpc/mochi-spack-packages.git ~/mochi-spack-packages

ADD ./spack.yaml /root/spack.yml

RUN . ~/spack/share/spack/setup-env.sh \
    && spack env create mofka /root/spack.yml

RUN . ~/spack/share/spack/setup-env.sh \
    && spack -e mofka compiler find

RUN . ~/spack/share/spack/setup-env.sh \
    && spack -e mofka repo add ~/mochi-spack-packages

RUN . ~/spack/share/spack/setup-env.sh \
    && spack -e mofka external find --not-buildable cmake autoconf automake m4 libtool

RUN . ~/spack/share/spack/setup-env.sh \
    && spack -e mofka concretize -f

RUN . ~/spack/share/spack/setup-env.sh \
    && spack -e mofka install

RUN . ~/spack/share/spack/setup-env.sh \
    && spack env activate mofka -p \
    && spack load py-pip \
    && pip install git+https://github.com/nsf-resume/dsaas-client.git

# temp solution until we fix dsaas code
RUN mkdir -p ~/.local/share/dsaas

RUN echo ". ~/spack/share/spack/setup-env.sh" >> ~/.bashrc
RUN echo "spack env activate mofka -p" >> ~/.bashrc
RUN echo "spack load py-pip" >> ~/.bashrc
SHELL ["/bin/bash -l -c"]

