"""El Cajón de los Recuerdos: mejoras permanentes (Chispas)."""
from __future__ import annotations

META_UPGRADES = [
    dict(id="dmg", name="Más vatios", desc="+3% Daño", add=dict(dmg=0.03), max_rank=6, base=30, grow=1.55),
    dict(id="hp", name="Acolchado del cajón", desc="+6 Vida máx.", add=dict(hp=6), max_rank=6, base=30, grow=1.5),
    dict(id="atk", name="Lubricante fino", desc="+2% Vel. ataque", add=dict(atk_speed=0.02), max_rank=6, base=30, grow=1.55),
    dict(id="speed", name="Ruedas nuevas", desc="+2% Velocidad", add=dict(speed=0.02), max_rank=5, base=30, grow=1.55),
    dict(id="light", name="Bombilla premium", desc="+4% Luz", add=dict(light=0.04), max_rank=5, base=40, grow=1.6),
    dict(id="chispas", name="Hucha escondida", desc="+6% Chispas ganadas", add=dict(chispas=0.06), max_rank=5, base=60, grow=1.7),
    dict(id="coins", name="Grapas de cobre", desc="+5% Monedas", add=dict(coin_gain=0.05), max_rank=5, base=40, grow=1.6),
    dict(id="xp", name="Dietario", desc="+4% Recuerdos", add=dict(xp_gain=0.04), max_rank=4, base=40, grow=1.65),
    dict(id="crit", name="Ojo de lince", desc="+1% Crítico", add=dict(crit=0.01), max_rank=5, base=50, grow=1.65),
    dict(id="critdmg", name="Corte limpio", desc="+6% Daño crítico", add=dict(crit_dmg=0.06), max_rank=4, base=45, grow=1.6),
    dict(id="armor", name="Carcasa reforzada", desc="+1 Armadura", add=dict(armor=1), max_rank=4, base=55, grow=1.6),
    dict(id="regen", name="Enchufe estable", desc="+0.2 Regeneración", add=dict(regen=0.2), max_rank=4, base=45, grow=1.6),
    dict(id="pickup", name="Tira imantada", desc="+8% Imán", add=dict(pickup=0.08), max_rank=3, base=35, grow=1.6),
    dict(id="luck", name="Trébol de chincheta", desc="+5% Suerte", add=dict(luck=0.05), max_rank=4, base=50, grow=1.65),
    dict(id="fogonazo", name="Condensador gordo", desc="Fogonazo: -5% recarga", add=dict(abl_cd=-0.05), max_rank=4, base=55, grow=1.6),
    dict(id="reroll", name="Mango reforzado", desc="+1 sacudida gratis por tienda", special=dict(extra_reroll=1), max_rank=3, base=70, grow=1.8),
    dict(id="slot", name="Escaparate ampliado", desc="+1 hueco en La Expendedora", special=dict(shop_slot=1), max_rank=2, base=140, grow=2.0),
    dict(id="rebaja", name="Regateo de pasillo", desc="-4% precios de tienda", special=dict(discount=0.04), max_rank=4, base=80, grow=1.75),
    dict(id="revivir", name="Fusible de repuesto", desc="Revives una vez por noche (50% vida)", special=dict(revive=1), max_rank=1, base=300, grow=2.0),
    dict(id="inicio", name="Arranque en frío", desc="Empiezas cada noche con +1 arma aleatoria", special=dict(start_weapon=1), max_rank=1, base=220, grow=2.0),
]

BY_ID = {m["id"]: m for m in META_UPGRADES}


def cost(up: dict, rank: int) -> int:
    raw = up["base"] * (up["grow"] ** rank)
    return int(round(raw / 5.0) * 5)


def aggregate_ranks(ranks: dict[str, int]):
    """Devuelve (adds, specials) para un dict de rangos."""
    adds: dict[str, float] = {}
    specials: dict[str, float] = {}
    for uid, r in ranks.items():
        up = BY_ID.get(uid)
        if not up or r <= 0:
            continue
        for k, v in up.get("add", {}).items():
            adds[k] = adds.get(k, 0) + v * r
        for k, v in up.get("special", {}).items():
            specials[k] = specials.get(k, 0) + v * r
    return adds, specials
