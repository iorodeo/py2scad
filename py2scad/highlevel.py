"""
Copyright 2010  IO Rodeo Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
try:
    import scipy as numpy
except ImportError:
    import numpy
from primitives import *
from transforms import *
from utility import DEG2RAD
from utility import RAD2DEG

INCH2MM = 25.4

class Basic_Enclosure(object):

    """
    Creates a basic tabbed enclosure for laser cutting. The enclosure is designed
    to be help together without any gluing (or solvent welding) using standoffs.

    Need to add more documentaion on how to use this class ...
    """

    def __init__(self, params):
        self.params = params

    def __make_top_and_bottom(self):
        """
        Create top and bottom panels of the enclosure. 
        """
        inner_x, inner_y, inner_z = self.params['inner_dimensions']
        wall_thickness = self.params['wall_thickness']
        top_x_overhang = self.params['top_x_overhang']
        top_y_overhang = self.params['top_y_overhang']
        bottom_x_overhang = self.params['bottom_x_overhang']
        bottom_y_overhang = self.params['bottom_y_overhang']
        lid_radius = self.params['lid_radius']

        # Add slots for tabs 
        slot_list = []
        lid2front_tab_width = self.params['lid2front_tab_width']
        lid2side_tab_width = self.params['lid2side_tab_width']
        
        # Add lid to front slots
        for loc in self.params['lid2front_tabs']:
            for sign in (-1,1):
                x_pos = inner_x*loc - 0.5*inner_x
                y_pos = sign*(0.5*inner_y + 0.5*wall_thickness)
                x_size = lid2front_tab_width
                y_size = wall_thickness
                slot = ((x_pos, y_pos), (x_size, y_size))
                slot_list.append(slot)

        # Add lid to side slots
        for loc in self.params['lid2side_tabs']:
            for sign in (-1,1):
                x_pos = sign*(0.5*inner_x + 0.5*wall_thickness)
                y_pos = (inner_y + 2*wall_thickness)*loc - 0.5*(inner_y +2*wall_thickness)
                x_size = wall_thickness
                y_size = lid2side_tab_width
                slot = ((x_pos, y_pos), (x_size, y_size))
                slot_list.append(slot)

        # Get dimensions of top and bottom panels
        top_x = inner_x + 2.0*(wall_thickness + top_x_overhang)
        top_y = inner_y + 2.0*(wall_thickness + top_y_overhang)
        top_z = wall_thickness
        self.top_x, self.top_y = top_x, top_y
        top_size = top_x, top_y, top_z
        bottom_x = inner_x + 2.0*(wall_thickness + bottom_x_overhang)
        bottom_y = inner_y + 2.0*(wall_thickness + bottom_y_overhang)
        bottom_z = wall_thickness
        self.bottom_x, self.bottom_y = bottom_x, bottom_y
        bottom_size = bottom_x, bottom_y, bottom_z
            
        # Create top and bottom panels
        top_params = {'size' : top_size, 'radius' : lid_radius, 'slots' : slot_list}
        bottom_params = {'size' : bottom_size, 'radius' : lid_radius, 'slots' : slot_list}
        top_plate_maker = Plate_W_Slots(top_params)
        self.top = top_plate_maker.make()
        bottom_plate_maker = Plate_W_Slots(bottom_params)
        self.bottom = bottom_plate_maker.make()

        # Add holes for standoffs
        standoff_diameter = self.params['standoff_diameter']
        standoff_offset = self.params['standoff_offset']
        standoff_hole_diameter = self.params['standoff_hole_diameter']

        hole_list = []
        self.standoff_xy_pos = []
        self.standoff_list = []
        for i in (-1,1):
            for j in (-1,1):
                # Create holes for standoffs
                x = i*(0.5*inner_x - 0.5*standoff_diameter - standoff_offset)
                y = j*(0.5*inner_y - 0.5*standoff_diameter - standoff_offset)
                self.standoff_xy_pos.append((x,y))
                top_hole = { 
                        'panel'     : 'top', 
                        'type'      : 'round',
                        'location'  : (x,y), 
                        'size'      : standoff_hole_diameter,
                        }
                bottom_hole = {
                        'panel'     : 'bottom', 
                        'type'      : 'round',
                        'location'  : (x,y), 
                        'size'      : standoff_hole_diameter,
                        }
                hole_list.append(top_hole)
                hole_list.append(bottom_hole)

                # Create standoff cylinders
                r = 0.5*standoff_diameter
                standoff = Cylinder(r1=r, r2=r, h=inner_z)
                self.standoff_list.append(standoff)

        self.add_holes(hole_list)


    def __make_left_and_right(self):
        """
        Creates the left and right side panels of the enclosure.
        """
        inner_x, inner_y, inner_z = self.params['inner_dimensions']
        wall_thickness = self.params['wall_thickness']
        lid2side_tab_width = self.params['lid2side_tab_width']
        side2side_tab_width = self.params['side2side_tab_width']

        # Create tab data for yz faces of side panels
        xz_pos = []
        xz_neg = []
        for loc in self.params['lid2side_tabs']:
            tab_data = (loc, lid2side_tab_width, wall_thickness, '+')
            xz_pos.append(tab_data)
            xz_neg.append(tab_data)

        # Create tab data for xz faces of side panels
        yz_pos = []
        yz_neg = []
        for loc in self.params['side2side_tabs']:
            tab_data = (loc, side2side_tab_width, wall_thickness, '-')
            yz_pos.append(tab_data)
            yz_neg.append(tab_data)

        # Pack panel data into parameters structure
        params = { 
                'size' : (inner_y+2*wall_thickness, inner_z, wall_thickness),
                'xz+'  : xz_pos,
                'xz-'  : xz_neg,
                'yz+'  : yz_pos,
                'yz-'  : yz_neg,
                }

        plate_maker = Plate_W_Tabs(params)
        self.left = plate_maker.make()
        self.right = plate_maker.make()


    def __make_front_and_back(self):
        """
        Creates the front and back panels of the enclosure.
        """
        inner_x, inner_y, inner_z = self.params['inner_dimensions']
        wall_thickness = self.params['wall_thickness']
        lid2front_tab_width =  self.params['lid2front_tab_width']
        side2side_tab_width = self.params['side2side_tab_width']

        # Create tab data for xz faces of front and back panels
        xz_pos = []
        xz_neg = []
        for loc in self.params['lid2front_tabs']:
            tab_data = (loc, lid2front_tab_width, wall_thickness, '+') 
            xz_pos.append(tab_data)
            xz_neg.append(tab_data)

        # Create tab data for yz faces of front and back panels
        yz_pos = []
        yz_neg = []
        for loc in self.params['side2side_tabs']:
            tab_data = (loc, side2side_tab_width, wall_thickness, '+')
            yz_pos.append(tab_data)
            yz_neg.append(tab_data)


        # Pack panel data into parameters structure
        params = { 
                'size' : (inner_x, inner_z, wall_thickness),
                'xz+'  : xz_pos,
                'xz-'  : xz_neg,
                'yz+'  : yz_pos,
                'yz-'  : yz_neg,
                }

        plate_maker = Plate_W_Tabs(params)
        self.front = plate_maker.make()
        self.back = plate_maker.make()

    def add_holes(self, hole_list):
        """
        Add holes to given panel of the enclosure. 
        """

        wall_thickness = self.params['wall_thickness']

        for hole in hole_list:

            # Create differencing cylinder for hole based on hole type.
            if hole['type'] == 'round':
                radius = 0.5*hole['size']
                hole_cyl = Cylinder(r1=radius, r2=radius, h = 2*wall_thickness)
            elif hole['type'] == 'square':
                sz_x, sz_y = hole['size']
                sz_z = 2*wall_thickness
                hole_cyl = Cube(size = (sz_x,sz_y,sz_z))
            elif hole['type'] == 'rounded_square':
                sz_x, sz_y, radius = hole['size']
                sz_z = 2*wall_thickness
                hole_cyl = rounded_box(sz_x, sz_y, sz_z, radius, round_z=False)
            else:
                raise ValueError, 'unkown hole type {0}'.format(hole['type'])

            # Translate cylinder into position
            x,y = hole['location']
            hole_cyl = Translate(hole_cyl, v = (x,y,0.0))

            # Get panel in which to make hole
            panel = getattr(self, hole['panel'])

            # Cut hole
            panel = Difference([panel, hole_cyl])
            setattr(self, hole['panel'], panel)
            
                    
    def make(self):
        self.__make_left_and_right()
        self.__make_front_and_back()
        self.__make_top_and_bottom()
        self.add_holes(self.params['hole_list'])
        return

    def get_assembly(self, explode=(0,0,0), show_top=True, show_bottom=True, show_front=True, 
            show_back=True, show_left=True, show_right=True, show_standoffs=True):
        """
        Returns a list of the enclosure parts in assembled positions.
        """
        inner_x, inner_y, inner_z = self.params['inner_dimensions']
        wall_thickness = self.params['wall_thickness']
        explode_x, explode_y, explode_z = explode

        # Translate top and bottom into assembled positions
        top_z_shift = 0.5*inner_z + 0.5*wall_thickness + explode_z
        bottom_z_shift = -top_z_shift
        top = Translate(self.top, v=(0.0,0.0,top_z_shift))
        bottom = Translate(self.bottom,v=(0.0,0.0,bottom_z_shift))

        # Rotate and translate front and back into assembled positions
        front = Rotate(self.front, a=90, v=(1,0,0))
        back = Rotate(self.back, a=90, v=(1,0,0))
        front_y_shift = 0.5*inner_y + 0.5*wall_thickness + explode_y
        back_y_shift = -front_y_shift
        front = Translate(front, v=(0.0, front_y_shift, 0.0))
        back = Translate(back, v=(0.0, back_y_shift, 0.0))

        # Rotate and translate sides into assembled positions
        right = Rotate(self.right, a=90, v=(0,0,1))
        right = Rotate(right, a=90, v=(0,1,0))
        left = Rotate(self.left, a=90, v=(0,0,1))
        left = Rotate(left, a=90, v=(0,1,0))
        right_x_shift = 0.5*inner_x + 0.5*wall_thickness + explode_x
        left_x_shift = -right_x_shift
        right = Translate(right,v=(right_x_shift,0,0))
        left = Translate(left,v=(left_x_shift,0,0))

        # Translate standoffs into position
        standoff_list = []
        for pos, standoff in zip(self.standoff_xy_pos, self.standoff_list):
            x_shift, y_shift = pos
            z_shift = 0.0
            standoff = Translate(standoff,v=(x_shift,y_shift,z_shift))
            standoff_list.append(standoff)

        # Return list of parts in assembly
        part_list = []
        if show_top == True:
            part_list.append(top)
        if show_bottom == True:
            part_list.append(bottom)
        if show_front == True:
            part_list.append(front)
        if show_back == True:
            part_list.append(back)
        if show_left == True:
            part_list.append(left)
        if show_right == True:
            part_list.append(right)
        if show_standoffs == True: 
            part_list.extend(standoff_list)
        return part_list


    def get_projection(self,show_ref_cube=True, spacing_factor=4):
        """
        Retruns a list of enclosure parts as 2D projections for saving as a dxf file.
        """
        inner_x, inner_y, inner_z = self.params['inner_dimensions']
        wall_thickness = self.params['wall_thickness']
        top_x_overhang = self.params['top_x_overhang']
        top_y_overhang = self.params['top_y_overhang']
        bottom_x_overhang = self.params['bottom_x_overhang']
        bottom_y_overhang = self.params['bottom_y_overhang']
        spacing = spacing_factor*wall_thickness
        bottom = self.bottom

        # Translate front panel
        y_shift = -(0.5*self.bottom_y + 0.5*inner_z + wall_thickness + spacing)
        front = Translate(self.front, v=(0,y_shift,0))

        # Translate back panel
        y_shift = 0.5*self.bottom_y + 0.5*inner_z + wall_thickness + spacing
        back = Translate(self.back, v=(0,y_shift,0))

        # Rotate and Translate left panel
        left = Rotate(self.left,a=90,v=(0,0,1))
        x_shift = -(0.5*self.bottom_x + 0.5*inner_z + wall_thickness + spacing)
        left = Translate(left, v=(x_shift,0,0))

        # Rotate and translate right panel
        right = Rotate(self.right,a=90,v=(0,0,1))
        x_shift = 0.5*self.bottom_x + 0.5*inner_z + wall_thickness + spacing
        right = Translate(right,v=(x_shift,0,0))

        # Rotate and translate top
        y_shift = -(0.5*self.bottom_y + 0.5*self.top_y + inner_z + 2*wall_thickness + 2*spacing)
        top = Translate(self.top, v=(0,y_shift,0))

        # Create reference cube
        ref_cube = Cube(size=(INCH2MM,INCH2MM,INCH2MM))
        y_shift = 0.5*self.bottom_y + 0.5*INCH2MM + inner_z + 2*wall_thickness + 2*spacing 
        ref_cube = Translate(ref_cube,v=(0,y_shift,0))

        # Create part list
        part_list = [top, bottom, front, back, left, right]
        if show_ref_cube == True:
            part_list.append(ref_cube)

        # Project parts
        part_list_proj = []
        for part in part_list:
            part_list_proj.append(Projection(part))
            
        return part_list_proj


class Plate_W_Slots(object):

    """
    Creates a plate with square (rectangular) slots. Plate is assumed to lie in the 
    x-y plane and the holes are cut through the xy faces.

    Usage:

    plate_maker = Plate_W_Slots(params)
    plate = plate_maker.make()

    where:

    params = {
        'size'   : (x,y,z),    # plate size
        'radius' : radius,     # plate raduis if not given assumed to be none 
        'slots'  : slot_list,  # list of hole data
    }

    slot_list = [
        (pos_0, size_0),  # position and size of slot 0
        (pos_1, size_1),  # position and size of slot 1 
        ... etc
        ]

    pos_i  = (pos_x, pos_y)    # the x and y coordinates of slot i
    size_i = (size_x, size_y)  # the x and y dimensions of slot i
    """

    def __init__(self, params):
        self.params = params

    def __add_holes(self):

        hole_list = []

        for pos, size in self.params['slots']:
            x, y = size 
            z = 2*self.params['size'][2]
            hole = Cube(size=(x, y, z)) 
            pos_x, pos_y = pos
            hole = Translate(hole,v=[pos_x, pos_y, 0])
            hole_list.append(hole)

        self.plate = Difference([self.plate] + hole_list)


    def make(self):
        try:
            radius = self.params['radius']
        except KeyError:
            radius = None

        if radius is None:
            self.plate = Cube(size=self.params['size'])
        else:
            x,y,z = self.params['size']
            self.plate = rounded_box(x, y, z, radius, round_z=False)

        self.__add_holes()
        return self.plate

class Plate_W_Tabs(object):

    """
    Creates a plate with tabs on the xz and yz faces. 

    Usage:

    plate_maker = Tabbed_Plate(params)  where
    plate = plate_maker.make()

    params is a dictionary of the plate's parameters:

    params = { 
        'size' : (x,y,z),   # size of plate
        'xz+'  : xz_pos,    # tab data for positive xz face 
        'xz-'  : xz_neg,    # tab data for negative xz face 
        'yz+'  : yz_pos,    # tab data for positive yz face 
        'yz-'  : yz_neg,    # tab data for negative yz face 
        }

    the tab data are lists with the follow form:

    tab_data = [ 
        (pos_0, width_0, depth_0, dir_0),  # data for 0th tab 
        (pos_1, width_1, depth_1, dir_1),  # data for 1st tab
        ... etc
        ]

    Where for the i-th tab:

    pos_i   =  position of tab as a fraction of face length. Face length is either
               x or y dimension of plate depending on whether tab is on the xz or yz 
               face of the plate. 
    width_i =  width of tab along x or y dimension depending of whether tab is on 
               the xz or yz face of the plate.
    depth_i =  depth of the tab
    dir_i   =  direction of the tab (either '+' or '-').
    """

    def __init__(self, params):
        self.params = params 

    def __add_tabs(self):

        plate_x, plate_y, plate_z = self.params['size']
        pos_tab_list = []
        neg_tab_list = []

        # Loop over face types
        for face in ('xz', 'yz'):

            # Loop over sign of faces
            for sign, sign_val in (('+',1), ('-',-1)):
                tab_data = self.params[face+sign]

                for fpos, width, depth, tab_dir in tab_data: 
                    # Make removed tabs, those wth '-' tab_dir, thicker than plate
                    if tab_dir == '-':
                        thickness = 1.5*plate_z
                    else:
                        thickness = plate_z

                    if face == 'xz':
                        # Create tabs for the xz faces
                        tab = Cube(size=(width,2*depth,thickness))
                        tx = fpos*plate_x - 0.5*plate_x
                        ty = sign_val*0.5*plate_y
                        tab = Translate(tab, v=(tx,ty,0))
                    elif face == 'yz':
                        # Create tabs for the yz faces
                        tab = Cube(size=(2*depth,width,thickness))
                        tx = sign_val*0.5*plate_x
                        ty = fpos*plate_y - 0.5*plate_y
                        tab = Translate(tab,v=(tx,ty,0))

                    # Add tabs to appropriate list of tabs based on sign of tab
                    if tab_dir == '+':
                        pos_tab_list.append(tab)
                    elif tab_dir == '-':
                        neg_tab_list.append(tab)

        # Add material for positive tabs
        if len(pos_tab_list) > 0:
            self.plate = Union([self.plate] + pos_tab_list)

        # Remove material for negative tabs
        if len(neg_tab_list) > 0:
            self.plate = Difference([self.plate] + neg_tab_list)


    def make(self):
        """
        Creates a tabbed plate.
        """
        self.plate = Cube(size=self.params['size'])
        self.__add_tabs()
        return self.plate


def rounded_box(length, width, height, radius,
                round_x=True, round_y=True, round_z=True):
    """
    Create a box with rounded corners
    """
    assert round_x or round_y == True, 'x and y faces not rounded - at least two sides must be rounded'
    assert round_x or round_z == True, 'x and z faces not rounded - at least two faces must be rounded'
    assert round_y or round_z == True, 'y and z faces not rounded - at least two faces must be rounded'

    if round_x == True:
        dx = length - 2.0*radius
    else:
        dx = length
    if round_y == True:
        dy = width - 2.0*radius
    else:
        dy = width
    if round_z == True:
        dz = height - 2.0*radius
    else:
        dz = height
    union_list = []

    inner_box = Cube([dx,dy,dz])
    union_list.append(inner_box)

    if round_x==True:
        xface_box = Cube([2*radius,dy,dz])
        xface_box0 = Translate(xface_box,v=[0.5*dx,0,0])
        xface_box1 = Translate(xface_box,v=[-0.5*dx,0,0])
        union_list.extend([xface_box0, xface_box1])

    if round_y==True:
        yface_box = Cube([dx,2*radius,dz])
        yface_box0 = Translate(yface_box,v=[0, 0.5*dy,0])
        yface_box1 = Translate(yface_box,v=[0, -0.5*dy,0])
        union_list.extend([yface_box0, yface_box1])

    if round_z==True:
        zface_box = Cube([dx,dy,2*radius])
        zface_box0 = Translate(zface_box,v=[0, 0, 0.5*dz])
        zface_box1 = Translate(zface_box,v=[0, 0, -0.5*dz])
        union_list.extend([zface_box0, zface_box1])

    xaxis_cly = Cylinder(h=dx,r1=radius,r2=radius)
    xaxis_cly = Rotate(xaxis_cly,a=90,v=[0,1,0])
    yaxis_cly = Cylinder(h=dy,r1=radius,r2=radius)
    yaxis_cly = Rotate(yaxis_cly,a=90,v=[1,0,0])
    zaxis_cly = Cylinder(h=dz,r1=radius,r2=radius)

    for i in [-1,1]:
        for j in [-1,1]:
            if round_y==True and round_z==True:
                temp_cyl = Translate(xaxis_cly,v=[0,i*0.5*dy,j*0.5*dz])
                union_list.append(temp_cyl)
            if round_z==True and round_x==True:
                temp_cyl = Translate(yaxis_cly,v=[i*0.5*dx,0,j*0.5*dz])
                union_list.append(temp_cyl)
            if round_x==True and round_y==True:
                temp_cyl = Translate(zaxis_cly,v=[i*0.5*dx,j*0.5*dy,0])
                union_list.append(temp_cyl)

    if round_x==True and round_y==True and round_z==True:
        corner_sph = Sphere(r=radius)
        for i in [-1,1]:
            for j in [-1,1]:
                for k in [-1,1]:
                    temp_sph = Translate(corner_sph,v=[i*0.5*dx,j*0.5*dy,k*0.5*dz])
                    union_list.append(temp_sph)

    box = Union(union_list)
    return box

def plate_w_holes(length, width, height, holes=[], hole_mod='', radius=False):
    """
    Create a plate with holes in it.

    Arguments:
      length = x dimension of plate
      width  = y dimension of plate
      height = z dimension of plate
      holes  = list of tuples giving x position, y position and diameter of
               holes
    """
    if radius == False:
        plate = Cube(size=[length,width,height])
    else:
        plate = rounded_box(length,width,height,radius)
    cylinders = []
    for x,y,r in holes:
        c = Cylinder(h=4*height,r1=0.5*r, r2=0.5*r)
        c = Translate(c,v=[x,y,0],mod=hole_mod)
        cylinders.append(c)
    obj_list = [plate] + cylinders
    plate = Difference(obj_list)
    return plate

def disk_w_holes(height, d1, holes=[], hole_mod=''):
    """
    Create a disk with holes in it.

    Arguments:
      d1 = diameter of the disk
      height = z dimension of disk
      holes  = list of tuples giving x position, y position and diameter of
               holes
    """

    cyl = Cylinder(h=height,r1=d1*0.5,r2=d1*0.5)
    cylinders = []
    for x,y,r in holes:
        c = Cylinder(h=4*height,r1=0.5*r, r2=0.5*r)
        c = Translate(c,v=[x,y,0],mod=hole_mod)
        cylinders.append(c)
    obj_list = [cyl] + cylinders
    disk = Difference(obj_list)
    return disk

def grid_box(length, width, height, num_length, num_width,top_func=None,bot_func=None):
    """
    Create a box with given length, width, and height. The top and bottom surface of the
    box will be triangulate bases on a grid with num_length and num_width points.
    Optional functions top_func and bot_func can be given to distort the top or bottom
    surfaces of the box.
    """
    nl = num_length + 1
    nw = num_width + 1
    xpts = numpy.linspace(-0.5*length,0.5*length,nl)
    ypts = numpy.linspace(-0.5*width,0.5*width,nw)

    points_top = []
    points_bot = []
    for y in ypts:
        for x in xpts:
            if top_func == None:
                zval_top = 0.0
            else:
                zval_top = top_func(x,y)
            if bot_func == None:
                zval_bot = 0.0
            else:
                zval_bot = bot_func(x,y)
            points_top.append([x,y,0.5*height+zval_top])
            points_bot.append([x,y,-0.5*height+zval_bot])

    faces_top = []
    faces_bot = []
    numtop = len(points_top)
    for i in range(0,nl-1):
        for j in range(0,nw-1):
            # Top triangles
            f = [(j+1)*nl+i, (j+1)*nl+i+1, j*nl+i+1]
            faces_top.append(f)
            f = [(j+1)*nl+i, j*nl+i+1, j*nl+i]
            faces_top.append(f)
            # Botton triangles
            f = [numtop+j*nl+i+1, numtop+(j+1)*nl+i+1, numtop+(j+1)*nl+i]
            faces_bot.append(f)
            f = [numtop+j*nl+i, numtop+j*nl+i+1,  numtop+(j+1)*nl+i]
            faces_bot.append(f)

    faces_front = []
    faces_back = []
    for i in range(0,nl-1):
        # Front triangles
        f = [i+1,numtop+i+1,numtop+i]
        faces_front.append(f)
        f = [i,i+1,numtop+i]
        faces_front.append(f)
        # Back triangles
        f = [2*numtop-nl+i+1,numtop-nl+i+1,numtop-nl+i]
        faces_back.append(f)
        f = [2*numtop-nl+i,2*numtop-nl+i+1,numtop-nl+i]
        faces_back.append(f)

    faces_right = []
    faces_left = []
    for j in range(0,nw-1):
        # Right triangles
        f = [nl-1 +(j+1)*nl,numtop+nl-1+(j+1)*nl,numtop+nl-1+j*nl]
        faces_right.append(f)
        f = [nl-1 + j*nl,nl-1 +(j+1)*nl,numtop+nl-1+j*nl]
        faces_right.append(f)
        # Left triangles
        f = [numtop+(j+1)*nl,(j+1)*nl,j*nl]
        faces_left.append(f)
        f = [numtop+j*nl,numtop+(j+1)*nl,j*nl]
        faces_left.append(f)

    points = points_top + points_bot
    faces = faces_top + faces_bot
    faces.extend(faces_front)
    faces.extend(faces_back)
    faces.extend(faces_right)
    faces.extend(faces_left)

    p = Polyhedron(points=points,faces=faces)
    return p

def wedge_cut(obj,ang0,ang1,r,h,numpts=20,mod=''):
    """
    Cut out a wedge from obj from ang0 to ang1 with given radius r
    and height h.
    """
    ang0rad = DEG2RAD*ang0
    ang1rad = DEG2RAD*ang1
    angs = numpy.linspace(ang0rad,ang1rad,numpts)
    points_arc = [[r*numpy.cos(a),r*numpy.sin(a)] for a in angs]
    points = [[0,0]]
    points.extend(points_arc)
    paths = [range(0,len(points))]
    poly = Polygon(points=points, paths=paths)
    cut = Linear_Extrude(poly,h=h,mod=mod)
    cut_obj = Difference([obj,cut])
    return cut_obj

def partial_cylinder(h,r1,r2,ang0,ang1,cut_extra=1.0,mod=''):
    """
    Create a partial cylinder with given height h, start and end
    radii r1 and r2, from angle ang0 t0 angle ang1.
    """
    cut_ang0 = ang1
    cut_ang1 = ang0 + 360.0
    cyl = Cylinder(h=h,r1=r1,r2=r2)
    cut_r = max([r1,r2]) + cut_extra
    cut_h = h + cut_extra
    cut_cyl = wedge_cut(cyl,cut_ang0,cut_ang1,cut_r,cut_h,mod=mod)
    return cut_cyl

def ellipse_edged_disk(h,r,edge_scale=1.0):
    """
    Create a disk with an ellipse around the edge
    """
    assert edge_scale <= r, 'edge_scale must be <= disk radius'
    edge_len = 0.5*h*edge_scale
    disk = Cylinder(h=h,r1=r-edge_len,r2=r-edge_len)
    c = Circle(r=0.5*h)
    c = Scale(c,v=[edge_scale,1.0,1.0])
    c = Translate(c,v=[r-edge_len,0,0])
    torus = Rotate_Extrude(c)
    disk = Union([disk,torus])
    return disk

def rounded_disk(h,r,edge_r):
    pass



def right_triangle(x,y,z):
    """
    Creates an object which is a right triangle in the x,y plane  and height z.
    The hypotenuse of the triangle is given by sqrt(x**2 + y**2) and the right
    angle of the triangle is located at the origin.
    """
    rect_base = Cube(size=[x,y,z])
    rect_diff = Cube(size=[2*numpy.sqrt(x**2+y**2),y,2*z])
    rect_diff = Translate(rect_diff,v=[0,0.5*y,0])
    theta = -RAD2DEG(numpy.arctan2(y,x))
    rect_diff = Rotate(rect_diff,a=theta,v=[0,0,1])
    triangle = Difference([rect_base,rect_diff])
    triangle = Translate(triangle,v=[0.5*x, 0.5*y, 0])
    return triangle


def right_triangle_w_tabs(x, y, z, num_x=1, num_y=1, tab_depth='z', tab_epsilon=0.0,
        solid=True, removal_frac=0.6):
    """
    Creates a polygonal object which is a right triangle in the x,y plane with
    hypotenuse sqrt(x**2 + y**2). The shape is rectangular in the x,z and y,z
    planes with the z dimension given by z. Tabs are placed along the x and y
    edges of the part.

    Arguments:
    x = x dimension of part
    y = y dimension of part
    z = z dimension of (thickness)

    Keyword Arguments:
    num_x         = number of tabs along the x dimension of the triangle (default=1)
    num_y         = number of tabs along the y dimension of the triangle (default=1)
    tab_depth     = the length the tabs should stick out from the part. If set to
                    'z' this will be the z dimension or thickness of the part.
                    Otherwise it should be a number. (default = 'z')
    tab_epsilon   = amount the tabs should be over/under sized. 2 times this value
                    is added to the tabe width.
    solid         = specifies whether the part should be solid or not.
    removal_frac  = specifies the fraction of the interior to be removed. Only used
                    when solid == False

    """
    if tab_depth in ('z','Z'):
        # Sets the depth of the tabs to that of the part z dim (the thickness)
        tab_depth = z

    triangle = right_triangle(x,y,z)
    tabs = []
    tabs = []
    if num_x > 0:
        # Make x-tabs
        tab_x_width = x/(2.0*num_x+1) + 2*tab_epsilon
        tab_x_base = Cube(size=[tab_x_width,2*tab_depth,z])
        tab_x_pos = numpy.linspace(0,x,num_x+2)
        tab_x_pos = tab_x_pos[1:-1]
        for x_pos in tab_x_pos:
            tabs.append(Translate(tab_x_base,v=[x_pos,0,0]))
    if num_y > 0:
        # Make y-tabe
        tab_y_width = y/(2.0*num_y+1) + 2*tab_epsilon
        tab_y_base = Cube(size=[2*tab_depth,tab_y_width,z])
        tab_y_pos = numpy.linspace(0,y,num_y+2)
        tab_y_pos = tab_y_pos[1:-1]
        for y_pos in tab_y_pos:
            tabs.append(Translate(tab_y_base,v=[0,y_pos,0]))

    triangle = Union([triangle]+tabs)

    if solid == False:
        xx,yy = removal_frac*x, removal_frac*y
        sub_triangle = right_triangle(xx,yy,2*z)
        x_shift = (x - xx)/3.0
        y_shift = (y - yy)/3.0
        sub_triangle = Translate(sub_triangle,v=[x_shift,y_shift,0])
        triangle = Difference([triangle,sub_triangle])

    return triangle


def right_angle_bracket(length_base, length_face, width, thickness, num_x_tabs=2, num_y_tabs=2,bracket_frac=0.6):
    """
    Creates a right angle bracket -- not finished yet.
    """
    length_face_adj = length_face - thickness
    base = Cube(size=[length_base, width, thickness])
    face = Cube(size=[length_face_adj, width, thickness])
    face= Rotate(face,a=90,v=[0,1,0])
    x_shift = 0.5*length_base-0.5*thickness
    z_shift = 0.5*length_face_adj+0.5*thickness
    face = Translate(face,v=[x_shift,0,z_shift])

    bracket_x = bracket_frac*(length_base - thickness)
    bracket_y = bracket_frac*length_face_adj
    bracket = right_triangle_w_tabs(bracket_x,bracket_y,thickness,num_x=num_x_tabs,num_y=num_y_tabs)
    bracket = Rotate(bracket,a=90,v=[1,0,0])
    bracket = Rotate(bracket,a=180,v=[0,0,1])
    bracket = Translate(bracket,v=[0,0,0.5*thickness])
    bracket = Translate(bracket,v=[0.5*length_base-thickness,0,0])
    y_shift = 0.5*width-0.5*thickness
    bracket_pos = Translate(bracket,v=[0,y_shift,0])
    bracket_neg = Translate(bracket,v=[0,-y_shift,0])

    #base.mod = '%'
    #face.mod = '%'
    return [base,face,bracket_pos,bracket_neg]
