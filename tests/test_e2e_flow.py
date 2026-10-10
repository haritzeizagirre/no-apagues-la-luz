"""E2E: flujo de jugador real con clics sintéticos (menú → jugar → pausa → secciones).

Inyecta eventos de ratón/teclado en la cola de pygame como haría un jugador y
verifica la navegación completa por botones: detectaría coordenadas mal puestas,
botones muertos o transiciones de escena rotas.
"""
import os
import tempfile

import pygame
import pytest


@pytest.fixture(scope="module")
def app():
    from main import build_app
    tmp = tempfile.mkdtemp(prefix="napal_e2e_")
    return build_app(headless=True, save_path=os.path.join(tmp, "m.json"), settings_path=os.path.join(tmp, "s.json"))


class _FakeClock:
    def tick(self, ms=0):
        return 16


def _step(app, pos, click=False, key=None):
    app.mouse = (lambda p: (lambda: p))(pos)
    if click:
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1))
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=pos, button=1))
    if key is not None:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key, unicode="", mod=0))
        pygame.event.post(pygame.event.Event(pygame.KEYUP, key=key, unicode="", mod=0))
    return app.frame()


def _scene(app):
    return type(app.scene).__name__


def test_full_click_flow(app):
    saved = app.clock
    app.clock = _FakeClock()
    try:
        app.set_scene("menu")
        _step(app, (0, 0))
        assert _scene(app) == "MenuScene"
        # JUGAR → selección de cacharro
        _step(app, (190, 141), click=True)
        assert _scene(app) == "CharSelectScene", "el botón JUGAR no navega"
        # EMPEZAR LA NOCHE → partida
        _step(app, (124, 331), click=True)
        assert _scene(app) == "RunScene", "el botón EMPEZAR no arranca la partida"
        for _ in range(5):
            _step(app, (320, 180))
        # ESC → pausa → CONTINUAR
        _step(app, (320, 180), key=pygame.K_ESCAPE)
        assert app.scene.paused, "ESC no pausa"
        _step(app, (192, 311), click=True)
        assert not app.scene.paused, "CONTINUAR no reanuda"
        # pausa otra vez → MENÚ
        _step(app, (320, 180), key=pygame.K_ESCAPE)
        _step(app, (450, 311), click=True)
        assert _scene(app) == "MenuScene", "el botón MENÚ de la pausa no vuelve al menú"
        # EL CAJÓN
        _step(app, (269, 175), click=True)
        assert _scene(app) == "CajonScene"
        _step(app, (0, 0), key=pygame.K_ESCAPE)
        assert _scene(app) == "MenuScene"
        # SELLOS + desplazar con flecha
        _step(app, (111, 207), click=True)
        assert _scene(app) == "SellosScene"
        _step(app, (0, 0), key=pygame.K_DOWN)
        _step(app, (0, 0), key=pygame.K_ESCAPE)
        assert _scene(app) == "MenuScene"
        # AJUSTES: el toggle de vibración cambia el ajuste
        _step(app, (111, 239), click=True)
        assert _scene(app) == "AjustesScene"
        before = app.settings["shake"]
        _step(app, (260, 191), click=True)
        assert app.settings["shake"] != before, "el toggle de vibración no responde"
        # PANTALLA COMPLETA (headless: solo cambia el ajuste) + RECENTRAR sin reventar
        fs0 = app.settings["fullscreen"]
        _step(app, (306, 327), click=True)
        _step(app, (306, 327))
        assert app.settings["fullscreen"] != fs0, "el botón de pantalla completa no responde"
        _step(app, (306, 327), click=True)
        _step(app, (306, 327))
        assert app.settings["fullscreen"] == fs0
        _step(app, (452, 327), click=True)
        _step(app, (452, 327))
        _step(app, (0, 0), key=pygame.K_ESCAPE)
        assert _scene(app) == "MenuScene"
        # HISTORIA y CRÉDITOS
        _step(app, (111, 175), click=True)
        assert _scene(app) == "LoreScene"
        _step(app, (0, 0), key=pygame.K_ESCAPE)
        assert _scene(app) == "MenuScene"
        _step(app, (269, 239), click=True)
        assert _scene(app) == "CreditosScene"
        _step(app, (0, 0), key=pygame.K_ESCAPE)
        assert _scene(app) == "MenuScene"
    finally:
        app.clock = saved


def test_quit_button_closes(app):
    saved = app.clock
    app.clock = _FakeClock()
    try:
        app.set_scene("menu")
        _step(app, (0, 0))
        alive = _step(app, (599, 337), click=True)
        assert not alive, "el botón ✕ SALIR no cierra la aplicación"
    finally:
        app.clock = saved
        app.running = True
