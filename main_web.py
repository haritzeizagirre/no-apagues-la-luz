"""Entrada 'web' para empaquetar con pygbag (móvil y navegador).

pygbag necesita que el bucle principal ceda el control al navegador
(await asyncio.sleep(0)) en cada fotograma; el resto del juego es el mismo.
"""
from __future__ import annotations

import asyncio
import json

from game import const as K
import pygame  # noqa: F401  (cargar pygame antes de tocar el FS: en WASM importa el orden)


def _prep_web_settings() -> None:
    """Ventana pequeña y sin audio para la prueba web."""
    try:
        K.ensure_app_dir()
        p = K.SETTINGS_PATH
        d = {}
        if p.exists():
            d = json.loads(p.read_text(encoding="utf-8"))
        d.update({"win_w": 640, "win_h": 360, "vol_music": 0.0, "vol_sfx": 0.0, "seen_intro": True})
        p.write_text(json.dumps(d), encoding="utf-8")
    except Exception as e:
        print("[web] prep settings:", e, flush=True)


async def _amain() -> None:
    def beacon(*a, **k):   # balizas neutralizadas (llamadas JS sin consumir)
        pass
    beacon("web:start")
    _prep_web_settings()
    beacon("web:settings_ok")
    from desktop_entry import build_app
    app = build_app(headless=False)
    # en web el limitador de FPS del reloj puede bloquear el hilo principal:
    import time as _t

    class _RealClock:   # reloj de TIEMPO REAL: dt correcto aunque el pump vaya a 144fps
        def __init__(self):
            self._t = _t.monotonic()

        def tick(self, fps=0):
            now = _t.monotonic()
            ms = int((now - self._t) * 1000)
            self._t = now
            return max(0, min(ms, 100))

    app.clock = _RealClock()
    beacon("web:app_built")
    print("[web] NO APAGUES LA LUZ arrancado", flush=True)
    if not app.settings["seen_intro"]:
        app.set_scene("lore", first=True)
    else:
        app.set_scene("menu")
    n = 0
    beacon("web:scene_ok")
    while app.running:
        app.frame()
        n += 1
        if n == 1:
            print("[web] primer frame dibujado", flush=True)
            beacon("web:frame1")
        elif n % 300 == 0:
            try:
                w = getattr(app.scene, "world", None)
                pl = getattr(w, "player", None)
                pos = f"({int(pl.x)},{int(pl.y)})" if pl is not None else "-"
            except Exception:
                pos = "?"
            print(f"[web] frames={n} escena={type(app.scene).__name__} pos={pos}", flush=True)
        # patron canonico de pygbag: sleep(0) puro cede al navegador;
        # un timer (sleep(0.016)) NO resuelve en modo main-thread
        await asyncio.sleep(0)
    try:
        app.settings.flush()
    except Exception:
        pass


def main() -> None:
    asyncio.run(_amain())


main()
