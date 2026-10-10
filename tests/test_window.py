"""Ventana redimensionable: cálculo de vista, migración de ajustes y recentrado."""
import os
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from game.core import App  # noqa: E402


def test_fit_view_escala_entera():
    assert App._fit_view(640, 360) == (1.0, (0, 0), (640, 360))
    assert App._fit_view(1280, 720) == (2.0, (0, 0), (1280, 720))
    assert App._fit_view(1920, 1080) == (3.0, (0, 0), (1920, 1080))
    assert App._fit_view(2560, 1440) == (4.0, (0, 0), (2560, 1440))


def test_fit_view_letras_y_escala_libre():
    f, off, view = App._fit_view(1366, 768)
    assert f == 2.0 and view == (1280, 720) and off == (43, 24)
    f, off, view = App._fit_view(1000, 700)
    assert 1.4 <= f <= 1.6 and view[0] <= 1000 and view[1] <= 700
    f, off, view = App._fit_view(500, 300)
    assert f < 1.0 and view[0] <= 500 and view[1] <= 300


def test_settings_migracion_scale_viejo():
    """Un settings.json viejo con 'scale' debe cargar sin problema (win_w/h por defecto)."""
    from game.save import Settings
    tmp = tempfile.mkdtemp(prefix="napal_win_mig_")
    path = os.path.join(tmp, "s.json")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write('{"scale": 3, "vol_master": 0.5}')
    st = Settings(path)
    assert st["vol_master"] == 0.5
    assert st["win_w"] == 1280 and st["win_h"] == 720


def test_resize_y_reset_window_smoke():
    from main import build_app
    tmp = tempfile.mkdtemp(prefix="napal_win_")
    app = build_app(headless=False, save_path=os.path.join(tmp, "m.json"), settings_path=os.path.join(tmp, "s.json"))
    # simula un resize manual de ventana
    app.window = pygame.display.set_mode((900, 500), pygame.RESIZABLE)
    app._sync_view()
    assert app.settings["win_w"] == 900 and app.settings["win_h"] == 500
    assert app.view[0] <= 900 and app.view[1] <= 500 and app.view[0] > 700
    app.frame()  # frame completo con esa vista (present con reescalado)
    # recentrado de rescate
    app.reset_window()
    info = pygame.display.get_desktop_sizes()[0] if pygame.display.get_desktop_sizes() else (1920, 1080)
    assert tuple(app.window.get_size()) == app._target_win_size(info)
    assert app.settings["fullscreen"] is False
    app.frame()  # frame completo tras el ciclo quit/init de display
    app.running = True
