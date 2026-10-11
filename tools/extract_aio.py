"""Extrae ficheros del main.data del runtime usando los offsets de main.js.

El metadata embebido tiene entradas {filename:..., start:..., end:...}.
"""
from __future__ import annotations

import pathlib
import re

WEB = pathlib.Path("build/web_src")
js = (WEB / "runtime_cpython_main.js").read_text("utf-8", "replace")
data = (WEB / "build/web-cache/0010b1a915587aacae3cec0776e8f5aa.data").read_bytes()

# localizar el bloque de metadata
m = re.search(r"\[\s*\{\s*filename:", js)
print("metadata en offset", m.start() if m else None)
blob = js[m.start():] if m else ""
entries = re.findall(r'\{\s*"filename"\s*:\s*"([^"]+)"\s*,\s*"start"\s*:\s*(\d+)\s*,\s*"end"\s*:\s*(\d+)\s*\}', blob)
if not entries:
    entries = re.findall(r"\{filename:\"([^\"]+)\",start:(\d+),end:(\d+)\}", blob)
print("entradas:", len(entries))
aio_entries = [(f, int(a), int(b)) for (f, a, b) in entries if "aio" in f]
print("ficheros aio:", len(aio_entries))
out = WEB / "runtime_aio"
out.mkdir(exist_ok=True)
for f, a, b in aio_entries:
    if b > len(data):
        print("  !! fuera de rango", f, a, b, len(data))
        continue
    name = f.strip("/").replace("/", "__")
    (out / name).write_bytes(data[a:b])
    print(f"  {f}  ({b - a} bytes) -> {name}")
# y también los asyncio base por si acaso
for f, a, b in entries:
    if f.endswith("asyncio/__init__.py") or f.endswith("asyncio/base_events.py") or f.endswith("asyncio/events.py"):
        name = f.strip("/").replace("/", "__")
        (out / name).write_bytes(data[a:b])
        print(f"  {f}  ({b - a} bytes) -> {name}")
