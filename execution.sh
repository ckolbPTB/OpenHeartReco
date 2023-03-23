#!/bin/bash

source /opt/conda/bin/activate RecoEnv
gadgetron &
python /reco_scripts/mr_cine_recon.py /input /output
kill $(pidof gadgetron)