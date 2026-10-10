"""Smoke de UI: todas las pantallas renderizan y las superposiciones no revientan."""
import os
import tempfile

import pygame
import pytest


@pytest.fixture(scope="module")
def app():
    from main import build_app
    tmp = tempfile.mkdtemp(prefix="napal_ui_")
    return build_app(headless=True, save_path=os.path.join(tmp, "m.json"), settings_path=os.path.join(tmp, "s.json"))


SCENES = ["menu", "lore", "charsel", "cajon", "sellos", "archivo", "ajustes", "creditos"]


def test_all_menu_scenes_render(app):
    for name in SCENES:
        app.set_scene(name)
        for _ in range(3):
            assert app.frame()


def test_menu_screen_not_blank(app):
    app.set_scene("menu")
    for _ in range(2):
        app.frame()
    colors = set()
    for i in range(0, 640, 16):
        for j in range(0, 360, 16):
            colors.add(app.screen.get_at((i, j))[:3])
    assert len(colors) > 25, f"solo {len(colors)} colores distintos: pantalla sospechosamente vacía"


def _screen_hash(app):
    import pygame
    return hash(pygame.image.tobytes(app.screen, "RGB"))


def test_run_scene_and_overlays(app):
    app.set_scene("run", char_id="lia", guardia=1, mut_ids=[], seed=5)
    scene = app.scene
    for _ in range(4):
        assert app.frame()
    h_base = _screen_hash(app)
    # subida de nivel: la superposición DEBE cambiar los píxeles
    scene.world.pending_levels = 1
    scene.world.phase = "levelup"
    scene.cards = scene.world.roll_levelup_cards()
    assert app.frame()
    h_level = _screen_hash(app)
    assert h_level != h_base, "la pantalla de subida de nivel no se dibuja"
    # tienda
    scene.cards = None
    scene.world.pending_levels = 0
    scene.world.phase = "active"
    scene.world._end_wave()
    assert app.frame()
    h_shop = _screen_hash(app)
    assert h_shop != h_level, "la tienda no se dibuja"
    # pausa
    scene.paused = True
    assert app.frame()
    h_pause = _screen_hash(app)
    assert h_pause != h_shop, "el menú de pausa no se dibuja"
    scene.paused = False
    # victoria
    scene.world.leave_shop()
    scene.world._finish(victory=True)
    assert app.frame()
    h_end = _screen_hash(app)
    assert h_end != h_pause, "la pantalla final no se dibuja"
    assert scene.world.phase == "victory"


def test_all_scenes_leave_without_crash(app):
    for name in SCENES + ["run"]:
        app.set_scene(name)
        app.frame()
    app.set_scene("menu")
    app.frame()


class _FakeClock:
    def tick(self, ms=0):
        return 16


def _sweep(app, scene_name, steps_y=7, steps_x=11, setup=None):
    """Barre el ratón por la pantalla: caza crashes de hover/tooltips en cualquier widget."""
    app.set_scene(scene_name)
    if setup:
        setup(app)
    saved_clock = app.clock
    app.clock = _FakeClock()
    try:
        for gy in range(steps_y):
            for gx in range(steps_x):
                pos = (gx * 60 + 25, gy * 50 + 22)
                app.mouse = (lambda p: (lambda: p))(pos)
                app.frame()
    finally:
        app.clock = saved_clock


def test_mouse_sweep_menus(app):
    for name in SCENES:
        _sweep(app, name)
    app.set_scene("menu")


def test_mouse_sweep_run_states(app):
    def to_levelup(a):
        s = a.scene
        s.world.pending_levels = 1
        s.world.phase = "levelup"
        s.cards = s.world.roll_levelup_cards()

    def to_shop(a):
        s = a.scene
        s.cards = None
        s.world.pending_levels = 0
        s.world.phase = "active"
        s.world._end_wave()

    def to_paused(a):
        a.scene.paused = True

    def to_end(a):
        s = a.scene
        s.paused = False
        s.world.leave_shop()
        s.world._finish(victory=False)

    _sweep(app, "run", setup=lambda a: a.set_scene("run", char_id="lia", guardia=1, mut_ids=[], seed=3), steps_x=8, steps_y=5)
    _sweep(app, "run", setup=to_levelup, steps_x=8, steps_y=5)
    _sweep(app, "run", setup=to_shop, steps_x=8, steps_y=5)
    _sweep(app, "run", setup=to_paused, steps_x=8, steps_y=5)
    _sweep(app, "run", setup=to_end, steps_x=8, steps_y=5)
    app.set_scene("menu")
