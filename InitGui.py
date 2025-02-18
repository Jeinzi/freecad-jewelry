# Copyright 2022-2025, Julian Heinzel and the freecad-jewelry contributors
# SPDX-License-Identifier: AGPL-3.0-or-later


class JewelryWorkbench(Workbench):
  MenuText = "Jewelry"
  ToolTip = "Tools for goldsmiths and jewelry designers"
  Icon = """paste here the contents of a 16x16 xpm icon"""

  def Initialize(self):
    """This function is executed when FreeCAD starts"""
    import Jewelry # Import all the needed files that create the FreeCAD commands
    self.list = ["AddRing", "AddSetting"] # A list of command names created in the line above
    self.appendToolbar("Jewelry", self.list)
    self.appendMenu("Jewelry", self.list)
    #self.appendMenu(["Jewelry", "My submenu"], self.list) # appends a submenu to an existing menu

  def Activated(self):
    """This function is executed when the workbench is activated"""
    return

  def Deactivated(self):
    """This function is executed when the workbench is deactivated"""
    return

  def ContextMenu(self, recipient):
    """This is executed whenever the user right-clicks on screen"""
    # "recipient" will be either "view" or "tree"
    self.appendContextMenu("My commands", self.list) # add commands to the context menu

  def GetClassName(self):
    # This function is mandatory if this is a full Python workbench
    # This is not a template, the returned string should be exactly "Gui::PythonWorkbench"
    return "Gui::PythonWorkbench"
     
Gui.addWorkbench(JewelryWorkbench())
