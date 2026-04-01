import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Blender 可执行文件路径
BLENDER = Path(r"D:\Software\Editor\blender\blender-4.5.7-windows-x64\blender-4.5.7-windows-x64\blender.exe")
BLEND = ROOT / "Assets" / "scene.blend"  # Blender 场景文件
SCRIPT = ROOT / "Scripts" / "render.py"
FOLDER = ROOT / "Assets" / "models" # 其下包含 initial.obj/final.obj
MATERIAL = "spiral_with_red_curve"  # 必填：scene.blend 里材质的名称

def main() -> int:
    initial = FOLDER / "initial.obj"
    final = FOLDER / "final.obj"
    output = FOLDER / "output.png"
    assert initial.exists() and final.exists(), "initial.obj or final.obj not found"

    output.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [str(BLENDER), "-b", str(BLEND), "-P", str(SCRIPT), "--", str(initial), str(final), str(output), MATERIAL],
        check=True,
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

