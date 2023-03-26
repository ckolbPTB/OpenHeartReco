import numpy as np
from collections import Counter
import sirf.Gadgetron as pMR


def write_dicom(image_data, fprefix_out):
    # Write dicoms
    print(f"We have {image_data.number()} images to write.")
    image_data = image_data.abs()
    image_data.write(str(fprefix_out / "sirfrecon.dcm"))
    
    # Verify that dicoms were written
    dcm_data = list(fprefix_out.glob("*.dcm"))
    assert len(dcm_data) > 0, 'No dicom images were written.'
    
    return True