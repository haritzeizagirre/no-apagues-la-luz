"""Plantas del edificio: mapas FIJOS por nivel de guardia.

Cada guardia juega en una planta distinta del Edificio Möbius: cambia la
distribución de muebles (mesas, taquillas, máquinas...) y la paleta de la
moqueta. Las posiciones son fijas; las cajas de cartón también.

Formato: props = [(kind, x, y)] con kinds: desk, chair, plant, cooler,
cabinet, lamp. boxes = [(x, y)].  Zonas de moqueta: (x, y, w, h, clave).
"""
from __future__ import annotations

# --- paletas (oscuras: la luz de LÍA debe mandar) --------------------------
NAVY = dict(base=(26, 31, 52), alt=(29, 35, 58), speck=(35, 43, 70), speck2=(47, 61, 94),
            zone_a=(31, 42, 66), zone_b=(33, 40, 62), zone_c=(36, 44, 68), wall=(44, 54, 84))
WINE = dict(base=(38, 28, 38), alt=(42, 31, 42), speck=(52, 36, 48), speck2=(70, 48, 62),
            zone_a=(46, 32, 44), zone_b=(50, 34, 46), zone_c=(54, 38, 50), wall=(74, 48, 62))
MOSS = dict(base=(28, 36, 34), alt=(31, 40, 38), speck=(40, 52, 48), speck2=(54, 70, 64),
            zone_a=(34, 44, 42), zone_b=(38, 48, 46), zone_c=(42, 54, 50), wall=(58, 78, 72))
PLUM = dict(base=(32, 28, 46), alt=(36, 31, 50), speck=(46, 40, 64), speck2=(62, 54, 86),
            zone_a=(40, 34, 56), zone_b=(44, 38, 60), zone_c=(48, 42, 64), wall=(78, 66, 110))
AMBER = dict(base=(40, 32, 26), alt=(44, 35, 29), speck=(56, 46, 34), speck2=(74, 60, 44),
             zone_a=(50, 40, 30), zone_b=(54, 44, 34), zone_c=(58, 48, 38), wall=(94, 76, 50))

MAPS = [
    dict(
        id="planta1", short="Cubículos", name="Planta 1 · Cubículos",
        desc="La planta de siempre: mesas en batería y moqueta azul.",
        floor=NAVY,
        zones=[(60, 60, 260, 200, "zone_a"), (560, 40, 300, 200, "zone_b"),
               (420, 300, 300, 220, "zone_a"), (100, 330, 260, 190, "zone_b"),
               (760, 300, 220, 220, "zone_c")],
        props=[
            ("desk", 140, 150), ("desk", 320, 150), ("desk", 140, 340), ("desk", 320, 340),
            ("desk", 620, 170), ("desk", 820, 170), ("desk", 620, 440), ("desk", 820, 440),
            ("chair", 200, 190), ("chair", 380, 190), ("chair", 200, 380), ("chair", 680, 210),
            ("chair", 880, 210), ("chair", 680, 480),
            ("cabinet", 54, 64), ("cabinet", 80, 64), ("cabinet", 940, 64), ("cabinet", 966, 64),
            ("cabinet", 54, 500), ("cabinet", 80, 500), ("cabinet", 940, 500), ("cabinet", 966, 500),
            ("plant", 250, 110), ("plant", 760, 120), ("plant", 500, 500), ("plant", 880, 340),
            ("cooler", 860, 80), ("cooler", 120, 470),
            ("lamp", 360, 300), ("lamp", 660, 300), ("lamp", 240, 470), ("lamp", 760, 470),
            ("lamp", 500, 120),
        ],
        boxes=[(220, 250), (420, 110), (560, 210), (700, 330), (300, 480), (560, 480),
               (880, 250), (160, 60)],
    ),
    dict(
        id="planta2", short="Reuniones", name="Planta 2 · Sala de reuniones",
        desc="Una mesa larga, sillas de más y una moqueta color vino.",
        floor=WINE,
        zones=[(40, 300, 280, 220, "zone_a"), (700, 40, 280, 200, "zone_b"),
               (300, 380, 340, 160, "zone_a"), (80, 60, 220, 180, "zone_c"),
               (760, 340, 220, 180, "zone_b")],
        props=[
            ("desk", 400, 160), ("desk", 460, 160), ("desk", 520, 160), ("desk", 580, 160),
            ("desk", 640, 160),
            ("chair", 430, 215), ("chair", 490, 215), ("chair", 550, 215), ("chair", 610, 215),
            ("chair", 430, 105), ("chair", 550, 105), ("chair", 670, 105),
            ("cabinet", 54, 80), ("cabinet", 80, 80), ("cabinet", 940, 80), ("cabinet", 966, 80),
            ("cabinet", 54, 480), ("cabinet", 966, 480),
            ("plant", 250, 150), ("plant", 250, 420), ("plant", 790, 420),
            ("cooler", 790, 140), ("cooler", 860, 480),
            ("lamp", 300, 290), ("lamp", 700, 290), ("lamp", 60, 290), ("lamp", 960, 290),
        ],
        boxes=[(180, 110), (180, 460), (850, 110), (850, 460), (512, 80), (512, 496), (350, 470)],
    ),
    dict(
        id="planta3", short="Archivo", name="Planta 3 · Archivo",
        desc="Pasillos de archivadores hasta donde alcanza la luz.",
        floor=MOSS,
        zones=[(60, 60, 200, 180, "zone_a"), (760, 60, 200, 180, "zone_b"),
               (60, 380, 200, 160, "zone_b"), (760, 380, 200, 160, "zone_a"),
               (400, 200, 220, 180, "zone_c")],
        props=[
            ("cabinet", 100, 100), ("cabinet", 180, 100), ("cabinet", 260, 100), ("cabinet", 340, 100),
            ("cabinet", 420, 100), ("cabinet", 600, 100), ("cabinet", 680, 100), ("cabinet", 760, 100),
            ("cabinet", 840, 100), ("cabinet", 920, 100),
            ("cabinet", 100, 288), ("cabinet", 180, 288), ("cabinet", 260, 288), ("cabinet", 340, 288),
            ("cabinet", 700, 288), ("cabinet", 780, 288), ("cabinet", 860, 288), ("cabinet", 940, 288),
            ("cabinet", 100, 476), ("cabinet", 180, 476), ("cabinet", 260, 476), ("cabinet", 340, 476),
            ("cabinet", 420, 476), ("cabinet", 600, 476), ("cabinet", 680, 476), ("cabinet", 760, 476),
            ("cabinet", 840, 476), ("cabinet", 920, 476),
            ("desk", 500, 100), ("desk", 500, 476),
            ("plant", 500, 40), ("plant", 500, 536),
            ("cooler", 982, 60), ("cooler", 982, 516),
            ("lamp", 300, 288), ("lamp", 724, 288), ("lamp", 60, 190), ("lamp", 964, 190),
            ("lamp", 60, 390), ("lamp", 964, 390),
        ],
        boxes=[(500, 180), (500, 380), (150, 200), (350, 200), (650, 200), (850, 200),
               (150, 380), (350, 380), (650, 380), (850, 380)],
    ),
    dict(
        id="planta4", short="Cafetería", name="Planta 4 · Cafetería",
        desc="Máquinas de agua, plantas de plástico y mesitas de tres patas.",
        floor=PLUM,
        zones=[(60, 60, 220, 180, "zone_c"), (720, 60, 220, 180, "zone_a"),
               (60, 360, 220, 180, "zone_b"), (720, 360, 220, 180, "zone_c"),
               (380, 120, 270, 140, "zone_a")],
        props=[
            ("cooler", 150, 100), ("cooler", 512, 64), ("cooler", 874, 100),
            ("cooler", 150, 480), ("cooler", 874, 480),
            ("plant", 100, 300), ("plant", 250, 480), ("plant", 774, 480), ("plant", 924, 300),
            ("plant", 400, 80), ("plant", 624, 80),
            ("desk", 300, 220), ("desk", 724, 220), ("desk", 300, 380), ("desk", 724, 380),
            ("chair", 250, 250), ("chair", 350, 250), ("chair", 674, 250), ("chair", 774, 250),
            ("chair", 300, 440), ("chair", 724, 440),
            ("cabinet", 54, 520), ("cabinet", 80, 520), ("cabinet", 940, 520), ("cabinet", 966, 520),
            ("cabinet", 54, 54), ("cabinet", 80, 54),
            ("lamp", 512, 480), ("lamp", 512, 150), ("lamp", 60, 180), ("lamp", 964, 180),
            ("lamp", 60, 400), ("lamp", 964, 400),
        ],
        boxes=[(170, 180), (850, 180), (170, 420), (850, 420), (512, 360), (512, 200),
               (400, 300), (624, 300)],
    ),
    dict(
        id="planta5", short="Dirección", name="Planta 5 · Dirección",
        desc="El despacho del jefe: trofeos, sillones y una moqueta cara.",
        floor=AMBER,
        zones=[(80, 80, 260, 200, "zone_a"), (680, 80, 260, 200, "zone_b"),
               (80, 340, 260, 180, "zone_b"), (680, 340, 260, 180, "zone_a"),
               (380, 220, 260, 180, "zone_c")],
        props=[
            ("desk", 660, 120), ("desk", 740, 120), ("desk", 820, 120),
            ("desk", 600, 200), ("desk", 880, 200),
            ("chair", 660, 170), ("chair", 740, 170), ("chair", 820, 170),
            ("chair", 600, 240), ("chair", 880, 240),
            ("cabinet", 180, 80), ("cabinet", 234, 80), ("cabinet", 288, 80),
            ("cabinet", 180, 106), ("cabinet", 234, 106), ("cabinet", 288, 106),
            ("cabinet", 940, 80), ("cabinet", 966, 80), ("cabinet", 940, 106), ("cabinet", 966, 106),
            ("plant", 100, 500), ("plant", 924, 500), ("plant", 512, 520), ("plant", 100, 300),
            ("cooler", 512, 60), ("cooler", 44, 532),
            ("lamp", 300, 300), ("lamp", 724, 300), ("lamp", 120, 300), ("lamp", 900, 300),
            ("lamp", 512, 440),
        ],
        boxes=[(350, 220), (674, 380), (350, 420), (820, 300), (220, 340), (512, 420)],
    ),
]


def for_guardia(g: int) -> dict:
    """Devuelve la planta correspondiente al nivel de guardia (1..5)."""
    return MAPS[min(max(1, int(g)), len(MAPS)) - 1]
