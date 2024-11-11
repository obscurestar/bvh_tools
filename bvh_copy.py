#!/usr/bin/env python3
'''Reads a BVH file and writes it back out.  The write process will
   assert XYZ position and rotation order, elminate resting pose,
   and change joint names to their preferred alias.'''

import sys
import argparse
import copy
from tools.bvh import BVH
from tools.bvh_write import bvh_write

def main(args):
    '''Plot BVH files and animate them'''
    parser = argparse.ArgumentParser( prog='bvh_plot',
                 description='Load, display, and play the passed BVH.')
    parser.add_argument( 'bvh', help='The Input BVH file to load' )
    parser.add_argument( 'output', help='The Output BVH file name.' )

    args = parser.parse_args()

    bvh = BVH( args.bvh, None )

    skel = copy.deepcopy(bvh.skeleton)
    #skel.set_unit_scale_factor()
    bvh_write( skel, args.output )

if __name__ == "__main__":
    main( sys.argv )
