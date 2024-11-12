'''An OpenGL plotting tool for a skeleton'''
import sys
from platform import system as which_os
import glm
from OpenGL import GL
from OpenGL.GLU import gluLookAt
from OpenGL import GLUT

from tools.skeleton import Skeleton

class Window():
    '''A trivial class to contain all the window creation stuff'''

    def __init__( self, name, position, size ):
        self.name = name
        self.position = position
        self.size = size
        self.window = None

    def initialize( self ):
        '''Initialize OpenGL'''
        GLUT.glutInit()

        # Set display mode
        GLUT.glutInitDisplayMode(GLUT.GLUT_SINGLE | GLUT.GLUT_RGB)

        # Set size and position of window size
        GLUT.glutInitWindowSize( self.size[0], self.size[1] )
        GLUT.glutInitWindowPosition( self.position[0], self.position[1] )

        # Create window with given title
        self.window = GLUT.glutCreateWindow(self.name)

        # Set background to black
        GL.glClearColor(0.0, 0.0, 0.0, 0.0)

        # Don't care about shading, use cheapest.
        GL.glShadeModel(GL.GL_FLAT)


class Plot():
    '''Passed a  fully populated skeleton, window name, postion, and size,
        initializes an OpenGL window to plot the skeleton.  Use arrow keys
         to orbit around the skeleton and  <SPACE> to toggle between the
        pose an the animation.'''

    def __init__( self, skeleton, name, window_pos=[100,100], window_size=[800,800] ):
        if not isinstance( skeleton, Skeleton ):
            raise Exception('Skeleton is required and must be of type skeleton')
        self.skeleton = skeleton
        self.window = Window( name, window_pos, window_size )
        self.rotate_y = 180.0
        self.rotate_x = 0.0
        self.scale = 1.0
        self.animating = False
        self.frame = 0

    def reshape(self, w, h):
        '''Callback function for handling reshape from glut'''

        GL.glViewport(0, 0, GL.GLsizei(w), GL.GLsizei(h))
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
#CURRENT WORKING
#        #TODO understand this instead of brute force picking some numbers.
#        GL.glScalef(3.0, 3.0, 3.0)  #Deals with near clipping plane weirdness.
#        GL.glFrustum(-1.0, 1.0, -1.0, 1.0, 2.0, 5.0) #Boutique config. :(
#        GL.glMatrixMode(GL.GL_MODELVIEW)
#
        GL.glScalef(2.0, 2.0, 2.0)  #Deals with near clipping plane weirdness.
        GL.glFrustum(-1.0, 1.0, -1.0, 1.0, 2.0, 5.0) #Boutique config. :(
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def keypress(self, key, x, y):
        '''Callback function for glut keyboard input handling.'''

        # Controls: UP - rotate up
        #           DOWN - rotate down
        #           LEFT - rotate left
        #           RIGHT - rotate right

        if key == GLUT.GLUT_KEY_RIGHT:
            self.rotate_y += 5
        if key == GLUT.GLUT_KEY_LEFT:
            self.rotate_y -= 5
        if key == GLUT.GLUT_KEY_UP:
            self.rotate_x += 5
        if key == GLUT.GLUT_KEY_DOWN:
            self.rotate_x -= 5
        if key == 32:  #Pressed the space bar, start animating!
            self.animating = not self.animating
            self.frame = 0

        if key in [3, 27]:  #Escape key or ^C terminate
            #Apparently not implemented on mac.  You must apple-quit
            if which_os() == 'Darwin':
                print ("Weirdly not supported, use apple-Q to quit.")
            else:
                GLUT.glutDestroyWindow(self.window.window)
                GLUT.glutLeaveMainLoop()
                sys.exit(0)

        GLUT.glutPostRedisplay()

    def display(self):
        '''Callback to actually render the skeleton'''

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Set the color to white
        GL.glColor3f(1.0, 1.0, 1.0)

        # Reset the matrix
        GL.glLoadIdentity()

        # Set the camera
        gluLookAt(0.0, 0.0, -3.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

        GL.glScalef(self.scale, self.scale, self.scale)
        GL.glRotatef(self.rotate_y, 0.0, 1.0, 0.0)

        GL.glRotatef(self.rotate_x, 1.0, 0.0, 0.0)

        self.draw_bone( self.skeleton.get_root() )

        GL.glFlush()

    def activate(self):
        '''This function is called once the skeleton is populated with
           data to activate the OpenGL view.'''

        self.window.initialize()

        # Callback for display
        GLUT.glutDisplayFunc( self.display )

        # Callback for reshape
        GLUT.glutReshapeFunc( self.reshape )

        ## Update the frame number
        GLUT.glutTimerFunc( self.skeleton.frame_rate,
                             self.update_frame, 1 )

        # Update the skeleton
        GLUT.glutIdleFunc( self.update_bones )

        # Callback for keyboard
        GLUT.glutSpecialFunc( self.keypress )

        # Start the main loop
        GLUT.glutMainLoop()

    def add_vertex( self, vec ):
        '''Creates a glVertex3f from a glm.vec3 scaled by the
           skeleton's scale_factor for unitization.'''

        scaled_vec = vec / self.skeleton.scale_factor
        GL.glVertex3f( scaled_vec[0], scaled_vec[1], scaled_vec[2] )

    def update_frame( self, _ ):
        '''Trivial function to update the frame number'''

        self.frame += 1
        GLUT.glutPostRedisplay()
        GLUT.glutTimerFunc(self.skeleton.frame_rate, self.update_frame, 1)

    def update_bone( self, joint, rotation  ):
        '''Updates the rotation/position/scale for an individual bone'''

        #TODO this aborts animating descendants.
        if len(joint.frames) < self.frame:
            return

        child_rot = joint.frames[self.frame].rotation * rotation
        if self.skeleton.has_resting:
            child_rot = glm.conjugate(joint.frames[self.frame].rotation) * rotation
        
        if joint.parent is not None:
            joint.w_position = joint.parent.w_position + \
                               joint.position * glm.conjugate(rotation)
            if self.skeleton.has_resting:
                joint.w_position = joint.parent.w_position + \
                                   joint.position * rotation
        else:
            joint.w_position = joint.position

        for child in joint.children:
            self.update_bone( child, child_rot )

    def update_bones( self ):
        '''When in animating mode, uses the time delta from the last frame and
           the framerate to determine which frame to display next, then
           recursively updates the skeleton with the motion data.'''

        if self.animating:
            #Loop the animation
            if self.frame >= self.skeleton.num_frames:
                self.frame = 0

            rotation = glm.quat(glm.vec3(0,0,0))
            self.update_bone( self.skeleton.get_root(), rotation )

    def draw_bone( self, joint ):
        '''Recursive function to draw line strips from a joint to each of
           if children.'''


        #TODO assigning joints colors would be cool. Move joint color to skeleton.
        GL.glColor3f(1.0, 1.0, 1.0)
        jname = joint.alias.upper()
        if 'RIGHT' in jname or jname[0]=='R':
            GL.glColor3f(1.0, 0.0, 0.0)
        elif 'LEFT' in jname or jname[0]=='L':
            GL.glColor3f(0.0, 0.0, 1.0)

        if joint.parent is not None:
            #Make a 2-vertex line segment
            GL.glBegin( GL.GL_LINE_STRIP )
            #Keep the root at the center of the screen.
            self.add_vertex( joint.parent.w_position - self.skeleton.get_root().w_position )
            self.add_vertex( joint.w_position - self.skeleton.get_root().w_position )
            GL.glEnd()

        #Recurse the children
        for child in joint.children:
            self.draw_bone( child )
