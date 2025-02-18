# Copyright 2025-2025, Julian Heinzel and the freecad-jewelry contributors
# SPDX-License-Identifier: AGPL-3.0-or-later

import Gem
import Part
import builtins
import FreeCAD as App
from enum import Enum


class AscParsingState(Enum):
  Comment = 0
  Angle = 1
  Radius = 2
  FacetName = 3
  Index = 4


def insert(path, arg2):
  # See [GemCad user guide](https://www.gemcad.com/downloads/gemcadman.pdf),
  # page 21 for reference.
  with builtins.open(path, encoding="ISO-8859-1") as file:
    # Create raw block of material.
    # ToDo: Make sure block size is sufficient.
    blockSize = 10
    block = Part.makeBox(blockSize, blockSize, blockSize)
    block.Placement.Base = (-blockSize / 2, -blockSize / 2, -blockSize / 2)

    # Skip all lines that do not define planes.
    header = []
    footer = []
    for line in file:
      if line[0] == 'g':
        # Index gear.
        fullRotation = int(line.split(' ')[1])
      if line[0] == "H":
        header.append(line[2:])
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

    # Gather instructions.
    instruction_lines = [line]
    for line in file:
      if line.startswith("F"):
        footer.append(line[2:])
        continue
      instruction_lines.append(line)

    # Instructions are separated by spaces. Related instructions can
    # span multiple lines, so all lines are concatenated.
    # Newlines are important as they terminate comments.
    instructions = "".join(instruction_lines).replace("\n", " \n ").split(" ")

    # Parse instructions.
    state = None
    for i in instructions:
      if i == "":
        # Could be caused by double spaces.
        continue

      if state == AscParsingState.FacetName:
        # Facet name is ignored. Note that the name could be anything,
        # even one of the magic letters below, see for example pc09168.
        # This is why this check needs to be up here.
        # After the name, more indices are coming up.
        state = AscParsingState.Index
        continue
      if state == AscParsingState.Comment and i != "\n":
        continue

      # Recognize special letter instructions and set the state
      # accordingly to properly interpret the values coming afterwards.
      if i == "a":
        # Introduces a facet set, its angle will be the next instruction.
        state = AscParsingState.Angle
        continue
      if i == "n":
        # The name of the facet will follow.
        state = AscParsingState.FacetName
        continue
      if i == "G":
        # This introduces a comment until the end of the line.
        state = AscParsingState.Comment
        continue
      if i == "\n":
        # Comments end at the end of a line. Apart from that, newlines
        # are ignored.
        if state == AscParsingState.Comment:
          state = None
        continue

      # Sanity check: The state should not be None. For example,
      # after a comment, a new special letter must follow immetiately.
      assert state is not None

      # Parse parameters supplied after special letter instructions.
      if state == AscParsingState.Angle:
        # Read the angle of the current facet set. The radius should come next.
        facetAngle = float(i)
        if facetAngle < 0:
          facetAngle += 180
        state = AscParsingState.Radius
        continue
      if state == AscParsingState.Radius:
        # Read the radius of the current facet set. Next, indices should come.
        r = float(i)
        state = AscParsingState.Index
        continue
      if state == AscParsingState.Index:
        # i is an index within the previously defined full rotation.
        zAngle = float(i) / fullRotation * 360
        face = templateFace.copy()
        face.Placement.Base = (0, 0, r)
        face.rotate(App.Vector(), App.Vector(1,0,0), facetAngle)
        face.rotate(App.Vector(), App.Vector(0,0,1), zAngle)
        extrusion = face.extrude(blockSize * face.normalAt(0,0))
        block = block.cut(extrusion)

  filename = path.split("/")[-1].split(".")[0]
  gem = App.ActiveDocument.addObject("Part::FeaturePython", "Gem")
  Gem.Gem(gem, block, filename, "".join(header).strip(), "".join(footer).strip())
  App.ActiveDocument.recompute()


def open(path):
  doc = App.newDocument()
  insert(path, None)
