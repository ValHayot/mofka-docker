#!/bin/sh
#PBS -l select=1:system=polaris
#PBS -l walltime=00:05:00
#PBS -l filesystems=home:grand
#PBS -q debug
#PBS -A SuperBERT


source ~/spack/share/spack/setup-env.sh
spack env activate pymofka -p
spack load py-pip

cd ~/mofka-docker
python example-app/app.py
sleep 3m
