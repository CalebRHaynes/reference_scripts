import glob
import nibabel as nib
import os
import sys

def extract_middle_slice(input_file, output_file):
    """
    Extract the middle 3D volume from a 4D NIfTI file and save it.
    """
    img = nib.load(input_file)

    if len(img.shape) == 4:
        middle_index = img.shape[-1] // 2
        middle_slice = img.slicer[..., middle_index]
        nib.save(middle_slice, output_file)
    else:
        print(f"Skipping {input_file}: not a 4D image")

def main(input_pattern):
    for nii_file in glob.glob(input_pattern):
        output_file = "middle_slice_" + os.path.basename(nii_file)
        extract_middle_slice(nii_file, output_file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_middle_slice.py '<input_glob_pattern>'")
    else:
        main(sys.argv[1])

