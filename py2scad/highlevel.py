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
import scipy
from primatives import *
from transforms import *
from utility import DEG2RAD
from utility import RAD2DEG

def rounded_box(length,width,height,radius,round_x=True,round_y=True,round_z=True):
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

def grid_box(length, width, height, num_length, num_width,top_func=None,bot_func=None):
    """
    Create a box with given length, width, and height. The top and bottom surface of the
    box will be triangulate bases on a grid with num_length and num_width points. 
    Optional functions top_func and bot_func can be given to distort the top or bottom
    surfaces of the box. 
    """
    nl = num_length + 1
    nw = num_width + 1
    xpts = scipy.linspace(-0.5*length,0.5*length,nl)
    ypts = scipy.linspace(-0.5*width,0.5*width,nw)

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
    angs = scipy.linspace(ang0rad,ang1rad,numpts)
    points_arc = [[r*scipy.cos(a),r*scipy.sin(a)] for a in angs]
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



    





