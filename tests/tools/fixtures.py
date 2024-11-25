'''Some fixtures to make testing more convenient'''

import os
import sys
import math
import glm
import pytest

from tools import putils
from tools.skeleton import KeyFrame, Joint, Skeleton

def add_keyframe(joint, iteration):
    '''Add rotation joints to every keyframe.'''

    #Frame 0 rotates 5 deg around x, Frame 1 10 deg around Y and so on.
    axis = iteration % 3
    euler = glm.vec3(0,0,0)
    euler[axis] = (iteration+1) * 5
    quat = glm.quat( putils.radians ( euler ) )

    keyframe = KeyFrame()
    keyframe.rotation = quat
    joint.frames.append(keyframe)

    for child in joint.children:
        add_keyframe(child, iteration)

@pytest.fixture(scope='function')
def joint_setup(request):
    '''Set up a dummy joint hierarchy for testing.  This will have a structure of
        root
            child1
                grandchild
            child2
    '''

    #Setup the root joint
    root = Joint( 'root', None )
    root.position = glm.vec3( 1.0, 0, 0 )

    #Give the root a child
    child1 = Joint ( 'child1', root )
    child1.position = glm.vec3( 1.0, 0, 0 )
    root.children.append( child1 )

    #Give the child a sibling
    child2 = Joint ( 'child2', root )
    child2.position = glm.vec3( 0.5 , 0, 0 )
    root.children.append( child2 )

    #Give the first child a child of its own
    gchild = Joint ( 'grandchild', child1 )
    gchild.position = glm.vec3( 0, 1.0, 0 )
    child1.children.append( gchild )

    #Generate some keyframes.
    for i in range(0,5):
        add_keyframe(root, i)

    #def joint_teardown():
    #   pass
    #request.addfinalizer(joint_teardown)

    return root

def recursively_get_joint_names(joint):
    '''Recurses children, returning a dict of joints'''

    return_dict = { joint.alias : joint }
    for child in joint.children:
        return_dict.update(recursively_get_joint_names(child))

    return return_dict


@pytest.fixture(scope='function')
def skeleton_setup(joint_setup, request):
    '''Set up a skeleton using the joint fixture'''

    skel = Skeleton()

    root = joint_setup
    skel.root_name = root.alias
    skel.joints  = recursively_get_joint_names(root)

    return skel
