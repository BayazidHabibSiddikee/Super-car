#!/usr/bin/env python3
"""
render_images.py — render high-resolution PNG images of the FCStd designs.

Runs in GUI mode (xvfb), opens each generated document, sets the camera,
and saves the 3D view via ActiveView.saveImage().

Usage:
    xvfb-run -a flatpak run org.freecad.FreeCAD freecad/render_images.py
"""

import FreeCAD as App
import FreeCADGui as Gui
import os

PROJECT_DIR = os.getcwd()
OUT_DIR = os.path.join(PROJECT_DIR, "docs", "images")
os.makedirs(OUT_DIR, exist_ok=True)

JOBS = [
    # (fcstd path, output name, view, width, height)
    ("freecad/output/print_plate.FCStd", "render_print_plate", "isometric", 1920, 1200),
    ("freecad/output/enzo_fpv_v2.FCStd", "render_enzo_fpv_v2", "isometric", 1920, 1200),
    ("freecad/output/enzo_fpv_v2.FCStd", "render_enzo_fpv_v2_top", "top", 1920, 1200),
    ("freecad/output/ferrari_enzo_fixed.FCStd", "render_ferrari_enzo_fixed", "isometric", 1920, 1200),
    ("freecad/output/ferrari_enzo_fixed.FCStd", "render_ferrari_enzo_fixed_top", "top", 1920, 1200),
    ("freecad/output/enzo_fpv_v3.FCStd", "render_enzo_fpv_v3", "isometric", 1920, 1200),
    ("freecad/output/enzo_fpv_v3.FCStd", "render_enzo_fpv_v3_top", "top", 1920, 1200),
]

VIEWS = {
    "isometric": lambda v: v.viewIsometric(),
    "top": lambda v: v.viewTop(),
}


def render(path, name, view_name, w, h):
    doc = App.openDocument(os.path.join(PROJECT_DIR, path))
    doc.recompute()
    v = Gui.ActiveDocument.ActiveView
    VIEWS[view_name](v)
    Gui.SendMsgToActiveView("ViewFit")
    out = os.path.join(OUT_DIR, name + ".png")
    v.saveImage(out, w, h, "Current")
    print("Rendered:", out)
    App.closeDocument(doc.Name)


for path, name, view_name, w, h in JOBS:
    try:
        render(path, name, view_name, w, h)
    except Exception as e:
        print("ERROR rendering", name, ":", e)

print("RENDER BATCH DONE")
