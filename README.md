# Quality control for Open Heart


## Build docker image
In order to build the docker image, clone this repository
```
git clone https://github.com/ckolbPTB/OpenHeartReco.git
```

Change into the directory
```
cd OpenHeartReco
```

and build docker image
```
docker build -t oh_reco .
```

Here we are tagging the image with *oh_reco*. Feel free to use any other tag, but make sure you select the correct image when starting the container.  

The build process will take some time (on a normal laptop with two cores around 1.5 hours) and the final image will be around 9GB in size.
