"""Sprites — TODO el arte del juego se genera por código.

Dibujo con primitivas sobre lienzos pequeños (1 px = 1 px de juego):
formas planas + contorno automático + variantes (flash, volteo, élite, muerte).
"""
from __future__ import annotations

import math

import pygame

from . import const as K

OUT = (10, 12, 22)

PAL = {
    "k": K.C["negro"], "d": K.C["gris_osc"], "g": K.C["gris"], "l": (170, 178, 190),
    "w": K.C["crema"], "a": K.C["ambar"], "A": K.C["ambar_claro"], "b": K.C["ambar_osc"],
    "r": K.C["rojo"], "R": K.C["rojo_claro"], "t": K.C["teal"], "T": K.C["teal_claro"],
    "u": K.C["azul"], "U": K.C["azul_claro"], "n": K.C["marino"], "v": K.C["verde"],
    "V": K.C["verde_claro"], "p": K.C["morado"], "P": K.C["morado_claro"],
    "e": (255, 255, 255), "x": (12, 14, 24), "m": (205, 211, 220), "M": (140, 148, 160),
    "s": (233, 196, 152), "h": (92, 64, 44), "y": (255, 231, 150), "o": OUT,
}


# ---------------------------------------------------------------- primitivas
def surf(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def rect(s, x, y, w, h, c):
    pygame.draw.rect(s, c, (x, y, w, h))


def ell(s, cx, cy, rx, ry, c):
    pygame.draw.ellipse(s, c, (int(cx - rx), int(cy - ry), int(rx * 2 + 1), int(ry * 2 + 1)))


def circ(s, cx, cy, r, c, width=0):
    pygame.draw.circle(s, c, (int(cx), int(cy)), int(r), width)


def poly(s, pts, c):
    pygame.draw.polygon(s, c, pts)


def line(s, *a):
    """Firma flexible: line(s, p1, p2, c, w=1) o line(s, x1, y1, x2, y2, c, w=1)."""
    if isinstance(a[0], (tuple, list)):
        p1, p2, c = a[0], a[1], a[2]
        w = a[3] if len(a) > 3 else 1
    else:
        x1, y1, x2, y2, c = a[:5]
        w = a[5] if len(a) > 5 else 1
        p1, p2 = (x1, y1), (x2, y2)
    pygame.draw.line(s, c, p1, p2, w)


def eyes(s, pts, style="normal", cx=None):
    """Ojos 2x2 con pupila. style: normal|angry|sleepy|dead|wide"""
    for (x, y) in pts:
        col = PAL["e"] if style != "dead" else (150, 150, 160)
        rect(s, x, y, 2, 2, col)
        px_col = PAL["x"]
        if style == "sleepy":
            line(s, (x - 1, y), (x + 2, y), PAL["x"])
            continue
        if style == "dead":
            line(s, (x, y), (x + 1, y + 1), PAL["x"])
            line(s, (x + 1, y), (x, y + 1), PAL["x"])
            continue
        if style == "wide":
            rect(s, x, y, 2, 2, PAL["e"])
            s.set_at((x + 1, y + 1), px_col)
        else:
            s.set_at((x + 1, y + 1), px_col)
        if style == "angry" and cx is not None:
            side = -1 if x < cx else 1
            _brow(s, x, y, side)


def _brow(s, x, y, side):
    if side < 0:
        s.set_at((x - 1, y - 1), PAL["x"])
        s.set_at((x, y - 2), PAL["x"])
        s.set_at((x + 1, y - 2), PAL["x"])
    else:
        s.set_at((x + 2, y - 1), PAL["x"])
        s.set_at((x + 1, y - 2), PAL["x"])
        s.set_at((x, y - 2), PAL["x"])


def outline(base, c=OUT):
    w, h = base.get_size()
    out = base.copy()
    mask = [[base.get_at((x, y))[3] != 0 for y in range(h)] for x in range(w)]
    for x in range(w):
        for y in range(h):
            if mask[x][y]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and mask[nx][ny]:
                    out.set_at((x, y), c)
                    break
    return out


def _white(base):
    c = base.copy()
    c.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGB_MAX)
    return c


def _tint(base, col):
    c = base.copy()
    c.fill(col + (255,), special_flags=pygame.BLEND_RGB_MULT)
    return c


class Sprite:
    __slots__ = ("n", "f", "flash", "flashf", "small", "elite", "w", "h")

    def __init__(self, base, do_outline=True):
        n = outline(base) if do_outline else base
        self.n = n
        self.f = pygame.transform.flip(n, True, False)
        self.flash = _white(n)
        self.flashf = pygame.transform.flip(self.flash, True, False)
        self.small = pygame.transform.scale(n, (max(1, n.get_width() * 3 // 5), max(1, n.get_height() * 3 // 5)))
        self.elite = _tint(n, (255, 214, 150))
        self.w, self.h = n.get_size()

    def draw(self, target, x, y, flip=False, flash=False, dy=0):
        img = self.flashf if (flash and flip) else (self.flash if flash else (self.f if flip else self.n))
        target.blit(img, (int(x - self.w // 2), int(y - self.h + 1 + dy)))


_SPRITE_CACHE: dict[str, Sprite] | None = None
_BUILDERS: dict[str, callable] = {}


def reg(name):
    def deco(fn):
        _BUILDERS[name] = fn
        return fn
    return deco


def build_all() -> dict[str, Sprite]:
    global _SPRITE_CACHE
    if _SPRITE_CACHE is None:
        _SPRITE_CACHE = {name: Sprite(fn()) for name, fn in _BUILDERS.items()}
    return _SPRITE_CACHE


def get(name: str) -> Sprite:
    return build_all()[name]


# sombras y glows (cacheados aparte)
_shadow_cache: dict[int, pygame.Surface] = {}
_glow_cache: dict[tuple, pygame.Surface] = {}
_radial_cache: dict[int, pygame.Surface] = {}


def shadow(w: int) -> pygame.Surface:
    w = max(4, (w // 2) * 2)
    if w not in _shadow_cache:
        s = surf(w + 4, w // 2 + 4)
        ell(s, (w + 4) / 2, (w // 2 + 4) / 2, w / 2, w / 4, (5, 7, 14, 105))
        _shadow_cache[w] = s
    return _shadow_cache[w]


def glow(radius: int, color, intensity: int = 110) -> pygame.Surface:
    """Disco de luz premultiplicado para blit aditivo (BLEND_RGB_ADD)."""
    key = (radius, color, intensity)
    if key not in _glow_cache:
        s = surf(radius * 2, radius * 2)
        for r in range(radius, 0, -1):
            f = (1.0 - r / radius) ** 2
            col = (int(color[0] * f * intensity / 255), int(color[1] * f * intensity / 255),
                   int(color[2] * f * intensity / 255))
            if sum(col) > 0:
                circ(s, radius, radius, r, col + (255,))
        _glow_cache[key] = s
    return _glow_cache[key]


def radial_mask(radius: int) -> pygame.Surface:
    """Alpha 255 en el centro → 0 en el borde (para recortar la oscuridad)."""
    if radius not in _radial_cache:
        s = surf(radius * 2, radius * 2)
        for r in range(radius, 0, -1):
            a = int(255 * (1 - (r / radius) ** 1.6))
            circ(s, radius, radius, r, (0, 0, 0, a))
        _radial_cache[radius] = s
    return _radial_cache[radius]


# ==========================================================================
# CACHARROS (jugables) — 8
# ==========================================================================
@reg("char_lia")
def _char_lia():
    s = surf(22, 20)
    ell(s, 11, 18, 7, 2, PAL["M"]); ell(s, 11, 17, 5, 1, PAL["m"])
    line(s, 12, 17, 11, 10, PAL["M"], 2); line(s, 11, 10, 14, 7, PAL["M"], 2)
    poly(s, [(15, 1), (19, 4), (15, 8), (4, 8), (4, 5)], PAL["a"])
    poly(s, [(15, 1), (19, 4), (15, 5), (14, 3)], PAL["b"])
    rect(s, 4, 5, 2, 3, PAL["b"])
    ell(s, 9, 10, 3, 2, PAL["A"])
    eyes(s, [(8, 5), (12, 5)], "normal", cx=10)
    s.set_at((10, 7), PAL["x"])
    return s


@reg("char_tosty")
def _char_tosty():
    s = surf(22, 20)
    rect(s, 3, 8, 16, 10, PAL["l"])
    rect(s, 3, 8, 16, 2, PAL["m"])
    rect(s, 3, 16, 16, 2, PAL["M"])
    rect(s, 6, 8, 4, 2, PAL["k"]); rect(s, 12, 8, 4, 2, PAL["k"])
    rect(s, 7, 4, 3, 5, PAL["w"]); rect(s, 12, 5, 3, 4, PAL["w"])
    rect(s, 7, 4, 3, 1, PAL["b"]); rect(s, 12, 5, 3, 1, PAL["b"])
    rect(s, 18, 10, 2, 5, PAL["r"])
    eyes(s, [(7, 11), (13, 11)], "normal", cx=11)
    rect(s, 5, 18, 2, 2, PAL["d"]); rect(s, 15, 18, 2, 2, PAL["d"])
    return s


@reg("char_ventilin")
def _char_ventilin():
    s = surf(22, 20)
    circ(s, 11, 8, 8, PAL["T"])
    circ(s, 11, 8, 8, PAL["t"], 1)
    circ(s, 11, 8, 5, PAL["w"], 1)
    circ(s, 11, 8, 2, PAL["g"])
    for i in range(4):
        ang = math.radians(45 + i * 90)
        x = 11 + math.cos(ang) * 3.5
        y = 8 + math.sin(ang) * 3.5
        line(s, (11, 8), (int(x), int(y)), PAL["l"], 2)
    rect(s, 10, 15, 2, 3, PAL["g"]); ell(s, 11, 18, 5, 2, PAL["d"])
    eyes(s, [(8, 11), (12, 11)], "normal", cx=11)
    return s


@reg("char_taza")
def _char_taza():
    s = surf(22, 20)
    rect(s, 4, 7, 12, 10, PAL["R"])
    rect(s, 4, 7, 12, 2, PAL["w"])
    rect(s, 5, 9, 10, 2, PAL["b"])
    circ(s, 17, 12, 3, PAL["R"], 1)
    line(s, 7, 4, 8, 2, PAL["w"]); line(s, 11, 4, 12, 1, PAL["w"])
    eyes(s, [(7, 11), (11, 11)], "normal", cx=10)
    line(s, (7, 15), (12, 15), PAL["w"])
    ell(s, 10, 18, 8, 2, PAL["w"])
    return s


@reg("char_grapa")
def _char_grapa():
    s = surf(22, 20)
    rect(s, 3, 14, 16, 5, PAL["r"])
    poly(s, [(5, 7), (19, 10), (19, 14), (5, 14)], PAL["R"])
    rect(s, 13, 12, 3, 3, PAL["d"])
    rect(s, 2, 14, 2, 5, PAL["M"])
    rect(s, 5, 15, 6, 2, PAL["r"])
    eyes(s, [(8, 15), (13, 15)], "angry", cx=10)
    return s


@reg("char_radio")
def _char_radio():
    s = surf(22, 20)
    rect(s, 2, 7, 16, 11, PAL["b"])
    rect(s, 2, 7, 16, 1, PAL["a"])
    rect(s, 4, 9, 6, 7, PAL["d"])
    for i in range(3):
        line(s, (5 + i * 2, 10), (5 + i * 2, 15), PAL["g"])
    rect(s, 12, 9, 5, 3, PAL["w"]); circ(s, 14, 10, 1, PAL["r"])
    line(s, 17, 7, 13, 0, PAL["g"])
    rect(s, 11, 13, 6, 4, PAL["d"])
    eyes(s, [(12, 14), (15, 14)], "normal", cx=13)
    return s


@reg("char_raton")
def _char_raton():
    s = surf(22, 20)
    line(s, 11, 5, 6, 0, PAL["d"]); line(s, 6, 0, 3, 2, PAL["d"])
    ell(s, 11, 11, 7, 7, PAL["l"])
    rect(s, 5, 5, 6, 4, PAL["m"]); rect(s, 11, 5, 6, 4, PAL["m"])
    rect(s, 10, 5, 2, 4, PAL["d"]); rect(s, 10, 6, 2, 2, PAL["g"])
    rect(s, 5, 4, 12, 1, PAL["M"])
    eyes(s, [(8, 12), (13, 12)], "normal", cx=11)
    line(s, (9, 16), (13, 16), PAL["M"])
    return s


@reg("char_alargador")
def _char_alargador():
    s = surf(22, 20)
    line(s, 4, 13, 2, 8, PAL["d"]); line(s, 2, 8, 0, 9, PAL["d"])
    rect(s, 0, 5, 3, 4, PAL["d"])
    rect(s, 4, 10, 16, 8, PAL["w"])
    rect(s, 4, 10, 16, 1, PAL["l"])
    rect(s, 6, 11, 3, 3, PAL["k"]); rect(s, 10, 11, 3, 3, PAL["k"]); rect(s, 14, 11, 3, 3, PAL["k"])
    rect(s, 18, 13, 2, 2, PAL["r"])
    eyes(s, [(8, 16), (13, 16)], "normal", cx=10)
    return s


# ==========================================================================
# JEFES — 4
# ==========================================================================
@reg("boss_despertador")
def _boss_despertador():
    s = surf(42, 38)
    ell(s, 21, 19, 17, 16, PAL["w"])
    ell(s, 21, 19, 17, 16, PAL["l"])
    circ(s, 21, 19, 15, PAL["l"], 1)
    circ(s, 21, 19, 11, PAL["m"], 2)
    ell(s, 11, 4, 6, 5, PAL["a"]); ell(s, 31, 4, 6, 5, PAL["a"])
    ell(s, 11, 4, 4, 3, PAL["A"]); ell(s, 31, 4, 4, 3, PAL["A"])
    line(s, 21, 8, 21, 3, PAL["d"], 2)
    line(s, 21, 19, 21, 9, PAL["k"], 2)
    line(s, 21, 19, 29, 19, PAL["k"], 2)
    eyes(s, [(15, 15), (26, 15)], "angry", cx=21)
    poly(s, [(14, 26), (16, 24), (18, 26), (20, 24), (22, 26), (24, 24), (26, 26)], PAL["k"])
    rect(s, 8, 33, 3, 4, PAL["d"]); rect(s, 20, 34, 3, 4, PAL["d"]); rect(s, 32, 33, 3, 4, PAL["d"])
    return s


@reg("boss_reunion")
def _boss_reunion():
    s = surf(46, 38)
    rect(s, 6, 26, 34, 8, PAL["n"])
    ell(s, 23, 24, 18, 10, PAL["a"])
    ell(s, 14, 16, 9, 8, PAL["A"])
    ell(s, 31, 15, 10, 8, PAL["a"])
    ell(s, 23, 12, 9, 7, PAL["A"])
    ell(s, 38, 24, 6, 5, PAL["y"])
    eyes(s, [(9, 14), (14, 13), (20, 10), (26, 10), (33, 12), (38, 23)], "angry", cx=23)
    poly(s, [(20, 26), (26, 26), (24, 34), (22, 34)], PAL["r"])
    poly(s, [(22, 34), (24, 34), (23, 37)], PAL["r"])
    rect(s, 2, 22, 5, 3, PAL["a"]); rect(s, 39, 16, 5, 3, PAL["A"])
    return s


@reg("boss_deadline")
def _boss_deadline():
    s = surf(42, 42)
    rect(s, 4, 6, 34, 32, PAL["r"])
    rect(s, 6, 8, 30, 28, PAL["R"])
    rect(s, 8, 10, 26, 22, PAL["w"])
    for i in range(4):
        rect(s, 10 + i * 6, 13, 4, 3, PAL["r"])
        rect(s, 10 + i * 6, 18, 4, 3, PAL["r"])
    rect(s, 10, 24, 20, 2, PAL["r"]); rect(s, 10, 27, 14, 2, PAL["r"])
    for i in range(3):
        ell(s, 12 + i * 9, 4, 3, 3, PAL["g"])
    eyes(s, [(14, 32), (24, 32)], "angry", cx=19)
    poly(s, [(14, 36), (17, 34), (20, 37), (23, 34), (26, 36)], PAL["k"])
    rect(s, 6, 38, 4, 4, PAL["d"]); rect(s, 18, 39, 4, 3, PAL["d"]); rect(s, 31, 38, 4, 4, PAL["d"])
    return s


@reg("boss_olvido")
def _boss_olvido():
    s = surf(50, 46)
    poly(s, [(25, 1), (34, 6), (44, 4), (48, 14), (46, 24), (49, 33), (40, 40), (28, 44),
             (16, 41), (6, 42), (2, 32), (5, 22), (0, 13), (10, 8), (14, 2)], PAL["k"])
    poly(s, [(25, 6), (33, 10), (42, 9), (44, 16), (43, 23), (45, 31), (38, 36), (28, 40),
             (18, 37), (9, 38), (6, 30), (8, 22), (4, 15), (12, 11), (16, 7)], K.C["negro_puro"])
    eyes(s, [(17, 18), (30, 17)], "wide", cx=24)
    rect(s, 17, 18, 2, 2, PAL["A"]); rect(s, 30, 17, 2, 2, PAL["A"])
    poly(s, [(20, 29), (24, 27), (28, 29), (25, 33), (22, 32)], PAL["x"])
    import random as _r
    rnd = _r.Random(7)
    for _ in range(26):
        x = rnd.randint(4, 45); y = rnd.randint(6, 40)
        if s.get_at((x, y))[3] > 0:
            s.set_at((x, y), PAL["p"] if rnd.random() < 0.5 else PAL["n"])
    return s


# ==========================================================================
# ENEMIGOS — 16
# ==========================================================================
@reg("en_clip")
def _en_clip():
    s = surf(14, 16)
    line(s, (4, 3), (4, 12), PAL["g"], 2); line(s, (10, 3), (10, 12), PAL["g"], 2)
    line(s, (4, 12), (10, 12), PAL["g"], 2)
    line(s, (7, 2), (7, 10), PAL["l"], 1); line(s, (7, 10), (7, 10), PAL["l"], 1)
    line(s, (4, 3), (12, 3), PAL["l"], 1)
    line(s, (7, 2), (10, 2), PAL["l"], 1)
    eyes(s, [(4, 6), (8, 6)], "angry", cx=7)
    return s


@reg("en_posti")
def _en_posti():
    s = surf(16, 16)
    poly(s, [(2, 2), (13, 2), (13, 12), (10, 14), (2, 14)], PAL["y"])
    poly(s, [(10, 14), (13, 12), (13, 14)], PAL["b"])
    line(s, (5, 5), (10, 5), PAL["b"]); line(s, (5, 8), (9, 8), PAL["b"])
    eyes(s, [(4, 9), (9, 9)], "angry", cx=7)
    return s


@reg("en_grapa")
def _en_grapa():
    s = surf(18, 16)
    rect(s, 2, 11, 14, 4, PAL["r"])
    poly(s, [(3, 5), (15, 8), (15, 11), (3, 11)], PAL["R"])
    poly(s, [(3, 11), (0, 12), (0, 14), (5, 14)], PAL["d"])
    rect(s, 10, 9, 2, 2, PAL["d"])
    eyes(s, [(5, 7), (9, 8)], "angry", cx=7)
    return s


@reg("en_taza")
def _en_taza():
    s = surf(16, 16)
    poly(s, [(2, 8), (12, 5), (14, 10), (6, 14)], PAL["R"])
    circ(s, 13, 8, 2, PAL["R"], 1)
    rect(s, 3, 12, 6, 2, PAL["b"])
    eyes(s, [(5, 9), (9, 8)], "sleepy", cx=7)
    return s


@reg("en_cable")
def _en_cable():
    s = surf(18, 12)
    for i in range(5):
        x = 2 + i * 3
        y = 6 + (2 if i % 2 == 0 else -2)
        circ(s, x, y, 2, PAL["k"])
    rect(s, 10, 2, 5, 4, PAL["d"])
    rect(s, 14, 2, 1, 4, PAL["g"])
    eyes(s, [(11, 3), (13, 3)], "angry", cx=12)
    return s


@reg("en_toner")
def _en_toner():
    s = surf(14, 16)
    rect(s, 2, 3, 10, 10, PAL["p"])
    rect(s, 2, 3, 10, 2, PAL["P"])
    rect(s, 3, 13, 3, 3, PAL["p"]); rect(s, 8, 12, 2, 2, PAL["p"])
    eyes(s, [(4, 6), (8, 6)], "angry", cx=6)
    line(s, (5, 10), (9, 10), PAL["x"])
    return s


@reg("en_pila")
def _en_pila():
    s = surf(10, 16)
    rect(s, 2, 3, 6, 11, PAL["v"])
    rect(s, 2, 3, 6, 3, PAL["V"])
    rect(s, 4, 1, 2, 2, PAL["g"])
    rect(s, 2, 14, 6, 1, PAL["d"])
    rect(s, 3, 11, 4, 2, PAL["b"])
    eyes(s, [(3, 6), (6, 6)], "angry", cx=4)
    return s


@reg("en_monitor")
def _en_monitor():
    s = surf(24, 20)
    rect(s, 2, 2, 19, 13, PAL["l"])
    rect(s, 4, 4, 15, 9, PAL["t"])
    line(s, (6, 5), (9, 9), PAL["T"]); line(s, (11, 6), (14, 11), PAL["T"])
    rect(s, 9, 15, 5, 3, PAL["M"])
    rect(s, 4, 18, 15, 2, PAL["d"])
    eyes(s, [(7, 7), (13, 7)], "angry", cx=10)
    line(s, (8, 11), (13, 11), PAL["x"])
    return s


@reg("en_silla")
def _en_silla():
    s = surf(18, 22)
    rect(s, 3, 1, 11, 9, PAL["u"])
    rect(s, 4, 2, 9, 7, PAL["U"])
    rect(s, 2, 10, 13, 4, PAL["d"])
    circ(s, 4, 15, 2, PAL["g"]); circ(s, 12, 15, 2, PAL["g"])
    line(s, (4, 15), (8, 18), PAL["d"], 2); line(s, (12, 15), (8, 18), PAL["d"], 2)
    line(s, (8, 14), (8, 18), PAL["d"], 2)
    eyes(s, [(5, 4), (10, 4)], "angry", cx=8)
    return s


@reg("en_raton")
def _en_raton():
    s = surf(16, 12)
    line(s, 3, 9, 1, 5, PAL["r"]); line(s, 1, 5, 13, 2, PAL["r"])
    ell(s, 9, 7, 5, 4, PAL["l"])
    rect(s, 6, 3, 3, 2, PAL["M"]); rect(s, 10, 3, 3, 2, PAL["M"])
    rect(s, 9, 3, 1, 3, PAL["d"])
    eyes(s, [(7, 6), (11, 6)], "angry", cx=9)
    s.set_at((8, 6), PAL["r"]); s.set_at((12, 6), PAL["r"])
    return s


@reg("en_bombilla")
def _en_bombilla():
    s = surf(14, 18)
    circ(s, 7, 7, 6, PAL["d"])
    circ(s, 7, 7, 5, PAL["g"], 1)
    line(s, (6, 6), (8, 8), PAL["b"]); line(s, (6, 8), (8, 7), PAL["b"])
    rect(s, 4, 13, 6, 2, PAL["M"]); rect(s, 5, 15, 4, 2, PAL["M"]); rect(s, 5, 17, 4, 1, PAL["g"])
    eyes(s, [(4, 6), (8, 6)], "sleepy", cx=7)
    return s


@reg("en_cuca")
def _en_cuca():
    s = surf(16, 10)
    ell(s, 8, 5, 5, 3, PAL["h"])
    ell(s, 8, 4, 4, 2, PAL["b"])
    line(s, (4, 3), (1, 1), PAL["h"]); line(s, (12, 3), (15, 1), PAL["h"])
    line(s, (5, 7), (3, 9), PAL["h"]); line(s, (9, 7), (8, 9), PAL["h"]); line(s, (12, 6), (14, 9), PAL["h"])
    s.set_at((6, 4), PAL["r"]); s.set_at((10, 4), PAL["r"])
    return s


@reg("en_papelera")
def _en_papelera():
    s = surf(18, 20)
    poly(s, [(3, 6), (15, 6), (13, 19), (5, 19)], PAL["g"])
    rect(s, 2, 4, 14, 3, PAL["d"])
    for i in range(3):
        line(s, (5 + i * 4, 7), (5 + i * 4, 17), PAL["d"])
    poly(s, [(6, 4), (5, 0), (9, 1), (10, 4)], PAL["w"])
    poly(s, [(10, 4), (12, 0), (15, 2), (14, 4)], PAL["w"])
    eyes(s, [(5, 10), (10, 10)], "angry", cx=8)
    return s


@reg("en_archivador")
def _en_archivador():
    s = surf(20, 24)
    rect(s, 2, 2, 16, 20, PAL["g"])
    rect(s, 3, 3, 14, 5, PAL["l"])
    rect(s, 3, 10, 14, 5, PAL["l"])
    rect(s, 3, 17, 14, 4, PAL["l"])
    rect(s, 7, 5, 6, 1, PAL["d"]); rect(s, 7, 12, 6, 1, PAL["d"])
    rect(s, 8, 19, 4, 1, PAL["d"])
    eyes(s, [(5, 4), (11, 4)], "angry", cx=8)
    return s


@reg("en_becario")
def _en_becario():
    s = surf(16, 22)
    rect(s, 4, 2, 8, 7, PAL["s"])
    rect(s, 3, 1, 10, 3, PAL["n"])
    rect(s, 2, 2, 12, 1, PAL["n"])
    eyes(s, [(5, 4), (9, 4)], "dead", cx=7)
    line(s, (5, 8), (9, 8), PAL["x"])
    rect(s, 4, 9, 8, 8, PAL["w"])
    poly(s, [(7, 9), (9, 9), (8, 14)], PAL["r"])
    rect(s, 1, 10, 3, 6, PAL["w"]); rect(s, 12, 10, 3, 6, PAL["w"])
    rect(s, 4, 17, 3, 5, PAL["u"]); rect(s, 9, 17, 3, 5, PAL["u"])
    return s


@reg("en_sombra")
def _en_sombra():
    s = surf(16, 16)
    poly(s, [(8, 1), (13, 4), (15, 10), (11, 15), (5, 15), (1, 10), (3, 4)], K.C["negro_puro"])
    poly(s, [(8, 4), (11, 6), (12, 10), (9, 13), (6, 12), (5, 8)], PAL["k"])
    eyes(s, [(5, 6), (10, 6)], "wide", cx=8)
    rect(s, 5, 6, 1, 1, PAL["p"]); rect(s, 10, 6, 1, 1, PAL["p"])
    return s


# ==========================================================================
# PROYECTILES Y PICKUPS
# ==========================================================================
@reg("pr_staple")
def _pr_staple():
    s = surf(8, 4)
    rect(s, 0, 0, 8, 1, PAL["m"])
    rect(s, 0, 1, 1, 3, PAL["m"]); rect(s, 7, 1, 1, 3, PAL["m"])
    return s


@reg("pr_tack")
def _pr_tack():
    s = surf(6, 8)
    circ(s, 3, 3, 3, PAL["r"])
    circ(s, 3, 2, 2, PAL["R"])
    line(s, (3, 5), (3, 7), PAL["m"])
    return s


@reg("pr_marker")
def _pr_marker():
    s = surf(8, 8)
    ell(s, 4, 4, 3, 3, PAL["t"])
    ell(s, 3, 3, 2, 2, PAL["T"])
    return s


@reg("pr_clip")
def _pr_clip():
    s = surf(7, 8)
    line(s, (2, 1), (2, 6), PAL["l"], 1); line(s, (5, 1), (5, 6), PAL["l"], 1)
    line(s, (2, 6), (5, 6), PAL["l"], 1)
    line(s, (3, 0), (5, 0), PAL["m"], 1); line(s, (3, 0), (3, 4), PAL["m"], 1)
    return s


@reg("pr_scissor")
def _pr_scissor():
    s = surf(12, 12)
    line(s, (2, 10), (9, 2), PAL["l"], 2)
    line(s, (10, 10), (3, 2), PAL["l"], 2)
    circ(s, 2, 10, 2, PAL["r"], 1); circ(s, 10, 10, 2, PAL["r"], 1)
    line(s, (2, 10), (5, 6), PAL["R"], 1); line(s, (10, 10), (7, 6), PAL["R"], 1)
    return s


@reg("pr_coffee")
def _pr_coffee():
    s = surf(7, 9)
    poly(s, [(3, 0), (6, 5), (6, 7), (3, 8), (0, 7), (0, 5)], PAL["b"])
    ell(s, 3, 5, 2, 2, PAL["a"])
    return s


@reg("pr_tape")
def _pr_tape():
    s = surf(9, 7)
    rect(s, 0, 2, 9, 3, PAL["w"])
    rect(s, 0, 2, 9, 1, PAL["y"])
    s.set_at((8, 3), PAL["y"]); s.set_at((2, 4), PAL["l"])
    return s


@reg("pr_missile")
def _pr_missile():
    s = surf(9, 11)
    poly(s, [(2, 2), (2, 9), (5, 7), (8, 10), (8, 7), (5, 5)], PAL["e"])
    return s


@reg("pr_sello")
def _pr_sello():
    s = surf(10, 10)
    circ(s, 5, 5, 4, PAL["r"], 2)
    circ(s, 5, 5, 2, PAL["R"], 1)
    return s


@reg("pr_toner")
def _pr_toner():
    s = surf(8, 8)
    ell(s, 4, 4, 3, 3, PAL["p"])
    ell(s, 3, 3, 2, 2, PAL["P"])
    s.set_at((2, 5), PAL["p"]); s.set_at((5, 6), PAL["P"])
    return s


@reg("pr_orb")
def _pr_orb():
    s = surf(8, 8)
    circ(s, 4, 4, 3, PAL["a"])
    circ(s, 4, 3, 2, PAL["A"])
    s.set_at((3, 3), PAL["e"])
    return s


@reg("pr_spark")
def _pr_spark():
    s = surf(6, 6)
    rect(s, 2, 0, 2, 6, PAL["A"]); rect(s, 0, 2, 6, 2, PAL["A"])
    rect(s, 2, 2, 2, 2, PAL["e"])
    return s


@reg("pk_xp")
def _pk_xp():
    s = surf(8, 10)
    poly(s, [(4, 0), (7, 4), (4, 9), (1, 4)], PAL["T"])
    poly(s, [(4, 2), (6, 4), (4, 7), (2, 4)], PAL["e"])
    return s


@reg("pk_coin")
def _pk_coin():
    s = surf(9, 9)
    circ(s, 4, 4, 4, PAL["b"])
    circ(s, 4, 4, 3, PAL["a"])
    rect(s, 4, 2, 1, 5, PAL["b"])
    return s


@reg("pk_heart")
def _pk_heart():
    s = surf(9, 9)
    poly(s, [(1, 1), (7, 1), (7, 7), (1, 7)], PAL["e"])
    poly(s, [(1, 5), (7, 5), (7, 7), (1, 7)], PAL["l"])
    rect(s, 3, 0, 2, 1, PAL["e"])
    return s


# ==========================================================================
# PROPS (decorado con y sin colisión)
# ==========================================================================
@reg("pp_desk")
def _pp_desk():
    s = surf(36, 22)
    rect(s, 1, 2, 34, 4, PAL["b"])
    rect(s, 1, 2, 34, 1, PAL["a"])
    rect(s, 3, 6, 2, 15, PAL["h"]); rect(s, 31, 6, 2, 15, PAL["h"])
    rect(s, 3, 6, 30, 3, PAL["h"])
    rect(s, 8, 0, 7, 3, PAL["w"]); rect(s, 19, 1, 5, 2, PAL["y"])
    return s


@reg("pp_chair")
def _pp_chair():
    s = surf(16, 22)
    rect(s, 2, 2, 11, 8, PAL["d"])
    rect(s, 3, 3, 9, 6, PAL["g"])
    rect(s, 1, 10, 13, 3, PAL["d"])
    circ(s, 3, 15, 2, PAL["g"]); circ(s, 12, 15, 2, PAL["g"])
    line(s, (3, 15), (8, 19), PAL["d"], 2); line(s, (12, 15), (8, 19), PAL["d"], 2)
    line(s, (8, 13), (8, 19), PAL["d"], 2)
    return s


@reg("pp_plant")
def _pp_plant():
    s = surf(16, 24)
    poly(s, [(4, 16), (12, 16), (11, 23), (5, 23)], PAL["b"])
    rect(s, 4, 16, 9, 2, PAL["a"])
    ell(s, 8, 8, 5, 6, PAL["v"])
    ell(s, 4, 12, 3, 4, PAL["V"]); ell(s, 12, 11, 3, 4, PAL["V"])
    ell(s, 8, 4, 3, 3, PAL["V"])
    return s


@reg("pp_cooler")
def _pp_cooler():
    s = surf(18, 30)
    rect(s, 2, 10, 14, 19, PAL["l"])
    rect(s, 2, 10, 14, 2, PAL["m"])
    poly(s, [(4, 1), (14, 1), (16, 10), (2, 10)], PAL["T"])
    rect(s, 5, 4, 8, 5, PAL["U"])
    rect(s, 7, 16, 4, 3, PAL["t"])
    rect(s, 3, 24, 12, 2, PAL["d"])
    return s


@reg("pp_vending")
def _pp_vending():
    s = surf(30, 46)
    rect(s, 1, 1, 28, 44, PAL["r"])
    rect(s, 3, 3, 24, 26, PAL["n"])
    for i in range(3):
        for j in range(3):
            rect(s, 5 + i * 8, 5 + j * 8, 6, 6, PAL["a"] if (i + j) % 2 else PAL["T"])
    rect(s, 3, 31, 13, 4, PAL["d"])
    rect(s, 3, 37, 13, 4, PAL["d"])
    rect(s, 18, 31, 8, 3, PAL["A"])
    rect(s, 18, 36, 8, 2, PAL["d"])
    rect(s, 18, 40, 8, 3, PAL["k"])
    return s


@reg("pp_box")
def _pp_box():
    s = surf(16, 14)
    rect(s, 1, 3, 14, 11, PAL["b"])
    rect(s, 1, 3, 14, 2, PAL["a"])
    rect(s, 7, 3, 2, 11, PAL["w"])
    rect(s, 1, 3, 2, 2, PAL["b"]); rect(s, 13, 3, 2, 2, PAL["b"])
    return s


@reg("pp_cabinet")
def _pp_cabinet():
    s = surf(18, 26)
    rect(s, 1, 1, 16, 24, PAL["d"])
    rect(s, 2, 2, 14, 11, PAL["g"])
    rect(s, 2, 13, 14, 11, PAL["g"])
    rect(s, 6, 7, 6, 1, PAL["l"]); rect(s, 6, 18, 6, 1, PAL["l"])
    rect(s, 2, 12, 14, 1, PAL["d"])
    return s


@reg("pp_lamp")
def _pp_lamp():
    s = surf(16, 34)
    ell(s, 8, 32, 5, 2, PAL["d"])
    line(s, 8, 30, 8, 8, PAL["g"], 1)
    poly(s, [(3, 2), (13, 2), (15, 8), (1, 8)], PAL["y"])
    poly(s, [(5, 8), (11, 8), (10, 10), (6, 10)], PAL["A"])
    return s


# ==========================================================================
# SUELO (bake completo de la arena)
# ==========================================================================
def bake_floor(seed=11, palette=None, zones=None):
    """Suelo de la planta. palette y zones permiten variar la decoración por mapa."""
    import random as _r
    rnd = _r.Random(seed)
    p = dict(base=(26, 31, 52), alt=(29, 35, 58), speck=(35, 43, 70), speck2=(47, 61, 94),
             zone_a=(31, 42, 66), zone_b=(33, 40, 62), zone_c=(36, 44, 68), wall=(44, 54, 84),
             rug_base=None)
    if palette:
        p.update(palette)
    zone_default = [(60, 60, 260, 200, "zone_a"), (560, 40, 300, 200, "zone_b"),
                    (420, 300, 300, 220, "zone_a"), (100, 330, 260, 190, "zone_b"),
                    (760, 300, 220, 220, "zone_c")]
    zl = zones or zone_default
    dark = tuple(max(0, c - 14) for c in p["base"])
    s = surf(K.ARENA_W, K.ARENA_H)
    s.fill(p["base"])
    for x in range(0, K.ARENA_W, 48):
        for y in range(0, K.ARENA_H, 48):
            if (x // 48 + y // 48) % 2 == 0:
                pygame.draw.rect(s, p["alt"], (x, y, 48, 48))
    for _ in range(3200):
        c = p["speck"] if rnd.random() < 0.8 else p["speck2"]
        s.set_at((rnd.randrange(K.ARENA_W), rnd.randrange(K.ARENA_H)), c)
    # zonas de moqueta (salas)
    for (zx, zy, zw, zh, zk) in zl:
        rect(s, zx + 3, zy + 3, zw, zh, dark)
        rect(s, zx, zy, zw, zh, p[zk])
        pygame.draw.rect(s, p["wall"], (zx, zy, zw, zh), 1)
    # alfombras
    for _ in range(5):
        rx, ry = rnd.randrange(40, K.ARENA_W - 200), rnd.randrange(40, K.ARENA_H - 160)
        rw, rh = rnd.randrange(90, 170), rnd.randrange(70, 120)
        base = p["rug_base"] or rnd.choice([(70, 60, 40), (40, 66, 72), (60, 44, 66)])
        rect(s, rx, ry, rw, rh, base)
        pygame.draw.rect(s, tuple(min(255, c + 22) for c in base), (rx, ry, rw, rh), 1)
        for i in range(4):
            pygame.draw.rect(s, tuple(c // 2 for c in base), (rx + 8 + i * (rw - 16) // 4, ry + 8, (rw - 16) // 5, rh - 16), 1)
    # manchas de café
    for _ in range(14):
        cx, cy = rnd.randrange(30, K.ARENA_W - 30), rnd.randrange(30, K.ARENA_H - 30)
        pygame.draw.circle(s, tuple(max(0, c - 6) for c in p["base"]), (cx, cy), rnd.randrange(4, 12))
        pygame.draw.circle(s, dark, (cx, cy), rnd.randrange(2, 5))
    # bordes oscuros
    for i in range(10):
        pygame.draw.rect(s, tuple(max(0, c - 12) for c in p["base"]), (i, i, K.ARENA_W - i * 2, K.ARENA_H - i * 2), 1)
    return s


# ==========================================================================
def required_names() -> list[str]:
    return list(_BUILDERS.keys())


# arranque perezoso de sombras bajo el jugador (helper de dibujo rápido)
def draw_shadow(target, x, y, w):
    sh = shadow(w)
    target.blit(sh, (int(x - sh.get_width() // 2), int(y - sh.get_height() // 2)))


# ==========================================================================
# ICONO DE LA APP (lámpara de escritorio inconfundible; .ico + ventana)
# ==========================================================================
def lamp_icon(size: int) -> pygame.Surface:
    """Dibuja el icono del juego: lámpara de escritorio encendida sobre noche."""
    u = size / 100.0

    def px(v):
        return max(1, int(v * u)) if v > 0 else int(v * u)

    def P(x, y):
        return (px(x), px(y))

    s = pygame.Surface((size, size), pygame.SRCALPHA)
    r = max(3, px(14))
    pygame.draw.rect(s, (14, 18, 34), (0, 0, size, size), border_radius=r)
    pygame.draw.rect(s, (52, 66, 108), (0, 0, size, size), max(1, px(2.5)), border_radius=r)
    # luna
    pygame.draw.circle(s, (246, 238, 196), P(80, 17), max(1, px(5)))
    pygame.draw.circle(s, (14, 18, 34), P(77.5, 15), max(1, px(4)))
    # halo cálido
    g = glow(max(6, int(size * 0.5)), (255, 200, 120), 70)
    s.blit(g, (px(50) - g.get_width() // 2, px(62) - g.get_height() // 2),
           special_flags=pygame.BLEND_RGB_ADD)
    # haz de luz
    beam = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.polygon(beam, (255, 205, 120, 64), [P(30, 52), P(70, 52), P(94, 95), P(6, 95)])
    s.blit(beam, (0, 0))
    # base
    pygame.draw.ellipse(s, (58, 66, 96), (px(27), px(79), px(46), px(12)))
    pygame.draw.ellipse(s, (96, 108, 150), (px(34), px(80), px(32), px(7)))
    # tallo
    pygame.draw.rect(s, (120, 132, 170), (px(47.5), px(50), max(1, px(5)), px(32)))
    # pantalla (trapecio) con borde
    shade = [P(26, 24), P(74, 24), P(87, 50), P(13, 50)]
    pygame.draw.polygon(s, (232, 176, 88), shade)
    pygame.draw.polygon(s, (120, 78, 34), shade, max(1, px(2.4)))
    # boca interior
    pygame.draw.rect(s, (120, 78, 34), (px(19), px(48), px(62), max(1, px(3.5))))
    # bombilla
    pygame.draw.ellipse(s, (255, 238, 170), (px(43), px(51.5), px(14), max(1, px(6.5))))
    pygame.draw.ellipse(s, (255, 252, 226), (px(46.5), px(52.5), px(7), max(1, px(3.4))))
    return s
