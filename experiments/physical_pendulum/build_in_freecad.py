"""Create & verify a tiny native FreeCAD project, inside FreeCADCmd 1.1.x."""
import csv
import math
import os
from pathlib import Path
import FreeCAD as App
import Part

OUT = Path(os.environ.get("PENDULUM_OUTPUT_DIR", "output")).resolve()
OUT.mkdir(parents=True, exist_ok=True)
L, WIDTH, THICK = 600.0, 30.0, 8.0
PIVOT = L * (0.5 - 1.0 / math.sqrt(12.0))
D, LM = (L / 2.0 - PIVOT) / 1000.0, L / 1000.0
OMEGA = math.sqrt(9.81 * D / (LM * LM / 12.0 + D * D))
PERIOD = 2.0 * math.pi / OMEGA
AMP = 10.0
assert abs(PIVOT - 126.794919243) < 0.0001
assert abs(PERIOD - 1.18118) < 0.002

doc = App.newDocument("PhysicalPendulum")
rod = doc.addObject("Part::Feature", "Rod")
rod.Label = "Moving rod, L = 600 mm"
rod.Shape = Part.makeBox(WIDTH, THICK, L,
                         App.Vector(-WIDTH / 2, -THICK / 2, PIVOT - L)).cut(
    Part.makeCylinder(4, THICK + 2,
                      App.Vector(0, -THICK / 2 - 1, 0), App.Vector(0, 1, 0)))
rod.addProperty("App::PropertyLength", "RodLength", "Physics")
rod.RodLength = L
rod.addProperty("App::PropertyLength", "PivotFromTop", "Physics")
rod.PivotFromTop = PIVOT
rod.addProperty("App::PropertyFloat", "SmallAnglePeriod", "Physics")
rod.SmallAnglePeriod = PERIOD
rod.addProperty("App::PropertyAngle", "Amplitude", "Physics")
rod.Amplitude = AMP
axle = doc.addObject("Part::Feature", "Axle")
axle.Label = "Fixed shaft"
axle.Shape = Part.makeCylinder(3.5, 48, App.Vector(0, -24, 0), App.Vector(0, 1, 0))
for name, y in [("WasherBack", -9.0), ("WasherFront", 6.0)]:
    washer = doc.addObject("Part::Feature", name)
    washer.Shape = Part.makeCylinder(9.0, 3.0, App.Vector(0, y, 0), App.Vector(0, 1, 0))
assert len(doc.Objects) == 4
assert all(obj.Shape.isValid() for obj in doc.Objects)
samples = []
for frame in range(73):
    t = frame / 30.0
    angle = AMP * math.cos(OMEGA * t)
    rod.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(0, 1, 0), angle))
    assert rod.Placement.Base.Length < 1e-10
    assert rod.Shape.isValid()
    samples.append((frame, round(t, 8), round(angle, 8)))
rod.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(0, 1, 0), AMP))
doc.recompute()
target = OUT / "PhysicalPendulum.FCStd"
doc.saveAs(str(target))
App.closeDocument(doc.Name)
reloaded = App.openDocument(str(target))
assert len(reloaded.Objects) == 4
assert all(obj.Shape.isValid() for obj in reloaded.Objects)
assert abs(float(reloaded.getObject("Rod").PivotFromTop) - PIVOT) < 0.001
App.closeDocument(reloaded.Name)
with (OUT / "pendulum_frames.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["frame", "time_s", "angle_deg"])
    writer.writerows(samples)
print("FREECAD_NATIVE_VERIFIED")
print("FreeCAD version:", App.Version())
print("Project:", target, "size:", target.stat().st_size)
print("valid solids: 4, frames: 73")
print("pivot_from_end_mm:", round(PIVOT, 6), "period_s:", round(PERIOD, 6))
