# SIRF for XNAT - Quality control for Open Heart

Create SIRF docker container to be called within XNAT via the container service plugin

## Introduction

For more detailed information on docker + SIRF please have a look at SIRF-SuperBuild/docker.

The idea here is to create a docker container which runs a reconstruction script at startup. The input and output for the docker container is defined in `LABEL` of `Dockerfile_xnat`. 

For more information on docker + XNAT please have a look here: [Docker images for XNAT container service](https://wiki.xnat.org/container-service/building-docker-images-for-container-service-122978872.html) 

## Step-by-step guide

### manifest.json
This describes the interface between the docker container and the XNAT database. It is not directly used but needs to be converted to a single string using e.g. [command2label.py](https://github.com/NrgXnat/docker-images/blob/master/command2label.py). This string is then added to `Dockerfile_xnat` as `LABEL`. 

### Reconstruction script
Manifest.json described above describes the input and output interface for the XNAT docker container. It allows to specify certain data formats to be provided as input to the script called inside the docker container. If the reconstruction script should be called for all files provided in the XNAT folders, then such a loop needs to be provided inside the reconstruction script. The input folder is read-only, the output folder is read and writeable. 

### Create docker image
Run
```
docker build . -t oh_reco
```
then tag this version and upload to dockerhub (ckolbptb dockerhub repo in this case)
```
docker tag oh_recon ckolbptb/oh_reco
docker push ckolbptb/oh_reco
```

### Add docker image to XNAT
The docker image can be easily added directly from dockerhub to the XNAT server. This requires administrative privileges. The interface between XNAT and the docker image described in `manifest.json` can be modified at this stage too. The docker image can then be made available to different projects. For more information see [XNAT container service](https://wiki.xnat.org/container-service/container-service-122978848.html) 
