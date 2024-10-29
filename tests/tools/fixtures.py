'''Some fixtures to make testing more convenient'''

import os
import sys
import math
import glm
import pytest

from tools import putils
from tools.skeleton import Joint
from tools.skeleton import Skeleton

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
