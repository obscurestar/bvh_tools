import os
import sys
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

