import os
import sys
from pathlib import Path
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.append(str(SCRIPTS_DIR))
from utils import (import_obj, assign_material, keep_top_surface_only, link_material, render_and_save)

def _parse_args():
    if "--" not in sys.argv:
        return None
    args = sys.argv[sys.argv.index("--") + 1:]
    if len(args) < 4:
        return None
    return (args[0], args[1], args[2], args[3])


def main():
    parsed = _parse_args()
    if parsed is None:
        print(
            "Usage: blender -b <scene.blend> -P Scripts/render.py -- "
            "<initial.obj> <final.obj> <output.png> <material_name>"
        )
        return 2

    undeformed_path, deformed_path, output_path, material_name = parsed

    undeformed = import_obj(undeformed_path)
    deformed = import_obj(deformed_path)

    keep_top_surface_only(undeformed)
    keep_top_surface_only(deformed)
    assign_material(undeformed, material_name)
    link_material(undeformed, deformed)

    out_abs = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(out_abs) or ".", exist_ok=True)
    if not render_and_save(out_abs, hide_obj=undeformed):
        print("Error: render failed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
    # main()    # if you want to run it in Blender
