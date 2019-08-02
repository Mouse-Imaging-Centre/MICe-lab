#!/usr/bin/env python

from setuptools import setup, find_packages

import sys

setup(name="MICe-lab",
      version='0.19',
      description='Scripts and pipelines that are specific to the Mouse Imaging Centre lab.',
      long_description='Scripts and pipelines that are specific to the Mouse Imaging Centre lab.',
      url='https://github.com/Mouse-Imaging-Centre/MICe-lab',
      install_requires=[
        'ConfigArgParse>=0.11',
        'numpy',
        'pyminc',
        'typing',
        'scipy',
        'snakemake<=5.2.2',
        'matplotlib',
        'Pillow',
        'fastai',
        'opencv-python'
      ],
      dependency_links=['https://github.com/opencv/opencv/archive/3.1.0.tar.gz',
                        'https://github.com/Mouse-Imaging-Centre/pydpiper',
                        'https://github.com/fastai/fastai',
                        'https://github.com/Mouse-Imaging-Centre/fastcell'],
      packages=find_packages(),
      scripts=['saddle_reconstruction/saddle_reconstruct.py',
               'convert_CT_image.py',
               'Snakefile',
               'crop_to_brain.py',
               'mri_python/mri_recon.py',
               'mri_python/fse3dmice_recon.py',
               'tissue_vision/TVBM.py',
               'tissue_vision/TV_minc_recon.py',
               'tissue_vision/TV_slice_recon.py',
               'tissue_vision/TV_stitch.py',
               'tissue_vision/stacks_to_volume.py',
               'tissue_vision/MIP_first.py',
               ],
      )
