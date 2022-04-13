import FreeCAD as App
import FreeCADGui as Gui
import Part

class AddRing:
  def Activated(self):
    App.Console.PrintMessage('Hello, World!')
    doc = App.activeDocument()
    
    #e = Part.Ellipse()
    #e.MajorRadius = 3
    #e.MinorRadius = 1
    #s = e.toShape()
    #w = Part.Wire(s.Edges)
    #f = Part.Face(w)
    #extrusion = f.extrude(App.Vector(0, 0, 5))
    #docObj = doc.addObject("Part::Feature", "Ellipse Extrusion")
    #docObj.Shape = extrusion
    #doc.recompute()

    e = Part.Ellipse()
    e.MajorRadius = 2
    e.MinorRadius = 1
    shape = e.toShape()
    w = Part.Wire(shape.Edges)
    f = Part.Face(w)
    docObjProfile = doc.addObject("Part::Feature", "Profile 1")
    docObjProfile.Shape = f
    docObjProfile.Placement.Rotation = App.Rotation(90, 0, 90)

    docObjRing = doc.addObject("Part::Revolution", "Ring")
    docObjRing.Source = docObjProfile
    docObjRing.Angle = 360
    docObjRing.Base = (0, 0, -19)
    docObjRing.Axis = (0, 1, 0)
    doc.recompute()

  def GetResources(self):
    return {'Pixmap' : 'path_to_an_icon/myicon.png', 'MenuText': 'Add Ring', 'ToolTip': 'More detailed text'}


Gui.addCommand('AddRing', AddRing())
