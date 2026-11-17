#!/usr/bin/env python3
"""
run_gui.py — GUI-mode FreeCAD batch runner for Supercar macros.

Runs every macro with the GUI up (App.GuiUp == True) so that:
  - ViewObject colors/transparency from the macros are applied
  - GuiDocument.xml is embedded in the saved .FCStd
  - The saved file opens correctly in the FreeCAD GUI (parts visible in tree)

Usage (headless display with Xvfb):
    xvfb-run -a flatpak run org.freecad.FreeCAD freecad/run_gui.py
"""

import FreeCAD as App
import Part
import os

PROJECT_DIR = os.getcwd()
OUTPUT_DIR = os.path.join(PROJECT_DIR, "freecad", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("GUI up:", App.GuiUp)


def run_macro(macro_name, doc_name, output_prefix):
    macro_path = os.path.join(PROJECT_DIR, macro_name)
    with open(macro_path, "r") as f:
        macro_source = f.read()

    try:
        exec(macro_source, {"App": App, "Part": Part, "__name__": "__main__"})
    except Exception as e:
        print(f"ERROR running {macro_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

    try:
        doc = App.getDocument(doc_name)
    except Exception as e:
        print(f"ERROR: Document '{doc_name}' not found after running {macro_name}: {e}")
        return False

    doc.recompute()

    fcstd_path = os.path.join(OUTPUT_DIR, f"{output_prefix}.FCStd")
    doc.saveAs(fcstd_path)
    print(f"Saved (GUI): {fcstd_path}")

    App.closeDocument(doc_name)
    return True


macros = [
    ("freecad/FPV_RC_Direct_Print_Plate.py", "FPV_RC_Direct_Print_Plate", "print_plate"),
    ("freecad/Ferrari_Enzo_Modular_Assembly.py", "Ferrari_Enzo_Modular_Assembly", "ferrari_enzo_modular"),
]

print("=" * 60)
print("FreeCAD GUI Batch Runner")
print("=" * 60)

success = 0
for macro_name, doc_name, output_prefix in macros:
    print(f"\n--- Running {macro_name} ---")
    if run_macro(macro_name, doc_name, output_prefix):
        success += 1

print(f"\nCompleted: {success}/{len(macros)} macros (GUI mode)")
