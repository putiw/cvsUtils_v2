import os
import subprocess
import nibabel as nib
import numpy as np
from scipy import ndimage

def strip_swi(swi_masked_path, output_prefix):
    """
    Refine an existing skull-stripped SWI image (e.g. from BET) using Gradient-Based Refinement.
    """
    print(f"Starting SWI Refinement on {swi_masked_path}...")
    
    # 1. Load Data
    img = nib.load(swi_masked_path)
    data = img.get_fdata()
    
    # 2. Create Mask from Input (assumes background is 0)
    mask = data > 0
    
    # 3. Gradient Refinement (Inside-Out)
    print("  Step 1: Gradient-Based Refinement (Inside-Out)...")
    
    core_mask = ndimage.binary_erosion(mask, iterations=8)
    final_mask = mask.copy()
    
    nx, ny, nz = mask.shape
    core_cols = np.any(core_mask, axis=2)
    x_indices, y_indices = np.where(core_cols)
    
    count_cuts = 0
    
    for x, y in zip(x_indices, y_indices):
        col_core = core_mask[x, y, :]
        z_core_top = np.max(np.where(col_core)[0])
        
        col_mask = mask[x, y, :]
        if not np.any(col_mask):
            continue
        z_mask_top = np.max(np.where(col_mask)[0])
        
        cut_z = -1
        
        for z in range(z_core_top, z_mask_top):
            if z + 1 >= nz:
                break
                
            val_curr = data[x, y, z]
            val_next = data[x, y, z+1]
            
            gradient = val_next - val_curr
            
            if gradient > 15 or val_next > 145:
                cut_z = z
                break
        
        if cut_z != -1:
            final_mask[x, y, cut_z+1:] = False
            count_cuts += 1
            
    print(f"  Refined {count_cuts} columns.")
    
    # 4. Morphological Smoothing
    print("  Step 2: Morphological smoothing (Enhanced)...")
    struct = ndimage.generate_binary_structure(3, 1)
    struct_open = ndimage.iterate_structure(struct, 2)
    final_mask = ndimage.binary_opening(final_mask, structure=struct_open)
    struct_close = ndimage.iterate_structure(struct, 3)
    final_mask = ndimage.binary_closing(final_mask, structure=struct_close)
    
    # 5. Connectivity
    print("  Step 3: Keeping largest component...")
    labeled_array, num_features = ndimage.label(final_mask)
    if num_features > 0:
        sizes = ndimage.sum(final_mask, labeled_array, range(num_features + 1))
        max_label = np.argmax(sizes)
        final_mask = (labeled_array == max_label)
        
    final_mask = ndimage.binary_fill_holes(final_mask)
    
    # 6. Save
    data_swi_brain = data * final_mask
    swi_brain_path = f"{output_prefix}swi_brain.nii.gz"
    new_img = nib.Nifti1Image(data_swi_brain, img.affine, img.header)
    nib.save(new_img, swi_brain_path)
    
    mask_path = f"{output_prefix}swi_brain_mask.nii.gz"
    mask_img = nib.Nifti1Image(final_mask.astype(np.uint8), img.affine, img.header)
    nib.save(mask_img, mask_path)
    
    print(f"  Saved {swi_brain_path}")
    return swi_brain_path
