"""
utility functions
"""

import math

import glm

def degrees(euler:glm.vec3) -> glm.vec3:
    '''Given a vector of 3 presumed floats representing radians,
       return a glm.vec3 of degrees'''
    return glm.vec3(math.degrees(euler[0]), math.degrees(euler[1]), math.degrees(euler[2]))

def radians(euler:glm.vec3) ->glm.vec3:
    '''Given a vector of 3 presumed floats representing degrees,
       return a glm.vec3 of radians'''
    return glm.vec3(math.radians(euler[0]), math.radians(euler[1]), math.radians(euler[2]))

def vec_to_str(vec:glm.vec3) -> str:
    '''A debug function for formatting list[float,float,float] or glm.vec3
       as a string of the format: ( #.##, #.##, #.## )'''
    return f"( {vec[0]:.2f}, {vec[1]:.2f}, {vec[2]:.2f} )"

def compare_vecs( vec1:glm.vec3, vec2:glm.vec3 ) -> bool:
    '''Given two vectors, verify every item matches whether simple list
       or glm.vec3.  Also returns false if lengths don't match.  Herein,
       match is defined as 'close enough' since we're dealing with a loss
       of precision in floats'''

    len1 = len(vec1)
    len2 = len(vec2)

    if isinstance(vec1, glm.vec3):
        len1 = 3
    if isinstance(vec2, glm.vec3):
        len2 = 3

    #Mismatched array lengths
    if len1 != len2:
        return False

    #Empty v empty is ok!
    if len1 == 0:
        return True

    for i in range(0, len1):
        if abs( float(vec1[i]) - float(vec2[i]) ) > 0.0001:
            return False

    return True

def make_up_vec(up_axis : glm.vec3) -> glm.vec3:
    '''Passed x,y, or z, returns identity vector for the up axis.
        returns None of not a valid axis'''

    up_str = up_axis.lower()
    if up_str == 'x':
        return glm.vec3( 1, 0, 0 )
    if up_str == 'y':
        return glm.vec3( 0, 1, 0 )
    if up_str == 'z':
        return glm.vec3( 0, 0, 1 )
    return None

def quat_to_euler(quat : glm.quat) -> glm.vec3:
    '''Coverts a quaternion to an Euler in XYZ order.  Returns as radians'''
    return glm.eulerAngles(glm.normalize(quat))

def rotate_vector(vec : glm.vec3, quat : glm.quat) -> glm.vec3:
    '''Rotate vector by a quaternion.  Assumes glm rot and quat'''
    return vec * quat

def shortest_arc(point_a : glm.vec3, point_b : glm.vec3) -> glm.quat:
    '''Given the vectors a and b return a quaternion representing the shortest arc between'''

    result = glm.quat(1.0,0.0,0.0,0.0)

    ab_dot = glm.dot(point_a,point_b)  #dot product
    cross = glm.cross(point_a,point_b) #cross product
    cross_sqr = glm.dot(cross,cross)  #Squared length of the crossproduct

    #Test if args have sufficient magnitude
    if ab_dot*ab_dot+cross_sqr != 0.0:
        #Test if the arguments are (anti)parllel
        if cross_sqr > 0.0:
            sqr = math.sqrt(ab_dot * ab_dot + cross_sqr) + ab_dot

            #Inverted magnitude of the quaternion.
            mag = 1.0 / math.sqrt(cross_sqr + sqr * sqr)
            result = glm.quat(sqr * mag, cross[0] * mag, cross[1] * mag, cross[2] * mag)
        elif ab_dot < 0.0: #Test if the angle is > than PI/2 (anti parallel)
            #The arguments are anti-parallel, we have to choose an axis
            point_c = point_a - point_b

            #The length is projected on the XY plane
            mag = math.sqrt( point_c[0] * point_c[0] + point_c[1] * point_c[1] )

            #F32 magnitude threshhold. Probably not needed.
            f32_mag_thresh = 0.0000001
            if mag > f32_mag_thresh:
                result = glm.quat( 0.0, -point_c[1]/mag, point_c[0]/mag, 0.0 )
            else:
                result = glm.quat( 0.0, 1.0, 0.0, 0.0 )
    return result

def dir_to_quat(dir_vec : glm.vec3 , up_str : str) -> glm.quat:
    '''Passed a vec3 direction and a character x,y, or z to designate up axis
        Returns quaternion representing angle in direction of.'''

    origin = glm.vec3(0,0,0)
    mat = glm.lookAt(origin, glm.normalize(dir_vec), make_up_vec(up_str))
    return glm.quat(mat)

def magnitude(vec : glm.vec3) -> float:
    '''Returns magnitude of a vector'''
    return glm.length(glm.vec3(vec))

def distance_3d(vec1 : glm.vec3, vec2 : glm.vec3) -> float:
    '''vec1 and vec2 are presumed to be points, get direction
       from vec1 to vec2 and return the distance between them.'''
    return magnitude(vec1 - vec2)

def clamp(num : float, lim : float) -> float:
    '''  Clamps number to +- the passed value.'''

    num = min(num, lim)
    nlim = -1.0 * lim
    num = max(num, nlim)
    return num
