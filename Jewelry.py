# Copyright 2022-2025, Julian Heinzel and the freecad-jewelry contributors
# SPDX-License-Identifier: AGPL-3.0-or-later

import Part
import FreeCAD as App
import FreeCADGui as Gui

import GemSetting
import RingGeneric



class AddRing:
  def Activated(self):
    if App.activeDocument() is None:
      App.newDocument()
    doc = App.activeDocument()

    # Use custom profile if a sketch is selected.
    sketch = None
    for sel in Gui.Selection.getSelection():
      if sel.TypeId == "Sketcher::SketchObject":
        sketch = sel

    obj = doc.addObject("Part::FeaturePython", "Ring")
    RingGeneric.RingGeneric(obj, sketch)
    obj.recompute()

  def GetResources(self):
    return {'Pixmap' : 'path_to_an_icon/myicon.png', 'MenuText': 'Add Ring', 'ToolTip': 'More detailed text'}



class AddSetting:
  def IsActive(self):
    for sel in Gui.Selection.getSelection():
      if bool(sel.Shape.Solids):
        return True
    return False

  def Activated(self):
    doc = App.activeDocument()
    if not Gui.Selection.getSelection():
      print("Please select a gemstone.")
      return

    for sel in Gui.Selection.getSelection():
      obj = doc.addObject("Part::FeaturePython", "Setting")
      GemSetting.Setting(obj, sel)
      obj.recompute()

  def GetResources(self):
    return {'Pixmap' : 'path_to_an_icon/myicon.png', 'MenuText': 'Add Setting', 'ToolTip': 'More detailed text'}



class ProngSetting:
  def Activated(self):
    doc = App.activeDocument()
    if not Gui.Selection.getSelection():
      print("Please select a gemstone.")
      return

    import ProngSetting
    obj = doc.addObject("Part::FeaturePython", "ProngSetting")
    ProngSetting.ProngSetting(obj)
    obj.ViewObject.Proxy = 0
    doc.recompute()

  def GetResources(self):
    return {'Pixmap' : 'path_to_an_icon/myicon.png', 'MenuText': 'Add Prong Setting', 'ToolTip': 'More detailed text'}



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
Gui.addCommand('AddSetting', AddSetting())
#Gui.addCommand('ProngSetting', ProngSetting())
