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
