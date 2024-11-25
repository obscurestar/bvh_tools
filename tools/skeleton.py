'''Skeleton and related classes'''

import copy
import glm

class KeyFrame:
    '''Keyframe info for an individual joint'''
    position : glm.vec3
    rotation : glm.vec3
    scale : glm.vec3
    def __init__( self ):
        self.position = None
        '''A glm.vec3 representing a change in joint position.'''
        self.rotation = None
        '''A glm.quat representing a change in rotation of the joint.'''
        self.scale = None
        '''A glm.vec3 representing a change in the scale of the joint'''

class Joint:
    '''A single joint in a skeleton'''
    name : str
    alias : str
    position : glm.vec3
    w_position : glm.vec3
    end_position : glm.vec3
    def __init__( self, name=None, parent=None ):
        self.name = name    #String
        '''The name of the joint as read from the BVH file'''
        self.alias = name   #default same as name
        '''A preferred name for the joint used for remapping.  Default is same as name'''
        self.parent = parent  #Pointer to another joint
        '''A reference to the object of this joint's parent joint.  None if joint is root'''
        self.position = glm.vec3()
        '''The joint's parent-relative position'''
        self.w_position = glm.vec3()
        '''The joint's world position'''
        self.end_position = None
        '''The end position for this joint. The average of this joint's children's
            parent-relative position.  None if no children.'''
        self.frames = []
        '''A list of keyframes for this joint.'''
        self.resting = None #Resting pose is a single Keyframe
        '''Some skeletons have a resting pose in addition to the bind pose.'''
        self.children = []
        '''A list of the child joints'''

    def extract_resting_pose( self, rotation : glm.quat ):
        '''Convert the 0th frame to a resting pose.'''

        if self.resting is not None:
            #Prevent accidental double use.
            raise Exception('Resting frame extraction failed.  Resting frame already present.')

        self.resting = copy.deepcopy(self.frames[0])
        self.frames = self.frames[1:]

        child_rot = glm.conjugate(self.resting.rotation) * rotation
        if self.parent is not None:
            self.w_position = self.parent.w_position + \
                               self.position * rotation
        else:
            self.w_position = self.position

        for child in self.children:
            child.extract_resting_pose( child_rot )

    def fix_end_position( self ):
        '''The end position for each joint can be created from
            either explicitly with an ENDSITE in the hierarchy
            definition or as the centroid of all its children.
        '''

        if self.end_position is None:
            if len(self.children) > 0:
                center = glm.vec3(0,0,0)

                for child in self.children:
                    center = center + child.position

                self.end_position = center/len(self.children)
            else:
                self.end_position = glm.vec3( 0, 0, 0 )

        for child in self.children:
            child.fix_end_position( )

    def init_world_position( self ):
        '''The hierarchy is initially generated as parent relative positions in the
           world relative rotational frame.'''

        if self.parent is None:
            self.w_position = glm.vec3( 0, 0, 0 )
        else:
            self.w_position = self.parent.w_position + self.position

        for child in self.children:
            child.init_world_position( )

    def compute_unit_scale(self, mag_sum : float=0) -> float:
        '''Recursive function for summing the magnitude of
           joint chains and returning the maximum magnitude
           of all branching possibilities.'''

        if self.position is None:
            return mag_sum

        mag_current = mag_sum + glm.length(self.position)
        mag_return = mag_current

        if len(self.children) > 0:
            for child in self.children:
                mag_return = max( mag_return, \
                                  child.compute_unit_scale( mag_current ) )
        return mag_return

class Skeleton:
    '''A digraph of bones.
       Of note:  self.joints should contain only one joint named
       self.root_name.  Handled this way to make skeleton processing
       generic regardless of start point.'''

    def __init__( self ):
        self.joints = {}        #Map of joint aliases to joint data.
        '''A dict mapping of joint aliases to the joint data'''
        self.root_name = None
        '''The name of the root joint'''
        self.num_frames = 0
        '''Number of frames in the animation'''
        self.frame_rate = 33
        '''Optimal minimum delay between displaying frames'''
        self.scale_factor = 1.0
        '''Number used to convert avatar to Vetruvian Scale
        (The largest sum of joint lengths from root an an end effector)'''
        self.has_resting = False
        '''Set true if there is a resting pose in the skeleton.'''

    def get_root( self ):
        '''Returns a pointer to the root joint'''
        if self.root_name is None or self.root_name not in self.joints:
            raise Exception( 'No root found' )
        return self.joints[ self.root_name ]

    def handle_resting_pose( self ):
        '''Sets the has resting flag and tells the joints to
           convert their 0th frame to a resting pose.'''

        if self.has_resting:
            rotation = glm.quat(glm.vec3(0,0,0))
            self.get_root().extract_resting_pose( rotation )

    def fix_end_positions( self ):
        '''BVH spec is a bit nebulous on where the end of a bone is so
           we'll make some choices'''
        self.get_root().fix_end_position()

    def init_world_positions( self ):
        '''Makes the joints set their world positions'''
        self.get_root().init_world_position()

    def set_unit_scale_factor(self):
        '''Starting from the root, sum the magnitudes of all the joints
           from root to each end effector.  The greatest sum becomes
           our unit size.
           This will be useful when plotting or comparing skeletons
           to one another.'''

        if self.root_name not in self.joints:
            self.scale_factor = 1.0
            return

        self.scale_factor = self.joints[self.root_name].compute_unit_scale()
