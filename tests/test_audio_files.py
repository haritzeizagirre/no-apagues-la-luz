# -*- coding: utf-8 -*-
"""Valida TODOS los WAV generados por tools/gen_audio.py ("No Apagues La Luz").

Comprueba: existencia, WAV valido (modulo `wave`) 22050 Hz / mono / 16-bit,
duracion en rango (sfx 0.04-3.6 s; musica 20-75 s), RMS > 0.004 (no silencio),
pico <= 0.99, |media| < 0.02 (sin DC) y, para musica, extremos ~0 y RMS de los
primeros/ultimos 30 ms dentro de factor 3 entre si (loop continuo).
"""
import os
import wave
from functools import lru_cache

import numpy as np
import pytest

SR = 22050
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
MUSIC_DIR = os.path.join(ROOT, "assets", "music")

SFX_NAMES = [
    "shoot_tack", "shoot_marker", "shoot_heavy", "shoot_throw", "beam_loop",
    "chain_zap", "aura_pulse", "nova", "explosion_small", "explosion_big",
    "hit_enemy", "hit_crit", "enemy_die", "enemy_die_big", "player_hurt",
    "player_dash", "fogonazo", "pickup_xp1", "pickup_xp2", "pickup_xp3",
    "pickup_coin", "pickup_heal", "levelup", "wave_start", "boss_spawn",
    "boss_die", "victory", "game_over", "ui_click", "ui_hover", "ui_deny",
    "shop_buy", "shop_reroll", "merge", "crate_break", "tape_hit",
]
MUSIC_NAMES = ["menu", "combat", "boss", "victory"]


@lru_cache(maxsize=None)
def read_wav(path):
    with wave.open(path, "rb") as w:
        nch, sw, fr, nf = (w.getnchannels(), w.getsampwidth(),
                           w.getframerate(), w.getnframes())
        raw = w.readframes(nf)
    x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    return {"nch": nch, "sw": sw, "fr": fr, "nf": nf, "x": x,
            "dur": (nf / fr) if fr else 0.0}


def rms(v):
    return float(np.sqrt(np.mean(np.square(v)))) if v.size else 0.0


def path_of(name, is_music):
    return os.path.join(MUSIC_DIR if is_music else SFX_DIR, name + ".wav")


CASES = [(n, False) for n in SFX_NAMES] + [(n, True) for n in MUSIC_NAMES]
IDS = [n for n, _ in CASES]


@pytest.mark.parametrize("name,is_music", CASES, ids=IDS)
def test_file_exists(name, is_music):
    assert os.path.isfile(path_of(name, is_music)), "falta %s.wav" % name


@pytest.mark.parametrize("name,is_music", CASES, ids=IDS)
def test_wav_header(name, is_music):
    st = read_wav(path_of(name, is_music))
    assert st["nch"] == 1, "debe ser mono"
    assert st["sw"] == 2, "debe ser PCM 16-bit"
    assert st["fr"] == SR, "debe ser 22050 Hz"
    assert st["nf"] > 0


@pytest.mark.parametrize("name,is_music", CASES, ids=IDS)
def test_duration_range(name, is_music):
    st = read_wav(path_of(name, is_music))
    lo, hi = (20.0, 75.0) if is_music else (0.04, 3.6)
    assert lo <= st["dur"] <= hi, "%s dura %.3f s" % (name, st["dur"])


@pytest.mark.parametrize("name,is_music", CASES, ids=IDS)
def test_not_silent_rms(name, is_music):
    st = read_wav(path_of(name, is_music))
    r = rms(st["x"])
    assert r > 0.004, "%s rms=%.5f (silencio cas) " % (name, r)


@pytest.mark.parametrize("name,is_music", CASES, ids=IDS)
def test_peak_below_clip(name, is_music):
    st = read_wav(path_of(name, is_music))
    pk = float(np.max(np.abs(st["x"])))
    assert pk <= 0.99, "%s pico=%.4f" % (name, pk)


@pytest.mark.parametrize("name,is_music", CASES, ids=IDS)
def test_dc_offset(name, is_music):
    st = read_wav(path_of(name, is_music))
    m = float(np.mean(st["x"]))
    assert abs(m) < 0.02, "%s media=%.5f" % (name, m)


@pytest.mark.parametrize("name", MUSIC_NAMES)
def test_music_loop_extremes(name):
    x = read_wav(path_of(name, True))["x"]
    assert abs(float(x[0])) < 0.03, "%s s[0]=%.4f" % (name, x[0])
    assert abs(float(x[-1])) < 0.03, "%s s[-1]=%.4f" % (name, x[-1])


@pytest.mark.parametrize("name", MUSIC_NAMES)
def test_music_loop_edge_rms_balance(name):
    x = read_wav(path_of(name, True))["x"]
    k = int(round(0.030 * SR))
    a, b = rms(x[:k]), rms(x[-k:])
    assert a > 0.0 and b > 0.0
    ratio = a / b
    assert (1.0 / 3.0) <= ratio <= 3.0, "%s ratio30ms=%.3f (head=%.5f tail=%.5f)" % (name, ratio, a, b)


def test_beam_loop_exact_two_seconds():
    st = read_wav(path_of("beam_loop", False))
    assert st["nf"] == 2 * SR, "beam_loop debe durar exactamente 2.000 s"
    assert abs(float(st["x"][0])) < 0.03, "beam_loop s[0]=%.4f" % st["x"][0]


def test_manifest_exact():
    have_sfx = sorted(f for f in os.listdir(SFX_DIR) if f.endswith(".wav"))
    have_mus = sorted(f for f in os.listdir(MUSIC_DIR) if f.endswith(".wav"))
    assert have_sfx == sorted(n + ".wav" for n in SFX_NAMES)
    assert have_mus == sorted(n + ".wav" for n in MUSIC_NAMES)
