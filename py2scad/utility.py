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
import math

TAB_WIDTH = 4
#DEG2RAD = math.pi/180.0
#RAD2DEG = 180.0/math.pi
DEG2RAD = math.degrees
RAD2DEG = math.radians

# Utility functions -----------------------------------------------------------

def float_list2(v):
    _v = float_list(v)
    assert len(_v) == 2, 'v must be convertable to a length2 list'
    return _v

def float_list3(v):
    _v = float_list(v)
    assert len(_v) == 3, 'v must be convertible to a length 3 list'
    return _v

def float_list4(v):
    _v = float_list(v)
    assert len(_v) == 4, 'v must be convertible to a length 4 list'
    return _v

def float_list(v):
    _v = list(v)
    _v = [float(x) for x in _v]
    return _v

def val_to_str(x,tab_level=0):
    tab_str = ''
    if tab_level:
        tab_str = ' '*TAB_WIDTH*tab_level
    if type(x) == float:
        x_str = '%s%f'%(tab_str,x,)
    else:
        x_str = '%s['%(tab_str,)
        cnt = 0
        for i,y in enumerate(x):
            x_str = '%s%s'%(x_str,val_to_str(y))
            if i < len(x)-1:
                x_str = '%s, '%(x_str,)
            cnt += 1
            if cnt >= 8:
                cnt = 0
                x_str = '%s\n%s'%(x_str,tab_str)
        x_str = '%s]'%(x_str,)
    return x_str

def write_obj_list(obj_list, filename, fn=100):
    fid = open(filename,'w')
    fid.write('$fn=%d;\n'%(fn,))
    for obj in obj_list:
        fid.write('%s\n'%(obj,))
    fid.close()
