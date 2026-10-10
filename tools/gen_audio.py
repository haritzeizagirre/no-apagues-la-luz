#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_audio.py — Sintetizador offline de TODO el audio de "No Apagues La Luz".

Roguelike survivor de oficina nocturna: vibe chiptune oscuro/tecnoso.
Genera, sin descargas y sin dependencias salvo numpy (+ stdlib `wave`):

    assets/sfx/<nombre>.wav    36 efectos, WAV PCM 16-bit con signo, mono, 22050 Hz
    assets/music/<nombre>.wav  4 loops perfectos (menu / combat / boss / victory)

Garantias de formato:
    - Mono, 22050 Hz, PCM 16-bit con signo (modulo `wave`).
    - Picos normalizados a 0.85 (nunca > 0.99).
    - Sin DC offset (se elimina la media flotante antes de cuantizar).
    - Determinista (seeds fijos): idempotente byte a byte.

Uso (venv del proyecto):
    "/c/VSCode/no-apagues-la-luz/.venv/Scripts/python.exe" tools/gen_audio.py
    "/c/VSCode/no-apagues-la-luz/.venv/Scripts/python.exe" -m pytest tests/test_audio_files.py -q
"""
import math
import os
import time
import wave

import numpy as np

TAU = 2.0 * math.pi
SR = 22050
PEAK_TARGET = 0.85

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
MUSIC_DIR = os.path.join(ROOT, "assets", "music")


# --------------------------------------------------------------------------
# Nucleo DSP (numpy puro)
# --------------------------------------------------------------------------
def _rng(seed):
    return np.random.default_rng(int(seed))


def _nsec(dur):
    """Muestras necesarias para `dur` segundos (>= 1)."""
    return max(int(round(float(dur) * SR)), 1)


def t_ax(n):
    return np.arange(n, dtype=np.float64) / SR


def ph_const(freq, n):
    """Fase (en ciclos) de un oscilador de frecuencia constante."""
    return float(freq) * t_ax(n)


def ph_sweep(f0, f1, n, kind="exp"):
    """Fase (en ciclos) de un barrido de frecuencia f0 -> f1, continua."""
    if kind == "exp":
        f = np.geomspace(float(f0), float(f1), n)
    else:
        f = np.linspace(float(f0), float(f1), n)
    return np.cumsum(f) / SR


def _osc(wave, ph, duty=0.5):
    if wave == "sin":
        return np.sin(TAU * ph)
    if wave == "tri":
        return (2.0 / np.pi) * np.arcsin(np.sin(TAU * ph))
    if wave == "saw":
        return 2.0 * np.mod(ph, 1.0) - 1.0
    if wave == "sqr":
        return np.where(np.mod(ph, 1.0) < duty, 1.0, -1.0)
    raise ValueError("oscilador desconocido: %r" % (wave,))


def osc_sin(ph):
    return np.sin(TAU * ph)


def osc_tri(ph):
    return (2.0 / np.pi) * np.arcsin(np.sin(TAU * ph))


def osc_saw(ph):
    return 2.0 * np.mod(ph, 1.0) - 1.0


def osc_sqr(ph, duty=0.5):
    return np.where(np.mod(ph, 1.0) < duty, 1.0, -1.0)


def env_perc(n, attack=0.004, tau=0.08):
    """Percusivo: rampa de ataque + decaimiento exponencial."""
    t = t_ax(n)
    return np.clip(t / max(float(attack), 1e-5), 0.0, 1.0) * np.exp(-t / max(float(tau), 1e-5))


def env_adsr(n, a=0.005, d=0.05, s=0.5, r=0.05):
    """ADSR muestreado; se reescala si a+d+r no cabe en n."""
    na = max(int(round(float(a) * SR)), 1)
    nd = max(int(round(float(d) * SR)), 1)
    nr = max(int(round(float(r) * SR)), 1)
    if na + nd + nr > n:
        k = n / float(na + nd + nr)
        na = max(int(na * k), 1)
        nd = max(int(nd * k), 1)
        nr = max(int(nr * k), 1)
    ns = max(n - na - nd - nr, 0)
    e = np.concatenate([
        np.linspace(0.0, 1.0, na, endpoint=False),
        np.linspace(1.0, float(s), nd, endpoint=False),
        np.full(ns, float(s)),
        np.linspace(float(s), 0.0, nr, endpoint=False),
    ])
    if e.size < n:
        e = np.concatenate([e, np.zeros(n - e.size)])
    return e[:n]


def white(rng, n):
    return rng.standard_normal(int(n))


def lp1(x, fc):
    """Paso-bajo one-pole (respuesta exacta) via FFT con cola de ceros."""
    x = np.asarray(x, dtype=np.float64)
    n = x.size
    if n < 8 or float(fc) >= SR * 0.45:
        return x.copy()
    a = 1.0 - math.exp(-TAU * float(fc) / SR)
    pad = min(n, 4096)
    xp = np.concatenate([x, np.zeros(pad)])
    fr = np.fft.rfftfreq(xp.size, 1.0 / SR)
    z = np.exp(-2j * np.pi * fr / SR)
    H = a / (1.0 - (1.0 - a) * z)
    y = np.fft.irfft(np.fft.rfft(xp) * H, n=xp.size)
    return y[:n]


def hp1(x, fc):
    return x - lp1(x, fc)


def bp1(x, f_lo, f_hi):
    return lp1(x, f_hi) - lp1(x, f_lo)


# --------------------------------------------------------------------------
# Mezcla y escritura WAV
# --------------------------------------------------------------------------
class Mix:
    """Buffer de mezcla; `wrap=True` renderiza en bucle (colas que cruzan el empalme)."""

    def __init__(self, n, wrap=False):
        self.n = int(n)
        self.wrap = bool(wrap)
        self.buf = np.zeros(self.n, dtype=np.float64)

    def add(self, t0, sig, gain=1.0):
        y = np.asarray(sig, dtype=np.float64)
        if gain != 1.0:
            y = y * gain
        L = y.size
        if L == 0:
            return
        s = int(round(float(t0) * SR))
        if self.wrap:
            s %= self.n
            if L >= self.n:
                for r in range((L + self.n - 1) // self.n):
                    chunk = y[r * self.n:(r + 1) * self.n]
                    self.buf[:chunk.size] += chunk
                return
            e = s + L
            if e <= self.n:
                self.buf[s:e] += y
            else:
                k = self.n - s
                self.buf[s:] += y[:k]
                self.buf[:e - self.n] += y[k:]
        else:
            if s >= self.n or s + L <= 0:
                return
            ss = max(s, 0)
            off = ss - s
            e = min(s + L, self.n)
            self.buf[ss:e] += y[off:off + (e - ss)]


def pack(dur, parts):
    """Mezcla lineal (SFX). `parts` = [(t0_s, sig, gain), ...]; crece si hace falta."""
    n = _nsec(dur)
    if parts:
        need = max(int(round(float(t) * SR)) + len(s) for t, s, _g in parts)
        n = max(n, need)
    m = Mix(n, wrap=False)
    for t0, sig, g in parts:
        m.add(t0, sig, g)
    return m.buf


def write_wav(path, x, peak=PEAK_TARGET, fade_in_ms=1.2, fade_out_ms=2.5):
    """DC=0 -> micro-fades -> normaliza a `peak` -> PCM 16-bit mono."""
    x = np.array(x, dtype=np.float64, copy=True)
    if x.size == 0:
        raise ValueError("buffer vacio para %s" % path)
    x -= x.mean()
    n = x.size
    fi = max(0, min(int(round(fade_in_ms * SR / 1000.0)), n // 4))
    fo = max(0, min(int(round(fade_out_ms * SR / 1000.0)), n // 4))
    if fi >= 2:
        x[:fi] *= 0.5 - 0.5 * np.cos(np.pi * np.arange(fi) / (fi - 1.0))
    if fo >= 2:
        x[n - fo:] *= 0.5 + 0.5 * np.cos(np.pi * np.arange(fo) / (fo - 1.0))
    m = float(np.max(np.abs(x)))
    if m < 1e-9:
        raise RuntimeError("silencio sintetizado para %s" % path)
    x *= (float(peak) / m)
    xi = np.clip(np.round(x * 32767.0), -32766.0, 32767.0).astype("<i2")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(xi.tobytes())


# --------------------------------------------------------------------------
# Azucar para SFX
# --------------------------------------------------------------------------
def tone(freq, dur, wave="sin", a=0.005, tau=0.10, duty=0.5):
    n = _nsec(dur)
    return _osc(wave, ph_const(freq, n), duty) * env_perc(n, a, tau)


def chirp(f0, f1, dur, wave="sin", a=0.004, tau=0.08, kind="exp", duty=0.5):
    n = _nsec(dur)
    return _osc(wave, ph_sweep(f0, f1, n, kind), duty) * env_perc(n, a, tau)


def nois(dur, seed, f_lo=None, f_hi=None, hp=None, a=0.003, tau=0.08):
    n = _nsec(dur)
    y = white(_rng(seed), n)
    if hp is not None:
        y = hp1(y, hp)
    if f_lo is not None and f_hi is not None:
        y = bp1(y, f_lo, f_hi)
    elif f_hi is not None:
        y = lp1(y, f_hi)
    return y * env_perc(n, a, tau)


def am_tone(freq, dur, rate, depth=0.5, a=0.005, tau=0.30):
    n = _nsec(dur)
    t = t_ax(n)
    m = (1.0 - depth) + depth * (0.5 - 0.5 * np.cos(TAU * rate * t))
    return osc_sin(ph_const(freq, n)) * m * env_perc(n, a, tau)


_BELL_PARTIALS = ((1.0, 1.00, 1.0), (2.0, 0.40, 1.5), (2.76, 0.25, 2.0), (5.4, 0.08, 3.0))


def bell(freq, dur, a=0.008, tau=0.50):
    n = _nsec(dur)
    t = t_ax(n)
    out = np.zeros(n)
    for r, amp, sp in _BELL_PARTIALS:
        out += amp * np.sin(TAU * r * freq * t + 0.15 * r) * np.exp(-t / (tau / sp))
    return out * np.clip(t / max(float(a), 1e-5), 0.0, 1.0)


# --------------------------------------------------------------------------
# 36 SFX
# --------------------------------------------------------------------------
def sfx_shoot_tack():
    # "tak" seco y corto (grapadora / chinchetas)
    return pack(0.07, [
        (0.0, chirp(2000, 900, 0.06, "sqr", 0.0005, 0.012), 1.00),
        (0.0, nois(0.006, 101, hp=3000, a=0.0002, tau=0.002), 0.70),
    ])


def sfx_shoot_marker():
    # click suave y humedo (rotulador)
    return pack(0.12, [
        (0.0, chirp(700, 320, 0.10, "sin", 0.008, 0.030), 1.00),
        (0.0, nois(0.08, 102, f_lo=500, f_hi=1600, a=0.010, tau=0.025), 0.55),
    ])


def sfx_shoot_heavy():
    # lanzamiento contundente y grave (sello de goma)
    return pack(0.35, [
        (0.0, chirp(210, 55, 0.30, "sin", 0.004, 0.090), 1.00),
        (0.0, nois(0.30, 103, f_hi=300, a=0.004, tau=0.120), 0.50),
        (0.0, tone(90, 0.10, "tri", 0.004, 0.030), 0.30),
        (0.0, tone(137, 0.08, "sin", 0.004, 0.025), 0.20),
    ])


def sfx_shoot_throw():
    # whoosh corto de lanzamiento (tijeras / clips)
    return pack(0.28, [
        (0.00, nois(0.24, 104, f_lo=350, f_hi=900, a=0.020, tau=0.070), 0.90),
        (0.02, nois(0.20, 105, f_lo=1500, f_hi=4500, a=0.030, tau=0.060), 0.60),
        (0.00, chirp(300, 850, 0.16, "sin", 0.020, 0.060), 0.25),
    ])


def sfx_beam_loop():
    # zumbido laser EXACTO de 2.000 s, PERFECTAMENTE en loop.
    # Todas las frecuencias son multiplos de 0.5 Hz -> periodo matematico = 2 s;
    # se gira el buffer a un cruce por cero para que x[0] ~= 0 sin romper el bucle.
    n = int(round(2.0 * SR))  # 44100
    t = t_ax(n)
    f0, A, r = 110.0, 2.0, 3.0
    ph0 = f0 * t + A * (1.0 - np.cos(TAU * r * t)) / (TAU * r)  # vibrado periodico
    sig = (osc_saw(ph0) * 0.45
           + osc_saw(ph0 * (111.0 / 110.0)) * 0.38
           + osc_sqr(ph0 * 0.5, 0.5) * 0.22
           + osc_sin(ph0 * 2.0) * 0.30
           + osc_sin(ph0 * 12.0) * 0.10)
    m = 0.72 + 0.28 * (0.5 - 0.5 * np.cos(TAU * 4.0 * t))
    sig = lp1(sig * m, 2600.0)
    k = int(np.argmin(np.abs(sig)))
    return np.roll(sig, -k)


def sfx_chain_zap():
    # chispazo electrico con crackle
    rng = _rng(1060)
    parts = [
        (0.00, chirp(1400, 260, 0.05, "sqr", 0.0003, 0.018), 0.85),
        (0.05, chirp(1500, 300, 0.05, "sqr", 0.0003, 0.016), 0.70),
        (0.12, chirp(1200, 220, 0.06, "sqr", 0.0003, 0.018), 0.60),
        (0.00, chirp(210, 90, 0.30, "saw", 0.002, 0.100), 0.30),
    ]
    for i in range(14):
        t0 = 0.03 + 0.30 * float(rng.random() ** 0.8)
        d = float(rng.uniform(0.003, 0.008))
        parts.append((t0, nois(d, 1061 + i, hp=3500, a=0.0002, tau=d * 0.6),
                      float(rng.uniform(0.25, 0.70))))
    return pack(0.46, parts)


def sfx_aura_pulse():
    # pulso tipo sonar/sub (aura de radio)
    return pack(0.85, [
        (0.000, chirp(64, 52, 0.75, "sin", 0.020, 0.350), 1.00),
        (0.000, tone(32, 0.60, "sin", 0.020, 0.300), 0.50),
        (0.000, tone(220, 0.50, "sin", 0.010, 0.150), 0.15),
        (0.015, tone(880, 0.08, "sin", 0.002, 0.050), 0.18),
    ])


def sfx_nova():
    # onda expansiva tipo boom con vibracion
    return pack(1.30, [
        (0.00, chirp(190, 38, 0.55, "sin", 0.003, 0.300), 1.00),
        (0.00, nois(0.90, 108, f_hi=1100, a=0.006, tau=0.400), 0.55),
        (0.05, am_tone(58, 0.90, 20.0, 0.60, a=0.010, tau=0.450), 0.60),
        (0.00, chirp(40, 34, 0.90, "sin", 0.010, 0.500), 0.30),
    ])


def sfx_explosion_small():
    return pack(0.32, [
        (0.0, nois(0.28, 109, f_hi=900, a=0.002, tau=0.090), 1.00),
        (0.0, chirp(190, 70, 0.20, "sin", 0.001, 0.070), 0.90),
        (0.0, nois(0.010, 110, hp=4000, a=0.0005, tau=0.004), 0.40),
    ])


def sfx_explosion_big():
    # boom grande con cola
    rng = _rng(1110)
    parts = [
        (0.00, chirp(130, 32, 0.80, "sin", 0.004, 0.450), 1.00),
        (0.00, nois(0.90, 111, f_hi=700, a=0.004, tau=0.500), 0.70),
        (0.00, nois(1.40, 112, f_lo=300, f_hi=2500, a=0.100, tau=0.600), 0.28),
        (0.00, am_tone(48, 1.00, 30.0, 0.50, a=0.010, tau=0.500), 0.35),
    ]
    for i in range(8):
        t0 = float(rng.uniform(0.0, 0.22))
        d = float(rng.uniform(0.005, 0.012))
        parts.append((t0, nois(d, 1111 + i, hp=3000, a=0.0003, tau=d * 0.6),
                      float(rng.uniform(0.30, 0.70))))
    return pack(1.60, parts)


def sfx_hit_enemy():
    # impacto corto y seco
    return pack(0.14, [
        (0.0, chirp(330, 140, 0.10, "sin", 0.001, 0.030), 1.00),
        (0.0, nois(0.06, 113, f_hi=2600, a=0.001, tau=0.020), 0.70),
        (0.0, nois(0.004, 114, hp=5000, a=0.0003, tau=0.002), 0.30),
    ])


def sfx_hit_crit():
    # impacto brillante/agudo
    return pack(0.30, [
        (0.0, chirp(420, 180, 0.12, "sin", 0.001, 0.035), 0.90),
        (0.0, nois(0.08, 115, f_lo=2000, f_hi=6500, a=0.001, tau=0.045), 0.60),
        (0.0, chirp(1900, 1150, 0.20, "sin", 0.001, 0.090), 0.50),
        (0.0, chirp(1250, 1000, 0.14, "sqr", 0.001, 0.120, duty=0.25), 0.30),
    ])


def sfx_enemy_die():
    # crujido pequeno + chispa
    return pack(0.42, [
        (0.00, nois(0.030, 1161, f_lo=600, f_hi=2200, a=0.0008, tau=0.012), 0.90),
        (0.04, nois(0.025, 1162, f_lo=650, f_hi=2100, a=0.0008, tau=0.010), 0.65),
        (0.09, nois(0.030, 1163, f_lo=560, f_hi=2400, a=0.0008, tau=0.012), 0.75),
        (0.05, nois(0.020, 1164, f_lo=700, f_hi=2000, a=0.0008, tau=0.009), 0.55),
        (0.12, nois(0.030, 1165, f_lo=520, f_hi=2300, a=0.0008, tau=0.012), 0.50),
        (0.18, chirp(1000, 360, 0.14, "sqr", 0.0005, 0.050), 0.45),
        (0.16, nois(0.05, 1166, hp=4500, a=0.0005, tau=0.020), 0.30),
        (0.00, tone(150, 0.10, "sin", 0.002, 0.050), 0.40),
    ])


def sfx_enemy_die_big():
    # splat + crunch mas gordo
    rng = _rng(1170)
    parts = [
        (0.00, nois(0.30, 117, f_hi=520, a=0.005, tau=0.070), 1.00),
        (0.00, chirp(120, 50, 0.25, "sin", 0.003, 0.100), 0.80),
        (0.00, tone(58, 0.40, "sin", 0.005, 0.250), 0.45),
        (0.25, nois(0.50, 118, f_hi=900, a=0.050, tau=0.300), 0.35),
        (0.55, chirp(900, 300, 0.20, "sqr", 0.0005, 0.070), 0.25),
    ]
    for i in range(9):
        t0 = float(rng.uniform(0.02, 0.50))
        d = float(rng.uniform(0.012, 0.030))
        parts.append((t0, nois(d, 1171 + i, f_lo=300, f_hi=2600, a=0.001, tau=d * 0.55),
                      float(rng.uniform(0.40, 0.90))))
    return pack(0.95, parts)


def sfx_player_hurt():
    # golpe + alarma
    return pack(0.55, [
        (0.00, nois(0.12, 119, f_hi=2200, a=0.001, tau=0.045), 0.90),
        (0.00, chirp(260, 95, 0.15, "sin", 0.001, 0.055), 0.70),
        (0.14, tone(760, 0.12, "sqr", 0.004, 0.090), 0.30),
        (0.30, tone(540, 0.12, "sqr", 0.004, 0.090), 0.30),
    ])


def sfx_player_dash():
    # swoosh rapido
    return pack(0.22, [
        (0.00, nois(0.18, 120, f_lo=700, f_hi=3000, a=0.020, tau=0.055), 0.90),
        (0.02, nois(0.14, 121, f_lo=2500, f_hi=7000, a=0.020, tau=0.045), 0.50),
        (0.00, chirp(250, 950, 0.15, "sin", 0.020, 0.050), 0.25),
    ])


def sfx_fogonazo():
    # flash de camara + whoosh brillante
    return pack(0.50, [
        (0.000, nois(0.006, 122, hp=6000, a=0.0002, tau=0.002), 0.50),
        (0.000, tone(4200, 0.09, "sin", 0.001, 0.045), 0.50),
        (0.004, tone(6300, 0.05, "sin", 0.001, 0.030), 0.30),
        (0.010, nois(0.35, 123, f_lo=1500, f_hi=6000, a=0.020, tau=0.100), 0.55),
        (0.000, nois(0.15, 124, f_hi=1500, a=0.005, tau=0.050), 0.35),
    ])


def _pickup_xp(tr):
    # blip ascendente; xp2 = +4 semitonos, xp3 = +7 semitonos
    return pack(0.13, [
        (0.0, chirp(660.0 * tr, 990.0 * tr, 0.09, "tri", 0.001, 0.032), 1.00),
        (0.0, chirp(660.0 * tr, 990.0 * tr, 0.09, "sqr", 0.001, 0.030), 0.25),
    ])


def sfx_pickup_xp1():
    return _pickup_xp(1.0)


def sfx_pickup_xp2():
    return _pickup_xp(2.0 ** (4.0 / 12.0))


def sfx_pickup_xp3():
    return _pickup_xp(2.0 ** (7.0 / 12.0))


def sfx_pickup_coin():
    # dos tonos tipo monedas
    return pack(0.40, [
        (0.00, tone(988, 0.07, "tri", 0.001, 0.050), 0.90),
        (0.06, tone(1319, 0.30, "tri", 0.001, 0.160), 0.90),
        (0.06, tone(2637, 0.20, "sin", 0.001, 0.100), 0.25),
    ])


def sfx_pickup_heal():
    # campanita calida ascendente
    parts = []
    for i, nt in enumerate(("C5", "E5", "G5")):
        parts.append((0.13 * i, bell(f_of(nt), 0.55, a=0.010, tau=0.28), 0.80))
    parts.append((0.26, bell(f_of("G4"), 0.45, a=0.010, tau=0.22), 0.30))
    return pack(0.75, parts)


def sfx_levelup():
    # jingle ascendente de ~1.2 s
    parts = []
    for i, nt in enumerate(("C5", "E5", "G5", "C6", "E6", "G6", "C7")):
        n = _nsec(0.13)
        ph = ph_const(f_of(nt), n)
        sig = (osc_sqr(ph, 0.30) * 0.72 + osc_sin(ph) * 0.28) * env_perc(n, 0.001, 0.050)
        parts.append((0.09 * i, sig, 0.55))
    for nt in ("C6", "E6", "G6"):
        n = _nsec(0.62)
        ph = ph_const(f_of(nt), n)
        sig = (osc_sqr(ph, 0.45) * 0.60 + osc_sin(ph) * 0.40) * env_perc(n, 0.004, 0.350)
        parts.append((0.68, sig, 0.30))
    return pack(1.30, parts)


def sfx_wave_start():
    # campana de reloj + papeles
    parts = [(0.0, bell(740.0, 1.10, a=0.002, tau=0.55), 0.80),
             (0.5, bell(741.0, 0.90, a=0.002, tau=0.45), 0.35)]
    rng = _rng(1240)
    for i in range(12):
        t0 = 0.35 + 0.75 * float(rng.random())
        d = float(rng.uniform(0.020, 0.045))
        parts.append((t0, nois(d, 1241 + i, f_lo=900, f_hi=4200, a=0.004, tau=d * 0.7),
                      float(rng.uniform(0.18, 0.45))))
    return pack(1.35, parts)


def sfx_boss_spawn():
    # sirena grave ominosa
    n = _nsec(3.0)
    t = t_ax(n)
    f = 52.0 + 6.0 * np.sin(TAU * 0.5 * t)
    ph1 = np.cumsum(f) / SR
    ph2 = np.cumsum(f * 1.06) / SR
    sub = np.cumsum(f * 0.5) / SR
    g = np.clip(t / 0.5, 0.0, 1.0) * np.exp(-np.maximum(t - 2.1, 0.0) / 0.45)
    siren = (osc_saw(ph1) * 0.50 + osc_saw(ph2) * 0.35 + osc_sin(sub) * 0.45) * g
    siren = lp1(siren, 600.0)
    rum = nois(3.0, 125, f_hi=150.0, a=0.30, tau=1.8)
    deep = osc_sin(TAU * 33.0 * t) * env_perc(n, 0.40, 1.5)
    return pack(3.0, [(0.0, siren, 1.00), (0.0, rum, 0.40), (0.0, deep, 0.30)])


def sfx_boss_die():
    # descenso largo + cola triunfal
    d = lp1(chirp(380, 45, 2.0, "saw", 0.006, 0.900), 1000.0)
    parts = [
        (0.00, d, 0.90),
        (0.50, nois(0.70, 126, f_hi=600, a=0.003, tau=0.500), 0.70),
        (0.50, chirp(100, 35, 0.50, "sin", 0.002, 0.300), 0.70),
        (2.00, nois(0.90, 127, hp=3200, a=0.002, tau=0.450), 0.30),
    ]
    for nt in ("C5", "E5", "G5", "C6"):
        n = _nsec(0.9)
        ph = ph_const(f_of(nt), n)
        sig = (osc_sin(ph) * 0.70 + osc_sqr(ph, 0.40) * 0.30) * env_perc(n, 0.05, 0.42)
        parts.append((2.05, sig, 0.20))
    return pack(3.40, parts)


def sfx_victory():
    # fanfarria corta (~3 s)
    parts = []

    def lead(t0, nt, dur, vel):
        n = _nsec(dur)
        ph = ph_const(f_of(nt), n)
        sig = (osc_sqr(ph, 0.5) * 0.65 + osc_sin(ph) * 0.35) * env_adsr(n, 0.004, 0.05, 0.65, 0.06)
        parts.append((t0, sig, vel))

    for i, nt in enumerate(("C5", "E5", "G5", "C6")):
        lead(0.12 * i, nt, 0.14, 0.55)
    lead(0.50, "G5", 0.12, 0.50)
    lead(0.62, "C6", 0.14, 0.55)
    for nt in ("C6", "E6", "G6"):
        lead(0.80, nt, 1.05, 0.40)
    for nt in ("C6", "E6", "G6", "C7"):
        lead(2.05, nt, 0.85, 0.42)
    sn = nois(0.09, 128, f_hi=6500, a=0.001, tau=0.050)
    sn2 = tone(190, 0.07, "sin", 0.001, 0.030)
    for t0, g in ((0.0, 0.40), (0.36, 0.40), (0.80, 0.45), (2.05, 0.50)):
        parts.append((t0, sn, g))
        parts.append((t0, sn2, g * 0.7))
    parts.append((2.05, nois(0.90, 129, hp=3500, a=0.002, tau=0.450), 0.35))
    return pack(3.00, parts)


def sfx_game_over():
    # apagado descendente de lampara (power down)
    d1 = lp1(chirp(620, 45, 1.7, "saw", 0.012, 1.10), 900.0)
    return pack(2.70, [
        (0.00, nois(0.006, 130, hp=5000, a=0.0003, tau=0.003), 0.35),
        (0.15, d1, 0.90),
        (0.15, chirp(310, 30, 1.7, "sin", 0.010, 1.05), 0.50),
        (2.15, chirp(70, 36, 0.40, "sin", 0.006, 0.160), 0.45),
    ])


def sfx_ui_click():
    # tecla de teclado
    return pack(0.06, [
        (0.0, nois(0.004, 131, hp=4000, a=0.0002, tau=0.002), 0.60),
        (0.0, tone(2200, 0.012, "sqr", 0.0005, 0.006), 0.45),
        (0.0, tone(1100, 0.020, "sin", 0.001, 0.010), 0.30),
    ])


def sfx_ui_hover():
    # tick suave
    return pack(0.055, [
        (0.0, tone(1350, 0.03, "sin", 0.002, 0.012), 0.70),
    ])


def sfx_ui_deny():
    # buzz de error
    n = _nsec(0.28)
    t = t_ax(n)
    ph = np.cumsum(np.linspace(150.0, 118.0, n)) / SR
    sq = osc_sqr(ph, 0.5) + 0.6 * osc_sqr(ph * 1.24, 0.5)
    am = 0.62 + 0.38 * (0.5 - 0.5 * np.cos(TAU * 28.0 * t))
    return pack(0.28, [(0.0, sq * am * env_perc(n, 0.005, 0.120), 0.75)])


def sfx_shop_buy():
    # moneda + clunk
    return pack(0.50, [
        (0.00, tone(988, 0.06, "tri", 0.001, 0.040), 0.80),
        (0.05, tone(1319, 0.12, "tri", 0.001, 0.080), 0.80),
        (0.16, chirp(150, 80, 0.15, "sin", 0.002, 0.060), 0.90),
        (0.16, nois(0.08, 132, f_hi=500, a=0.002, tau=0.040), 0.50),
        (0.16, tone(300, 0.03, "sqr", 0.001, 0.012), 0.20),
    ])


def sfx_shop_reroll():
    # traqueteo de maquina expendedora
    parts = [(0.02, tone(1568, 0.05, "sin", 0.001, 0.030), 0.25)]
    for i, t0 in enumerate((0.00, 0.09, 0.17, 0.24, 0.30, 0.35, 0.39, 0.42)):
        parts.append((t0, nois(0.014, 1333 + i, f_lo=800, f_hi=2600, a=0.0005, tau=0.008),
                      0.45 + 0.05 * i))
    parts.append((0.50, nois(0.05, 1341, f_lo=500, f_hi=1800, a=0.001, tau=0.030), 0.90))
    parts.append((0.50, tone(210, 0.08, "sin", 0.002, 0.040), 0.50))
    return pack(0.90, parts)


def sfx_merge():
    # clac de grapadora + zip
    parts = [
        (0.00, chirp(1500, 650, 0.06, "sqr", 0.0004, 0.018), 0.90),
        (0.00, nois(0.006, 135, hp=3200, a=0.0003, tau=0.003), 0.40),
    ]
    for i in range(36):
        parts.append((0.06 + 0.009 * i, tone(1400.0 + 45.0 * i, 0.006, "sin", 0.0003, 0.0025), 0.22))
    parts.append((0.42, nois(0.006, 136, hp=2500, a=0.0003, tau=0.004), 0.50))
    parts.append((0.42, tone(700, 0.02, "sqr", 0.001, 0.008), 0.30))
    return pack(0.50, parts)


def sfx_crate_break():
    # carton rompiendose
    rng = _rng(1370)
    parts = [
        (0.00, chirp(200, 75, 0.08, "sin", 0.001, 0.040), 0.60),
        (0.02, nois(0.40, 137, f_lo=600, f_hi=3200, a=0.010, tau=0.220), 0.50),
        (0.05, nois(0.30, 138, f_lo=1500, f_hi=5000, a=0.020, tau=0.180), 0.35),
    ]
    for i in range(16):
        t0 = float(rng.uniform(0.01, 0.50))
        d = float(rng.uniform(0.010, 0.030))
        parts.append((t0, nois(d, 1371 + i, f_lo=700, f_hi=2800, a=0.001, tau=d * 0.6),
                      float(rng.uniform(0.30, 0.85))))
    return pack(0.75, parts)


def sfx_tape_hit():
    # despegue pegajoso
    n = _nsec(0.42)
    t = t_ax(n)
    base = lp1(white(_rng(1390), n), 2400.0)
    mod = 0.55 + 0.45 * np.clip(np.sin(TAU * 13.0 * t + 3.0 * np.sin(TAU * 2.1 * t)), 0.0, 1.0)
    sig = base * mod * env_perc(n, 0.045, 0.18)
    return pack(0.45, [
        (0.0, sig, 0.90),
        (0.0, nois(0.15, 140, f_lo=200, f_hi=700, a=0.020, tau=0.060), 0.40),
        (0.30, chirp(900, 420, 0.09, "sin", 0.002, 0.030), 0.40),
    ])


# --------------------------------------------------------------------------
# Musica: notas, instrumentos, secuenciador
# --------------------------------------------------------------------------
_PC = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6,
       "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def mid_of(name):
    """'A#4' / 'Bb3' -> numero MIDI (A4 = 69)."""
    s = name.strip()
    letter = s[0].upper()
    i = 1
    acc = 0
    while i < len(s) and s[i] in "#b":
        acc += 1 if s[i] == "#" else -1
        i += 1
    octv = int(s[i:])
    return 12 * (octv + 1) + _PC[letter] + acc


def f_of(name):
    """Nombre de nota -> frecuencia en Hz (temperamento igual, A4 = 440)."""
    return 440.0 * (2.0 ** ((mid_of(name) - 69) / 12.0))


PAD_CHORDS = {
    "Am": ["A3", "C4", "E4"],
    "F": ["F3", "A3", "C4"],
    "C": ["C4", "E4", "G4"],
    "G": ["G3", "B3", "D4"],
    "Dm": ["D3", "F3", "A3"],
    "E": ["E3", "G#3", "B3"],
    "Bb": ["A#3", "D4", "F4"],
}
BASS_ROOT = {"Am": "A2", "F": "F2", "C": "C3", "G": "G2",
             "Dm": "D2", "E": "E2", "Bb": "A#2"}


def chord_freqs(ch):
    return [f_of(n) for n in PAD_CHORDS[ch]]


def inst_pad(freq, dur, vel=1.0):
    """Pad oscuro: 3 voces desafinadas, ataque/release lentos."""
    n = _nsec(dur)
    t = t_ax(n)
    out = np.zeros(n)
    for det, g in ((0.996, 1.0), (1.0, 1.0), (1.004, 0.9)):
        ph = freq * det * t
        out += g * (np.sin(TAU * ph) + 0.42 * np.sin(2 * TAU * ph)
                    + 0.18 * np.sin(3 * TAU * ph) + 0.07 * np.sin(5 * TAU * ph))
    a = min(int(0.55 * SR), n // 3)
    r = min(int(0.90 * SR), n // 3)
    w = np.ones(n)
    if a > 1:
        w[:a] = np.linspace(0.0, 1.0, a) ** 1.5
    if r > 1:
        w[-r:] *= np.linspace(1.0, 0.0, r) ** 1.1
    return out * w * (vel / 3.2)


def pad_chord(ch, dur, vel):
    return sum(inst_pad(f, dur, vel) for f in chord_freqs(ch))


def inst_bass(freq, dur, vel=1.0):
    """Bajo chiptune en negras/octavas."""
    n = _nsec(dur)
    ph = ph_const(freq, n)
    env = env_adsr(n, 0.008, 0.03, 0.72, 0.05)
    return (osc_sin(ph) + 0.42 * osc_sin(ph * 2.0) + 0.16 * osc_tri(ph)) * env * (vel / 1.6)


def inst_pluck(freq, dur, vel=1.0):
    n = _nsec(dur)
    ph = ph_const(freq, n)
    env = env_adsr(n, 0.002, 0.045, 0.18, 0.04)
    return (osc_sqr(ph, 0.35) * 0.72 + osc_sin(ph) * 0.28) * env * vel


def inst_lead(freq, dur, vel=1.0):
    n = _nsec(dur)
    ph = ph_const(freq, n)
    env = env_adsr(n, 0.004, 0.04, 0.60, 0.05)
    return (osc_sqr(ph, 0.5) * 0.70 + osc_sin(ph) * 0.30) * env * vel


def inst_bell(freq, dur, vel=1.0, tau=0.8):
    n = _nsec(dur)
    t = t_ax(n)
    out = np.zeros(n)
    for r, amp, sp in ((1.0, 1.00, 1.0), (2.0, 0.40, 1.5), (2.76, 0.25, 2.0), (5.4, 0.08, 3.0)):
        out += amp * np.sin(TAU * r * freq * t + 0.15 * r) * np.exp(-t / (tau / sp))
    return out * np.clip(t / 0.004, 0.0, 1.0) * vel


def inst_kick(vel=1.0, seed=9001):
    sig = chirp(150, 46, 0.24, "sin", 0.0006, 0.085)
    cl = nois(0.005, seed, hp=3000, a=0.0002, tau=0.002)
    sig[:cl.size] += cl * 0.5
    return sig * vel


def inst_hat(vel=1.0, open_=False, seed=9002):
    tau = 0.070 if open_ else 0.016
    dur = 0.18 if open_ else 0.06
    return hp1(hp1(nois(dur, seed, a=0.0004, tau=tau), 4000.0), 4000.0) * 0.5 * vel


def inst_snare(vel=1.0, seed=9003):
    a = nois(0.16, seed, f_hi=6200, a=0.0008, tau=0.050)
    b = tone(190, 0.08, "sin", 0.0008, 0.030)
    a[:b.size] += b * 0.5
    return a * 0.5 * vel


def inst_crash(vel=1.0, seed=9004):
    y = hp1(hp1(white(_rng(seed), _nsec(1.4)), 3200.0), 3200.0)
    y = lp1(y, 8000.0)
    return y * env_perc(y.size, 0.002, 0.55) * 0.5 * vel


def inst_stab(freqs, dur, vel=1.0):
    n = _nsec(dur)
    out = np.zeros(n)
    for f in freqs:
        ph = ph_const(f, n)
        out += osc_sqr(ph, 0.45) * 0.6 + osc_sin(ph) * 0.4
    return out * env_adsr(n, 0.003, 0.05, 0.12, 0.05) * (vel / max(len(freqs), 1))


class Song:
    """Secuenciador por pasos (negra = unidad) con render en bucle (wrap)."""

    def __init__(self, bpm, total_beats):
        self.bpm = float(bpm)
        self.spb = 60.0 / self.bpm            # segundos por negra
        self.total_beats = float(total_beats)
        self.n = int(round(self.total_beats * self.spb * SR))
        self.mix = Mix(self.n, wrap=True)

    def add(self, beat, sig, gain=1.0):
        self.mix.add(float(beat) * self.spb, sig, gain)


# ------------------------------- piezas -----------------------------------
def build_menu():
    """60 s exactos a 72 bpm (18 compases 4/4), ambient oscuro en La menor."""
    bpm = 72.0
    s = Song(bpm, 18 * 4)
    spb = 60.0 / bpm
    chords = ["Am", "F", "C", "G", "Am", "F", "Dm", "E", "Am"]  # 2 compases c/u
    for i, ch in enumerate(chords):
        t0 = i * 8.0 - (1.2 if i == 0 else 0.0)  # el 1er pad ataca cruzando el empalme
        s.add(t0, pad_chord(ch, 8 * spb + 0.9, 0.55))
    for bar in range(18):
        ch = chords[bar // 2]
        s.add(bar * 4.0, inst_bass(f_of(BASS_ROOT[ch]), 4 * spb * 0.96, 0.50))
    mel = [(4.0, "E5", 0.30), (6.5, "A5", 0.20), (10.0, "C5", 0.26), (17.0, "D5", 0.24),
           (22.0, "G5", 0.20), (27.0, "C5", 0.28), (37.0, "A4", 0.28), (50.0, "D5", 0.24),
           (60.0, "B4", 0.26), (66.0, "A4", 0.30), (70.0, "E5", 0.24)]
    for b, nt, v in mel:
        s.add(b, inst_bell(f_of(nt), 2.6, v * 0.8, tau=1.1))
    for b0 in (16.0, 48.0):
        n = _nsec(12.0)
        y = lp1(white(_rng(400 + int(b0)), n), 320.0)
        w = np.sin(np.pi * np.arange(n) / (n - 1.0)) ** 2
        s.add(b0, y * w * 0.05)
    return s


def build_combat():
    """64 s exactos a 120 bpm (32 compases): arpegio + bajo + kick/hat/snare."""
    bpm = 120.0
    s = Song(bpm, 32 * 4)
    spb = 60.0 / bpm
    prog = ["Am", "F", "C", "G"]
    for bar in range(32):
        ch = prog[bar % 4]
        b = bar * 4.0
        s.add(b, pad_chord(ch, 4 * spb + 0.4, 0.30))
        s.add(b, inst_kick(0.95))
        s.add(b + 2.0, inst_kick(0.85))
        if bar % 4 == 3:
            s.add(b + 3.5, inst_kick(0.50))
        s.add(b + 1.0, inst_snare(0.60))
        s.add(b + 3.0, inst_snare(0.60))
        for k in range(8):
            v = 0.30 if k % 2 == 0 else 0.22
            if k in (3, 7):
                v *= 0.6
            s.add(b + 0.5 * k, inst_hat(v))
        if bar % 2 == 1:
            s.add(b + 3.75, inst_hat(0.25, open_=True))
        root = f_of(BASS_ROOT[ch])
        for k in range(8):
            ff = root * (2.0 if k in (3, 7) else 1.0)
            vv = 0.50 if k % 2 == 0 else 0.36
            s.add(b + 0.5 * k, inst_bass(ff, 0.6 * spb, vv))
        cf = chord_freqs(ch)
        seq = (cf[0], cf[1], cf[2], cf[1])
        for k16 in range(16):
            s.add(b + 0.25 * k16, inst_pluck(seq[k16 % 4] * 2.0, 0.3 * spb, 0.30))
    s.add(32 * 4 - 0.4, inst_crash(0.90, seed=9006))   # crash que resuelve en el loop
    s.add(64.0, inst_crash(0.55, seed=9007))
    for k in range(8):
        s.add(124.0 + 0.5 * k, inst_snare(0.25 + 0.05 * k, seed=9010 + k))
    s.add(124.0, inst_bass(f_of("G2"), 2.6, 0.55))     # raiz sostenida que cruza el empalme
    return s


def build_boss():
    """56 s exactos a 150 bpm (35 compases): agresivo, tension cromatica."""
    bpm = 150.0
    s = Song(bpm, 35 * 4)
    spb = 60.0 / bpm
    bars = (["Am", "Bb", "Am", "E"] * 8 + ["F", "E", "Am"])[:35]
    riff = ["A4", "A#4", "A4", "E5", "D5", "C5", "B4", "A4"]
    for bar in range(35):
        ch = bars[bar]
        b = bar * 4.0
        s.add(b, pad_chord(ch, 4 * spb + 0.3, 0.24))
        for k in range(4):
            s.add(b + k, inst_kick(0.85 if k % 2 == 0 else 0.72))
        for k in range(16):
            s.add(b + 0.25 * k, inst_hat(0.14 if k % 2 else 0.26))
        if bar % 4 == 3:
            s.add(b + 3.75, inst_hat(0.22, open_=True))
        root = f_of(BASS_ROOT[ch])
        for k in range(8):
            ff = root
            if ch == "E" and k == 5:
                ff = root * (2.0 ** (6.0 / 12.0))   # paso de tritono
            if k in (3, 7):
                ff = ff * 2.0
            s.add(b + 0.5 * k, inst_bass(ff, 0.6 * spb, 0.46 if k % 2 == 0 else 0.34))
        if ch in ("E", "Bb"):
            s.add(b + 2.5, inst_stab(chord_freqs(ch), 0.35, 0.50))
            if ch == "E":
                s.add(b + 3.5, inst_stab(chord_freqs(ch), 0.35, 0.45))
        if (8 <= bar < 16) or (24 <= bar < 32):
            for k in range(8):
                s.add(b + 0.5 * k, inst_lead(f_of(riff[k]), 0.55 * spb, 0.26))
    s.add(140.0 - 0.4, inst_crash(0.90, seed=9020))
    for k in range(8):
        s.add(136.0 + 0.5 * k, inst_snare(0.20 + 0.05 * k, seed=9030 + k))
    for nt, v in (("A2", 0.50), ("A3", 0.42)):          # campana grave que pesa sobre el empalme
        s.add(135.0, inst_bell(f_of(nt), 4.2, v, tau=2.6))
    return s


def build_victory():
    """24 s exactos a 120 bpm (12 compases), Do mayor triunfal."""
    bpm = 120.0
    s = Song(bpm, 12 * 4)
    spb = 60.0 / bpm
    barsch = ["C", "C", "C", "G", "F", "G", "C", "F", "G", "C", "C", "C"]
    for bar in range(12):
        s.add(bar * 4.0, pad_chord(barsch[bar], 4 * spb + 0.4, 0.30))
    arp = ["C5", "E5", "G5", "C6", "E5", "G5", "C6", "E6"]
    for k in range(16):
        s.add(k * 0.5, inst_pluck(f_of(arp[k % 8]), 0.55, 0.20 + 0.02 * k))
    for k in range(8):
        s.add(4.0 + 0.5 * k, inst_snare(0.15 + 0.06 * k, seed=9040 + k))
    mel = [
        (8.0, "E5", 1.0, 0.55), (9.0, "G5", 0.5, 0.50), (9.5, "C6", 2.5, 0.60),
        (12.0, "G5", 1.0, 0.50), (13.0, "A5", 0.5, 0.50), (13.5, "G5", 0.5, 0.50),
        (14.0, "E5", 1.0, 0.55), (15.0, "C5", 1.0, 0.50),
        (16.0, "F5", 1.5, 0.55), (17.5, "A5", 1.0, 0.55), (18.5, "C6", 1.5, 0.60),
        (20.0, "D6", 1.0, 0.55), (21.0, "B5", 1.0, 0.50), (22.0, "G5", 2.0, 0.55),
        (24.0, "C6", 2.0, 0.60), (26.0, "E6", 1.0, 0.50), (27.0, "G5", 1.0, 0.50),
        (28.0, "A5", 2.0, 0.55), (30.0, "C6", 2.0, 0.60),
        (32.0, "B5", 2.0, 0.55), (34.0, "D6", 2.0, 0.60),
        (36.0, "C6", 3.5, 0.65),
    ]
    for b, nt, dur, v in mel:
        s.add(b, inst_lead(f_of(nt), dur * spb * 0.98 + 0.1, v))
    for nt in ("C6", "E6", "G6"):
        s.add(40.0, inst_lead(f_of(nt), 8 * spb + 0.6, 0.40))   # cola cruza el empalme
        s.add(40.0, inst_bell(f_of(nt), 8 * spb + 0.5, 0.28, tau=1.4))
    for bar in range(12):
        s.add(bar * 4.0, inst_bass(f_of(BASS_ROOT[barsch[bar]]) * 2.0, 3.6 * spb, 0.50))
    for bar in range(2, 10):
        s.add(bar * 4.0, inst_kick(0.70))
        s.add(bar * 4.0 + 2.0, inst_kick(0.60))
    s.add(0.0, inst_crash(0.90, seed=9050))
    s.add(8.0, inst_crash(0.40, seed=9051))
    s.add(40.0, inst_crash(0.90, seed=9052))
    s.add(47.6, inst_crash(0.50, seed=9053))   # cola cruza el empalme
    return s


# --------------------------------------------------------------------------
# Registro, diagnostico y main
# --------------------------------------------------------------------------
SFX_BUILDERS = [
    ("shoot_tack", sfx_shoot_tack),
    ("shoot_marker", sfx_shoot_marker),
    ("shoot_heavy", sfx_shoot_heavy),
    ("shoot_throw", sfx_shoot_throw),
    ("beam_loop", sfx_beam_loop),
    ("chain_zap", sfx_chain_zap),
    ("aura_pulse", sfx_aura_pulse),
    ("nova", sfx_nova),
    ("explosion_small", sfx_explosion_small),
    ("explosion_big", sfx_explosion_big),
    ("hit_enemy", sfx_hit_enemy),
    ("hit_crit", sfx_hit_crit),
    ("enemy_die", sfx_enemy_die),
    ("enemy_die_big", sfx_enemy_die_big),
    ("player_hurt", sfx_player_hurt),
    ("player_dash", sfx_player_dash),
    ("fogonazo", sfx_fogonazo),
    ("pickup_xp1", sfx_pickup_xp1),
    ("pickup_xp2", sfx_pickup_xp2),
    ("pickup_xp3", sfx_pickup_xp3),
    ("pickup_coin", sfx_pickup_coin),
    ("pickup_heal", sfx_pickup_heal),
    ("levelup", sfx_levelup),
    ("wave_start", sfx_wave_start),
    ("boss_spawn", sfx_boss_spawn),
    ("boss_die", sfx_boss_die),
    ("victory", sfx_victory),
    ("game_over", sfx_game_over),
    ("ui_click", sfx_ui_click),
    ("ui_hover", sfx_ui_hover),
    ("ui_deny", sfx_ui_deny),
    ("shop_buy", sfx_shop_buy),
    ("shop_reroll", sfx_shop_reroll),
    ("merge", sfx_merge),
    ("crate_break", sfx_crate_break),
    ("tape_hit", sfx_tape_hit),
]

MUSIC_BUILDERS = [
    ("menu", build_menu),
    ("combat", build_combat),
    ("boss", build_boss),
    ("victory", build_victory),
]

# beam_loop no lleva micro-fades: el bucle es matematicamente perfecto (cruce por cero).
SFX_FADE_OVERRIDES = {"beam_loop": (0.0, 0.0)}


def analyze_file(path):
    with wave.open(path, "rb") as w:
        fr = w.getframerate()
        nf = w.getnframes()
        raw = w.readframes(nf)
    x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    X = np.abs(np.fft.rfft(x)) ** 2 if x.size else np.zeros(1)
    f = np.fft.rfftfreq(max(x.size, 1), 1.0 / (fr or SR))
    cent = float((f * X).sum() / max(X.sum(), 1e-30))
    return {
        "dur": nf / float(fr or SR),
        "rms": float(np.sqrt(np.mean(x * x))) if x.size else 0.0,
        "peak": float(np.max(np.abs(x))) if x.size else 0.0,
        "mean": float(np.mean(x)) if x.size else 0.0,
        "cent": cent,
        "x": x,
        "nf": nf,
        "fr": fr,
    }


def report():
    warn = []
    print("\n== SFX (%d) ==" % len(SFX_BUILDERS))
    print("%-18s %7s %8s %7s %8s %10s" % ("archivo", "dur_s", "rms", "pico", "media", "centro_Hz"))
    for name, _ in SFX_BUILDERS:
        st = analyze_file(os.path.join(SFX_DIR, name + ".wav"))
        print("%-18s %7.3f %8.4f %7.3f %8.4f %10.1f"
              % (name + ".wav", st["dur"], st["rms"], st["peak"], st["mean"], st["cent"]))
        if not (0.04 <= st["dur"] <= 3.6):
            warn.append(name + ":duracion")
        if st["rms"] <= 0.004:
            warn.append(name + ":rms")
        if st["peak"] > 0.99:
            warn.append(name + ":pico")
        if abs(st["mean"]) >= 0.02:
            warn.append(name + ":dc")
    st = analyze_file(os.path.join(SFX_DIR, "beam_loop.wav"))
    print("beam_loop: nf=%d (%.3f s) |x[0]|=%.5f |x[-1]|=%.5f"
          % (st["nf"], st["dur"], abs(float(st["x"][0])), abs(float(st["x"][-1]))))

    print("\n== MUSICA (%d) ==" % len(MUSIC_BUILDERS))
    print("%-10s %7s %8s %7s %10s %11s  bloques_rms(8)"
          % ("archivo", "dur_s", "rms", "pico", "centro_Hz", "ratio30ms"))
    for name, _ in MUSIC_BUILDERS:
        st = analyze_file(os.path.join(MUSIC_DIR, name + ".wav"))
        x = st["x"]
        k = int(round(0.030 * st["fr"]))
        rh = float(np.sqrt(np.mean(x[:k] ** 2)))
        rt = float(np.sqrt(np.mean(x[-k:] ** 2)))
        ratio = rh / rt if rt > 1e-12 else float("inf")
        br = " ".join("%.3f" % float(np.sqrt(np.mean(b * b))) for b in np.array_split(x, 8))
        print("%-10s %7.2f %8.4f %7.3f %10.1f %11.3f  %s"
              % (name + ".wav", st["dur"], st["rms"], st["peak"], st["cent"], ratio, br))
        if not (20.0 <= st["dur"] <= 75.0):
            warn.append(name + ":duracion")
        if st["rms"] <= 0.004:
            warn.append(name + ":rms")
        if st["peak"] > 0.99:
            warn.append(name + ":pico")
        if abs(st["mean"]) >= 0.02:
            warn.append(name + ":dc")
        if not (abs(float(x[0])) < 0.03 and abs(float(x[-1])) < 0.03):
            warn.append(name + ":extremos")
        if not (1.0 / 3.0 <= ratio <= 3.0):
            warn.append(name + ":ratio30ms=%.2f" % ratio)

    if warn:
        print("\nAVISOS: " + ", ".join(warn))
    else:
        print("\n[ok] %d archivos: formato/duracion/rms/pico/dc/extremos OK"
              % (len(SFX_BUILDERS) + len(MUSIC_BUILDERS)))


def main():
    os.makedirs(SFX_DIR, exist_ok=True)
    os.makedirs(MUSIC_DIR, exist_ok=True)
    t0 = time.time()
    print("[gen_audio] sintetizando %d SFX ..." % len(SFX_BUILDERS))
    for name, fn in SFX_BUILDERS:
        fi, fo = SFX_FADE_OVERRIDES.get(name, (1.2, 2.5))
        write_wav(os.path.join(SFX_DIR, name + ".wav"), fn(), fade_in_ms=fi, fade_out_ms=fo)
    print("[gen_audio] sintetizando %d loops de musica ..." % len(MUSIC_BUILDERS))
    for name, fn in MUSIC_BUILDERS:
        song = fn()
        write_wav(os.path.join(MUSIC_DIR, name + ".wav"), song.mix.buf,
                  fade_in_ms=12.0, fade_out_ms=12.0)
    report()
    print("[gen_audio] hecho en %.1f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
