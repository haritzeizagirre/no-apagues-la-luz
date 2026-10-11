"""Reconstruye la web del juego y la publica en GitHub Pages (rama gh-pages).

Uso:
    ./.venv/Scripts/python.exe tools/publish_web.py

Hace, en orden:
  1. build_web.py --build  (monta y empaqueta con pygbag, + PWA)
  2. commit del sitio en build/web_src/build/web
  3. push forzado a la rama gh-pages del repo de GitHub (Pages la sirve)

El codigo fuente vive en la rama main (push normal del repo del juego).
URL publica: https://haritzeizagirre.github.io/no-apagues-la-luz/
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "build" / "web_src" / "build" / "web"
REMOTE = "https://github.com/haritzeizagirre/no-apagues-la-luz.git"
URL = "https://haritzeizagirre.github.io/no-apagues-la-luz/"


def run(cmd, cwd=None) -> int:
    print("[publish]", " ".join(cmd))
    return subprocess.call(cmd, cwd=cwd)


def main() -> int:
    py = sys.executable
    rc = run([py, str(ROOT / "tools" / "build_web.py"), "--build"])
    if rc != 0:
        print("[publish] build fallido")
        return rc
    run(["git", "init", "-b", "main"], cwd=SITE)
    run(["git", "add", "-A"], cwd=SITE)
    run(["git", "-c", "user.name=Hermes (agente)", "-c", "user.email=hermes@local",
         "commit", "-m", "web: build y publicacion"], cwd=SITE)
    # primer push: sin remoto configurado; siguientes: reutiliza origin
    run(["git", "remote", "remove", "origin"], cwd=SITE)
    run(["git", "remote", "add", "origin", REMOTE], cwd=SITE)
    rc = run(["git", "push", "-f", "origin", "main:gh-pages"], cwd=SITE)
    if rc == 0:
        print(f"[publish] LISTO -> {URL} (Pages tarda ~1-2 min en refrescar)")
    else:
        print("[publish] push fallido: revisa gh auth status / conexion")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
