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
