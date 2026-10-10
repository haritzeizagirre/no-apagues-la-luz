"""Batch de simulación de balance: python tools/simbatch.py [n_seeds] [char] [guardia]"""
import os
import sys
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import build_app  # noqa: E402
from game.simharness import fast_run  # noqa: E402

n = int(sys.argv[1]) if len(sys.argv) > 1 else 16
char = sys.argv[2] if len(sys.argv) > 2 else "lia"
guardia = int(sys.argv[3]) if len(sys.argv) > 3 else 1
muts = [m for m in (sys.argv[4].split(",") if len(sys.argv) > 4 and sys.argv[4] else []) if m]

tmp = tempfile.mkdtemp()
app = build_app(headless=True, save_path=os.path.join(tmp, "m.json"), settings_path=os.path.join(tmp, "s.json"))
res = []
import time as _t
for seed in range(1, n + 1):
    t0 = _t.perf_counter()
    r = fast_run(app, char, guardia, muts, seed=seed, max_time=2000)
    wall = _t.perf_counter() - t0
    res.append(r)
    print(f"seed {seed:>2}: h{r['best_wave']:<3} t={r['time']:>6}s kills={r['kills']:<4} lvl{r['level']:<3} "
          f"armas={len(r['weapons'])} items={r['items']:<2} {'VICTORIA' if r['victory'] else '        '} "
          f"(sim {wall:.1f}s)", flush=True)
waves = sorted(r["best_wave"] for r in res)
print("median:", waves[len(waves) // 2], "| victorias:", sum(1 for r in res if r["victory"]), "/", len(res))
print("horas:", waves)
