#!/usr/bin/env python3
"""
run_headless.py — FreeCAD headless runner for Supercar macros
Runs all FreeCAD Python macros and saves .FCStd + .stl files.

Usage:
    flatpak run --command=FreeCADCmd org.freecad.FreeCAD -c "exec(open('freecad/run_headless.py').read())"
"""

import FreeCAD as App
import Part
import Mesh
import os

PROJECT_DIR = os.getcwd()
OUTPUT_DIR = os.path.join(PROJECT_DIR, "freecad", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_macro(macro_name, doc_name, output_prefix):
    """Run a FreeCAD macro file, save as .FCStd, and export STL for each object."""
    macro_path = os.path.join(PROJECT_DIR, macro_name)
    
    # Read the macro source
    with open(macro_path, "r") as f:
        macro_source = f.read()
    
    # Execute the macro (it creates its own document via App.newDocument)
    try:
        exec(macro_source, {"App": App, "Part": Part, "__name__": "__main__"})
    except Exception as e:
        print(f"ERROR running {macro_name}: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Get the document created by the macro
    try:
        doc = App.getDocument(doc_name)
    except Exception as e:
        print(f"ERROR: Document '{doc_name}' not found after running {macro_name}: {e}")
        return False
    
    # Recompute
    doc.recompute()
    
    # Save as .FCStd
    fcstd_path = os.path.join(OUTPUT_DIR, f"{output_prefix}.FCStd")
    doc.saveAs(fcstd_path)
    print(f"Saved: {fcstd_path}")
    
    # Export each object as STL
    stl_count = 0
    for obj in doc.Objects:
        if hasattr(obj, "Shape") and obj.Shape is not None:
            stl_path = os.path.join(OUTPUT_DIR, f"{output_prefix}_{obj.Name}.stl")
            Mesh.export([obj], stl_path)
            print(f"  Exported: {stl_path}")
            stl_count += 1
    
    # Close the document
    App.closeDocument(doc_name)
    
    print(f"  Objects exported: {stl_count}")
    return True

# ==========================================
# Run all macros
# ==========================================
macros = [
    ("freecad/rc_gearboxes.py", "RC_Car_Gearboxes_500g", "gearboxes"),
    ("freecad/complete_chassis_v2.py", "Complete_FPV_RC_Chassis_500g_v2", "chassis_v2"),
    ("freecad/body_shell.py", "FPV_RC_Aerodynamic_Shell", "body_shell"),
    ("freecad/wheels_tires.py", "RC_Car_Wheels_And_Tires_500g", "wheels_tires"),
]

print("=" * 60)
print("FreeCAD Headless Batch Runner")
print("=" * 60)

success_count = 0
for macro_name, doc_name, output_prefix in macros:
    print(f"\n--- Running {macro_name} ---")
    if run_macro(macro_name, doc_name, output_prefix):
        success_count += 1

print(f"\n{'=' * 60}")
print(f"Completed: {success_count}/{len(macros)} macros")
print(f"Output directory: {OUTPUT_DIR}")
print(f"{'=' * 60}")