# Copyright 2025-2025, Julian Heinzel and the freecad-jewelry contributors
# SPDX-License-Identifier: AGPL-3.0-or-later

import Part
from math import *
import FreeCAD as App


class Gem:
  def __init__(self, obj, shape, name):
    obj.Proxy = self
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "Name", "", "Name of the gem - does not matter").Name = name
    obj.addProperty("App::PropertyFloat", "Density", "", "Density of the gemstone in kg/m³").Density = 3515
    obj.addProperty("App::PropertyFloat", "Carats", "", "Weight of the gem in ct").Carats = self.calc_carats(obj)
    self.last_carats = obj.Carats

    if obj.ViewObject is not None:
      # ViewObject does not exist in headless mode.
      obj.ViewObject.Transparency = 20
      obj.ViewObject.Proxy = 0


  def calc_carats(self, obj, volume=None):
    if volume is None:
      volume = obj.Shape.Volume
    return volume * obj.Density / 10**6 * 5


  def execute(self, obj):
    # If density has changed, just update weight in carats.
    # If carats have changed, scale gemstone appropriately.
    if self.last_carats != obj.Carats:
      current_carats = self.calc_carats(obj) # In case density has changed.
      factor = (obj.Carats / current_carats)**(1/3)
      obj.Shape = obj.Shape.scaled(factor)
      # ToDo: Fix position

    obj.Carats = self.calc_carats(obj)
    self.last_carats = obj.Carats

    #print(f"{new_scale=}, {old_scale=}")
    #print(f"new factor: {factor}")
