import os
import shutil

from pathlib import Path
import sirf_preprocessing as preprocess
import sirf_util as util
import sirf.Gadgetron as pMR

from cil.optimisation.algorithms import FISTA
from cil.optimisation.functions import LeastSquares, ZeroFunction

import sys
from pathlib import Path

# Support scan times
scan_types = {'0001' : 'm2DCartCine',
                '0002' : '2DRadRTCine'}


def main_recon(fpath_in, fpath_output_prefix):

    print(f"Reading from {fpath_in}, writing into {fpath_output_prefix}")
    assert os.access(fpath_in, os.R_OK), f"You don't have read permission in {fpath_in}"
    assert os.access(fpath_output_prefix, os.W_OK), f"You don't have write permission in {fpath_output_prefix}"

    list_rawdata = sorted(fpath_in.glob("*.h5"))
    success = True

    for fname_raw in list_rawdata:
        # Select reconstruction type
        scan_type_code = str(fname_raw)[-7:-3]
        if scan_type_code == '0001': # M2D Cartesian Cine
            success *= sirf_m2d_cine_cart_recon(str(fname_raw), fpath_output_prefix)
        elif scan_type_code == '0002': # 2D Real-time non-Cartesian
            success *= sirf_2d_rt_non_cart_recon(str(fname_raw), fpath_output_prefix)
        else:
            raise KeyError(f'Scan type {scan_type_code} not recognised. Supporte scan type codes are {scan_types}')
    
    list_attribute_files = sorted(fpath_output_prefix.glob( "*_attrib.xml"))
    print(f"We remain with {len(list_attribute_files)} to delete.")
    [os.remove(attrib_file) for attrib_file in list_attribute_files]

    print(f'Reconstruction finished successful? {success}')

    return int(not success)


def sirf_2d_rt_non_cart_recon(fname_raw: str, fprefix_out: Path):
    
    # Load in data
    rd = pMR.AcquisitionData(fname_raw, all_=False)
    rd = pMR.preprocess_acquisition_data(rd)
    
    # Check if trajectory exists
    try:
        ktraj = pMR.get_data_trajectory(rd)
    except Exception as e:
        print(f'Trajectory not found: {e}.')
        return(False)

    # Verify data is not Cartesian
    assert rd.check_traj_type('cartesian') == False, 'Cartesian data cannot be reconstructed as radial'
    
    # Calculate coil sensitivity maps
    csm = pMR.CoilSensitivityData()
    csm.smoothness = 100
    csm.calculate(rd)

    # Set up iterative reconstruction
    x_init = pMR.ImageData()
    x_init.from_acquisition_data(rd)
    E = pMR.AcquisitionModel(acqs=rd, imgs=x_init)
    E.set_coil_sensitivity_maps(csm)

    # Define our objective/loss function as least squares between Ex and y
    f = LeastSquares(E, rd, c=1)

    # No regularisation
    G = ZeroFunction()

    # Set up FISTA
    fista = FISTA(initial=x_init, f=f, g=G)
    fista.max_iteration = 100
    fista.update_objective_interval = 10

    # Run FISTA for least squares
    fista.run(20, verbose=True)
    
    # Retrieve images
    image_data = fista.get_output()
    
    # Save dicome images
    util.write_dicom(image_data, fprefix_out)

    return(True)


def sirf_m2d_cine_cart_recon(fname_raw: str, fpath_output_prefix: Path):
    mr_data = preprocess.equally_fill_cardiac_phases(fname_raw)
    return(sirf_cine_recon(mr_data, fpath_output_prefix))
            
            
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

    # Retrieve reconstruced image
    # image_data = recon.get_output('Image PhysioInterp')
    image_data = recon.get_output('image')
    
    # Save dicome images
    util.write_dicom(image_data, fprefix_out)

    return True


### looped reconstruction over files in input path
path_in  = Path(sys.argv[1])
path_out = Path(sys.argv[2])

if __name__ == "__main__":
    success = main_recon(path_in, path_out)
    sys.exit(success)

