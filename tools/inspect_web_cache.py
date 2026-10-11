"""Inspección del runtime de pygbag cacheado en build/web_src/build/web-cache.

Identifica qué es cada fichero (site.py, pythons.js, parches de asyncio...) y busca
el mecanismo real de cesión al navegador (sleep/yield) y la API del módulo `platform`.
"""
from __future__ import annotations

import pathlib
import re

CACHE = pathlib.Path("build/web_src/build/web-cache")


def main() -> None:
    print("=== cabeceras (.head):")
    for head in sorted(CACHE.glob("*.head")):
        txt = head.read_text("utf-8", "replace").replace("\n", " | ")[:220]
        data = head.with_suffix(".data")
        size = data.stat().st_size if data.exists() else -1
        print(f"  {head.stem[:14]} {size:>9}  {txt}")

    print("\n=== contenidos (.data):")
    for data in sorted(CACHE.glob("*.data")):
        b = data.read_bytes()
        head = b[:110].decode("utf-8", "replace").replace("\n", "\\n")
        print(f"  {data.stem[:14]} {len(b):>9}  {head[:100]!r}")

    print("\n=== búsquedas clave:")
    pats = {
        "def sleep": rb"[^\n]{0,60}def sleep[^\n]{0,140}",
        "setTimeout": rb"[^\n]{0,70}setTimeout[^\n]{0,90}",
        "queueMicrotask": rb"[^\n]{0,70}queueMicrotask[^\n]{0,90}",
        "requestAnimationFrame": rb"[^\n]{0,70}requestAnimationFrame[^\n]{0,90}",
        "class platform": rb"[^\n]{0,70}class platform[^\n]{0,140}",
        "def window": rb"[^\n]{0,70}def window[^\n]{0,140}",
        "fetch": rb"[^\n]{0,60}fetch[^\n]{0,90}",
        "asyncio.run": rb"[^\n]{0,60}asyncio\.run[^\n]{0,90}",
        "wakeup": rb"[^\n]{0,60}wakeup[^\n]{0,90}",
    }
    for data in sorted(CACHE.glob("*.data")):
        b = data.read_bytes()
        hits = {}
        for name, pat in pats.items():
            ms = list(re.finditer(pat, b))[:3]
            if ms:
                hits[name] = [m.group(0).decode("utf-8", "replace")[:170] for m in ms]
        if hits:
            print(f"\n--- {data.stem[:14]} ({len(b)} bytes):")
            for name, lines in hits.items():
                for ln in lines:
                    print(f"   [{name}] {ln}")


if __name__ == "__main__":
    main()
