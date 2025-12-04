# cvsUtils

**cvsUtils** is a collection of specialized utilities for processing Susceptibility Weighted Imaging (SWI) and other MRI sequences, developed for Central Vein Sign (CVS) research.

## Features

### Robust SWI Skull Stripping
Standard skull stripping tools often fail on SWI images due to the high intensity of the superior scalp and dura. `cvsUtils` provides a robust, multi-stage solution:

1.  **Initial Skull Stripping (External)**: Uses FSL BET (called via runner scripts) to remove the bulk of the skull.
2.  **Gradient-Based Refinement**: Scans the superior region of the pre-stripped brain to detect and remove any remaining scalp/dura based on intensity gradients.
3.  **Morphological Smoothing**: Applies enhanced morphological opening and closing to ensure a smooth, clean brain mask.

## Installation

```bash
pip install .
```

## Usage

```python
from cvsutils import swi_strip

# Input must be an already skull-stripped image (e.g. from BET)
swi_strip.strip_swi(
    swi_masked_path='path/to/swi_bet.nii.gz',
    output_prefix='output/prefix_'
)
```

## Requirements
- Python 3.x
- `nibabel`
- `numpy`
- `scipy`
- FSL (installed and accessible for runner scripts)
