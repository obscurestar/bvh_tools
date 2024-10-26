'''A simple library for parsing BVH files.'''

import copy
import glm
from tools import putils
from tools.skeleton import KeyFrame, Joint, Skeleton

class Channels:
    '''Which channels are active for a given joint
       this has been abstracted out of joints to keep them
       lighter as it's only used for parsing and then discarded.'''
    def __init__(self, joint, line, offset):
        self.joint = joint
        self.rotation = {}
        self.position = {}
        self.scale = {}
        self._parse(line, offset)

    def _parse(self, line, offset):
        '''line is a small lie.  It is the line to parse but it is a list'''
        index = 0
        fields = [field.upper() for field in line[2:]]

        for field in fields:
            axis = field[0]
            chan = field[1:]

            if chan == 'ROTATION':
                self.rotation[axis] = index + offset
            elif chan == 'POSITION':
                self.position[axis] = index + offset
            elif chan == 'SCALE':
                self.scale[axis] = index + offset
            else:
                raise Exception(f'Channel parsing: {chan} Ignored unrecognized token {field}')
            index = index + 1

class BVH:
    '''BVH parser'''
    def __init__( self, filename=None, max_depth=None, ignore_after=None ):
        self.skeleton = Skeleton()
        self.max_depth = max_depth
        self.ignore_after_list = ignore_after
        self.channels = []
        self.channel_offset = 0 #A running counter of channels
        self.depth = -1

        if filename is not None:
            self.read_file( filename )
            self.skeleton.fix_end_positions()
            self.skeleton.init_world_positions()

    @staticmethod
    def _read_hierarchy_line( fptr ):
        '''A slovenly line parser with an awkward return
            because python is too stupid to pass by reference
            unless it feels like screwing your dicts and lists'''

        line = fptr.readline()
        if not line:
            return False, None, []

        fields = line.strip().split()
        tag = fields[0].upper()

        return True, tag, fields

    @staticmethod
    def _read_motion_line( fptr ):
        '''Like read hierarchy line but for motion'''

        line = fptr.readline()
        if not line:
            return []

        channels = line.strip().split()

        return [float(channel) for channel in channels]

    def _parse_endsite( self, joint, fptr ):
        paren_count = 0
        valid, tag, fields = self._read_hierarchy_line( fptr )

        while valid:
            if tag == '{':
                paren_count += 1
            elif tag == 'OFFSET':
                joint.end_position = glm.vec3( float( fields[1] ),
                                               float( fields[2] ),
                                               float( fields[3] ) )
            elif tag == '}':
                if paren_count != 1:
                    raise Exception( f'Paren count mismatch in end site for {joint.name}' )
                return True
            else:
                raise Exception( f'Unrecognized {tag} in endsite for {joint.name}' )
            valid, tag, fields = self._read_hierarchy_line( fptr )
        raise Exception( f'Unexpected EOF searching for endsite in {joint.name}' )

    def _parse_joint( self, name, parent, fptr  ):
        '''Parse a joint, recursing into children as needed'''

        joint = Joint( name, parent )

        if self.max_depth is None or self.depth <= self.max_depth:
            self.skeleton.joints[ joint.alias ] = joint
            if parent is not None:
                parent.children.append(joint)

        valid, tag, fields = self._read_hierarchy_line( fptr )

        if not valid:
            return False    #Bad formatting
        if tag != '{':
            return False    #Bad formatting

        valid, tag, fields = self._read_hierarchy_line( fptr )
        while valid:
            if tag == 'OFFSET':
                joint.position = glm.vec3( float( fields[1] ),
                                           float( fields[2] ),
                                           float( fields[3] ) )
            if tag == 'CHANNELS':
                chan = Channels( joint, fields, self.channel_offset )
                self.channel_offset = self.channel_offset + int(fields[1])
                self.channels.append( chan )
            if tag == 'JOINT':
                self.depth = self.depth + 1
                self._parse_joint( fields[1], joint, fptr )
            if tag == 'END' and fields[1].upper() == 'SITE':
                if not self._parse_endsite( joint, fptr ):
                    self.depth -= 1
                    return False    #Bad formatting
            if tag == '}':
                self.depth -= 1
                return True
            valid, tag, fields = self._read_hierarchy_line( fptr )
        raise Exception( f'Unexpected EOF while reading {name}' )

    def _parse_hierarchy( self, fptr ):
        '''In the hierarchy portion of the file, read until
           MOTION or end of file.'''

        valid, tag, fields = self._read_hierarchy_line( fptr )
        while valid:
            parent = None
            if tag == 'ROOT':
                self.skeleton.root_name = fields[1]
                self.channel_offset = 0
                self._parse_joint( fields[1], parent, fptr )
            if tag in ('FRAMES:', 'FRAME', 'MOTION'):
                return tag, fields
            valid, tag, fields = self._read_hierarchy_line( fptr )
        return '', []

    @staticmethod
    def _extract_vector( indicies, data, base ):
        '''Extract indicies from data and order as XYZ in a glm.vec3'''

        vec = glm.vec3( base, base, base )

        for key,index in indicies.items():
            if key == 'X':
                vec[0] = data[index]
            if key == 'Y':
                vec[1] = data[index]
            if key == 'Z':
                vec[2] = data[index]

    @staticmethod
    def _extract_rotation( indicies, data ):
        '''Extract indicies from data and create a glm.quat by summing
            the rotations'''

        quat = glm.quat( glm.vec3() )
        for key,index in indicies.items():
            euler = glm.vec3()
            if key == 'X':
                euler[0] = data[index]
            if key == 'Y':
                euler[1] = data[index]
            if key == 'Z':
                euler[2] = data[index]
            quat = quat * glm.quat( putils.radians( euler ) )
        return quat

    def _parse_motion( self, fptr ):
        '''Parse the motion portion of the file'''

        frame_no = 0
        channels = self._read_motion_line( fptr )

        while len(channels) > 0:
            frame = KeyFrame()
            for channel in self.channels:
                if len(channel.rotation) > 0:
                    frame.rotation = self._extract_rotation( channel.rotation,
                                                             channels )
                if len(channel.position) > 0:
                    frame.position = self._extract_vector( channel.position,
                                                           channels,
                                                           0.0 )
                if len(channel.scale) > 0:
                    frame.scale = self._extract_vector( channel.scale,
                                                        channels,
                                                        1.0 )

                #TODO figure out what stupid python thing requires a copy

                channel.joint.frames.append( copy.deepcopy(frame) )

            channels = self._read_motion_line( fptr )
            frame_no += 1
        return frame_no

    def read_file( self, filename, max_depth=None, ignore_after_list=None ):
        '''Attempts to read the BVH file.  If max_depth is set,
           ignore joints below this depth.  If ignore_list is set,
           if a joint name matches one in the ignore_list, ignore
           joints below the named joint.'''

        if max_depth is not None:
            self.max_depth = max_depth
        if ignore_after_list is not None:
            self.ignore_after_list = ignore_after_list

        with open( filename, 'r', encoding='utf-8' ) as fptr:
            valid, tag, fields = self._read_hierarchy_line( fptr )
            while valid:
                if tag == 'HIERARCHY':
                    tag,fields = self._parse_hierarchy( fptr )
                if tag == 'MOTION':
                    _, _, fields = self._read_hierarchy_line( fptr )
                    self.skeleton.num_frames = int( fields[1] )
                    _, _, fields = self._read_hierarchy_line( fptr )
                    self.skeleton.frame_rate = int ( float (fields[2]) * 1000.0 )  #In ms
                    num_frames_read =  self._parse_motion( fptr )

                    if self.skeleton.num_frames != num_frames_read:
                        raise Exception(f'Expected {self.skeleton.num_frames} got {num_frames_read}')
                valid, tag, fields = self._read_hierarchy_line( fptr )
