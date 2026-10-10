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
