# Copyright 2022-2025, Julian Heinzel and the freecad-jewelry contributors
# SPDX-License-Identifier: AGPL-3.0-or-later

import FreeCAD as App
import FreeCADGui as Gui
import Part


class AddRing:
  def Activated(self):
    doc = App.activeDocument()
    import RingGeneric
    obj = doc.addObject("Part::FeaturePython", "Ring")
    RingGeneric.RingGeneric(obj)
    obj.ViewObject.Proxy = 0
    doc.recompute()

  def GetResources(self):
    return {'Pixmap' : 'path_to_an_icon/myicon.png', 'MenuText': 'Add Ring', 'ToolTip': 'More detailed text'}



class AddStoneBrilliant:
  def Activated(self):
    doc = App.activeDocument()
    import StoneBrilliant
    obj = doc.addObject("Part::FeaturePython", "Brilliant")
    StoneBrilliant.StoneBrilliant(obj)
    obj.ViewObject.Proxy = 0
    doc.recompute()

  def GetResources(self):
    return {'Pixmap' : 'path_to_an_icon/myicon.png', 'MenuText': 'Add Brilliant', 'ToolTip': 'More detailed text'}


Gui.addCommand('AddRing', AddRing())
