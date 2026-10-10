"""NO APAGUES LA LUZ — punto de entrada.

Modos:
  (sin args)     juego
  --selftest     autocontrol headless completo (integridad + sims) y sale
  --simulate     simula una noche con bot y muestra informe
  --screenshot   genera capturas PNG de las pantallas clave
"""
from __future__ import annotations

import json
import os
import random
import sys
import traceback


def _print(*a, **k):
    """print seguro: en el .exe empaquetado sin consola stdout puede no existir."""
    try:
        print(*a, **k)
    except Exception:
        pass


def _headless_args(argv):
    return any(a in argv for a in ("--selftest", "--simulate", "--screenshot", "--headless"))


def _setup_env(headless: bool):
    if headless:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")


def _crash_log(exc: BaseException):
    from game import const as K
    try:
        K.ensure_app_dir()
        path = K.APP_DIR / "crash.txt"
        with open(path, "a", encoding="utf-8") as f:
            import datetime
            f.write(f"\n=== {datetime.datetime.now().isoformat()} ===\n")
            f.write("".join(traceback.format_exception(exc)))
        return path
    except Exception:
        return None


def build_app(headless=False, save_path=None, settings_path=None):
    from game import const as K
    from game.audio import Audio
    from game.core import App
    from game.save import Save, Settings
    K.ensure_app_dir()
    settings = Settings(settings_path) if settings_path else Settings()
    save = Save(save_path) if save_path else Save()
    audio = Audio(settings)
    app = App(settings, save, audio, headless=headless)
    from game import screens as SC
    from game.run_ui import RunScene
    app.scenes = {
        "menu": SC.MenuScene(app),
        "lore": SC.LoreScene(app),
        "charsel": SC.CharSelectScene(app),
        "cajon": SC.CajonScene(app),
        "sellos": SC.SellosScene(app),
        "archivo": SC.ArchivoScene(app),
        "ajustes": SC.AjustesScene(app),
        "creditos": SC.CreditosScene(app),
        "run": RunScene(app),
    }
    return app


# ---------------------------------------------------------------- selftest
def run_selftest(argv=None) -> int:
    report = {"ok": True, "checks": [], "sims": []}

    def check(name, fn):
        try:
            val = fn()
            report["checks"].append({"name": name, "ok": True, "info": val})
        except Exception as e:
            report["ok"] = False
            report["checks"].append({"name": name, "ok": False, "error": f"{type(e).__name__}: {e}"})

    import tempfile
    tmp = tempfile.mkdtemp(prefix="napal_selftest_")
    app = build_app(headless=True, save_path=os.path.join(tmp, "meta.json"),
                    settings_path=os.path.join(tmp, "settings.json"))

    check("sprites.build", lambda: len(__import__("game.sprites", fromlist=["build_all"]).build_all()))
    check("icons", lambda: len(__import__("game.icons", fromlist=["get_icon"]).get_icon("ic_w_grapadora").get_size()))
    check("audio.report", lambda: app.audio.report()["enabled"])
    check("fonts", lambda: app.fonts.ok)

    def _save_roundtrip():
        app.save.earn(100)
        app.save.unlock("char:tosty")
        app.save.flush()
        from game.save import Save
        s2 = Save(app.save.path)
        assert s2.chispas == 100 and s2.has("char:tosty")
        return "ok"
    check("save.roundtrip", _save_roundtrip)

    # sims cortas de varias combinaciones
    from game.simharness import fast_run
    combos = [("lia", 1, []), ("tosty", 1, ["apagon"]), ("raton", 2, [])]
    for (cid, g, muts) in combos:
        try:
            res = fast_run(app, cid, g, muts, seed=random.randint(1, 9999), max_time=240.0)
            report["sims"].append(res)
            assert res["phase"] not in ("levelup",)
            assert res["kills"] >= 0
        except Exception as e:
            report["ok"] = False
            report["sims"].append({"error": f"{cid}: {type(e).__name__}: {e}", "trace": traceback.format_exc()[-800:]})

    # sim larga: una noche completa (o hasta morir)
    try:
        res = fast_run(app, "lia", 1, [], seed=7, max_time=1400.0)
        report["sims"].append({"long": True, **res})
    except Exception as e:
        report["ok"] = False
        report["sims"].append({"error": f"long: {type(e).__name__}: {e}", "trace": traceback.format_exc()[-1200:]})

    # rendimiento: 300 pasos con 150 enemigos
    def _perf():
        import time as _t
        from game.world import RunWorld
        w = RunWorld(app, "lia", 1, [], seed=1)
        w.wave = 15
        for i in range(150):
            w._spawn_at("posti", 100 + (i % 30) * 28, 100 + (i // 30) * 28)
        w.player.hp = w.player.max_hp = 10 ** 9
        w.phase = "active"
        w.intro_t = 0
        t0 = _t.perf_counter()
        for _ in range(300):
            w.update(1 / 60)
        ms = (_t.perf_counter() - t0) / 300 * 1000
        assert ms < 16, f"{ms:.1f} ms/paso con {len(w.enemies)} enemigos"
        return f"{ms:.2f} ms/paso · {len(w.enemies)} enemigos · {len(w.projs)} proyectiles"
    check("perf.logic", _perf)

    out = os.path.join(os.environ.get("TEMP", tmp), "napal_selftest_report.json")
    try:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
    except Exception:
        pass
    _print(json.dumps(report, ensure_ascii=False, indent=1))
    _print(f"[selftest] informe: {out}")
    return 0 if report["ok"] else 1


# ---------------------------------------------------------------- simulate
def run_simulate(argv) -> int:
    import tempfile
    tmp = tempfile.mkdtemp(prefix="napal_sim_")
    app = build_app(headless=True, save_path=os.path.join(tmp, "meta.json"),
                    settings_path=os.path.join(tmp, "settings.json"))
    from game.simharness import fast_run

    def arg(name, default=None):
        if name in argv:
            i = argv.index(name)
            if i + 1 < len(argv):
                return argv[i + 1]
        return default

    char = arg("--char", "lia")
    guardia = int(arg("--guardia", "1"))
    muts = (arg("--muts", "") or "").split(",") if arg("--muts", "") else []
    muts = [m for m in muts if m]
    seed = int(arg("--seed", str(random.randint(1, 99999))))
    mins = float(arg("--minutes", "25"))
    res = fast_run(app, char, guardia, muts, seed=seed, max_time=mins * 60)
    _print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


# ---------------------------------------------------------------- screenshots
def run_screenshot(argv) -> int:
    import tempfile
    from game import const as K
    tmp = tempfile.mkdtemp(prefix="napal_shot_")
    app = build_app(headless=True, save_path=os.path.join(tmp, "meta.json"),
                    settings_path=os.path.join(tmp, "settings.json"))
    K.ensure_app_dir()
    out = K.APP_DIR / "capturas"
    out.mkdir(exist_ok=True)
    shots = []

    def frame_shot(name, frames=2):
        for _ in range(frames):
            app.frame()
        p = out / f"{name}.png"
        import pygame
        pygame.image.save(app.screen, str(p))
        shots.append(str(p))
        _print(f"[screenshot] {p}")

    from game.simharness import bot_step, FakeAppInput
    app.set_scene("menu")
    frame_shot("01_menu")
    app.set_scene("lore")
    frame_shot("02_lore")
    app.set_scene("charsel")
    frame_shot("03_charsel")
    app.set_scene("cajon")
    frame_shot("04_cajon")
    app.set_scene("sellos")
    frame_shot("05_sellos")
    app.set_scene("archivo")
    frame_shot("06_archivo")
    app.set_scene("ajustes")
    frame_shot("07_ajustes")
    app.set_scene("creditos")
    frame_shot("08_creditos")
    app.set_scene("run", char_id="lia", guardia=1, mut_ids=[], seed=3)
    world = app.scene.world
    inp = FakeAppInput()
    app.input = inp
    # 40 s de juego
    for i in range(int(40 * 60)):
        bot_step(world, inp, i / 60)
        world.update(1 / 60)
        world.events.clear()
        if world.phase == "levelup":
            world.pending_levels = 0
            world.phase = "active"
    world.cam.follow(world.player.x, world.player.y, snap=True)
    frame_shot("10_combate", 2)
    # subida de nivel forzada
    world.pending_levels = 1
    world.phase = "levelup"
    world.events.clear()
    app.scene.cards = world.roll_levelup_cards()
    frame_shot("11_levelup")
    # tienda
    world.pending_levels = 0
    world._end_wave()
    frame_shot("12_tienda")
    # jefe
    world.leave_shop()
    world.wave = 5
    world.next_wave()
    frame_shot("13_boss_intro")
    for _ in range(int(2.6 * 60)):
        world.update(1 / 60)
    frame_shot("14_boss")
    # pausa
    app.scene.paused = True
    frame_shot("15_pausa")
    app.scene.paused = False
    # victoria
    world._finish(victory=True)
    frame_shot("16_victoria")
    app.set_scene("cajon")
    frame_shot("17_cajon")
    _print(json.dumps({"shots": shots}, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------- main
def main(argv=None) -> int:
    argv = list(argv if argv is not None else sys.argv[1:])
    headless = _headless_args(argv)
    _setup_env(headless)
    if "--selftest" in argv:
        return run_selftest(argv)
    if "--simulate" in argv:
        return run_simulate(argv)
    if "--screenshot" in argv:
        return run_screenshot(argv)
    try:
        app = build_app(headless=False)
        if not app.settings["seen_intro"]:
            app.set_scene("lore", first=True)
        else:
            app.set_scene("menu")
        while app.running:
            app.frame()
        try:
            app.settings.flush()   # recuerda el tamaño de ventana al cerrar con la X
        except Exception:
            pass
        return 0
    except BaseException as e:
        path = _crash_log(e)
        traceback.print_exc()
        try:
            import ctypes
            msg = f"NO APAGUES LA LUZ encontró un error.\n\n{type(e).__name__}: {e}\n\nRegistro: {path}"
            ctypes.windll.user32.MessageBoxW(0, msg, "Error", 0x10)
        except Exception:
            pass
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
