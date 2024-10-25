'''Non-realtime plotting using matplotlib scatter graph.'''
import matplotlib.pyplot as mat_plot
from mpl_toolkits.mplot3d import Axes3D

class Plot:
    '''Object for making plots'''
    def __init__(self):
        self.jointnames = []
        self.points = [ [], [], [] ]
        self.parent_ids = []
        self.plotted_points=None

        mat_plot.ion()      #Turn on interactive mode
        #The figsize=(5,5) somehow sets the window size
        self.figure = mat_plot.figure(figsize=(7,7))
        self.axis = Axes3D(self.figure)
        self.colors = ['r','g','b','c','m','y']

    def set_graph_range(self,x,y,z,name=None):
        '''Set the extents to be displayed.'''

        if name is None:
            name = "BVH data"

        #Clear axis
        mat_plot.cla()

        #Draw the axis
        self.axis = Axes3D(self.figure)

        #self.figure.canvas.set_window_title(name)
        self.figure.canvas.manager.set_window_title(name)
        #Elevation and azimuth are in degrees.
        self.axis.view_init(elev=120, azim=-90)
        #self.axis.view_init(elev=0, azim=0)

        # setting title and labels
        self.axis.set_title(name)
        self.axis.set_xlabel('X-axis')
        self.axis.set_ylabel('Y-axis')
        self.axis.set_zlabel('Z-axis')

        # set the range of the graphed area
        self.axis.set_xlim(x[0],x[1])
        self.axis.set_ylim(y[0],y[1])
        self.axis.set_zlim(z[0],z[1])

        self.plotted_points = None

    def clear(self):
        '''Clear what's currently plotted in the window'''
        #mat_plot.clf()
        self.points = [ [], [], [] ]
        self.parent_ids = []

    def flush(self):
        '''Flush the plotted points'''
        self.jointnames = []

#    def add_perp_point(self, point):
#        '''Add a point to the perpendicular data to be plotted.'''
#
#        if (self.frame_number % self.interval != 0):
#            return
#
#        self.perp_pts[0].append(point[0])
#        self.perp_pts[1].append(point[1]*-1.0)
#        self.perp_pts[2].append(point[2])

    def plot_hierarchy(self, hptr, parent_id=-1, scale_factor=1.0):
        '''Add the joints in hptr to the plot in window'''
        if 'name' not in hptr:
            return
        new_parent_id = self.add_joint(hptr['name'], hptr['world_position'] / scale_factor, parent_id)

        if 'children' in hptr:
            for _,child in hptr['children'].items():
                self.plot_hierarchy(child, new_parent_id, scale_factor)

    def add_joint(self, name, offset, parent_id):
        '''Add a joint.   Returns id of the row created.'''
        self.jointnames.append(name)
        self.points[0].append(offset.x)
        self.points[1].append(offset.y)
        self.points[2].append(offset.z)
        self.parent_ids.append(parent_id)
        return len(self.parent_ids) - 1

    def stop(self):
        '''Releases the plot'''
        mat_plot.cla()

    def _scale_array(self, array, factor):
        '''Scales array by factor'''
        x = len(array)
        i = 0
        while i<x:
            array[i] = array[i] / factor
            i = i + 1

    def unitize(self):
        '''Gets the largest direction in any axis and sets that as 1.0'''
        if len(self.points[0]) == 0:
            return #Nothing to do.

        factor = 1.0
        factor0 = max(self.points[0])
        factor1 = max(self.points[1])
        factor2 = max(self.points[2])
        factor = max(factor,factor0,factor1,factor2)
        self._scale_array(self.points[0], factor)
        self._scale_array(self.points[1], factor)
        self._scale_array(self.points[2], factor)

    def scale(self, factor):
        '''Scale all points in array by factor'''
        self._scale_array(self.points[0], factor)
        self._scale_array(self.points[1], factor)
        self._scale_array(self.points[2], factor)

    def _offset_array(self, array, offset):
        '''Offset all elements in array by amount'''
        x = len(array)
        i = 0
        while i<x:
            array[i] = array[i] + offset
            i = i + 1

    #def offset(self, offset_vec):
    #    '''Passed a XYZ vector representing offset amounts'''
    #    self._unitize_array(self.points[0],offset_vec[0])
    #    self._unitize_array(self.points[1],offset_vec[1])
    #    self._unitize_array(self.points[2],offset_vec[2])

    def draw_lines(self):
        '''Draw lines connecting each child to its parent'''
        for line in self.axis.get_lines():
            line.remove()

        count = 0
        for parent in self.parent_ids:
            if parent != -1:
                self.axis.plot( [ self.points[0][parent], \
                                  self.points[0][count] ], \
                                [ self.points[1][parent], \
                                  self.points[1][count] ] , \
                                [ self.points[2][parent], \
                                  self.points[2][count] ] , \
                                 color = self.colors[count%len(self.colors)])
            count += 1
    def draw(self, showlabels = False):
        '''Draw the plot'''
        if self.plotted_points is not None:
            self.plotted_points.remove()

        if self.jointnames is not None:
            #self.axis.text.remove()
            for text in self.axis.texts:
                del text # self.axis.texts

        self.draw_lines()
        self.plotted_points = self.axis.scatter( \
                                self.points[0], \
                                self.points[1], \
                                self.points[2], \
                                color='green')
        if showlabels:
            jointcount = 0
            while jointcount < len(self.jointnames):
                self.axis.text( self.points[0][jointcount]+.001,
                                self.points[1][jointcount]+.001,
                                self.points[2][jointcount]+.001,
                                self.jointnames[jointcount],
                                fontsize=5 )
                jointcount += 1

        mat_plot.draw()
        mat_plot.pause(0.01)
        self.flush()
