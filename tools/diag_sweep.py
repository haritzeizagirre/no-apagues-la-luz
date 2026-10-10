"""Diagnóstico: barrido de ratón por el menú con variantes para aislar el crash de audio."""
import os
import sys
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

variant = sys.argv[1] if len(sys.argv) > 1 else "full"
pytest_like = "pytest_like" in sys.argv[2:]

if pytest_like:
    # replica exacta de tests/conftest.py antes de construir la app
    import pygame
    pygame.display.init()
    pygame.display.set_mode((320, 180))
    pygame.font.init()


def make_app():
    from main import build_app
    tmp = tempfile.mkdtemp(prefix="napal_diag_")
    return build_app(headless=True, save_path=os.path.join(tmp, "m.json"), settings_path=os.path.join(tmp, "s.json"))


class FC:
    def tick(self, ms=0):
        return 16


app = make_app()
print(f"[{variant}] audio.enabled inicial:", app.audio.enabled, flush=True)

if variant == "no_audio":
    app.audio.enabled = False
elif variant == "no_music":
    app.audio.play_music = lambda *a, **k: None
elif variant == "throttle":
    import time as _t
    state = {"last": {}, "t0": _t.perf_counter()}
    real_play = app.audio.play

    def throttled(name, vol=1.0, pitch=0):
        now = _t.perf_counter()
        if now - state["last"].get(name, -9) < 0.05:
            return
        state["last"][name] = now
        real_play(name, vol, pitch)

    app.audio.play = throttled
elif variant == "no_hover":
    real_play = app.audio.play

    def no_hover(name, vol=1.0, pitch=0):
        if name != "ui_hover":
            real_play(name, vol, pitch)

    app.audio.play = no_hover

app.clock = FC()
n = 0
for scene in ("menu", "lore", "charsel", "cajon", "sellos", "archivo", "ajustes", "creditos"):
    app.set_scene(scene)
    for gy in range(7):
        for gx in range(11):
            pos = (gx * 60 + 25, gy * 50 + 22)
            app.mouse = (lambda p: (lambda: p))(pos)
            app.frame()
            n += 1
print(f"[{variant}] PASS — {n} frames sin crash", flush=True)
