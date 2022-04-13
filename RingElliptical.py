class RingElliptical:
  def __init__(self, obj):
    obj.Proxy = self
    obj.addProperty("App::PropertyFloat", "Size").Size = 50
    obj.addProperty("App::PropertyFloat", "Width").Width = 5
    obj.addProperty("App::PropertyFloat", "Thickness").Thickness = 2

  def execute(self, obj):
    import FreeCAD as App
    import Part, math
    # if len(App.ActiveDocument.getObjectsByLabel("myLine")) == 0:
    #   line = App.ActiveDocument.addObject("Part::Line", "myLine")
    #   line.X1 = 0
    #   line.Y1 = -32
    #   line.Z1 = 0
    #   line.X2 = 0
    #   line.Y2 = 32
    #   line.Z2 = 0

    e = Part.Ellipse()
    e.MajorRadius = obj.Width / 2
    e.MinorRadius = obj.Thickness / 2
    wire = Part.Wire(e.toShape().Edges)
    face = Part.Face(wire)
    face.Placement.Rotation = App.Rotation(90, 0, 90)
    face.Placement.Base = (0, 0, obj.Size/2/math.pi + e.MinorRadius)
    solid = face.revolve(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 360)

    obj.Shape = solid
