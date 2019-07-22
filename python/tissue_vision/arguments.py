from configargparse import ArgParser, Namespace
from pydpiper.core.util import NamedTuple
from pydpiper.core.arguments import BaseParser, AnnotatedParser



#############################################

def _mk_TV_stitch_parser():
    p = ArgParser(add_help=False)
    # p.add_argument("--skip-tile-match", dest="skip_tile_match",
    #                action="store_true", default=False,
    #                help="Skip tile matching and place tiles on perfect grid (for debugging)")
    p.add_argument("--scale-output", dest="scale_output",
                   type=int,
                   default=None,  # TODO raise a warning when this isn't specified
                   help="Multiply slice images by this value before saving to file")
    # p.add_argument("--Zstart", dest="Zstart",
    #                type=int,
    #                default=None,
    #                help="Z start index")
    # p.add_argument("--Zend", dest="Zend",
    #                type=int,
    #                default=None,
    #                help="Z end index")
    # p.add_argument("--Ystart", dest="Ystart",
    #                type=int,
    #                default=None,
    #                help="Y start index")
    # p.add_argument("--Yend", dest="Yend",
    #                type=int,
    #                default=None,
    #                help="Y end index")
    # p.add_argument("--Xstart", dest="Xstart",
    #                type=int,
    #                default=None,
    #                help="X start index")
    # p.add_argument("--Xend", dest="Xend",
    #                type=int,
    #                default=None,
    #                help="X end index")
    # p.add_argument("--brain", dest="brain",
    #                type=str,
    #                default=None,
    #                help="Name of the brain")
    # p.add_argument("--no-gradient-image", dest="no_gradient_image",
    #                action="store_true", default=False,
    #                help="Do not use gradient and raw image combined for correlation")
    p.add_argument("--keep-stitch-tmp", dest="keep_tmp",
                   action="store_true", default=False,
                   help="Keep temporary files from TV_stitch.")
    p.add_argument("--save-positions-file", dest="save_positions_file",
                   action="store_true", default=False,
                   help="Save the final positions to file (for subsequent use with --use-positions-file)")
    # p.add_argument("--use-positions-file", dest="use_positions_file",
    #                type=str,
    #                default=None,
    #                help="Use an existing positions file instead of generation positions from the input")
    # p.add_argument("--overlapx", dest="overlapx",
    #                type=int,
    #                default=None,
    #                help="%% tile overlap in x direction")
    # p.add_argument("--overlapy", dest="overlapy",
    #                type=int,
    #                default=None,
    #                help="%% tile overlap in y direction")
    # p.add_argument("--channel", dest="channel",
    #                type=str,
    #                default=None,
    #                help="channel to stitch")
    # p.add_argument("--Zref", dest="Zref",
    #                type=int,
    #                default=None,
    #                help="Z plane reference during tiling")
    # p.add_argument("--inormalize-piezo-stack", dest="inormalize_piezo_stack",
    #                action="store_true", default=False,
    #                help="Intensity normalize piezo stacked images")
    # p.add_argument("--fast-piezo", dest="fast_piezo",
    #                action="store_true", default=False,
    #                help="Piezo stack tiles are stored consecutively instead of plane-wise")
    # p.add_argument("--short-int", dest="short_int",
    #                action="store_true", default=False,
    #                help="Write short int data to file instead of byte")
    # p.add_argument("--use-imagemagick", dest="use_imagemagick",
    #                action="store_true", default=False,
    #                help="Use imagemagick for preprocessing (old behaviour)")

    return p

TV_stitch_parser = AnnotatedParser(parser=BaseParser(_mk_TV_stitch_parser(), "TV_stitch"),
                                   namespace="TV_stitch")

#############################################

def _mk_deep_segment_parser():
    p = ArgParser(add_help=False)
    p.add_argument("--temp-dir", dest="temp_dir", type=str, default=None)
    p.add_argument("--deep-segment-pipeline", dest="deep_segment_pipeline",
                   type=str,
                   default=None,
                   help="This is the segmentation pipeline")
    p.add_argument("--anatomical-name", dest="anatomical_name",
                   type=str,
                   default="cropped",
                   help="Specify the name of the anatomical images outputted by deep_segment.py")
    p.add_argument("--count-name", dest="count_name",
                   type=str,
                   default="count",
                   help="Specify the name of the count images outputted by deep_segment.py")
    p.add_argument("--segment-name", dest="segment_name",
                   type=str,
                   default=None,
                   help="Specify the name of the segmentation images outputted by deep_segment.py")
    p.add_argument("--outline-name", dest="outline_name",
                   type=str,
                   default=None,
                   help="Specify the name of the outline images outputted by deep_segment.py")
    return p

deep_segment_parser = AnnotatedParser(parser=BaseParser(_mk_deep_segment_parser(), "deep_segment"),
                                      namespace="deep_segment")

#############################################

def _mk_stacks_to_volume_parser():
    p = ArgParser(add_help=False)
    p.add_argument("--input-resolution", dest="input_resolution",
                   type=float,
                   default=0.00137,
                   help="The raw in-plane resolution of the tiles in mm. [default = %(default)s]")
    p.add_argument("--plane-resolution", dest="plane_resolution",
                   type=float,
                   default=None,
                   help="The output in-plane resolution of the tiles in mm")
    return p

stacks_to_volume_parser = AnnotatedParser(parser=BaseParser(_mk_stacks_to_volume_parser(), "stacks_to_volume"),
                                      namespace="stacks_to_volume")

#############################################

def _mk_autocrop_parser():
    p = ArgParser(add_help=False)
    p.add_argument("--x-pad", dest="x_pad",
                   type=str,
                   default='0,0',
                   help="Padding in mm will be added to each sides. [default = %(default)s]")
    p.add_argument("--y-pad", dest="y_pad",
                   type=str,
                   default='0,0',
                   help="Padding in mm will be added to each sides. [default = %(default)s]")
    p.add_argument("--z-pad", dest="z_pad",
                   type=str,
                   default='0,0',
                   help="Padding in mm will be added to each side. [default = %(default)s]")
    return p

autocrop_parser = AnnotatedParser(parser=BaseParser(_mk_autocrop_parser(), "autocrop"), namespace="autocrop")

def _mk_consensus_to_atlas_parser():
    p = ArgParser(add_help=False)
    p.add_argument("--atlas-target", dest="atlas_target",
                   type=str,
                   default=None,
                   help="Register the consensus average to the ABI Atlas")
    p.add_argument("--atlas-target-label", dest="atlas_target_label",
                   type=str,
                   default=None,
                   help="Register the consensus average to the ABI Atlas")
    p.add_argument("--atlas-target-mask", dest="atlas_target_mask",
                   type=str,
                   default=None,
                   help="Register the consensus average to the ABI Atlas")
    return p

consensus_to_atlas_parser = AnnotatedParser(parser=BaseParser(_mk_consensus_to_atlas_parser(), 'consensus_to_atlas'),
                                            namespace='consensus_to_atlas')

