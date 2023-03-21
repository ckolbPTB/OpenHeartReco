import os
import shutil

from pathlib import Path
import sirf_preprocessing as preprocess
import sirf.Gadgetron as pMR

import sys
from pathlib import Path


def main_cine_recon(fpath_in, fpath_output_prefix):

    print(f"Reading from {fpath_in}, writing into {fpath_output_prefix}")
    assert os.access(fpath_in, os.R_OK), f"You don't have read permission in {fpath_in}"
    assert os.access(fpath_output_prefix, os.W_OK), f"You don't have write permission in {fpath_output_prefix}"

    list_rawdata = sorted(fpath_in.glob("*.h5"))
    success = True

    for fname_raw in list_rawdata:
        mr_data = preprocess.equally_fill_cardiac_phases(str(fname_raw))
        success *= sirf_cine_recon(mr_data, fpath_output_prefix)

    list_attribute_files = sorted(fpath_output_prefix.glob( "*_attrib.xml"))
    print(f"We remain with {len(list_attribute_files)} to delete.")
    [os.remove(attrib_file) for attrib_file in list_attribute_files]

    print(f'Reconstruction finished successful? {success}')

    return int(not success)

def sirf_cine_recon(mr_rawdata: pMR.AcquisitionData, fprefix_out: Path):

    # Pre-process this input data.
    # (Currently this is a Python script that just sets up a 3 chain gadget.
    # In the future it will be independent of the MR recon engine.)
    preprocessed_data = pMR.preprocess_acquisition_data(mr_rawdata)

    # Perform reconstruction of the preprocessed data.
    # 1. set the reconstruction to be for Cartesian GRAPPA data.

    recon_gadgets = ['AcquisitionAccumulateTriggerGadget',
            'B2B:BucketToBufferGadget',
            'GenericReconCartesianReferencePrepGadget',
            'GRAPPA:GenericReconCartesianGrappaGadget',
            'GenericReconFieldOfViewAdjustmentGadget',
            'GenericReconImageArrayScalingGadget',
            'ImageArraySplitGadget',
            # 'PhysioInterpolationGadget(phases=30, mode=0, first_beat_on_trigger=false, interp_method=BSpline)',
            ]
    recon = pMR.Reconstructor(recon_gadgets)

    # 2. set the reconstruction input to be the data we just preprocessed.
    recon.set_input(preprocessed_data)

    # 3. run (i.e. 'process') the reconstruction.
    print('---\n reconstructing...\n')
    recon.process()

    # retrieve reconstruced image and G-factor data
    # image_data = recon.get_output('Image PhysioInterp')
    image_data = recon.get_output('image')
    print(f"We have {image_data.number()} images to write.")
    image_data = image_data.abs()
    image_data.write(str(fprefix_out / "sirfrecon.dcm"))

    return True


### looped reconstruction over files in input path
path_in  = Path(sys.argv[1])
path_out = Path(sys.argv[2])

if __name__ == "__main__":
    success = main_cine_recon(path_in, path_out)
    sys.exit(success)

