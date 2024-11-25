'''This suite of tests cover the Skeleton and supporting classes.'''

import os
import sys
import math
import glm
import pytest

from tools import putils
from tools.skeleton import Joint, Skeleton

from tests.tools.fixtures import joint_setup, skeleton_setup

#Tests related to the Joints class
def test_joint_setup(joint_setup):
    '''Make sure our fixture works as a smoke test.'''
    root = joint_setup

    assert isinstance(root, Joint)
    assert len(root.children) == 2
    assert len(root.children[0].children) == 1
    assert len(root.children[1].children) == 0
    assert root.children[0].parent == root
    assert len(root.frames) > 0

def test_extract_resting_pos(joint_setup):
    '''The resting pose is the 0th frame prior to extraction'''

    zeroth = glm.vec3(5,0,0)
    first = glm.vec3(0,10,0)

    root = joint_setup
    num_frames = len(root.frames)

    assert putils.compare_vecs(putils.degrees( putils.quat_to_euler(root.frames[0].rotation) ), zeroth)
    assert putils.compare_vecs(putils.degrees( putils.quat_to_euler(root.frames[1].rotation) ), first)
    assert root.resting is None

    root.extract_resting_pose()
    assert putils.compare_vecs(putils.degrees( putils.quat_to_euler(root.frames[0].rotation) ), first)
    assert root.resting is not None
    assert putils.compare_vecs(putils.degrees( putils.quat_to_euler(root.resting.rotation) ), zeroth)

    with pytest.raises(Exception) as excinfo:
        root.extract_resting_pose()

    assert str(excinfo.value) == 'Resting frame extraction failed.  Resting frame already present.'


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

#Tests related to the Skeleton class
def test_skeleton(skeleton_setup):
    '''Most of the skeleton class is just a wrapper to the Joints class
       with a bit of decorator data at the toplevel, but in particular,
       let's make sure that the root gets set up and the joint dictionary 
       manipulates the same instance that the hierarchial joint structure does.'''

    skel = skeleton_setup

    #Test getting the root.
    root = skel.get_root()
    assert isinstance( root, Joint )

    #Verify the associations.
    child0 = root.children[0]   #Get the first child of root

    assert isinstance( child0, Joint )
    assert child0 != root       #Sanity check since these are of same type
    assert child0 == skel.joints[child0.alias]  #Look up child in skel by alias


def test_extract_resting_pose(skeleton_setup):
    '''Most of this is handled in testing of joint's extract_resting_pose
    but let's make sure things get set and exception bubbles up 
    if triggered.'''

    skel = skeleton_setup

    root = skel.get_root()

    assert not skel.has_resting
    assert root.resting is None
    skel.extract_resting_pose()
    assert skel.has_resting
    assert root.resting is not None

    with pytest.raises(Exception) as excinfo:
        skel.extract_resting_pose()

    assert str(excinfo.value) == 'Resting frame extraction failed.  Resting frame already present.'
