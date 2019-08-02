#!/usr/bin/env python3
import os

import pandas as pd

from pydpiper.core.stages import Stages, Result
from pydpiper.execution.application import mk_application
from pydpiper.core.files import FileAtom
from pydpiper.minc.files import MincAtom
from pydpiper.minc.registration import autocrop, create_quality_control_images

from tissue_vision.arguments import deep_segment_parser, stacks_to_volume_parser, autocrop_parser

from tissue_vision.reconstruction import TV_stitch_wrap, deep_segment, stacks_to_volume, \
    antsRegistration, get_like, tif_to_minc, get_through_plane_xfm, concat_xfm, mincmath, get_brains, Brain



def tv_recon_pipeline(options):
    output_dir = options.application.output_directory
    pipeline_name = options.application.pipeline_name

    s = Stages()

    brains = get_brains(options.application) # List(Brain,...)

    # Hold results obtained in the loop
    all_anatomical_pad_results = []
    all_count_pad_results = []
    reconstructed_mincs = []
    all_count_resampled = []
    all_atlas_resampled = []

#############################
# Step 2: Run deep_segment.py
#############################
    for brain in brains:
        anatomical = options.deep_segment.anatomical_name
        count = options.deep_segment.count_name

        brain.ds_directory = os.path.join(output_dir, pipeline_name + "_deep_segmentation", brain.name)

        outlines = []
        anatomicals = []
        counts = []

        for z in range(brain.z_start, brain.z_end+1):
            brain.slice_outline = FileAtom(
                os.path.join(brain.ds_directory, brain.name + "_Z%04d_outline.tiff" % z))
            brain.slice_anatomical = FileAtom(
                os.path.join(brain.ds_directory, brain.name + "_Z%04d_" % z + anatomical + ".tiff"))
            brain.slice_count = FileAtom(
                os.path.join(brain.ds_directory, brain.name + "_Z%04d_" % z + count + ".tiff"))
            outlines.append(brain.slice_outline)
            anatomicals.append(brain.slice_anatomical)
            counts.append(brain.slice_count)

        deep_segment_result = s.defer(deep_segment(stitched = stitched,
                                                   deep_segment_pipeline = FileAtom(options.deep_segment.deep_segment_pipeline),
                                                   anatomicals = anatomicals,
                                                   counts = counts,
                                                   Zstart = brain.z_start,
                                                   Zend = brain.z_end,
                                                   output_dir = output_dir,
                                                   temp_dir = options.deep_segment.temp_dir
                                        ))

#############################
# Step 3: Run stacks_to_volume.py
#############################
        anatomical_volume = MincAtom(os.path.join(output_dir, pipeline_name + "_stacked",
                                                  brain.name + "_" + anatomical + "_stacked.mnc"),
                                 output_sub_dir=os.path.join(output_dir, pipeline_name + "_stacked"))
        count_volume = MincAtom(os.path.join(output_dir, pipeline_name + "_stacked",
                                      brain.name + "_" + count + "_stacked.mnc"),
                                 output_sub_dir=os.path.join(output_dir, pipeline_name + "_stacked"))

        if not brain.z_section:
            anatomical_slices_to_volume_results = s.defer(stacks_to_volume(
                slices = anatomicals,
                volume = anatomical_volume,
                stacks_to_volume_options=options.stacks_to_volume,
                uniform_sum=False,
                z_resolution=brain.z_resolution,
                output_dir=output_dir
                ))

            count_slices_to_volume_results = s.defer(stacks_to_volume(
                slices = counts,
                volume = count_volume,
                stacks_to_volume_options=options.stacks_to_volume,
                z_resolution=brain.z_resolution,
                uniform_sum = True,
                output_dir=output_dir
                ))

        # if brain.z_section:
        #
        #     anatomical_volume_1 = MincAtom(os.path.join(output_dir, pipeline_name + "_stacked",
        #                                           brain.name + "_" + anatomical + "_stacked_1.mnc"),
        #                          output_sub_dir=os.path.join(output_dir, pipeline_name + "_stacked"))
        #     anatomical_slices_to_volume_results = s.defer(stacks_to_volume(
        #         slices=anatomicals[0 : brain.z_section - brain.z_start],
        #         volume=anatomical_volume_1,
        #         stacks_to_volume_options=options.stacks_to_volume,
        #         uniform_sum=False,
        #         z_resolution=brain.z_resolution,
        #         output_dir=output_dir
        #     ))
        #
        #     anatomical_volume_2 = MincAtom(os.path.join(output_dir, pipeline_name + "_stacked",
        #                                           brain.name + "_" + anatomical + "_stacked_2.mnc"),
        #                          output_sub_dir=os.path.join(output_dir, pipeline_name + "_stacked"))
        #     anatomical_slices_to_volume_results = s.defer(stacks_to_volume(
        #         slices=anatomicals[brain.z_section - brain.z_start:brain.z_end-1],
        #         volume=anatomical_volume_2,
        #         stacks_to_volume_options=options.stacks_to_volume,
        #         uniform_sum=False,
        #         z_resolution=brain.z_resolution,
        #         output_dir=output_dir
        #     ))
        #
        #     count_volume_1 = MincAtom(os.path.join(output_dir, pipeline_name + "_stacked",
        #                                           brain.name + "_" + count + "_stacked_1.mnc"),
        #                          output_sub_dir=os.path.join(output_dir, pipeline_name + "_stacked"))
        #     count_slices_to_volume_results = s.defer(stacks_to_volume(
        #         slices=counts[0 : brain.z_section - brain.z_start],
        #         volume=count_volume_1,
        #         stacks_to_volume_options=options.stacks_to_volume,
        #         z_resolution=brain.z_resolution,
        #         uniform_sum=True,
        #         output_dir=output_dir
        #     ))
        #
        #     count_volume_2 = MincAtom(os.path.join(output_dir, pipeline_name + "_stacked",
        #                                           brain.name + "_" + count + "_stacked_2.mnc"),
        #                          output_sub_dir=os.path.join(output_dir, pipeline_name + "_stacked"))
        #     count_slices_to_volume_results = s.defer(stacks_to_volume(
        #         slices=counts[brain.z_section - brain.z_start:brain.z_end-1],
        #         volume=count_volume_2,
        #         stacks_to_volume_options=options.stacks_to_volume,
        #         z_resolution=brain.z_resolution,
        #         uniform_sum=True,
        #         output_dir=output_dir
        #     ))
        #
        #     #create minc slices for registration
        #     fixed_minc = s.defer(tif_to_minc(
        #         tif=anatomicals[brain.z_section - brain.z_start - 1],
        #         volume=MincAtom(anatomicals[brain.z_section - brain.z_start - 1].path.replace("tiff","mnc"),
        #                          output_sub_dir=os.path.join(output_dir, pipeline_name + "_stacked")),
        #         stacks_to_volume_options=options.stacks_to_volume,
        #         z_resolution=brain.z_resolution,
        #         output_dir=output_dir))
        #     moving_minc = s.defer(tif_to_minc(
        #         tif=anatomicals[brain.z_section - brain.z_start],
        #         volume=MincAtom(anatomicals[brain.z_section - brain.z_start].path.replace("tiff","mnc"),
        #                          output_sub_dir=os.path.join(output_dir, pipeline_name + "_stacked")),
        #         stacks_to_volume_options=options.stacks_to_volume,
        #         z_resolution=brain.z_resolution,
        #         output_dir=output_dir))
        #
        #     #create in-plane transform
        #     in_plane_transform = FileAtom(os.path.join(output_dir, pipeline_name + "_stacked",
        #                                           brain.name + "0_GenericAffine.xfm"))
        #     s.defer(antsRegistration(fixed = fixed_minc,
        #                              moving = moving_minc,
        #                              transform = in_plane_transform,
        #                              output_dir=output_dir))
        #
        #     #create through-plane transform
        #     through_plane_xfm = FileAtom(os.path.join(output_dir, pipeline_name + "_stacked",
        #                                           brain.name + "_through_plane.xfm"))
        #     s.defer(get_through_plane_xfm(img = anatomical_volume_1,
        #                                   xfm = through_plane_xfm,
        #                                   output_dir = output_dir))
        #
        #     #concatenate the transforms
        #     xfm_concat = FileAtom(os.path.join(output_dir, pipeline_name + "_stacked",
        #                                           brain.name + "_concat.xfm"))
        #     s.defer(concat_xfm(xfms=[in_plane_transform, through_plane_xfm],
        #                        outxfm = xfm_concat,
        #                        output_dir = output_dir))
        #
        #     # create like file from first section
        #     anatomical_volume_1_like = MincAtom(os.path.join(output_dir, pipeline_name + "_stacked",
        #                                                  brain.name + "_" + anatomical + "_stacked_like.mnc"),
        #                          output_sub_dir=os.path.join(output_dir, pipeline_name + "_stacked"))
        #     s.defer(get_like(img=anatomical_volume_1, ref=anatomical_volume_2,
        #                      like=anatomical_volume_1_like, output_dir=output_dir))
        #     count_volume_1_like = MincAtom(os.path.join(output_dir, pipeline_name + "_stacked",
        #                                                  brain.name + "_" + count + "_stacked_like.mnc"),
        #                          output_sub_dir=os.path.join(output_dir, pipeline_name + "_stacked"))
        #     s.defer(get_like(img=count_volume_1, ref=count_volume_2,
        #                      like=count_volume_1_like, output_dir=output_dir))
        #
        #     #transform the second section
        #     anatomical_volume_2_transformed = MincAtom(os.path.join(output_dir, pipeline_name + "_stacked",
        #                                         brain.name + "_" + anatomical + "_stacked_2_transformed.mnc"),
        #                          output_sub_dir=os.path.join(output_dir, pipeline_name + "_stacked"))
        #     s.defer(mincresample(img = anatomical_volume_2,
        #                          xfm = xfm_concat,
        #                          like = anatomical_volume_1_like,
        #                          resampled = anatomical_volume_2_transformed,
        #                          output_dir = output_dir))
        #     count_volume_2_transformed = MincAtom(os.path.join(output_dir, pipeline_name + "_stacked",
        #                                             brain.name + "_" + count + "_stacked_2_transformed.mnc"),
        #                          output_sub_dir=os.path.join(output_dir, pipeline_name + "_stacked"))
        #     s.defer(mincresample(img=count_volume_2,
        #                          xfm=xfm_concat,
        #                          like=count_volume_1_like,
        #                          resampled=count_volume_2_transformed,
        #                          output_dir=output_dir))
        #
        #     #add the first section's like with the transformed second section
        #     s.defer(mincmath(imgs = [anatomical_volume_1_like, anatomical_volume_2_transformed],
        #                      result = anatomical_volume,
        #                      output_dir=output_dir))
        #     s.defer(mincmath(imgs=[count_volume_1_like, count_volume_2_transformed],
        #                      result=count_volume,
        #                      output_dir=output_dir))

#############################
# Step 4: Run autocrop to resample to isotropic
#############################
        anatomical_volume_isotropic = MincAtom(os.path.join(output_dir, pipeline_name + "_stacked",
                                                        brain.name + "_" + anatomical + "_stacked_isotropic.mnc"),
                                 output_sub_dir=os.path.join(output_dir, pipeline_name + "_stacked"))
        anatomical_volume_isotropic_results = s.defer(autocrop(
            isostep = options.stacks_to_volume.plane_resolution,
            img = anatomical_volume,
            autocropped = anatomical_volume_isotropic
        ))

        count_volume_isotropic = MincAtom(os.path.join(output_dir, pipeline_name + "_stacked",
                                                 brain.name + "_" + count + "_stacked_isotropic.mnc"),
                                 output_sub_dir=os.path.join(output_dir, pipeline_name + "_stacked"))
        count_volume_isotropic_results = s.defer(autocrop(
            isostep = options.stacks_to_volume.plane_resolution,
            img = count_volume,
            autocropped = count_volume_isotropic,
            nearest_neighbour = True
        ))

#############################
# Step 5: Run autocrop to pad the isotropic images
#############################
        x_pad = options.autocrop.x_pad
        y_pad = options.autocrop.y_pad
        z_pad = options.autocrop.z_pad

        anatomical_padded = MincAtom(os.path.join(output_dir, pipeline_name + "_stacked",
                                              brain.name + "_" + anatomical + "_padded.mnc"))
        anatomical_pad_results = s.defer(autocrop(
            img = anatomical_volume_isotropic,
            autocropped = anatomical_padded,
            x_pad = x_pad,
            y_pad = y_pad,
            z_pad = z_pad
        ))
        all_anatomical_pad_results.append(anatomical_pad_results)
        reconstructed_mincs.append(anatomical_pad_results)

        count_padded = MincAtom(os.path.join(output_dir, pipeline_name + "_stacked",
                                                        brain.name + "_" + count + "_padded.mnc"))
        count_resampled = MincAtom(os.path.join(output_dir, pipeline_name + "_resampled",
                                          brain.name + "_" + count + "_resampled.mnc"))
        atlas_resampled = MincAtom(os.path.join(output_dir, pipeline_name + "_resampled",
                                          "atlas_to_" + brain.name + "_resampled.mnc"))
        count_pad_results = s.defer(autocrop(
            img = count_volume_isotropic,
            autocropped = count_padded,
            x_pad = x_pad,
            y_pad = y_pad,
            z_pad = z_pad
        ))
        all_count_pad_results.append(count_pad_results)
        all_count_resampled.append(count_resampled)
        all_atlas_resampled.append(atlas_resampled)
        reconstructed_mincs.append(count_pad_results)

    csv_file = pd.read_csv(options.application.csv_file)
    reconstructed = pd.DataFrame({'brain_directory': [brain.brain_directory.path for brain in brains],
                                  'z_slices': [brain.z for brain in brains],
                                  'z_resolution': [brain.z_resolution for brain in brains],
                                  'anatomical_padded': [anatomical_padded.path for anatomical_padded in all_anatomical_pad_results],
                                  'count_padded': [count_padded.path for count_padded in all_count_pad_results]})

    reconstructed = csv_file.merge(reconstructed)
    reconstructed.to_csv("reconstructed.csv", index=False)
    #TODO overlay them
    # s.defer(create_quality_control_images(imgs=reconstructed_mincs, montage_dir = output_dir,
    #     montage_output=os.path.join(output_dir, pipeline_name + "_stacked", "reconstructed_montage"),
    #                                       message="reconstructed_mincs"))

    s.defer(create_quality_control_images(imgs=all_anatomical_pad_results, montage_dir=output_dir,
                                          montage_output=os.path.join(output_dir, pipeline_name + "_stacked",
                                                                      "%s_montage" % anatomical),
                                          message="%s_mincs" % anatomical))
    s.defer(create_quality_control_images(imgs=all_count_pad_results, montage_dir=output_dir,
                                          montage_output=os.path.join(output_dir, pipeline_name + "_stacked",
                                                                      "%s_montage" % count),
                                          auto_range=True,
                                          message="%s_mincs" % count))
    return Result(stages=s, output=())

tv_recon_application = mk_application(parsers = [deep_segment_parser,
                                                 stacks_to_volume_parser,
                                                 autocrop_parser],
                                      pipeline = tv_recon_pipeline)

if __name__ == "__main__":
    tv_recon_application()