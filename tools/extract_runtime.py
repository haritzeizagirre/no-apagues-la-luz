"""Extrae el runtime de pygbag cacheado a ficheros legibles (pythonrc.py, pythons.js)."""
from __future__ import annotations

import pathlib

CACHE = pathlib.Path("build/web_src/build/web-cache")
OUT = pathlib.Path("build/web_src")

for data in sorted(CACHE.glob("*.data")):
    b = data.read_bytes()
    if b.startswith(b"#!pythonrc.py"):
        (OUT / "runtime_pythonrc.py").write_bytes(b)
        print("pythonrc.py  ->", OUT / "runtime_pythonrc.py", len(b), "bytes")
    elif b[:20].startswith(b'"use strict";') and b"WebAssembly.promising" in b[:300]:
        (OUT / "runtime_pythons.js").write_bytes(b)
        print("pythons.js   ->", OUT / "runtime_pythons.js", len(b), "bytes")
    elif b.startswith(b"var Module=typeof Module"):
        (OUT / "runtime_cpython_main.js").write_bytes(b)
        print("cpython main.js ->", len(b), "bytes")
print("fin")
