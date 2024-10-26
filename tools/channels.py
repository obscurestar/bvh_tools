'''Channels are the individual factors of X Y and Z for each of rotation,
    scale, and position'''

#TODO move this class into bvh since nothing else uses it.

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
