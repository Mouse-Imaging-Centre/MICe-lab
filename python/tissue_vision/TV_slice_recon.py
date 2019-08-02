#!/usr/bin/env python3
import os, re
from typing import  Union, Dict

import pandas as pd

from pydpiper.core.stages import Stages, Result
from pydpiper.core.files import FileAtom
from pydpiper.execution.application import mk_application

from tissue_vision.reconstruction import TV_stitch_wrap
from tissue_vision.arguments import TV_stitch_parser

def read_mosaic(file: str) -> Dict:
    with open(file) as f: mosaic = f.read()
    keys = re.findall(r"(?<=\n).*?(?=:)", "\n" + mosaic)
    values = re.findall(r"(?<=:).*?(?=\n)", mosaic + "\n")
    return dict(zip(keys, values))

def tv_slice_recon_pipeline(options):
    output_dir = options.application.output_directory
    pipeline_name = options.application.pipeline_name

    s = Stages()

    df = pd.read_csv(options.application.csv_file)
    brains = get_brains(options.application)  # List(Brain,...)
#############################
# Step 1: Run TV_stitch.py
#############################
    for brain in brains:
        slice_directory = os.path.join(output_dir, pipeline_name + "_stitched", brain.name)

        stitched = []
        brain.x, brain.y, brain.z, brain.z_resolution = \
            get_params(os.path.join(brain.brain_directory.path, brain.name))

        #accounting for errors in tile acquisition
        brain.z_start = 1 if pd.isna(brain.z_start) else int(brain.z_start)
        brain.z_end = brain.z if pd.isna(brain.z_end) else int(brain.z_end)

        for z in range (brain.z_start, brain.z_end + 1):
            brain.slice_stitched = FileAtom(os.path.join(slice_directory, brain.name + "_Z%04d.tif" % z))
            stitched.append(brain.slice_stitched)

        if not brain.z_section:
            TV_stitch_result = s.defer(TV_stitch_wrap(brain_directory = brain.brain_directory,
                                                    brain_name = brain.name,
                                                    stitched = stitched,
                                                    TV_stitch_options = options.TV_stitch,
                                                    Zstart=brain.z_start,
                                                    Zend=brain.z_end,
                                                    output_dir = output_dir
                                                    ))
    return Result(stages=s, output=())

tv_slice_recon_application = mk_application(parsers=[TV_stitch_parser],
                                      pipeline=tv_slice_recon_pipeline)

if __name__ == "__main__":
    tv_slice_recon_application()