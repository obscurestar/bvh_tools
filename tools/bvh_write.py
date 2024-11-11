'''A simple library for parsing BVH files.'''

import copy
import glm
from tools import putils
from tools.skeleton import KeyFrame, Joint, Skeleton

def vec_to_str(vec):
    '''Turns a glm.vec3 into a string complaint with BVH format.
        assumes x y z order'''
    return str("%.7f %.7f %.7f" % (vec[0], vec[1], vec[2]))

def quat_to_str(quat):
    '''Turns a glm.quat into a string complaint with BVH format.
        assumes x y z order and degrees'''
    return vec_to_str( putils.degrees( putils.quat_to_euler(quat) ) )

def write_joint( fptr, joint, rotation, indent=0):
    '''Writes the joint data'''

    is_root = False
    tag = 'JOINT'
    if indent == 0:
        is_root = True
        tag = 'ROOT'

    p_tabs = '\t' * indent
    fptr.write(f'{p_tabs}{tag} {joint.alias}\n')
    fptr.write(p_tabs + '{\n')
    c_indent = indent + 1
    tabs = '\t' * c_indent

    #Get rid of the resting pos
    child_rot = rotation
    if joint.resting is not None:
        child_rot = glm.conjugate(joint.resting.rotation) * rotation
        joint.position = joint.position * rotation

    fptr.write(f'{tabs}OFFSET {vec_to_str(joint.position)}\n')
    if is_root:
        fptr.write(f'{tabs}CHANNELS 6 Xposition Yposition Zposition Xrotation Yrotation Zrotation\n')
    else:
        fptr.write(f'{tabs}CHANNELS 3 Xrotation Yrotation Zrotation\n')

    if len(joint.children) > 0:
        for child in joint.children:
            write_joint( fptr, child, child_rot, c_indent )
    else:
        fptr.write(f'{tabs}End Site\n{tabs}')
        fptr.write('{\n\t')
        fptr.write(f'{tabs}OFFSET {vec_to_str(joint.end_position)}\n{tabs}')
        fptr.write('}\n')

    #Close up.
    fptr.write(p_tabs + '}\n')
    
def recurse_channels(joint, frame_no, fptr):
    '''Recurse through joints, writing their rotation to the keyframe data'''

    rotation = joint.frames[frame_no].rotation

    #TODO fixme
    if joint.resting is not None:
        #rotation = glm.conjugate(joint.resting.rotation) * rotation
        rotation = joint.resting.rotation * rotation

    fptr.write(f' {quat_to_str(rotation)}')
    for child in joint.children:
        recurse_channels(child, frame_no, fptr)

def bvh_write( skeleton, filename):
    '''Writes a BVH file in a single format with no options.  Very basic.'''

    root = skeleton.get_root()

    with open( filename, 'w', encoding='utf-8' ) as fptr:
        fptr.write('HIERARCHY\n')
        rotation = glm.quat(glm.vec3(0,0,0))
        write_joint( fptr, root, rotation )
        fptr.write('MOTION\n')

        num_frames = skeleton.num_frames
        if skeleton.has_resting:
            num_frames = num_frames - 1 
        fptr.write(f'Frames: {num_frames}\n')
        fptr.write(f'Frame Time: {float(skeleton.frame_rate/1000.0)}\n')

        #Loop through frames
        for frame_no in range(1,len(root.frames)):
            fptr.write(f'{vec_to_str(root.frames[frame_no].position)}')
            recurse_channels(root, frame_no, fptr)
            fptr.write('\n')

