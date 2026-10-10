"""Estrés de audio: ningún sonido (Kenney OGG ni sintetizado) debe tumbar el mixer.

Este test existe por un access violation real de SDL_mixer: con el mixer a 22050
mono, los OGG de Kenney (44100) colgaban el proceso al reproducirse. El mixer
debe inicializarse a 44100 (ver game/audio.py).
"""
import os
import pathlib
import tempfile

import pygame
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def audio():
    from game.audio import Audio
    from game.save import Settings
    tmp = tempfile.mkdtemp(prefix="napal_stress_")
    st = Settings(os.path.join(tmp, "s.json"))
    a = Audio(st)
    assert a.enabled, "el mixer debería inicializarse en el entorno de test"
    return a


def test_audio_stress_all_sfx(audio):
    """Todos los sonidos lógicos, muchas reproducciones seguidas."""
    for name in audio.sounds:
        for _ in range(40):
            audio.play(name)
    # sin excepción y el proceso sigue vivo = pass


def test_audio_stress_kenney_ogg(audio):
    import json
    am = json.load(open(ROOT / "assets" / "audio_map.json", encoding="utf-8"))
    for rel in am["sfx"].values():
        snd = pygame.mixer.Sound(str(ROOT / "assets" / rel))
        for _ in range(60):
            snd.play()
    assert True


def test_audio_throttle_limits_burst(audio):
    """El throttle evita ráfagas: 1000 llamadas seguidas en el mismo instante cuentan como 1."""
    audio._now = 1000.0
    audio.play("ui_hover")
    assert abs(audio._last["ui_hover"] - 1000.0) < 1e-9
    for _ in range(1000):
        audio.play("ui_hover")
    assert audio._last["ui_hover"] == 1000.0  # ninguna llamada extra pasó el filtro


def test_music_tracks_load(audio):
    for t in ("menu", "combat", "boss", "victory"):
        assert t in audio._music_cache, f"falta la pista {t}"
