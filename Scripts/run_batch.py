import subprocess
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Blender 可执行文件路径
BLENDER = Path(r"D:\Software\Editor\blender\blender-4.5.7-windows-x64\blender-4.5.7-windows-x64\blender.exe")
BLEND = ROOT / "Assets" / "scene.blend" # Blender 场景文件
SCRIPT = ROOT / "Scripts" / "render.py"
INPUT_ROOT = ROOT / "Assets" / "test" # 输入根目录
MATERIAL = "circular"  # 必填：scene.blend 里材质的名称
PARALLEL = 4    # 并行 Blender 进程数

def run_one(folder_path):
    folder = Path(folder_path)
    initial = folder / "initial.obj"
    final = folder / "final.obj"
    output = folder / "output.png"
    if not initial.exists() or not final.exists():
        return folder, "skip"
    subprocess.run([str(BLENDER), "-b", str(BLEND), "-P", str(SCRIPT), "--",
                   str(initial), str(final), str(output), MATERIAL], check=True)
    return folder, "ok"

if __name__ == "__main__":
    folders = sorted({p.parent for p in INPUT_ROOT.rglob("initial.obj") if (p.parent / "final.obj").exists()})
    print(f"Total: {len(folders)}, parallel: {PARALLEL}")
    with Pool(PARALLEL) as p:
        for i, (folder, status) in enumerate(p.imap_unordered(run_one, folders), 1):
            print(f"[{i}/{len(folders)}] {folder.name}: {status}")