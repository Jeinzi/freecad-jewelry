# Copyright 2022-2025, Julian Heinzel and the freecad-jewelry contributors
# SPDX-License-Identifier: AGPL-3.0-or-later

import Part
from math import *
import FreeCAD as App
import FreeCADGui as Gui


class Setting:
  def __init__(self, obj, selection):
    obj.Proxy = self
    obj.ViewObject.Proxy = 0
    obj.addProperty("App::PropertyFloat", "WallThickness", "", "Thickness of the outer wall of the bezel setting").WallThickness = 0.3
    obj.addProperty("App::PropertyFloat", "Margin", "", "Spacing between gem and setting").Margin = 0.05
    obj.addProperty("App::PropertyFloat", "StepDepthPercentage", "", "How far the step should reach down from the girdle towards the culet in relation to the pavilion depth.").StepDepthPercentage = 0.2
    obj.addProperty("App::PropertyFloat", "ProtrusionPercentage", "", "How much the setting should protrude above the girdle in relation to the crown height.").ProtrusionPercentage = 0.3
    obj.addProperty("App::PropertyFloat", "BottomExtension", "", "How much deeper the setting extends below the culet, in mm.").BottomExtension = 0.2
    obj.addProperty("App::PropertyFloat", "MaxNoncircularity", "", "Up to which deviation from an ideal circle the circular approximation is used, in percent.").MaxNoncircularity = 0.05
    obj.addProperty("App::PropertyLink", "Gem", "", "Which gem needs a setting?").Gem = selection


  def get_slice(self, shape, z):
    normal = App.Vector(0, 0, 1)
    wires = []
    for i in shape.slice(normal, z):
        wires.append(i)
    if len(wires) > 1:
      print("Warning: Unusual gem shape is not supported.")
    return wires[0]


  def is_similar(self, wire1, wire2, max_deviation):
    # Checks whether to wires span about the same area.
    face1 = Part.makeFace(wire1)
    face2 = Part.makeFace(wire2)
    dissimilarity = face1.Area/face2.Area - 1
    if abs(dissimilarity) < max_deviation:
      return True
    return False


  def execute(self, obj):
    # Assumptions for the setting generator:
    # - The gem has facets and thus vertices.
    # - The gem increases in circumference from the bottom to some
    #   point in the middle, where the facets are vertical (girdle), and then gets smaller again.

    # First, we'll move a copy of the gem to its original position.
    # There, the table must face in the z direction for all of the following to work.
    gem = obj.Gem.Shape.copy()
    gem.Placement.Rotation.Angle = 0
    gem.Placement.Base = (0, 0, 0)

    # We want to identify one vertex on the upper edge of the
    # girdle (upper_gv) and one on the lower part (lower_gv). To do
    # that, we search for vertices that have the greatest distance from
    # the center line of the stone (within the xy plane, ignoring z).
    # This returns the z coordinates of the gem's girdle.
    # Maybe this could be done more concisely by sorting numpy arrays?
    c = gem.BoundBox.Center

    max_r = float("-inf")
    upper_gv = None
    lower_gv = None
    eps = 10**-3
    for v in gem.Vertexes:
      dx = v.X - c.x
      dy = v.Y - c.y
      r = sqrt(dx**2 + dy**2)
      if abs(r - max_r) < eps:
        # If two vertices have the same distance r from the center,
        # compare z coordinate.
        if abs(v.Z - upper_gv.Z) < eps:
          # If z is also the same, nothing to do.
          continue
        # Else, assign upper_gv and lower_gv accordingly.
        if v.Z < upper_gv.Z:
          lower_gv = v
        else:
          lower_gv = upper_gv
          upper_gv = v
      elif r > max_r:
        # If we find a vertex at a greater radius, that's our new upper_gv
        # for now. Because of the vertical facets at the girdle, we'll
        # find another vertex at the same radius that's either
        # heigher or lower and then use that as lower_gv (or switch them).
        max_r = r
        upper_gv = v

    # Get some lengths to later define other values proportional to them.
    height = gem.BoundBox.ZMax - upper_gv.Z   # Length from girdle to top.
    depth = lower_gv.Z - gem.BoundBox.ZMin    # Length from girdle to bottom.
    girdle = upper_gv.Z - lower_gv.Z

    # How far down from the girdle should the step be?
    dz = depth*obj.StepDepthPercentage
    # Get cross section at that z coordinate.
    lower_slice = self.get_slice(gem, lower_gv.Z - dz)

    # Get cross section at the girdle. For some reason taking the
    # cross section in the middle works, but a cross section at
    # lower_gv.Z sometimes does not (for example pc04001.asc).
    upper_slice = self.get_slice(gem, lower_gv.Z+girdle/2)

    # Automatically simplify cross sections.
    # For round-ish shapes like a brilliant, a circle is used.
    # ToDo: For other shapes, maybe line segments, arcs or splines
    # could be used to approximate the 2D offset.
    upper_center = App.Vector(c.x, c.y, lower_gv.Z+girdle/2)
    normal = App.Vector(0, 0, 1)
    upper_circle = Part.Circle(upper_center, normal, max_r).toShape()
    if self.is_similar(upper_slice, upper_circle, obj.MaxNoncircularity):
      upper_slice = upper_circle

    # Check whether lower section is more or less a circle as well.
    lower_max_r = float("-inf")
    lower_center = App.Vector(c.x, c.y, lower_gv.Z - dz)
    for v in lower_slice.Vertexes:
      dx = v.X - lower_center.x
      dy = v.Y - lower_center.y
      r = sqrt(dx**2 + dy**2)
      if r > lower_max_r:
        lower_max_r = r
    lower_circle = Part.Circle(lower_center, normal, lower_max_r).toShape()
    if self.is_similar(lower_slice, lower_circle, obj.MaxNoncircularity):
      lower_slice = lower_circle

    # Move girdle cross section down to the step.
    upper_slice = upper_slice.translate(App.Vector(0, 0, -dz-girdle/2))

    # Offset the gem cross sections to create the wires that define
    # the lower and upper part of the step the gem rests on.
    outer_offset = upper_slice.makeOffset2D(obj.WallThickness+obj.Margin)
    mid_offset = upper_slice.makeOffset2D(obj.Margin)
    inner_offset = lower_slice.makeOffset2D(obj.Margin)

    # ToDo: Cut out the empty center of the setting in case part of
    # a ring is there.

    # Combine the wires to form the sections of the step...
    lower_compound = Part.makeCompound([outer_offset, inner_offset])
    upper_compound = Part.makeCompound([outer_offset, mid_offset])

    # ...and turn them into faces...
    lower_face = Part.makeFace(lower_compound)
    upper_face = Part.makeFace(upper_compound)

    # ...so they can be extruded to form a solid.
    lower_extrusion = lower_face.extrude(App.Vector(0, 0, -depth-obj.BottomExtension+dz))
    upper_extrusion = upper_face.extrude(App.Vector(0, 0, dz + girdle + height*obj.ProtrusionPercentage))

    # Fuse upper and lower part of the step together and refine.
    # Then move setting to gem position.
    setting = upper_extrusion.fuse(lower_extrusion).removeSplitter()
    obj.Shape = setting
    obj.Placement = obj.Gem.Placement
