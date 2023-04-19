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
COPY reco_environment.yml .
RUN conda env create --file reco_environment.yml
ENV PATH=/opt/conda/bin:$PATH

# SIRF-SuperBuild version
ARG SIRF_SB_TAG="v3.4.0"

# get specific version of SIRF 
ENV INSTALL_DIR=/opt
#RUN git clone -b oh-recon --single-branch https://github.com/johannesmayer/SIRF.git --depth 1 $INSTALL_DIR/SIRF
RUN git clone -b open-heart-reco https://github.com/ckolbPTB/SIRF.git $INSTALL_DIR/SIRF

# install gadgetron and sirf
COPY sirf_gadgetron.sh .
RUN bash sirf_gadgetron.sh
RUN rm sirf_gadgetron.sh
RUN chmod -R go+rwX /opt/SIRF-SuperBuild/INSTALL
ENV PATH=/opt/SIRF-SuperBuild/INSTALL/bin:$PATH
ENV LD_LIBRARY_PATH=/opt/SIRF-SuperBuild/INSTALL/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH=/opt/SIRF-SuperBuild/INSTALL/python:$PYTHONPATH

# remove SIRF repo folder
RUN rm -r $INSTALL_DIR/SIRF

# reconstruction code
RUN mkdir /reco_scripts
COPY reco_scripts/sirf_preprocessing.py /reco_scripts
COPY reco_scripts/sirf_util.py /reco_scripts
COPY reco_scripts/mr_cine_recon.py /reco_scripts

# define entry point
COPY execution.sh .
RUN chmod +x execution.sh

LABEL org.nrg.commands="[{\"name\": \"oh_reco\", \"description\": \"QC for raw MR data using SIRF\", \"label\": \"oh_reco\", \"version\": \"0.2\", \"schema-version\": \"1.0\", \"type\": \"docker\", \"image\": \"ckolbptb/oh_reco\", \"command-line\": \"./execution.sh\", \"mounts\": [{\"name\": \"raw-in\", \"writable\": \"false\", \"path\": \"/input\"}, {\"name\": \"dcm-out\", \"writable\": \"true\", \"path\": \"/output\"}], \"inputs\": [{\"name\": \"other-options\", \"description\": \"Other command-line flags to pass to qc_dicom_nii\", \"type\": \"string\", \"required\": false, \"replacement-key\": \"[OTHER_OPTIONS]\"}], \"outputs\": [{\"name\": \"dicom\", \"description\": \"Reconstructed dcm files\", \"mount\": \"dcm-out\", \"required\": \"true\"}], \"xnat\": [{\"name\": \"sirf_qc\", \"description\": \"Run QC on MR raw data\", \"label\": \"sirf_qc_mr\", \"contexts\": [\"xnat:imageScanData\"], \"external-inputs\": [{\"name\": \"scan\", \"description\": \"Input scan\", \"type\": \"Scan\", \"required\": true, \"matcher\": \"'MR_RAW' in @.resources[*].label\"}], \"derived-inputs\": [{\"name\": \"scan-raw\", \"description\": \"The raw resource on the scan\", \"type\": \"Resource\", \"derived-from-wrapper-input\": \"scan\", \"provides-files-for-command-mount\": \"raw-in\", \"matcher\": \"@.label == 'MR_RAW'\"}], \"output-handlers\": [{\"name\": \"dcm-resource\", \"accepts-command-output\": \"dicom\", \"as-a-child-of\": \"scan\", \"type\": \"Resource\", \"label\": \"DICOM\"}]}, {\"name\": \"sirf_qc_resource\", \"description\": \"Run QC on MR raw data resource\", \"label\": \"sirf_qc_mr_resource\", \"contexts\": [\"xnat:resourceCatalog\"], \"external-inputs\": [{\"name\": \"scan-raw\", \"description\": \"The raw resource on the scan\", \"type\": \"Resource\", \"provides-files-for-command-mount\": \"raw-in\", \"matcher\": \"@.label == 'MR_RAW'\"}], \"derived-inputs\": [{\"name\": \"scan\", \"description\": \"Input scan\", \"type\": \"Scan\", \"derived-from-wrapper-input\": \"scan-raw\"}], \"output-handlers\": [{\"name\": \"dcm-resource\", \"accepts-command-output\": \"dicom\", \"as-a-child-of\": \"scan\", \"type\": \"Resource\", \"label\": \"DICOM\"}]}]}]"




