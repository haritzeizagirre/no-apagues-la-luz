"""Marcas del Turno: modificadores de riesgo/recompensa elegidos antes de la noche."""
from __future__ import annotations

MUTATORS = [
    dict(id="apagon", name="APAGÓN", desc="Tu luz es un 20% más débil. Chispas +25%.",
         mods=dict(light=-0.20), reward=1.25, unlock="mutator:apagon"),
    dict(id="sobrecarga", name="SOBRECARGA", desc="Los enemigos van un 15% más rápido. Recuerdos +20%.",
         mods=dict(enemy_spd=0.15, xp_gain=0.20), reward=1.20, unlock="mutator:sobrecarga"),
    dict(id="austeridad", name="AUSTERIDAD", desc="La máquina no se deja sacudir. Monedas +30%.",
         mods=dict(no_reroll=1, coin_gain=0.30), reward=1.25, unlock="mutator:austeridad"),
    dict(id="plaga", name="PLAGA", desc="Aparecen un 30% más de enemigos, pero con un 15% menos de vida.",
         mods=dict(enemy_count=0.30, enemy_hp=-0.15), reward=1.15, unlock="mutator:plaga"),
    dict(id="jefe_furioso", name="JEFE FURIOSO", desc="Los jefes son un 30% más fuertes. Chispas +20%.",
         mods=dict(boss=0.30), reward=1.20, unlock="mutator:jefe_furioso"),
    dict(id="turno_doble", name="TURNO DOBLE", desc="Las horas duran un 25% más. Chispas +15%.",
         mods=dict(wave_len=0.25), reward=1.15, unlock="mutator:turno_doble"),
]

BY_ID = {m["id"]: m for m in MUTATORS}


def aggregate(ids: list[str]) -> dict:
    mods: dict[str, float] = {}
    reward = 1.0
    for mid in ids:
        m = BY_ID.get(mid)
        if not m:
            continue
        reward *= m["reward"]
        for k, v in m["mods"].items():
            mods[k] = mods.get(k, 0) + v
    mods["reward"] = reward
    return mods
