#!/usr/bin/env python3
'''Loads a BVH file. Takes a parameter for joint outputs the parent and world positions
for the joint, the resting rotation (if applicable) and the 1st frame'''

import sys
import argparse
import copy
from tools.bvh import BVH
from tools  import putils

def main(args):
    '''Plot BVH files and animate them'''
    parser = argparse.ArgumentParser( prog='bvh_extract',
                 description='Load, display, and play the passed BVH.')
    parser.add_argument( 'bvh', help='The BVH file to load' )
    parser.add_argument( 'joint', help='Joint to extract' )

    args = parser.parse_args()

    bvh = BVH( args.bvh, None )

    skel = copy.deepcopy(bvh.skeleton)
    skel.set_unit_scale_factor()

    #Bail out if joint not found.
    if args.joint not in skel.joints:
        print(f'Joint {args.joint} not found in skeleton of {args.bvh}')
        return

    joint = skel.joints[args.joint]
    resting_str = 'Resting:     <NONE>   '
    if joint.resting is not None:
        euler = putils.degrees(putils.quat_to_euler(joint.resting.rotation))
        resting_str = f'Resting: {putils.vec_to_str(euler)}'

    euler = putils.degrees(putils.quat_to_euler(joint.frames[0].rotation))

    print(f'Pos: {putils.vec_to_str(joint.position)} WPos: {putils.vec_to_str(joint.w_position)} {resting_str} Frame1: {putils.vec_to_str(euler)}')

    

if __name__ == "__main__":
    main( sys.argv )
