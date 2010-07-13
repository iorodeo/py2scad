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

# 3D transformations ---------------------------------------------------------

class Scale(base.SCAD_CMP_Object):

    def __init__(self,obj,v=[1.0,1.0,1.0], mod=''):
        base.SCAD_CMP_Object.__init__(self, obj, mod=mod)
        self.v = utility.float_list3(v)

    def cmd_str(self,tab_level=0):
        v_str = utility.val_to_str(self.v)
        return 'scale(v=%s)'%(v_str)

class Rotate(base.SCAD_CMP_Object):

    def __init__(self,obj,a=0.0,v=[1.0,0.0,0.0],mod=''):
        base.SCAD_CMP_Object.__init__(self,obj,mod=mod)
        self.a = float(a)
        self.v = utility.float_list3(v) 

    def cmd_str(self,tab_level=0):
        a_str = utility.val_to_str(self.a)
        v_str = utility.val_to_str(self.v)
        return 'rotate(a=%s,v=%s)'%(a_str,v_str)

class AnimRotate(base.SCAD_CMP_Object):

    def __init__(self,obj,a=0.0,v=[0.0,0.0,0.0],mod=''):
        base.SCAD_CMP_Object.__init__(self,obj,mod=mod)
        self.a = a
        self.v = v

    def cmd_str(self,tab_level=0):
        return 'rotate(a=%s,v=%s)'%(self.a,self.v)

class Translate(base.SCAD_CMP_Object):

    def __init__(self,obj,v=[0.0,0.0,0.0],mod=''):
        base.SCAD_CMP_Object.__init__(self,obj,mod=mod)
        self.v = utility.float_list3(v)

    def cmd_str(self,tab_level=0):
        v_str = utility.val_to_str(self.v)
        return 'translate(v=%s)'%(v_str,)

class AnimTranslate(base.SCAD_CMP_Object):

    def __init__(self,obj,v=[0.0,0.0,0.0],mod=''):
        base.SCAD_CMP_Object.__init__(self,obj,mod=mod)
        self.v = v

    def cmd_str(self,tab_level=0):
        return 'translate(v=%s)'%(self.v,)
       
class Mirror(base.SCAD_CMP_Object):

    def __init__(self,obj,v=[1.0,0.0,0.0],mod=''):
        base.SCAD_CMP_Object.__init__(self,obj,mod=mod)
        self.v = utility.float_list3(v)

    def cmd_str(self,tab_level=0):
        v_str = utility.val_to_str(self.v)
        return 'mirror(v=%s)'%(v_str,)

class MultMatrix(base.SCAD_CMP_Object):

    #######################################
    # NOT DONE
    #######################################

    def __init__(self,obj):
        base.SCAD_CMP_Object.__init__(self,obj,mod=mod)
        pass

class Color(base.SCAD_CMP_Object):

    def __init__(self,obj,rgba=[0.5, 0.5, 0.5, 1.0],mod=''):
        base.SCAD_CMP_Object.__init__(self,obj,mod=mod)
        self.rgba = utility.float_list4(rgba)
        assert self.rgba_ok(), 'rgba values must be in [0,1]'

    def cmd_str(self,tab_level=0):
        rgba_str = utility.val_to_str(self.rgba)
        return 'color(%s)'%(rgba_str,)

    def rgba_ok(self):
        for x in self.rgba:
            if x < 0.0 or x > 1.0:
                return False
        return True

# CGS Operations -------------------------------------------------------------

class Union(base.SCAD_CMP_Object):

    def cmd_str(self,tab_level=0):
        return 'union()'

class Difference(base.SCAD_CMP_Object):

    def cmd_str(self,tab_level=0):
        return 'difference()'

class Intersection(base.SCAD_CMP_Object):

    def cmd_str(self,tab_level=0):
        return 'intersection()'
    
# 2D to 3D Extrusion -----------------------------------------------------------

class Linear_Extrude(base.SCAD_CMP_Object):

    def __init__(self,obj,h=1, twist=0, center=True, mod='', convexity=5,slices=None):
        base.SCAD_CMP_Object.__init__(self,obj,center=center,mod=mod)
        self.h = float(h)
        self.twist = float(twist)
        self.convexity = int(convexity)
        try:
            self.slices = int(slices)
        except TypeError:
            self.slices = None

    def cmd_str(self,tab_level=0):
        h_str = utility.val_to_str(self.h)
        twist_str = utility.val_to_str(self.twist)
        center_str = self.center_str()
        if self.slices == None:
            str_tup = (h_str,twist_str,center_str,self.convexity)
            rtn_str = 'linear_extrude(height=%s,twist=%s,center=%s,convexity=%d)'%str_tup
        else:
            str_tup = (h_str,twist_str,center_str,self.convexity,self.slices)
            rtn_str = 'linear_extrude(height=%s,twist=%s,center=%s,convexity=%d,slices=%d)'%str_tup
        return rtn_str

class Linear_DXF_Extrude(base.SCAD_Object):

    def __init__(self,filename,height=1.0,layer=None,center=True,convexity=10,twist=0,mod=''):
        base.SCAD_Object.__init__(self,center=center,mod=mod)
        self.filename = filename
        self.height = float(height)
        self.layer = layer
        self.twist = float(twist)
        self.convexity = int(convexity)

    def cmd_str(self, tab_level=0):
        arg_str = 'file="%s"'%(self.filename,)
        if not self.layer == None:
            arg_str = '%s, layer=%s'%(arg_str,self.layer,)
        arg_str = '%s, height=%f'%(arg_str,self.height)
        arg_str = '%s, center=%s'%(arg_str,self.center_str())
        arg_str = '%s, convexity=%d'%(arg_str,self.convexity)
        arg_str = '%s, twist=%f'%(arg_str,self.twist)
        return 'linear_extrude(%s);'%(arg_str,)

class Rotate_Extrude(base.SCAD_CMP_Object):

    def __init__(self,obj,convexity=5,mod=''):
        base.SCAD_CMP_Object.__init__(self,obj,mod=mod)
        self.convexity = convexity

    def cmd_str(self,tab_level=0):
        rtn_str = 'rotate_extrude(convexity=%d)'%(self.convexity,)
        return rtn_str


# 3D to 2D projection ---------------------------------------------------------

class Projection(base.SCAD_CMP_Object):

    def __init__(self,obj,cut=True,mod=''):
        base.SCAD_CMP_Object.__init__(self,obj,mod=mod)
        self.cut = cut

    def cmd_str(self,tab_level=0):
        cut_str = '%s'%(self.cut,)
        cut_str = cut_str.lower()
        return 'projection(cut=%s)'%(cut_str,)
