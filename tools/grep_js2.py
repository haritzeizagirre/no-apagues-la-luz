"""Contexto de 'is_worker' en el JS minificado del runtime."""
from __future__ import annotations

import pathlib
import re

for name in ("runtime_cpython_main.js", "runtime_pythons.js"):
    p = pathlib.Path("build/web_src") / name
    txt = p.read_text("utf-8", "replace")
    print(f"##### {name}")
    for k in ("is_worker", "threads", "worker"):
        idxs = [m.start() for m in re.finditer(re.escape(k), txt)][:4]
        for i in idxs:
            a = max(0, i - 130)
            b = min(len(txt), i + 170)
            print(f"  [{k}] …{txt[a:b].replace(chr(10), ' ')}…")
        if not idxs:
            print(f"  [{k}] (no está)")
