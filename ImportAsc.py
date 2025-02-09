# Copyright 2025-2025, Julian Heinzel and the freecad-jewelry contributors
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import builtins
import numpy as np
import FreeCAD as App
import Part

def insert(filename, arg2):
  with builtins.open(filename) as file:
    # Create raw block of material.
    blockSize = 10
    block = Part.makeBox(blockSize, blockSize, blockSize)
    block.Placement.Base = (-blockSize / 2, -blockSize / 2, -blockSize / 2)
    #Part.show(block)

    # Skip all lines that do not define planes.
    #fullRotation = 96
    for l in file:
      if l[0] == 'g':
        fullRotation = int(l.split(' ')[1])
      if l[0] == 'a':
        break

    # Create a basic plane.
    planeSize = 2 * blockSize
    points = [
      App.Vector(planeSize, planeSize, 0),
      App.Vector(-planeSize, planeSize, 0),
      App.Vector(-planeSize, -planeSize, 0),
      App.Vector(planeSize, -planeSize, 0)
    ]
    lines = [
      Part.LineSegment(points[0], points[1]),
      Part.LineSegment(points[1], points[2]),
      Part.LineSegment(points[2], points[3]),
      Part.LineSegment(points[3], points[0]),
    ]
    edges = [Part.Edge(l) for l in lines]
    templateFace = Part.Face(Part.Wire(edges))

    # Parse cutting planes.
    while l:
      arr = l.split(' ')[1:]
      planeAngle = float(arr[0])
      if planeAngle < 0:
        planeAngle += 180
      r = arr[1]
      skipNext = False
      for zAngle in arr[2:]:
        if skipNext:
          skipNext = False
          continue
        if zAngle == "n":
          skipNext = True
          continue

        zAngle = int(zAngle) / fullRotation * 360

        face = templateFace.copy()
        face.Placement.Base = (0, 0, r)
        face.rotate(App.Vector(), App.Vector(1,0,0), planeAngle)
        face.rotate(App.Vector(), App.Vector(0,0,1), zAngle)
        #Part.show(face)
        extrusion = face.extrude(blockSize * face.normalAt(0,0))
        block = block.cut(extrusion)

      l = file.readline()
  Part.show(block)
  doc.recompute()

def open(filename):
  doc = App.newDocument()
  insert(filename)
