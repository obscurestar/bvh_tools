'''This suite of tests cover the Skeleton and supporting classes.'''

import os
import sys
import math
import glm
import pytest

from tools import putils
from tools.skeleton import Joint

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

def test_joint_setup(joint_setup):
    '''Make sure our fixture works as a smoke test.'''
    root = joint_setup

    assert isinstance(root, Joint)
    assert len(root.children) == 2
    assert len(root.children[0].children) == 1
    assert len(root.children[1].children) == 0
    assert root.children[0].parent == root

def test_fix_end_position(joint_setup):
    '''end positions are recursively set from joint positions.'''

    root = joint_setup
    root.fix_end_position()
    
    assert putils.compare_vecs( root.end_position, [ 0.75, 0, 0 ] )
    assert putils.compare_vecs( root.children[0].end_position, [ 0, 1, 0 ] )
    assert putils.compare_vecs( root.children[1].end_position, [ 0, 0, 0 ] )

def test_init_world_positions(joint_setup):
    '''World positions for joints are the combination of their parents positions.
       Since the root has no parent it will always be 0,0,0'''

    root = joint_setup
    root.init_world_position()

    assert putils.compare_vecs( root.w_position, [ 0, 0, 0 ] )
    assert putils.compare_vecs( root.children[0].w_position, [ 1, 0, 0 ] )
    assert putils.compare_vecs( root.children[1].w_position, [ 0.5, 0, 0 ] )
    assert putils.compare_vecs( root.children[0].children[0].w_position, \
                                [ 1, 1, 0 ] )

def test_compute_unit_scale(joint_setup):
    '''Unit scale is used for rendering and for mapping one skeleton to another'''

    root = joint_setup
    assert root.children[1].compute_unit_scale() == 0.5
    assert root.compute_unit_scale() == 3.0
