"""Extrae contexto alrededor de claves en los JS minificados del runtime pygbag."""
from __future__ import annotations

import pathlib
import re

FILES = {
    "cpython_main": pathlib.Path("build/web_src/runtime_cpython_main.js"),
    "pythons": pathlib.Path("build/web_src/runtime_pythons.js"),
}
KEYS = ["faking", "onCustomMessage", "set_main_loop", "main_loop", "requestAnimationFrame",
        "Asyncify", "asyncify", "sleep", "postMessage", "onmessage", "SDL_GetTicks"]


def main() -> None:
    for name, p in FILES.items():
        if not p.exists():
            continue
        txt = p.read_text("utf-8", "replace")
        print(f"##### {name} ({len(txt)} chars)")
        for k in KEYS:
            idxs = [m.start() for m in re.finditer(re.escape(k), txt)][:3]
            for i in idxs:
                a = max(0, i - 120)
                b = min(len(txt), i + 200)
                snippet = txt[a:b].replace("\n", " ")
                print(f"  [{k}] …{snippet}…")
            if not idxs:
                print(f"  [{k}] (no está)")


if __name__ == "__main__":
    main()
