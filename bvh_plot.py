#!/usr/bin/env python3
'''Open file begin reading until encounters ROOT, JOINT, or ^MOTION
On ROOT or JOINT, see if next word matches passed in name.
Continue until CHANNELS.  If ROOT, JOINT, or MOTION before CHANNELS, abort.
If joint name matched, get #channels, continue on to ^MOTION  if name doesn't
match, add # after channels to channel count.

Once in motion, if name found: read each line, spit out the relevant channels.
else done.'''

import sys
import argparse
import copy
from tools.bvh import BVH
from tools.glplot import Plot

def main(args):
    '''Plot BVH files and animate them'''
    parser = argparse.ArgumentParser( prog='bvh_plot',
                 description='Load, display, and play the passed BVH.')
    parser.add_argument( 'bvh', help='The BVH file to load' )
    parser.add_argument( '-d','--max_depth',
                        type=int,
                        default=None,
                        help='Max depth of child joints to load.' )
    parser.add_argument( '-z','--zero_frame', dest='zero_frame',
                         default=False,
                         action='store_true',
                         help='Use the zero frame as resting pose')

    args = parser.parse_args()

    bvh = BVH( args.bvh, args.max_depth )

    skel = copy.deepcopy(bvh.skeleton)
    skel.set_unit_scale_factor()
    plot = Plot( skel, args.bvh )
    plot.activate()

if __name__ == "__main__":
    main( sys.argv )
