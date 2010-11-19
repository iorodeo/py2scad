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
import base
import utility

# Variable delcaration -------------------------------------------------------

class Variables(dict):
    """Group variable declarations for inclusion in output file."""
    # Any constructor kwargs become variables
    # Attribute getter returns the varaible name
    # Attribute setter sets variable value
    # cmd_str method returns variable definition in scad syntax
    def __init__(self, **kwargs):
        dict.__init__(self, kwargs)
        self._initialised = True

    def __getattr__(self, name):
        """Return the openscad representation of the indicated variable."""
        if name in self:
            return name
        raise AttributeError(name)

    def __setattr__(self, name, value):
        """Change the value of the named variable."""
        if not self.__dict__.has_key('_initialised'):  # this test allows attributes to be set in the __init__ method
            return dict.__setattr__(self, name, value)
        elif name in self: # any normal attributes are handled normally
            dict.__setattr__(self, name, value)
        else:
            self.__setitem__(name, value)

    def cmd_str(self, tab_level=0):
        tab_str = ' '*utility.TAB_WIDTH*tab_level
        rtn_str = '\n'
        for k,v in self.items():
            rtn_str += '{0} = {1};\n'.format(k, utility.val_to_str(v))
        return rtn_str + '\n'

# 3D primitives ---------------------------------------------------------------

class Cube(base.SCAD_Object):

    def __init__(self, size=1.0, center=True, *args, **kwargs):
        base.SCAD_Object.__init__(self, center=center, *args, **kwargs)
        self.size = size

    def cmd_str(self,tab_level=0):
        size_str = utility.val_to_str(self.size)
        center_str = self.center_str()
        return 'cube(size=%s,center=%s);'%(size_str, center_str)

class Sphere(base.SCAD_Object):

    def __init__(self, r=1.0, center=True, *args, **kwargs):
        base.SCAD_Object.__init__(self, center=center, *args, **kwargs)
        self.r = r

    def cmd_str(self,tab_level=0):
        r_str = utility.val_to_str(self.r)
        center_str = self.center_str()
        return 'sphere(r=%s,center=%s);'%(r_str, center_str)

class Cylinder(base.SCAD_Object):

    def __init__(self, h=1.0, r1=1.0, r2=None, center=True, *args, **kwargs):
        base.SCAD_Object.__init__(self, center=center, *args, **kwargs)
        self.h = h
        self.r1 = r1
        # r2 is optional
        self.r2 = r2

    def cmd_str(self,tab_level=0):
        center_str = self.center_str()
        h_str = utility.val_to_str(self.h)
        r1_str = utility.val_to_str(self.r1)
        if self.r2:
            r2_str = utility.val_to_str(self.r2)
            return 'cylinder(h={0},r1={1},r2={2},center={3});'.format(h_str,
                                                                      r1_str,
                                                                      r2_str,
                                                                      center_str)
        # When Cylinder is constant radius the argument is just called 'r'
        return 'cylinder(h=%s,r=%s,center=%s);'%(h_str, r1_str, center_str)

class Polyhedron(base.SCAD_Object):

    def __init__(self, points, faces, center=True, *args, **kwargs):
        base.SCAD_Object.__init__(self, center=center, *args, **kwargs)
        self.points = [utility.float_list3(x) for x in points]
        self.faces = [utility.float_list(x) for x in faces]

    def cmd_str(self,tab_level=0):
        tab_str0 = ' '*utility.TAB_WIDTH*tab_level
        tab_str1 = ' '*utility.TAB_WIDTH*(tab_level+1)
        rtn_str = 'polyhedron(\n'
        rtn_str = '%s%spoints = [\n'%(rtn_str,tab_str1,)
        for p in self.points:
            p_str = utility.val_to_str(p,tab_level=tab_level+2)
            rtn_str = '%s%s,\n'%(rtn_str,p_str)
        rtn_str = '%s%s],\n'%(rtn_str,tab_str1,)
        rtn_str = '%s%striangles = [\n'%(rtn_str,tab_str1,)
        for p in self.faces:
            p_str = utility.val_to_str(p,tab_level=tab_level+2)
            rtn_str = '%s%s,\n'%(rtn_str,p_str)
        rtn_str = '%s%s]\n'%(rtn_str,tab_str1,)
        rtn_str = '%s%s);\n'%(rtn_str,tab_str0)
        return rtn_str

class Import_STL(base.SCAD_Object):

    def __init__(self, filename, convexity=5, *args, **kwargs):
        base.SCAD_Object.__init__(self, *args, **kwargs)
        self.filename = filename
        self.convexity = convexity

    def cmd_str(self,tab_level=0):
        return 'import_stl("{0.filename}",convexity={0.convexity:d});'.format(self)

# 2D primatives ---------------------------------------------------------------

class Circle(base.SCAD_Object):

    def __init__(self, r=1, *args, **kwargs):
        base.SCAD_Object.__init__(self, *args, **kwargs)
        self.r = r

    def cmd_str(self,tab_level=0):
        r_str = utility.val_to_str(self.r)
        rtn_str = 'circle(r={0});'.format(r_str)
        return rtn_str

class Square(base.SCAD_Object):

    def __init__(self, size=[1,1], center=True, *args, **kwargs):
        base.SCAD_Object.__init__(self, center=center, *args, **kwargs)
        self.size = size

    def cmd_str(self,tab_level=0):
        size_str = utility.val_to_str(self.size)
        center_str = self.center_str()
        return 'square(size=%s,center=%s);'%(size_str,center_str)

class Polygon(base.SCAD_Object):

    def __init__(self, points, paths, *args, **kwargs):
        base.SCAD_Object.__init__(self, *args, **kwargs)
        self.points = [utility.float_list2(p) for p in points]
        self.paths = [utility.float_list(p) for p in paths]

    def cmd_str(self,tab_level=0):
        tab_str0 = ' '*utility.TAB_WIDTH*tab_level
        tab_str1 = ' '*utility.TAB_WIDTH*(tab_level+1)
        rtn_str = 'polygon(\n'
        rtn_str = '%s%spoints = [\n'%(rtn_str,tab_str1,)
        for p in self.points:
            p_str = utility.val_to_str(p,tab_level=tab_level+2)
            rtn_str = '%s%s,\n'%(rtn_str,p_str)
        rtn_str = '%s%s],\n'%(rtn_str,tab_str1,)
        rtn_str = '%s%spaths = [\n'%(rtn_str,tab_str1,)
        for p in self.paths:
            p_str = utility.val_to_str(p,tab_level=tab_level+2)
            rtn_str = '%s%s,\n'%(rtn_str,p_str)
        rtn_str = '%s%s]\n'%(rtn_str,tab_str1,)
        rtn_str = '%s%s);\n'%(rtn_str,tab_str0)
        return rtn_str

if __name__ == "__main__":
    v = Variables(foo=5)
    v.bar = [10, 2, 4]
    v.baz = "strings aren't usefull yet!"
    print("{0.foo}, {0.bar}, {0.baz}".format(v))
    print(v.cmd_str())
