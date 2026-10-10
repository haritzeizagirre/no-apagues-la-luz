"""14 armas de oficina. Kinds implementados en game/weapons.py.

params base (nivel 1); 'grow' multiplica por nivel (1+g)^(n-1); 'step' suma por nivel.
"""
from __future__ import annotations

WEAPONS = [
    dict(id="grapadora", name="Grapadora", icon="ic_w_grapadora", tier=1, kind="shot",
         desc="Dispara grapas en abanico. El clásico que nunca falla.",
         base=dict(count=3, spread=20, dmg=10, speed=390, pierce=0, life=0.42, kb=0.5, size=1.0, proj="pr_staple"),
         grow=dict(dmg=0.32, cd=-0.075), step=dict(count=1),
         cd=0.85, unlock=None),
    dict(id="chinchetas", name="Lanza-chinchetas", icon="ic_w_chinchetas", tier=1, kind="shot",
         desc="Abanico amplio de chinchetas. Poco daño, mucho odio.",
         base=dict(count=5, spread=46, dmg=6, speed=330, pierce=0, life=0.38, kb=0.35, size=0.9, proj="pr_tack"),
         grow=dict(dmg=0.3, cd=-0.07), step=dict(count=1),
         cd=1.05, unlock=None),
    dict(id="cinta", name="Rollo de cinta", icon="ic_w_cinta", tier=1, kind="tape",
         desc="Lanza cinta adhesiva: ralentiza y pega tinta a quien toca.",
         base=dict(count=1, spread=8, dmg=9, speed=300, pierce=1, life=0.8, kb=0.3, slow=0.4, slow_t=2.2,
                   dot=4, dot_t=2.0, proj="pr_tape"),
         grow=dict(dmg=0.3, cd=-0.07, dot=0.25), step=dict(count=1),
         cd=1.3, unlock=None),

    dict(id="rotulador", name="Rotulador grueso", icon="ic_w_rotulador", tier=2, kind="shot",
         desc="Trazo perforante que atraviesa lo que pilla.",
         base=dict(count=1, spread=6, dmg=17, speed=520, pierce=2, life=0.62, kb=0.4, size=1.1, proj="pr_marker"),
         grow=dict(dmg=0.34, cd=-0.08), step=dict(pierce=1),
         cd=1.0, unlock=None),
    dict(id="regla", name="Regla de metal", icon="ic_w_regla", tier=2, kind="melee",
         desc="Reglazo en arco. Ofensivo y pedagógico.",
         base=dict(dmg=25, radius=64, arc=105, kb=1.6, cd=0.92),
         grow=dict(dmg=0.32, radius=0.05, cd=-0.07), step=dict(),
         cd=0.92, unlock=None),
    dict(id="clips", name="Clips saltarines", icon="ic_w_clips", tier=2, kind="bounce",
         desc="Clips que rebotan por toda la oficina.",
         base=dict(count=2, spread=25, dmg=11, speed=310, pierce=0, life=2.6, kb=0.4, bounces=4, proj="pr_clip"),
         grow=dict(dmg=0.3, cd=-0.08), step=dict(count=1, bounces=1),
         cd=1.35, unlock=None),

    dict(id="tijeras", name="Tijeras de punta", icon="ic_w_tijeras", tier=3, kind="boomerang",
         desc="Van y vuelven cortando a la ida y a la vuelta.",
         base=dict(count=2, spread=30, dmg=16, speed=320, range=165, pierce=99, kb=0.8, proj="pr_scissor"),
         grow=dict(dmg=0.32, cd=-0.075, range=0.06), step=dict(count=1),
         cd=1.25, unlock=None),
    dict(id="cafe", name="Café ardiendo", icon="ic_w_cafe", tier=3, kind="lob",
         desc="Lo lanza lejos y deja un charco abrasador.",
         base=dict(count=1, dmg=13, aoe=48, speed=260, dot=7, dot_t=2.6, puddle_t=3.4, kb=0.8, proj="pr_coffee"),
         grow=dict(dmg=0.3, aoe=0.06, cd=-0.07, dot=0.22), step=dict(count=1),
         cd=1.9, unlock=None),
    dict(id="cable", name="Cable pelado", icon="ic_w_cable", tier=3, kind="chain",
         desc="Descarga eléctrica que salta de enemigo en enemigo.",
         base=dict(dmg=13, hops=3, hop_range=95, falloff=0.85, kb=0.5),
         grow=dict(dmg=0.34, cd=-0.07), step=dict(hops=1),
         cd=1.5, unlock="weapon:cable"),
    dict(id="radio", name="Radio vieja", icon="ic_w_radio", tier=3, kind="aura",
         desc="Pulso bajo que sacude todo lo que la rodea.",
         base=dict(dmg=15, radius=100, kb=0.8, pulse=1.55),
         grow=dict(dmg=0.32, radius=0.05, cd=-0.07), step=dict(),
         cd=1.55, unlock="weapon:radio"),
    dict(id="toner", name="Bote de tóner", icon="ic_w_toner", tier=3, kind="tape",
         desc="Rocía tinta tóxica en abanico. Mancha y envenena.",
         base=dict(count=3, spread=32, dmg=6, speed=280, pierce=0, life=0.55, kb=0.2, slow=0.15, slow_t=1.2,
                   dot=8, dot_t=2.4, proj="pr_toner"),
         grow=dict(dmg=0.28, cd=-0.075, dot=0.26), step=dict(count=1),
         cd=1.45, unlock=None),

    dict(id="laser", name="Puntero láser", icon="ic_w_laser", tier=4, kind="beam",
         desc="Haz continuo que derrite presentaciones y enemigos.",
         base=dict(dps=30, length=235, width=3, tick=0.12),
         grow=dict(dps=0.34, length=0.05), step=dict(),
         cd=0.0, unlock="weapon:laser"),
    dict(id="sello", name="Sello notarial", icon="ic_w_sello", tier=4, kind="slam",
         desc="Sellazo sísmico alrededor de LÍA. APRUEBA: destrucción.",
         base=dict(dmg=36, radius=84, kb=2.4, cd=2.5, tarea=0.35),
         grow=dict(dmg=0.34, radius=0.06, cd=-0.07), step=dict(),
         cd=2.5, unlock=None),
    dict(id="movil", name="Móvil vibrando", icon="ic_w_movil", tier=4, kind="nova",
         desc="Novas expansivas de vibración pura. 47 llamadas perdidas.",
         base=dict(dmg=14, radius=96, kb=1.8, cd=2.15),
         grow=dict(dmg=0.34, radius=0.07, cd=-0.075), step=dict(),
         cd=2.15, unlock="weapon:movil"),
]

BY_ID = {w["id"]: w for w in WEAPONS}

# resúmenes para la tienda: (nombre corto, efecto en 1-2 líneas)
SHORT = {
    "grapadora": ("Grapadora", "Abanico de 3 grapas"),
    "chinchetas": ("Chinchetas", "Abanico amplio"),
    "cinta": ("Cinta", "Ralentiza y pega tinta"),
    "rotulador": ("Rotulador", "Perfora en línea recta"),
    "regla": ("Regla", "Arco cuerpo a cuerpo"),
    "clips": ("Clips", "Rebotan por la sala"),
    "tijeras": ("Tijeras", "Bumerán de ida y vuelta"),
    "cafe": ("Café", "Charco ardiente en área"),
    "cable": ("Cable", "Rayo en cadena"),
    "radio": ("Radio", "Pulso sonoro en área"),
    "toner": ("Tóner", "Nube tóxica (veneno)"),
    "laser": ("Láser", "Haz continuo perforante"),
    "sello": ("Sello", "Sellazo en área"),
    "movil": ("Móvil", "Onda que empuja"),
}

STARTING_WEAPONS = ["grapadora", "chinchetas", "cinta", "rotulador", "regla", "clips"]

MAX_WEAPON_LEVEL = 4
MAX_WEAPON_SLOTS = 6


def effective(w: dict, level: int) -> dict:
    """Devuelve los params efectivos del arma a un nivel (1..4)."""
    lv = max(1, int(level))
    p = dict(w["base"])
    for key, g in w.get("grow", {}).items():
        p[key] = p.get(key, 0) * ((1 + g) ** (lv - 1))
    for key, s in w.get("step", {}).items():
        p[key] = p.get(key, 0) + s * (lv - 1)
    p["cd"] = max(0.12, p.get("cd", 0.8))
    if "pulse" in p:
        p["pulse"] = max(0.3, p["pulse"] * ((1 + w["grow"].get("cd", -0.06)) ** (lv - 1)))
    return p
