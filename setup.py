from setuptools import setup, find_packages

setup(
    name="cvsutils",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "nibabel",
        "numpy",
        "scipy",
    ],
    scripts=['run_bids_swi.py', 'run_swi_test.py'],
    author="CVS Research Team",
    description="Utilities for CVS MRI processing",
)
