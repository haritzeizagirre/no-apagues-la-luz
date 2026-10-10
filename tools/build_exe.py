"""Construye el .exe con PyInstaller (onefile, sin consola).

Uso:  .venv\\Scripts\\python.exe tools/build_exe.py
Genera: dist/NoApaguesLaLuz.exe  (+ dist/informe_build.json)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
SEP = os.pathsep


def version_file() -> str:
    path = os.path.join(ROOT, "build", "version_info.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sys.path.insert(0, ROOT)
    from game import const as K
    parts = K.VERSION.split(".")
    while len(parts) < 4:
        parts.append("0")
    v = ", ".join(parts[:4])
    content = f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers=({v}), prodvers=({v}), mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([
      StringTable('040a04b0', [
        StringStruct('CompanyName', 'Hermes x indeg'),
        StringStruct('FileDescription', '{K.TITLE} — survivor-like de oficina nocturna'),
        StringStruct('FileVersion', '{K.VERSION}'),
        StringStruct('InternalName', 'NoApaguesLaLuz'),
        StringStruct('OriginalFilename', 'NoApaguesLaLuz.exe'),
        StringStruct('ProductName', '{K.TITLE}'),
        StringStruct('ProductVersion', '{K.VERSION}'),
        StringStruct('LegalCopyright', 'Arte y código generados para este proyecto. Fuentes OFL, audio CC0/sintetizado.')
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [1034, 1200])])
  ]
)
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def main() -> int:
    os.chdir(ROOT)
    # 0) matar instancias en marcha (pueden bloquear dist/NoApaguesLaLuz.exe)
    subprocess.run(["taskkill", "/F", "/IM", "NoApaguesLaLuz.exe"], capture_output=True)
    # 1) icono
    subprocess.run([PY, os.path.join("tools", "make_icon.py")], check=True)
    vf = version_file()
    icon = os.path.join(ROOT, "assets", "icon.ico")
    # 2) limpiar builds previos
    for d in ("build/NoApaguesLaLuz", "dist"):
        p = os.path.join(ROOT, d)
        if os.path.isdir(p):
            import shutil
            shutil.rmtree(p, ignore_errors=True)
    cmd = [
        PY, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--onefile", "--windowed",
        "--name", "NoApaguesLaLuz",
        "--icon", icon,
        "--version-file", vf,
        f"--add-data=assets{SEP}assets",
        "--exclude-module", "numpy",
        "--exclude-module", "pytest",
        "--exclude-module", "PIL",
        "--exclude-module", "tkinter",
        "main.py",
    ]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    ok = proc.returncode == 0
    exe = os.path.join(ROOT, "dist", "NoApaguesLaLuz.exe")
    report = {
        "ok": ok, "returncode": proc.returncode, "time_s": round(time.time() - t0, 1),
        "exe": exe, "exe_bytes": os.path.getsize(exe) if os.path.exists(exe) else 0,
        "tail": (proc.stdout or "")[-1500:] if not ok else "",
    }
    with open(os.path.join(ROOT, "dist", "informe_build.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
