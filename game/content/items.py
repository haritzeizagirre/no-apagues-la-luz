"""28 ítems pasivos. Mitad con contrapartida (decisiones, no solo números)."""
from __future__ import annotations

ITEMS = [
    # --- TIER 1
    dict(id="taza_oficina", name="La taza de siempre", icon="ic_i_taza", tier=1,
         desc="+6% Daño, -2% Velocidad", stats=dict(dmg=0.06, speed=-0.02), unlock=None),
    dict(id="postis_pila", name="Taco de post-its", icon="ic_i_postit", tier=1,
         desc="+8% Recuerdos", stats=dict(xp_gain=0.08), unlock=None),
    dict(id="grapa_suelta", name="Grapa suelta", icon="ic_i_grapa", tier=1,
         desc="+4% Crítico", stats=dict(crit=0.04), unlock=None),
    dict(id="chinchetas_caja", name="Caja de chinchetas", icon="ic_i_chinchetas", tier=1,
         desc="+4% Daño, +2 Espinas", stats=dict(dmg=0.04, thorn=2), unlock=None),
    dict(id="cafe_maquina", name="Café de máquina", icon="ic_i_cafe", tier=1,
         desc="+0.3 Regeneración, -3% Vel. ataque", stats=dict(regen=0.3, atk_speed=-0.03), unlock=None),
    dict(id="boligrafo", name="Bolígrafo mordido", icon="ic_i_boligrafo", tier=1,
         desc="+5% Vel. ataque", stats=dict(atk_speed=0.05), unlock=None),
    # --- TIER 2
    dict(id="teclado_mecanico", name="Teclado mecánico", icon="ic_i_teclado", tier=2,
         desc="+10% Vel. ataque, -3% Velocidad", stats=dict(atk_speed=0.10, speed=-0.03), unlock=None),
    dict(id="raton_gamer", name="Ratón gamer", icon="ic_i_raton", tier=2,
         desc="+6% Velocidad, +3% Crítico", stats=dict(speed=0.06, crit=0.03), unlock=None),
    dict(id="auriculares", name="Auriculares ANC", icon="ic_i_auriculares", tier=2,
         desc="+6% Suerte, -10% Élites", stats=dict(luck=0.06, elite_lure=-0.10), unlock=None),
    dict(id="sobre_nomina", name="Sobre de nómina", icon="ic_i_sobre", tier=2,
         desc="+10% Monedas, -4% Recuerdos", stats=dict(coin_gain=0.10, xp_gain=-0.04), unlock=None),
    dict(id="pila_alcalina", name="Pila alcalina", icon="ic_i_pila", tier=2,
         desc="+8% Luz, +4% Daño", stats=dict(light=0.08, dmg=0.04), unlock=None),
    dict(id="almohadilla", name="Almohadilla del cajón", icon="ic_i_almohadilla", tier=2,
         desc="+14 Vida máx.", stats=dict(hp=14), unlock=None),
    dict(id="cactus_mini", name="Cactus de cubículo", icon="ic_i_cactus", tier=2,
         desc="+3 Espinas, -2% Velocidad", stats=dict(thorn=3, speed=-0.02), unlock=None),
    dict(id="extintor_mini", name="Extintor de pared", icon="ic_i_extintor", tier=2,
         desc="+1 Armadura", stats=dict(armor=1), unlock=None),
    # --- TIER 3
    dict(id="alfombrilla_xl", name="Alfombrilla XL", icon="ic_i_alfombrilla", tier=3,
         desc="+10% Imán, +4% Velocidad", stats=dict(pickup=0.10, speed=0.04), unlock=None),
    dict(id="silla_ergo", name="Silla ergonómica", icon="ic_i_silla", tier=3,
         desc="+4% Esquiva, -5 Vida máx.", stats=dict(dodge=0.04, hp=-5), unlock=None),
    dict(id="ventilador_bolsillo", name="Ventilador de bolsillo", icon="ic_i_ventilador", tier=3,
         desc="+25% Empuje, +5% Vel. ataque", stats=dict(kb=0.25, atk_speed=0.05), unlock=None),
    dict(id="usb3", name="USB 3.0", icon="ic_i_usb", tier=3,
         desc="+14% Recuerdos, -5% Monedas", stats=dict(xp_gain=0.14, coin_gain=-0.05), unlock="item:usb3"),
    dict(id="calculadora", name="Calculadora solar", icon="ic_i_calculadora", tier=3,
         desc="+12% Monedas", stats=dict(coin_gain=0.12), unlock=None),
    dict(id="botiquin", name="Botiquín de planta", icon="ic_i_botiquin", tier=3,
         desc="+0.5 Regeneración, +6 Vida máx.", stats=dict(regen=0.5, hp=6), unlock=None),
    dict(id="flexo_extra", name="Flexo de repuesto", icon="ic_i_flexo", tier=3,
         desc="+12% Luz", stats=dict(light=0.12), unlock=None),
    dict(id="sello_urgente", name="Sello URGENTE", icon="ic_i_sello", tier=3,
         desc="+12% Daño, -6% Vel. ataque", stats=dict(dmg=0.12, atk_speed=-0.06), unlock=None),
    # --- TIER 4
    dict(id="grapadora_oro", name="Grapadora dorada", icon="ic_i_grapadora_oro", tier=4,
         desc="+6% Crítico, +15% Daño crítico", stats=dict(crit=0.06, crit_dmg=0.15), unlock="item:grapadora_oro"),
    dict(id="alargador_pro", name="Alargador reforzado", icon="ic_i_alargador", tier=4,
         desc="+15% Luz, +5% Vel. ataque", stats=dict(light=0.15, atk_speed=0.05), unlock="item:alargador_pro"),
    dict(id="tarjeta_plata", name="Tarjeta de plata", icon="ic_i_tarjeta", tier=4,
         desc="+10% Chispas, -5% Monedas", stats=dict(chispas=0.10, coin_gain=-0.05), unlock="item:tarjeta_plata"),
    dict(id="funda_antigolpe", name="Funda antigolpes", icon="ic_i_funda", tier=4,
         desc="+10 Vida máx., +1 Armadura", stats=dict(hp=10, armor=1), unlock="item:funda_antigolpe"),
    dict(id="multipresa", name="Multipresa inteligente", icon="ic_i_multipresa", tier=4,
         desc="+1 Proyectiles", stats=dict(proj_add=1), unlock="item:multipresa"),
    dict(id="diario", name="Diario del turno", icon="ic_i_diario", tier=4,
         desc="+10% Recuerdos, +10% Chispas, -8 Vida máx.", stats=dict(xp_gain=0.10, chispas=0.10, hp=-8),
         unlock="item:diario"),
]

BY_ID = {i["id"]: i for i in ITEMS}

# pool inicial (sin desbloquear): tiers 1-2
STARTER = [i["id"] for i in ITEMS if i["unlock"] is None]


def price(item: dict) -> int:
    base = {1: 10, 2: 17, 3: 26, 4: 36}[item["tier"]]
    return base
