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

# 3D primitives ---------------------------------------------------------------

class Cube(base.SCAD_Object):

    def __init__(self, size=1.0, center=True, mod=''):
        base.SCAD_Object.__init__(self,center=center,mod=mod)
        try:
            self.size = float(size)
        except:
            self.size = utility.float_list3(size)

    def cmd_str(self,tab_level=0):
        size_str = utility.val_to_str(self.size)
        center_str = self.center_str()
        return 'cube(size=%s,center=%s);'%(size_str,center_str)

class Sphere(base.SCAD_Object):

    def __init__(self, r=1.0, center=True,mod=''):
        base.SCAD_Object.__init__(self,center=center,mod=mod)
        self.r = float(r)

    def cmd_str(self,tab_level=0):
        r_str = utility.val_to_str(self.r)
        center_str = self.center_str()
        return 'sphere(r=%s,center=%s);'%(r_str, center_str)

class Cylinder(base.SCAD_Object):

    def __init__(self, h=1.0, r1=1.0, r2=None, center=True, mod=''):
        base.SCAD_Object.__init__(self,center=center,mod=mod)
        self.h = float(h)
        self.r1 = float(r1)
        # r2 is optional
        self.r2 = r2
        if r2:
            self.r2 = float(r2)

    def cmd_str(self,tab_level=0):
        center_str = self.center_str()
        h_str = utility.val_to_str(self.h)
        r1_str = utility.val_to_str(self.r1)
        if self.r2:
            r2_str = utility.val_to_str(self.r2)
            return 'cylinder(h=%s,r1=%s,r2=%s,center=%s);'%(h_str, r1_str, r2_str, center_str)
        return 'cylinder(h=%s,r=%s,center=%s);'%(h_str, r1_str, center_str)

class Polyhedron(base.SCAD_Object):

    def __init__(self, points, faces, center=True, mod=''):
        base.SCAD_Object.__init__(self,center=center,mod=mod)
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

    def __init__(self, filename, convexity=5,mod=''):
        base.SCAD_Object.__init__(self,mod=mod)
        self.filename = filename
        self.convexity = convexity

    def cmd_str(self,tab_level=0):
        return 'import_stl("%s",convexity=%d);'%(self.filename,self.convexity)

# 2D primatives ---------------------------------------------------------------

class Circle(base.SCAD_Object):

    def __init__(self,r=1,mod=''):
        base.SCAD_Object.__init__(self,mod=mod)
        self.r = float(r)

    def cmd_str(self,tab_level=0):
        r_str = utility.val_to_str(self.r)
        rtn_str = 'circle(r=%s);'%(r_str,)
        return rtn_str

class Square(base.SCAD_Object):

    def __init__(self,size=[1,1],center=True, mod=''):
        base.SCAD_Object.__init__(self,center=center,mod=mod)
        self.size = utility.float_list2(size)

    def cmd_str(self,tab_level=0):
        size_str = utility.val_to_str(self.size)
        center_str = self.center_str()
        return 'square(size=%s,center=%s);'%(size_str,center_str)

class Polygon(base.SCAD_Object):

    def __init__(self,points,paths,mod=''):
        base.SCAD_Object.__init__(self,mod=mod)
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
