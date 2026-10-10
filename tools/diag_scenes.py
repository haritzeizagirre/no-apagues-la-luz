"""Diagnóstico: mide la 'tinta' (contenido visible) de cada pantalla contra el fondo.

Sirve para cazar regresiones del tipo 'pantalla vacía' (contenido dibujado en update()
y borrado por el fill/draw) sin necesidad de mirar PNGs a ojo.
"""
import os
import sys
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pygame

from game import const as K
from game import screens as SC
from main import build_app

_tobytes = getattr(pygame.image, "tobytes", None) or pygame.image.tostring


class FC:
    def tick(self, ms=0):
        return 16


tmp = tempfile.mkdtemp(prefix="napal_diag_")
app = build_app(headless=True, save_path=os.path.join(tmp, "m.json"), settings_path=os.path.join(tmp, "s.json"))
app.clock = FC()

CASES = [("menu", 104), ("lore", 104), ("charsel", 58), ("cajon", 58),
         ("sellos", 58), ("archivo", 58), ("ajustes", 58), ("creditos", 58)]

for name, y0 in CASES:
    app.set_scene(name)
    app.frame()
    a = np.frombuffer(_tobytes(app.screen, "RGB"), dtype=np.uint8).reshape(K.H, K.W, 3).astype(np.int16)
    ref = pygame.Surface((K.W, K.H))
    SC.draw_bg(app, ref, app.time)
    b = np.frombuffer(_tobytes(ref, "RGB"), dtype=np.uint8).reshape(K.H, K.W, 3).astype(np.int16)
    d = np.abs(a - b).max(axis=2) > 24
    reg = d[y0:346, 4:636]
    ink = int(reg.sum())
    ys, xs = np.nonzero(reg)
    bbox = (int(xs.min()) + 4, int(ys.min()) + y0, int(xs.max()) + 4, int(ys.max()) + y0) if ink else None
    print(f"=== {name}: ink={ink} bbox={bbox}")
    # sonda de la franja inferior izquierda (x 0..170, y 338..360): ¿hay algo raro?
    strip = a[338:360, 0:170]
    vals, counts = np.unique(strip.reshape(-1, 3), axis=0, return_counts=True)
    order = np.argsort(-counts)[:5]
    print("   franja inf-izq:", [(tuple(int(v) for v in vals[i]), int(counts[i])) for i in order])
    h = reg.shape[0]
    for gy in range(4):
        row = ""
        for gx in range(6):
            sub = reg[gy * h // 4:(gy + 1) * h // 4, gx * 632 // 6:(gx + 1) * 632 // 6]
            m = float(sub.mean())
            row += "#" if m > 0.25 else ("+" if m > 0.05 else ("." if m > 0.005 else " "))
        print("   |" + row + "|")
    pygame.image.save(app.screen, os.path.join(tmp, f"{name}.png"))

print("PNGs en:", tmp)
