import numpy as np
from collections import Counter
import sirf.Gadgetron as pMR

def equally_fill_cardiac_phases(fname_in):

    rd = pMR.AcquisitionData(fname_in, all_=False)

    rd_preprocessed = rd.new_acquisition_data()
    slices = np.unique(rd.get_ISMRMRD_info('slice'))
    acquired_kspace_dims = get_acquired_kspace_dimensions(rd)
    print(f"We have found kspace dimensions to be {acquired_kspace_dims} ")
    if acquired_kspace_dims['phase'] == 1:
        rd_preprocessed = rd
    else:
        for slc in slices:
            rd_slice = get_slice_subset(rd, slc)
            print(f"We have {rd_slice.number()} acquisitions in the slice {slc}.")

            rd_slice = fill_undersampled_phases(rd_slice)
            append_acquisitiondata(rd_preprocessed, rd_slice)

    return rd_preprocessed

def append_acquisitiondata(rd_to, rd_from):

    for i in range(rd_from.number()):
        acq = rd_from.acquisition(i)
        rd_to.append_acquisition(acq)

    return rd_to

def get_acquired_kspace_dimensions(rd):
    slices = np.unique(rd.get_ISMRMRD_info('slice'))
    phases = np.unique(rd.get_ISMRMRD_info('phase'))

    print(f"We found {phases} phases in the kspace dims.")
    dims = {'phase': len(phases),
            'slice': len(slices)}

    return dims

def fill_undersampled_phases(rawdata):

    rd_phase_filled = rawdata.copy()

    # get the undersampled and last fully sampled phase
    undersampled_phases, fsp = get_undersampled_phases(rawdata)

    # get phase encoding for last fully sampled phase
    pe_fs = get_phasencoding_for_phase(rawdata,fsp)

    fullysampled_data = get_phase_subset(rawdata, fsp)

    print(f"We have found undersampled phases: {undersampled_phases}.")
    print(f"Fully sampled reference phase: {fsp}.")
    for usp in undersampled_phases:
        cphaseenc = get_phasencoding_for_phase(rawdata,usp)

        missing_points = list(set(pe_fs) - set(cphaseenc))
        rd_missing = get_missing_pe_points(fullysampled_data, missing_points)

        max_time_stamp = get_maximum_physio_timestamp_for_phase(rawdata, usp)
        print(f"Setting the time stamp of {max_time_stamp} to hope for better distribution.")
        print(f"adding {rd_missing.number()} phase encoding points to phase {usp}")
        for i in range(rd_missing.number()):
            acq = rd_missing.acquisition(i)
            acq.set_phase(usp)
            acq.set_physiology_time_stamp(max_time_stamp,0)
            rd_phase_filled.append_acquisition(acq)

    return rd_phase_filled

def get_maximum_physio_timestamp_for_phase(rawdata, phase):

    rd = get_phase_subset(rawdata, phase)
    return np.max(rd.get_ISMRMRD_info('physiology_time_stamp'))

def get_undersampled_phases(rawdata):
    cardiac_phase = rawdata.get_ISMRMRD_info('phase')
    cpc = Counter(cardiac_phase)
    pe_pts_per_phase = [cpc[key] for key in cpc]

    # TODO: check for that if all have same number of readouts as median

    median_num_ro_per_phase = np.median(sorted(pe_pts_per_phase))
    undersampled_phases = np.where(pe_pts_per_phase < median_num_ro_per_phase)
    last_fullysampled_phase = np.min(undersampled_phases[0]) - 1

    return undersampled_phases[0], last_fullysampled_phase

def get_phasencoding_for_phase(rawdata, phase_number):

    rawdata = get_phase_subset(rawdata,phase_number)
    return rawdata.get_ISMRMRD_info('kspace_encode_step_1')

def get_encoding_subset(rawdata, encoding_dimension, dim_number):

    acquisition_dim = rawdata.get_ISMRMRD_info(encoding_dimension, which=range(0,rawdata.number()))
    idx_all = np.arange(rawdata.number())
    idx_phase_number = idx_all[acquisition_dim == dim_number]

    return rawdata.get_subset(idx_phase_number)


def get_phase_subset(rawdata,phase_number):

    return get_encoding_subset(rawdata, 'phase', phase_number)

def get_slice_subset(rawdata,slice_number):

    return get_encoding_subset(rawdata, 'slice', slice_number)

def get_missing_pe_points(rawdata,missing_points):

    pe_points = rawdata.get_ISMRMRD_info('kspace_encode_step_1')

    overlap = np.isin(pe_points, missing_points)
    idx_all = np.arange(rawdata.number())
    idx_missing = idx_all[overlap]

    return rawdata.get_subset(idx_missing)

