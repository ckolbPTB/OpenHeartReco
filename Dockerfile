ARG BASE_IMAGE=ubuntu:22.04
FROM ${BASE_IMAGE} as base

USER root
ARG DEBIAN_FRONTEND=noninteractive

# install ubuntu dependencies
COPY ubuntu.sh .
RUN bash ubuntu.sh
RUN rm ubuntu.sh

# install ismrmrd
COPY ismrmrd.sh .
RUN bash ismrmrd.sh
RUN rm ismrmrd.sh
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# install anaconda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH
RUN conda update -n base -c defaults conda

# create conda environment
COPY recon_environment.yml .
RUN conda env create --file recon_environment.yml
ENV PATH=/opt/conda/bin:$PATH

# get specific version of SIRF 
ENV INSTALL_DIR=/opt
RUN git clone -b oh-recon --single-branch https://github.com/johannesmayer/SIRF.git --depth 1 $INSTALL_DIR/SIRF

# install gadgetron and sirf
COPY sirf_gadgetron.sh .
RUN bash sirf_gadgetron.sh
RUN rm sirf_gadgetron.sh
RUN chmod -R go+rwX /opt/SIRF-SuperBuild/INSTALL
ENV PATH=/opt/SIRF-SuperBuild/INSTALL/bin:$PATH
ENV LD_LIBRARY_PATH=/opt/SIRF-SuperBuild/INSTALL/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH=/opt/SIRF-SuperBuild/INSTALL/python:$PYTHONPATH

# reconstruction code
RUN mkdir /reco_scripts
COPY reco_scripts/sirf_preprocessing.py /reco_scripts
COPY reco_scripts/mr_cine_recon.py /reco_scripts





