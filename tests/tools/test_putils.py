import os
import sys
import math
import glm

from tools import putils

def test_degrees():
    '''While we can probably trust math.degrees()
       exercise type conversion.'''

    x=[math.pi, 0.0, math.pi/4.0]

    y = putils.degrees(x)

    assert isinstance(y, glm.vec3)
    assert y[0] == 180.0
    assert y[1] == 0.0
    assert y[2] == 45.0

def test_radians():
    '''Test radians and typecasting'''

    euler = glm.vec3( 180.0, 0.0, 45.0 )
    y = putils.radians(euler)

    assert isinstance(y, glm.vec3)
    assert abs(y[0] - math.pi) <= 0.0001
    assert y[1] == 0.0
    assert abs(y[2] - math.pi/4.0) <= 0.0001

def test_vec_to_str():
    '''This test isn't really very useful.'''
    
    euler = glm.vec3( 180.0, 0.0, 45.0 )
    assert putils.vec_to_str(euler) == "( 180.00, 0.00, 45.00 )"

def test_compare_vecs():
    '''A utility function mostly for testing'''
    assert putils.compare_vecs([], [])
    assert not putils.compare_vecs([], [1,2,3])
    assert putils.compare_vecs([1,2,3], [1,2,3])
    assert not putils.compare_vecs([3,2,1], [1,2,3])
    assert putils.compare_vecs( glm.vec3(1,2,3), glm.vec3(1,2,3) )
    assert not putils.compare_vecs( glm.vec3(0,0,0), glm.vec3(1,2,3) )
    assert putils.compare_vecs( [1,2,3], glm.vec3(1,2,3) )
    assert putils.compare_vecs( [1.0,2,3], glm.vec3(1.0,2,3) )
    assert putils.compare_vecs( glm.vec3(1.0,2,3), glm.vec3(1.0,2,3) )
    assert putils.compare_vecs( [1,2.0,3], glm.vec3(1.0,2,3) )
    assert putils.compare_vecs( glm.vec3(1,2.0,3), glm.vec3(1.0,2,3) )

def test_quat_to_euler():
    '''Verify the eulers generated match the inputs.'''

    eulers = [ glm.vec3( 0, 33.0, 0 ),
               glm.vec3( 0, 45.0, 0 ),
               glm.vec3( 0, 90.0, 0 ),
               glm.vec3( 0, 45.0, 45.0 ),
               glm.vec3( 0, 45.0, 33.0 )
             ]

    for euler in eulers:
        quat = glm.quat( putils.radians(euler) )
        assert putils.compare_vecs(putils.degrees( putils.quat_to_euler(quat) ), euler)

def test_make_up_vec():
    '''Super basic test'''
    assert putils.make_up_vec('x') == glm.vec3( 1, 0, 0 )
    assert putils.make_up_vec('X') == glm.vec3( 1, 0, 0 )
    assert putils.make_up_vec('potato') == None

def test_rotate_vector():
    '''Verify that points rotated by euler are the expected output'''
    '''This test presumes quat_to_euler test was successful and
       uses eulers for test values to make the test more human readable'''

    points = [ [ 1.0, 0, 0 ],
               [ 0.0, 1.0, 0 ], 
               [ 1.0, 1.0, 0 ]
             ]

    eulers = [ glm.vec3( 0, 180.0, 0 ),
               glm.vec3( 0, 90.0, 0 ),
               glm.vec3( 0, 45.0, 0 ),
               glm.vec3( 0, 22.5, 0 ),
             ]

    quats = []
    for euler in eulers:
        quats.append( glm.quat( putils.radians(euler) ) ) 

    #180
    npoint = putils.rotate_vector( points[0], quats[0] )
    assert putils.compare_vecs( npoint, glm.vec3( -1, 0, 0 ) )
    npoint = putils.rotate_vector( points[1], quats[0] )
    assert putils.compare_vecs( npoint, glm.vec3( 0, 1, 0 ) )
    npoint = putils.rotate_vector( points[2], quats[0] )
    assert putils.compare_vecs( npoint, glm.vec3( -1, 1, 0 ) )

    #90
    npoint = putils.rotate_vector( points[0], quats[1] )
    assert putils.compare_vecs( npoint, glm.vec3( 0, 0, 1 ) )
    npoint = putils.rotate_vector( points[1], quats[1] )
    assert putils.compare_vecs( npoint, glm.vec3( 0, 1, 0 ) )
    npoint = putils.rotate_vector( points[2], quats[1] )
    assert putils.compare_vecs( npoint, glm.vec3( 0, 1, 1 ) )

    #45
    half = math.sqrt(2)/2.0
    npoint = putils.rotate_vector( points[0], quats[2] )
    assert putils.compare_vecs( npoint, glm.vec3( half, 0, half ) )
    npoint = putils.rotate_vector( points[2], quats[2] )
    assert putils.compare_vecs( npoint, glm.vec3( half, 1, half ) )

    #22.5
    npoint = putils.rotate_vector( points[1], quats[3] )
    assert putils.compare_vecs( npoint, glm.vec3( 0, 1, 0 ) )
    


def test_shortest_arc():
    '''Shortest_arc is something like the reciprocal of 
       rotate_vector but can be a bit tricky as there may be multiple
       solutions'''

    half = math.sqrt(2)/2.0
    points = [ [ 1, 0, 0 ],
               [ half, 0, half ],
             ]
    
    #Verify directionality
    euler = putils.degrees( putils.quat_to_euler( \
                putils.shortest_arc( points[1], points[0] ) ) )
    assert putils.compare_vecs( euler, glm.vec3( 0, 45, 0 ) )

    euler = putils.degrees( putils.quat_to_euler( \
                putils.shortest_arc( points[0], points[1] ) ) )
    assert putils.compare_vecs( euler, glm.vec3( 0, -45, 0 ) )

    #An arbitary small rotation
    arbitrary = glm.vec3(0, 22, 0 )
    arbitrary_quat = glm.quat( putils.radians( arbitrary ) )
    npoint = putils.rotate_vector( points[0],  arbitrary_quat )

    euler = putils.degrees( putils.quat_to_euler( \
                putils.shortest_arc( npoint, points[0] ) ) )
    assert putils.compare_vecs( euler, arbitrary )
    
    #TODO add multi-axis tests.

def test_dir_to_quat():
    '''Given a direction and an up axis, get a quaternion.
       Once again using euler degrees for human readability.'''

    quat = putils.dir_to_quat( glm.vec3(1, 0, 0), 'x' )
    euler = putils.degrees( putils.quat_to_euler( quat ) )
    assert putils.compare_vecs( euler, [ 0, 90, 0 ] )

    quat = putils.dir_to_quat( glm.vec3(1, 0, -1), 'x' )
    euler = putils.degrees( putils.quat_to_euler( quat ) )
    assert putils.compare_vecs( euler, [ 0, 45, 90 ] )

def test_magnitude():
    '''Convenience function that's just a wrapper to glm.length'''

    x = math.sqrt(2)
    assert abs(putils.magnitude( glm.vec3(1,1,0) ) - x) <= 0.0001

def test_distance_3d():
    '''Simply a wrapper to magnitude for a non-axis start point'''

    assert putils.distance_3d( glm.vec3(1,2,3), glm.vec3(1,2,4) ) == 1.0

def test_clamp():
    '''Ensures a number fits within a rage eg -127 to + 127'''

    assert putils.clamp( 234, 127 ) == 127
    assert putils.clamp( -234, 127 ) == -127

