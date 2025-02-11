# Copyright 2025-2025, Julian Heinzel and the freecad-jewelry contributors
# SPDX-License-Identifier: AGPL-3.0-or-later

import builtins
import FreeCAD as App
import Part


def insert(filename, arg2):
  # See [GemCad user guide](https://www.gemcad.com/downloads/gemcadman.pdf),
  # page 21 for reference.
  with builtins.open(filename) as file:
    # Create raw block of material.
    # ToDo: Make sure block size is sufficient.
    blockSize = 10
    block = Part.makeBox(blockSize, blockSize, blockSize)
    block.Placement.Base = (-blockSize / 2, -blockSize / 2, -blockSize / 2)

    # Skip all lines that do not define planes.
    for line in file:
      if line[0] == 'g':
        # Index gear.
        fullRotation = int(line.split(' ')[1])
      if line[0] == 'a':
        # Header is done, now facet data is coming.
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
    while line:
      instructions = line.split(' ')
      if instructions[0] != "a":
        # If line does not begin with a, it (probably?) does not
        # define facets. A line can begin with "F" for the footnote
        # or G for cutting instructions.
        line = file.readline()
        continue

      facetAngle = float(instructions[1])
      if facetAngle < 0:
        facetAngle += 180
      r = float(instructions[2])
      skipNext = False
      for i in instructions[3:]:
        if skipNext:
          skipNext = False
          continue
        if i == "n":
          # The name of the facet will follow.
          skipNext = True
          continue
        if i == "G":
          # This introduces a comment until the end of the line.
          break

        # If no special letter instruction is detected, i is the
        # index within the previously defined full rotation.
        zAngle = float(i) / fullRotation * 360

        face = templateFace.copy()
        face.Placement.Base = (0, 0, r)
        face.rotate(App.Vector(), App.Vector(1,0,0), facetAngle)
        face.rotate(App.Vector(), App.Vector(0,0,1), zAngle)
        extrusion = face.extrude(blockSize * face.normalAt(0,0))
        block = block.cut(extrusion)

      line = file.readline()

  gem = App.ActiveDocument.addObject("Part::Feature", "Gem")
  gem.Shape = block
  #gem.ViewObject.DisplayMode = "Shaded"
  gem.ViewObject.Transparency = 20
  App.ActiveDocument.recompute()


def open(filename):
  doc = App.newDocument()
  insert(filename, None)
