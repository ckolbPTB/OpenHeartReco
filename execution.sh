#!/bin/bash --login

exec source /opt/conda/bin/activate RecoEnv
exec gadgetron &
exec python /recon/mr_cine_recon.py /input /output
exec kill $(pidof gadgetron)