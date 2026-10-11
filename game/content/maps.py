"""Plantas del edificio: mapas FIJOS por nivel de guardia.

Cada guardia juega en una planta distinta del Edificio Möbius: cambia la
distribución de muebles (mesas, taquillas, máquinas...) y la paleta de la
moqueta. Las posiciones son fijas; las cajas de cartón también.

DISEÑO (una oficina con sentido, no muebles al azar):
- Puesto de trabajo = mesa + silla justo debajo (dy=36).
- Baterías de mesas alineadas cada 120 px; pasillo central libre (x 480-544)
  y pasillo horizontal libre (y 272-304) en las plantas de mesas.
- Taquillas en filas regulares pegadas a los muros (cada 56 px).
- Plantas y fuentes en esquinas y remates de pasillo; lámparas en rejilla.
- Nada a menos de 55 px del centro de la arena (spawn del jugador).

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


def _battery(xs, y):
    """Batería de mesas alineadas con su silla justo debajo (dy=36)."""
    out = []
    for x in xs:
        out.append(("desk", x, y))
        out.append(("chair", x, y + 36))
    return out


def _run(x0, x1, step, y):
    """Fila regular de taquillas/archivadores."""
    return [("cabinet", x, y) for x in range(x0, x1 + 1, step)]


MAPS = [
    dict(
        id="planta1", short="Cubículos", name="Planta 1 · Cubículos",
        desc="La planta de siempre: mesas en batería y moqueta azul.",
        floor=NAVY,
        zones=[(96, 96, 352, 192, "zone_a"), (576, 96, 352, 192, "zone_b"),
               (96, 336, 352, 192, "zone_b"), (576, 336, 352, 192, "zone_a"),
               (448, 224, 128, 128, "zone_c")],
        props=(
            # cuatro baterías de 3 mesas (puesto = mesa + silla)
            _battery((144, 264, 384), 160) + _battery((640, 760, 880), 160)
            + _battery((144, 264, 384), 400) + _battery((640, 760, 880), 400)
            # taquillas pegadas a los muros norte y sur
            + _run(144, 368, 56, 64) + _run(640, 864, 56, 64)
            + _run(144, 368, 56, 512) + _run(640, 864, 56, 512)
            # remates de pasillo y esquinas
            + [("plant", 480, 64), ("plant", 544, 64), ("plant", 480, 512), ("plant", 544, 512),
               ("plant", 112, 288), ("plant", 912, 288),
               ("cooler", 112, 96), ("cooler", 912, 96), ("cooler", 112, 480), ("cooler", 912, 480),
               ("lamp", 264, 288), ("lamp", 760, 288), ("lamp", 512, 176), ("lamp", 512, 400),
               ("lamp", 512, 64)]
        ),
        boxes=[(448, 224), (576, 224), (448, 352), (576, 352), (200, 264), (824, 264)],
    ),
    dict(
        id="planta2", short="Reuniones", name="Planta 2 · Sala de reuniones",
        desc="Una mesa larga partida por el pasillo y moqueta color vino.",
        floor=WINE,
        zones=[(96, 96, 320, 200, "zone_c"), (608, 96, 320, 200, "zone_a"),
               (96, 336, 320, 200, "zone_a"), (608, 336, 320, 200, "zone_c"),
               (352, 200, 320, 176, "zone_b")],
        props=(
            # mesa de reuniones: dos mitades separadas por el pasillo central
            [("desk", 368, 240), ("desk", 448, 240), ("desk", 576, 240), ("desk", 656, 240)]
            + [("chair", 368, 204), ("chair", 448, 204), ("chair", 576, 204), ("chair", 656, 204),
               ("chair", 368, 276), ("chair", 448, 276), ("chair", 576, 276), ("chair", 656, 276),
               ("chair", 328, 240), ("chair", 696, 240)]
            # cuatro puestos en las esquinas
            + [("desk", 160, 160), ("chair", 160, 196), ("desk", 864, 160), ("chair", 864, 196),
               ("desk", 160, 400), ("chair", 160, 436), ("desk", 864, 400), ("chair", 864, 436)]
            # taquillas en los muros
            + _run(144, 368, 56, 64) + _run(656, 880, 56, 64)
            + _run(144, 368, 56, 512) + _run(656, 880, 56, 512)
            + [("plant", 480, 120), ("plant", 544, 120), ("plant", 480, 456), ("plant", 544, 456),
               ("plant", 112, 288), ("plant", 912, 288),
               ("cooler", 112, 96), ("cooler", 912, 96), ("cooler", 112, 480), ("cooler", 912, 480),
               ("lamp", 264, 288), ("lamp", 760, 288), ("lamp", 512, 112), ("lamp", 512, 464)]
        ),
        boxes=[(448, 176), (576, 176), (448, 344), (576, 344), (256, 96), (768, 96)],
    ),
    dict(
        id="planta3", short="Archivo", name="Planta 3 · Archivo",
        desc="Pasillos de archivadores hasta donde alcanza la luz.",
        floor=MOSS,
        zones=[(64, 64, 416, 224, "zone_a"), (544, 64, 416, 224, "zone_b"),
               (64, 288, 416, 224, "zone_b"), (544, 288, 416, 224, "zone_a"),
               (448, 64, 128, 448, "zone_c")],
        props=(
            # cuatro filas de archivadores con pasillos regulares (hueco central)
            _run(96, 416, 64, 96) + _run(608, 928, 64, 96)
            + _run(96, 416, 64, 208) + _run(608, 928, 64, 208)
            + _run(96, 416, 64, 320) + _run(608, 928, 64, 320)
            + _run(96, 416, 64, 432) + _run(608, 928, 64, 432)
            # el puesto del archivero, en el pasillo central
            + [("desk", 496, 96), ("chair", 496, 132), ("desk", 496, 464), ("chair", 496, 428)]
            + [("plant", 112, 64), ("plant", 912, 64), ("plant", 112, 512), ("plant", 912, 512),
               ("cooler", 64, 288), ("cooler", 960, 288),
               ("lamp", 512, 160), ("lamp", 512, 416), ("lamp", 256, 288), ("lamp", 768, 288)]
        ),
        boxes=[(480, 176), (544, 176), (480, 368), (544, 368), (320, 96), (704, 432)],
    ),
    dict(
        id="planta4", short="Cafetería", name="Planta 4 · Cafetería",
        desc="Máquinas expendedoras, plantas de plástico y mesitas de tres patas.",
        floor=PLUM,
        zones=[(128, 64, 320, 224, "zone_c"), (576, 64, 320, 224, "zone_a"),
               (128, 288, 320, 224, "zone_b"), (576, 288, 320, 224, "zone_c"),
               (448, 224, 128, 128, "zone_a")],
        props=(
            # cuatro mesitas (2x2 mesas) con sus sillas
            [("desk", 240, 180), ("desk", 360, 180), ("desk", 240, 260), ("desk", 360, 260),
             ("desk", 664, 180), ("desk", 784, 180), ("desk", 664, 260), ("desk", 784, 260),
             ("desk", 240, 380), ("desk", 360, 380), ("desk", 240, 460), ("desk", 360, 460),
             ("desk", 664, 380), ("desk", 784, 380), ("desk", 664, 460), ("desk", 784, 460)]
            + [("chair", 300, 220), ("chair", 724, 220), ("chair", 300, 420), ("chair", 724, 420),
               ("chair", 300, 140), ("chair", 724, 140), ("chair", 300, 500), ("chair", 724, 500)]
            # máquinas expendedoras en los muros
            + [("cooler", 144, 96), ("cooler", 512, 96), ("cooler", 880, 96),
               ("cooler", 144, 480), ("cooler", 512, 480), ("cooler", 880, 480)]
            + [("plant", 256, 96), ("plant", 768, 96), ("plant", 256, 480), ("plant", 768, 480),
               ("plant", 512, 64), ("plant", 512, 512),
               ("cabinet", 64, 64), ("cabinet", 96, 64), ("cabinet", 928, 64), ("cabinet", 960, 64),
               ("cabinet", 64, 512), ("cabinet", 96, 512), ("cabinet", 928, 512), ("cabinet", 960, 512),
               ("lamp", 300, 300), ("lamp", 724, 300), ("lamp", 512, 200), ("lamp", 512, 376),
               ("lamp", 144, 288), ("lamp", 880, 288)]
        ),
        boxes=[(448, 288), (576, 288), (180, 380), (844, 380), (180, 180), (844, 180)],
    ),
    dict(
        id="planta5", short="Dirección", name="Planta 5 · Dirección",
        desc="El despacho del jefe: trofeos, sillones y una moqueta cara.",
        floor=AMBER,
        zones=[(80, 80, 260, 200, "zone_a"), (680, 80, 260, 200, "zone_b"),
               (80, 340, 260, 180, "zone_b"), (680, 340, 260, 180, "zone_a"),
               (380, 220, 260, 180, "zone_c")],
        props=(
            # el escritorio del jefe, en L
            [("desk", 660, 120), ("desk", 740, 120), ("desk", 820, 120),
             ("desk", 600, 200), ("desk", 880, 200),
             ("chair", 660, 156), ("chair", 740, 156), ("chair", 820, 156),
             ("chair", 600, 236), ("chair", 880, 236)]
            # vitrinas de trofeos (bloques alineados)
            + [("cabinet", 176, 80), ("cabinet", 232, 80), ("cabinet", 288, 80),
               ("cabinet", 176, 112), ("cabinet", 232, 112), ("cabinet", 288, 112),
               ("cabinet", 928, 80), ("cabinet", 960, 80), ("cabinet", 928, 112), ("cabinet", 960, 112)]
            + [("plant", 100, 500), ("plant", 924, 500), ("plant", 512, 520),
               ("plant", 100, 300), ("plant", 924, 300),
               ("cooler", 512, 60), ("cooler", 64, 532),
               ("lamp", 300, 300), ("lamp", 724, 300), ("lamp", 120, 300), ("lamp", 900, 300),
               ("lamp", 512, 440)]
        ),
        boxes=[(350, 220), (674, 380), (350, 420), (820, 300), (220, 340), (512, 420)],
    ),
]


def for_guardia(g: int) -> dict:
    """Devuelve la planta correspondiente al nivel de guardia (1..5)."""
    return MAPS[min(max(1, int(g)), len(MAPS)) - 1]
