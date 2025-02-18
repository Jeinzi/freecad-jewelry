# Copyright 2022-2025, Julian Heinzel and the freecad-jewelry contributors
# SPDX-License-Identifier: AGPL-3.0-or-later

import math
import Part
import FreeCAD as App


class RingGeneric:
  def __init__(self, obj, sketch=None):
    obj.Proxy = self
    if obj.ViewObject is not None:
      obj.ViewObject.Proxy = 0

    # https://wiki.freecad.org/FeaturePython_Custom_Properties
    obj.addProperty("App::PropertyFloat", "Size", "", "Inner ring circumference in mm. (ISO 8653:2016)").Size = 57
    obj.addProperty("App::PropertyFloat", "Width", "", "Axial width of the ring.").Width = 5
    obj.addProperty("App::PropertyFloat", "Thickness", "", "Radial thickness of the ring.").Thickness = 2
    #obj.addProperty("App::PropertyBool", "Correct_Shrinkage", "", "Correct for shrinking of cast material when cooling").Correct_Shrinkage = True
    obj.addProperty("App::PropertyEnumeration", "Profile", "", "Presets for the ring cross section. Will be ignored if custom sketch is linked.").Profile = ["Elliptical", "Rectangular"]
    obj.addProperty("App::PropertyLink", "CustomProfile", "", "Select a sketch with a custom cross section.")
    if sketch is not None:
      obj.CustomProfile = sketch

    # https://en.wikipedia.org/wiki/Ring_size
    title_size_section = "International Sizes (read only)"
    obj.addProperty("App::PropertyFloat", "NorthAmerican", title_size_section, "Ring size used in Canada, Mexico and the US.", read_only=True)
    obj.addProperty("App::PropertyFloat", "Swiss", title_size_section, "Ring size used in Switzerland, Italy and Spain.", read_only=True)
    obj.addProperty("App::PropertyFloat", "Diameter", title_size_section, "Inner diameter in mm.", read_only=True)


  def update_sizes(self, obj):
    obj.NorthAmerican = (obj.Size - 36.5) / (2.55348651)
    obj.Diameter = obj.Size/math.pi
    obj.Swiss = obj.Size - 40


  def execute(self, obj):
    if obj.CustomProfile is not None:
      shape = obj.CustomProfile.Shape.copy()
      shape.Placement.Base.z = obj.Size/2/math.pi
      face = Part.Face(shape.Wires)
    elif obj.Profile == "Elliptical":
      rot = 0
      w = obj.Width
      t = obj.Thickness
      if t > w:
        # Ellipse major radius can't be bigger than minor radius.
        rot = 90
        t,w = w,t
      e = Part.Ellipse()
      e.MajorRadius = w / 2
      e.MinorRadius = t / 2
      wire = Part.Wire(e.toShape().Edges)
      face = Part.Face(wire)
      face.Placement.Rotation = App.Rotation(90, rot, 90)
      face.Placement.Base = (0, 0, obj.Size/2/math.pi + obj.Thickness/2)
    else:
      v1 = App.Vector(0, -obj.Width/2, 0)
      v2 = App.Vector(0, obj.Width/2, 0)
      v3 = App.Vector(0, obj.Width/2, obj.Thickness)
      v4 = App.Vector(0, -obj.Width/2, obj.Thickness)
      l1 = Part.LineSegment(v1, v2)
      l2 = Part.LineSegment(v2, v3)
      l3 = Part.LineSegment(v3, v4)
      l4 = Part.LineSegment(v4, v1)
      s1 = Part.Shape([l1, l2, l3, l4])
      w = Part.Wire(s1.Edges)
      face = Part.Face(w)
      face.Placement.Base = (0, 0, obj.Size/2/math.pi)

    solid = face.revolve(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 360)
    obj.Shape = solid
    self.update_sizes(obj)
