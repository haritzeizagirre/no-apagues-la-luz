"""Medición de coste real en escritorio: arranque, fotogramas de menú y de partida.

Sirve de línea base para extrapolar a WASM (el navegador es ~5-20x más lento).
"""
from __future__ import annotations

import os
import sys
import tempfile
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
sys.path.insert(0, ".")

from main import build_app  # noqa: E402


def main() -> None:
    tmp = tempfile.mkdtemp(prefix="napal_time_")
    t0 = time.perf_counter()
    app = build_app(headless=True, save_path=os.path.join(tmp, "m.json"),
                    settings_path=os.path.join(tmp, "s.json"))
    t1 = time.perf_counter()
    print(f"build_app          : {(t1 - t0) * 1000:8.1f} ms")

    app.set_scene("menu")
    for _ in range(30):          # primer fotograma incluye horneado perezoso de sprites
        app.frame()
    t2 = time.perf_counter()
    print(f"30 frames menu     : {(t2 - t1) * 1000:8.1f} ms  ({(t2 - t1) / 30 * 1000:6.2f} ms/frame)")

    app.save.data["seen_tut"] = True
    app.set_scene("run", char_id="lia", guardia=3, mut_ids=[], seed=1)
    w = app.scene.world
    t3 = time.perf_counter()
    n = 0
    for i in range(900):
        app.frame()
        n += 1
        if w.phase == "levelup":
            w.pending_levels = 0
            w.phase = "active"
    t4 = time.perf_counter()
    print(f"900 frames partida : {(t4 - t3) * 1000:8.1f} ms  ({(t4 - t3) / n * 1000:6.2f} ms/frame, "
          f"enemigos={len(w.enemies)}, proyectiles={len(getattr(w, 'projectiles', []))})")

    # coste del horneado completo de sprites (lo que en WASM puede ser brutal)
    from game import sprites as S
    t5 = time.perf_counter()
    S.get("char_lia"), S.get("pp_lamp"), S.get("en_clip")
    t6 = time.perf_counter()
    print(f"sprites ya cacheados: {(t6 - t5) * 1000:8.2f} ms (si es ~0, el horneado ya ocurrió)")


if __name__ == "__main__":
    main()
