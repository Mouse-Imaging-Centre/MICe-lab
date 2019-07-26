#!/usr/bin/env python3
import os

import pandas as pd

from pydpiper.core.stages import Stages, Result
from pydpiper.core.files import FileAtom
from pydpiper.execution.application import mk_application

from tissue_vision.reconstruction import get_brains, Brain, TV_stitch_wrap
from tissue_vision.TV_stitch import get_params
from tissue_vision.arguments import TV_stitch_parser

def tv_slice_recon_pipeline(options):
    output_dir = options.application.output_directory
    pipeline_name = options.application.pipeline_name

    s = Stages()

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
        brain.z_section = None if pd.isna(brain.z_section) else int(brain.z_section)

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

        if brain.z_section:
            TV_stitch_result = s.defer(TV_stitch_wrap(brain_directory=brain.brain_directory,
                                                      brain_name=brain.name,
                                                      stitched=stitched[0 : brain.z_section - brain.z_start],
                                                      TV_stitch_options=options.TV_stitch,
                                                      Zstart=brain.z_start,
                                                      Zend=brain.z_section - 1,
                                                      output_dir=output_dir
                                                      ))

            TV_stitch_result = s.defer(TV_stitch_wrap(brain_directory=brain.brain_directory,
                                                      brain_name=brain.name,
                                                      stitched=stitched[brain.z_section - brain.z_start:brain.z_end-1],
                                                      TV_stitch_options=options.TV_stitch,
                                                      Zstart=brain.z_section,
                                                      Zend=brain.z_end,
                                                      output_dir=output_dir
                                                      ))
    return Result(stages=s, output=())

tv_slice_recon_application = mk_application(parsers=[TV_stitch_parser],
                                      pipeline=tv_slice_recon_pipeline)

if __name__ == "__main__":
    tv_slice_recon_application()