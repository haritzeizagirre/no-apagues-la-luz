"""Oleadas: composición, ritmo de spawn, escalado y anuncios."""
from __future__ import annotations

import random

from .. import const as K
from . import enemies as E
from .enemies import BOSS_BY_HORA


def is_boss_hora(hora: int) -> bool:
    return hora in BOSS_BY_HORA


def wave_len(hora: int, mods: dict) -> float:
    if is_boss_hora(hora) and hora <= K.HORAS_NOCHE:
        return 85.0 * (1 + mods.get("wave_len", 0) * 0.5)
    base = min(62.0, 28 + 3 * hora)
    return base * (1 + mods.get("wave_len", 0))


def spawn_rate(hora: int, mods: dict) -> float:
    base = min(9.0, 0.55 + 0.38 * hora)
    if hora > K.HORAS_NOCHE:
        base = min(13.0, 9.5 + 0.5 * (hora - K.HORAS_NOCHE))
    return base * (1 + mods.get("enemy_count", 0))


def elite_chance(hora: int, luck: float) -> float:
    if hora < 6:
        return 0.0
    base = min(0.14, 0.014 * (hora - 5))
    return base * (1 + luck)


def hp_scale(hora: int, guardia: int, mods: dict, assist: bool) -> float:
    s = (1 + 0.155 * (hora - 1)) * (1 + 0.22 * (guardia - 1))
    s *= (1 + mods.get("enemy_hp", 0)) * (1 + mods.get("boss_extra_hp", 0) if False else 1)
    if hora > K.HORAS_NOCHE:
        s *= 1.08 ** (hora - K.HORAS_NOCHE)
    if assist:
        s *= 0.75
    return s


def dmg_scale(hora: int, guardia: int, mods: dict) -> float:
    return (1 + 0.065 * (hora - 1)) * (1 + 0.15 * (guardia - 1))


def spd_scale(mods: dict) -> float:
    return 1 + mods.get("enemy_spd", 0)


def composition(hora: int, rng: random.Random, mods: dict) -> list[str]:
    """Lista ponderada de ids disponibles en esta hora."""
    pool: list[tuple[str, float]] = []
    for e in E.ENEMIES:
        w = 0.0
        for (from_w, weight) in e["weights"]:
            if hora >= from_w:
                w = weight
        if w > 0 and e["id"] != "pagina":
            pool.append((e["id"], w))
    out: list[str] = []
    for eid, w in pool:
        out.extend([eid] * max(1, int(w)))
    return out


# olas especiales: "avalancha" cada noche en horas concretas
SURGE_HORAS = {3, 7, 9, 11, 13, 14, 16, 17, 18, 19}

WAVE_INTROS = {
    1: "18:00 — El turno comienza. La oficina bosteza.",
    4: "21:00 — Los cubículos despiertan.",
    8: "01:00 — Hora bruja. Cuidado con los cables.",
    12: "05:00 — La impresora gruñe en la oscuridad.",
    16: "07:00 — Amanece en otra parte. Aquí no.",
    21: "HORA EXTRA — El reloj se ha rendido. La máquina sigue.",
}


def wave_intro(hora: int) -> str:
    if hora > K.HORAS_NOCHE:
        return WAVE_INTROS[21]
    best = ""
    for h in sorted(WAVE_INTROS):
        if hora >= h and h <= K.HORAS_NOCHE:
            best = WAVE_INTROS[h]
    return best


def wave_bonus_coins(hora: int) -> int:
    return int(6 + 1.6 * hora)


def amb_dark(hora: int, mods: dict) -> int:
    a = K.DARK_BASE + K.DARK_PER_HORA * (hora - 1)
    return int(min(K.DARK_MAX, a * (1 + 0.15 * mods.get("dark", 0))))


BOSS_HP = {"despertador": 950, "reunion": 1750, "deadline": 2800, "olvido": 4300}
BOSS_DMG = {"despertador": 20, "reunion": 22, "deadline": 24, "olvido": 26}


def boss_scaled(boss: dict, hora: int, guardia: int, mods: dict, assist: bool) -> dict:
    b = dict(boss)
    g = 1 + 0.22 * (guardia - 1)
    m = 1 + mods.get("boss", 0)
    if hora > K.HORAS_NOCHE:
        m *= 1.35
    if assist:
        g *= 0.8
    b["hp"] = boss["hp"] * g * m
    b["dmg"] = boss["dmg"] * (1 + 0.1 * (guardia - 1)) * (1 + 0.15 * (mods.get("boss", 0)))
    return b
