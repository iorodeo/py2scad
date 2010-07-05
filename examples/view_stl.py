#!/usr/bin/env python
#
# view_stl.py - A simple vtk based stl file viewer
#
# Author: William Dickson 12/21/04
#
# --------------------------------------------------------------
import vtk, sys

stl_files = sys.argv[1:]

actor_list = []
for f in stl_files:

    # Create the reader and read a data file.  
    sr = vtk.vtkSTLReader()
    sr.SetFileName(f)

    # Connect the mapper and actor 
    stlMapper = vtk.vtkPolyDataMapper()
    stlMapper.SetInput(sr.GetOutput())
    stlActor = vtk.vtkLODActor()
    stlActor.SetMapper(stlMapper)
    actor_list.append(stlActor)

# Create the Renderer, RenderWindow, and RenderWindowInteractor
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Add the actors to the render; set the background and size
for a in actor_list:
    ren.AddActor(a)

ren.SetBackground(0.1, 0.2, 0.4)
renWin.SetSize(600, 600)

# Render
iren.Initialize()
ren.ResetCameraClippingRange()
renWin.Render()
iren.Start()
