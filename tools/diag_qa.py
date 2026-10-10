"""QA visual: vuelca en ASCII cada pantalla y estado de partida para revisarlos.

Escribe diag_qa.txt (arte ASCII a 1 char por bloque de 4x4 px) con TODAS las vistas:
menús y estados en partida (activa, subida de nivel, tienda, pausa, victoria).
"""
import os
import pathlib
import sys
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame

from game import const as K
from main import build_app


class FC:
    def tick(self, ms=0):
        return 16


tmp = tempfile.mkdtemp(prefix="napal_qa_")
app = build_app(headless=True, save_path=os.path.join(tmp, "m.json"), settings_path=os.path.join(tmp, "s.json"))
app.clock = FC()

OUT = ROOT / "diag_qa.txt"
fh = open(OUT, "w", encoding="utf-8")


def dump(name, step=4):
    img = app.screen
    fh.write(f"\n===== {name} =====\n")
    for y in range(0, K.H, step):
        row = ""
        for x in range(0, K.W, step):
            s = sum(img.get_at((x, y))[:3])
            row += "#" if s > 500 else ("+" if s > 230 else ("." if s > 80 else " "))
        fh.write(row + "\n")
    pygame.image.save(img, os.path.join(tmp, f"{name}.png"))


for name in ["menu", "lore", "charsel", "cajon", "sellos", "archivo", "ajustes", "creditos"]:
    app.set_scene(name)
    app.frame()
    app.frame()
    dump(name)

app.set_scene("run", char_id="lia", guardia=1, mut_ids=[], seed=3)
w = app.scene.world
for _ in range(90):
    app.frame()
w.player.hp -= 30
w.player.combo = 7
for _ in range(30):
    app.frame()
dump("run_activa")
app.scene.cards = None
w.pending_levels = 1
w.phase = "levelup"
app.scene.cards = w.roll_levelup_cards()
app.frame()
dump("run_levelup")
app.scene.cards = None
w.pending_levels = 0
w.phase = "active"
w._end_wave()
app.frame()
dump("run_tienda")
app.scene.paused = True
app.frame()
dump("run_pausa")
app.scene.paused = False
w.leave_shop()
w._finish(victory=True)
app.frame()
dump("run_victoria")

fh.close()
print("QA escrito en:", OUT)
print("PNGs en:", tmp)
