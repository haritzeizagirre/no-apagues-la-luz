"""Perfila el coste por fotograma del juego (escritorio) para saber dónde optimizar.

Objetivo: dejar el coste lo más bajo posible para que WASM (≈5-15x más lento) sea jugable.
"""
from __future__ import annotations

import cProfile
import io
import os
import pstats
import sys
import tempfile
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
sys.path.insert(0, ".")

from main import build_app  # noqa: E402


def main() -> None:
    tmp = tempfile.mkdtemp(prefix="napal_prof_")
    app = build_app(headless=True, save_path=os.path.join(tmp, "m.json"),
                    settings_path=os.path.join(tmp, "s.json"))
    app.save.data["seen_tut"] = True
    app.set_scene("run", char_id="lia", guardia=5, mut_ids=[], seed=2)
    w = app.scene.world
    w.wave = 12          # densidad alta desde el principio

    def step():
        w.player.max_hp = 99999        # invulnerable: sin pantalla de fin falseando el perfil
        w.player.hp = 99999
        app.frame()
        w.player.hp = 99999
        if w.phase == "levelup":
            w.pending_levels = 0
            w.phase = "active"
        if w.phase == "shop":
            w.leave_shop()

    for _ in range(1500):    # calentar y llenar el mapa
        step()
    print(f"enemigos={len(w.enemies)} proyectiles={len(w.projs)}")

    t0 = time.perf_counter()
    for _ in range(300):
        step()
    t1 = time.perf_counter()
    print(f"300 frames: {(t1 - t0) * 1000:.0f} ms -> {(t1 - t0) / 300 * 1000:.2f} ms/frame")

    pr = cProfile.Profile()
    pr.enable()
    for _ in range(300):
        step()
    pr.disable()
    s = io.StringIO()
    pstats.Stats(pr, stream=s).sort_stats("tottime").print_stats(30)
    out = s.getvalue()
    print(out[:5200])


if __name__ == "__main__":
    main()
