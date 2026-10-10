"""Iconos pequeños (armas, ítems, stats, UI) dibujados por código."""
from __future__ import annotations

import pygame

from .sprites import PAL, ell, circ, line, outline, poly, rect, surf

_ICONS: dict[str, pygame.Surface] = {}
_FNS: dict[str, callable] = {}


def ic(name):
    def deco(fn):
        _FNS[name] = fn
        return fn
    return deco


def get_icon(name: str) -> pygame.Surface:
    if not _ICONS:
        for n, fn in _FNS.items():
            s = fn()
            _ICONS[n] = outline(s)
    return _ICONS.get(name, _ICONS.get("ic_s_dmg", pygame.Surface((8, 8), pygame.SRCALPHA)))


# ============================================================ ARMAS
@ic("ic_w_grapadora")
def _():
    s = surf(16, 16)
    rect(s, 2, 10, 12, 4, PAL["r"]); poly(s, [(3, 5), (14, 8), (14, 10), (3, 10)], PAL["R"])
    rect(s, 10, 8, 2, 2, PAL["d"]); rect(s, 1, 10, 2, 4, PAL["M"])
    return s


@ic("ic_w_chinchetas")
def _():
    s = surf(16, 16)
    for i, (x, y) in enumerate([(4, 4), (11, 3), (8, 9)]):
        circ(s, x, y, 3, PAL["r"]); circ(s, x, y - 1, 2, PAL["R"]); line(s, (x, y + 3), (x, y + 6), PAL["m"])
    return s


@ic("ic_w_cinta")
def _():
    s = surf(16, 16)
    circ(s, 8, 8, 7, PAL["y"]); circ(s, 8, 8, 3, PAL["n"]); circ(s, 8, 8, 7, PAL["b"], 1)
    rect(s, 7, 1, 2, 4, PAL["w"])
    return s


@ic("ic_w_rotulador")
def _():
    s = surf(16, 16)
    poly(s, [(3, 13), (11, 3), (14, 6), (6, 15)], PAL["t"])
    poly(s, [(11, 3), (14, 6), (15, 5), (12, 2)], PAL["k"])
    rect(s, 2, 12, 3, 3, PAL["T"])
    return s


@ic("ic_w_regla")
def _():
    s = surf(16, 16)
    poly(s, [(1, 12), (10, 2), (15, 6), (5, 15)], PAL["l"])
    for i in range(3):
        line(s, (4 + i * 3, 9 - i * 3), (6 + i * 3, 11 - i * 3), PAL["d"])
    return s


@ic("ic_w_clips")
def _():
    s = surf(16, 16)
    line(s, (4, 3), (4, 12), PAL["l"]); line(s, (9, 3), (9, 12), PAL["l"]); line(s, (4, 12), (9, 12), PAL["l"])
    line(s, (6, 5), (6, 13), PAL["m"]); line(s, (11, 5), (11, 13), PAL["m"]); line(s, (6, 13), (11, 13), PAL["m"])
    return s


@ic("ic_w_tijeras")
def _():
    s = surf(16, 16)
    line(s, (2, 14), (12, 3), PAL["l"], 2); line(s, (13, 14), (4, 3), PAL["l"], 2)
    circ(s, 12, 11, 3, PAL["r"], 1); circ(s, 3, 11, 3, PAL["r"], 1)
    return s


@ic("ic_w_cafe")
def _():
    s = surf(16, 16)
    rect(s, 3, 6, 9, 9, PAL["R"]); rect(s, 3, 6, 9, 2, PAL["w"])
    circ(s, 13, 10, 3, PAL["R"], 1); line(s, (5, 4), (6, 1), PAL["w"]); line(s, (9, 4), (8, 1), PAL["w"])
    rect(s, 4, 8, 7, 2, PAL["b"])
    return s


@ic("ic_w_cable")
def _():
    s = surf(16, 16)
    line(s, (1, 12), (5, 9), PAL["k"], 2); line(s, (5, 9), (9, 12), PAL["k"], 2); line(s, (9, 12), (12, 8), PAL["k"], 2)
    rect(s, 11, 3, 4, 4, PAL["d"]); rect(s, 14, 4, 1, 1, PAL["g"]); rect(s, 14, 6, 1, 1, PAL["g"])
    rect(s, 2, 9, 2, 1, PAL["A"]); rect(s, 5, 6, 1, 2, PAL["A"])
    return s


@ic("ic_w_radio")
def _():
    s = surf(16, 16)
    rect(s, 2, 5, 12, 9, PAL["b"]); rect(s, 3, 6, 5, 7, PAL["d"]); rect(s, 9, 6, 4, 2, PAL["w"])
    circ(s, 11, 10, 1, PAL["r"]); line(s, (12, 5), (15, 1), PAL["g"])
    return s


@ic("ic_w_toner")
def _():
    s = surf(16, 16)
    rect(s, 3, 3, 10, 10, PAL["p"]); rect(s, 3, 3, 10, 2, PAL["P"])
    rect(s, 5, 12, 2, 3, PAL["p"]); rect(s, 9, 11, 2, 2, PAL["P"])
    return s


@ic("ic_w_laser")
def _():
    s = surf(16, 16)
    poly(s, [(2, 14), (6, 10), (8, 12), (4, 16 - 2)], PAL["d"])
    line(s, (7, 11), (14, 3), PAL["R"], 2); circ(s, 14, 2, 2, PAL["R"]); circ(s, 14, 2, 1, PAL["e"])
    return s


@ic("ic_w_sello")
def _():
    s = surf(16, 16)
    rect(s, 4, 2, 8, 5, PAL["M"]); rect(s, 6, 7, 4, 4, PAL["d"]); rect(s, 2, 11, 12, 3, PAL["r"])
    return s


@ic("ic_w_movil")
def _():
    s = surf(16, 16)
    rect(s, 5, 1, 6, 14, PAL["k"]); rect(s, 6, 3, 4, 9, PAL["U"]); rect(s, 7, 13, 2, 1, PAL["g"])
    line(s, (2, 4), (3, 5), PAL["A"]); line(s, (14, 4), (13, 5), PAL["A"])
    line(s, (1, 8), (3, 8), PAL["A"]); line(s, (15, 8), (13, 8), PAL["A"])
    return s


# ============================================================ ÍTEMS
@ic("ic_i_taza")
def _():
    s = surf(16, 16)
    rect(s, 3, 5, 9, 9, PAL["R"]); rect(s, 3, 5, 9, 2, PAL["w"]); circ(s, 13, 9, 3, PAL["R"], 1)
    return s


@ic("ic_i_postit")
def _():
    s = surf(16, 16)
    poly(s, [(3, 2), (13, 2), (13, 12), (10, 14), (3, 14)], PAL["y"])
    line(s, (5, 5), (10, 5), PAL["b"]); line(s, (5, 8), (9, 8), PAL["b"])
    return s


@ic("ic_i_grapa")
def _():
    s = surf(16, 16)
    rect(s, 4, 4, 2, 8, PAL["m"]); rect(s, 10, 4, 2, 8, PAL["m"]); rect(s, 4, 2, 8, 2, PAL["m"])
    return s


@ic("ic_i_chinchetas")
def _():
    s = surf(16, 16)
    circ(s, 8, 5, 4, PAL["r"]); circ(s, 8, 4, 3, PAL["R"]); line(s, (8, 9), (8, 14), PAL["m"])
    return s


@ic("ic_i_cafe")
def _():
    s = surf(16, 16)
    rect(s, 3, 6, 9, 8, PAL["b"]); rect(s, 3, 6, 9, 2, PAL["a"]); line(s, (5, 4), (6, 1), PAL["l"]); line(s, (9, 4), (8, 1), PAL["l"])
    return s


@ic("ic_i_boligrafo")
def _():
    s = surf(16, 16)
    poly(s, [(4, 12), (11, 3), (13, 5), (6, 14)], PAL["U"]); rect(s, 3, 11, 3, 3, PAL["d"])
    return s


@ic("ic_i_teclado")
def _():
    s = surf(16, 16)
    rect(s, 1, 5, 14, 7, PAL["d"])
    for i in range(4):
        rect(s, 3 + i * 3, 7, 2, 2, PAL["g"])
        rect(s, 3 + i * 3, 10, 2, 1, PAL["g"])
    return s


@ic("ic_i_raton")
def _():
    s = surf(16, 16)
    ell(s, 8, 9, 5, 6, PAL["l"]); rect(s, 5, 4, 3, 3, PAL["m"]); rect(s, 9, 4, 3, 3, PAL["m"])
    rect(s, 8, 5, 1, 3, PAL["d"])
    return s


@ic("ic_i_auriculares")
def _():
    s = surf(16, 16)
    circ(s, 8, 8, 6, PAL["d"], 2)
    rect(s, 1, 8, 3, 5, PAL["d"]); rect(s, 12, 8, 3, 5, PAL["d"])
    rect(s, 2, 9, 1, 3, PAL["g"]); rect(s, 13, 9, 1, 3, PAL["g"])
    return s


@ic("ic_i_sobre")
def _():
    s = surf(16, 16)
    rect(s, 2, 4, 12, 9, PAL["w"]); line(s, (2, 4), (8, 9), PAL["l"]); line(s, (14, 4), (8, 9), PAL["l"])
    rect(s, 10, 2, 4, 3, PAL["r"])
    return s


@ic("ic_i_pila")
def _():
    s = surf(16, 16)
    rect(s, 6, 2, 2, 1, PAL["g"]); rect(s, 4, 3, 8, 11, PAL["V"]); rect(s, 5, 5, 6, 7, PAL["w"])
    return s


@ic("ic_i_almohadilla")
def _():
    s = surf(16, 16)
    rect(s, 3, 4, 10, 8, PAL["U"]); rect(s, 4, 5, 8, 6, PAL["T"]); line(s, (3, 8), (13, 8), PAL["U"])
    return s


@ic("ic_i_cactus")
def _():
    s = surf(16, 16)
    rect(s, 7, 3, 3, 10, PAL["v"]); rect(s, 3, 6, 2, 4, PAL["v"]); rect(s, 3, 6, 4, 2, PAL["v"])
    rect(s, 11, 4, 2, 5, PAL["v"]); rect(s, 9, 4, 4, 2, PAL["v"])
    rect(s, 5, 13, 6, 3, PAL["b"])
    return s


@ic("ic_i_extintor")
def _():
    s = surf(16, 16)
    rect(s, 5, 5, 6, 10, PAL["r"]); rect(s, 6, 3, 4, 2, PAL["d"]); line(s, (11, 5), (13, 7), PAL["d"])
    rect(s, 6, 7, 4, 2, PAL["w"])
    return s


@ic("ic_i_alfombrilla")
def _():
    s = surf(16, 16)
    rect(s, 2, 4, 12, 8, PAL["t"]); rect(s, 3, 5, 10, 6, PAL["n"]); rect(s, 6, 7, 4, 2, PAL["t"])
    return s


@ic("ic_i_silla")
def _():
    s = surf(16, 16)
    rect(s, 4, 2, 8, 6, PAL["u"]); rect(s, 3, 8, 10, 3, PAL["d"]); circ(s, 5, 12, 1, PAL["g"]); circ(s, 11, 12, 1, PAL["g"])
    return s


@ic("ic_i_ventilador")
def _():
    s = surf(16, 16)
    circ(s, 8, 7, 5, PAL["T"]); circ(s, 8, 7, 2, PAL["g"])
    for i in range(3):
        x = 8 + int(3 * (i - 1) * 1.2)
        line(s, (8, 7), (x, 3), PAL["l"])
    rect(s, 7, 13, 3, 2, PAL["g"])
    return s


@ic("ic_i_usb")
def _():
    s = surf(16, 16)
    rect(s, 4, 3, 8, 10, PAL["d"]); rect(s, 5, 4, 6, 5, PAL["g"]); rect(s, 6, 2, 4, 1, PAL["l"])
    return s


@ic("ic_i_calculadora")
def _():
    s = surf(16, 16)
    rect(s, 3, 2, 10, 13, PAL["l"]); rect(s, 4, 3, 8, 3, PAL["T"])
    for i in range(3):
        for j in range(3):
            rect(s, 4 + i * 3, 8 + j * 2, 2, 1, PAL["d"])
    return s


@ic("ic_i_botiquin")
def _():
    s = surf(16, 16)
    rect(s, 2, 5, 12, 9, PAL["w"]); rect(s, 7, 2, 4, 3, PAL["l"])
    rect(s, 7, 7, 4, 5, PAL["r"]); rect(s, 5, 9, 8, 2, PAL["r"])
    return s


@ic("ic_i_flexo")
def _():
    s = surf(16, 16)
    ell(s, 5, 14, 4, 2, PAL["M"]); line(s, (5, 12), (8, 6), PAL["M"], 1)
    poly(s, [(5, 2), (13, 2), (15, 7), (3, 7)], PAL["y"]); rect(s, 7, 7, 4, 2, PAL["A"])
    return s


@ic("ic_i_sello")
def _():
    s = surf(16, 16)
    rect(s, 4, 2, 8, 4, PAL["M"]); rect(s, 6, 6, 4, 5, PAL["d"]); rect(s, 2, 11, 12, 3, PAL["r"])
    return s


@ic("ic_i_grapadora_oro")
def _():
    s = surf(16, 16)
    rect(s, 2, 10, 12, 4, PAL["a"]); poly(s, [(3, 5), (14, 8), (14, 10), (3, 10)], PAL["A"])
    rect(s, 10, 8, 2, 2, PAL["b"])
    return s


@ic("ic_i_alargador")
def _():
    s = surf(16, 16)
    rect(s, 2, 6, 12, 6, PAL["w"]); rect(s, 4, 7, 2, 3, PAL["k"]); rect(s, 7, 7, 2, 3, PAL["k"]); rect(s, 10, 7, 2, 3, PAL["k"])
    line(s, (14, 9), (15, 12), PAL["d"])
    return s


@ic("ic_i_tarjeta")
def _():
    s = surf(16, 16)
    rect(s, 2, 4, 12, 8, PAL["l"]); rect(s, 2, 6, 12, 2, PAL["d"]); rect(s, 4, 9, 4, 2, PAL["a"])
    return s


@ic("ic_i_funda")
def _():
    s = surf(16, 16)
    rect(s, 4, 1, 8, 14, PAL["u"]); rect(s, 5, 3, 6, 8, PAL["U"]); circ(s, 8, 6, 2, PAL["k"])
    return s


@ic("ic_i_multipresa")
def _():
    s = surf(16, 16)
    rect(s, 1, 5, 14, 7, PAL["w"])
    for i in range(4):
        rect(s, 2 + i * 3, 6, 2, 2, PAL["k"])
    rect(s, 6, 9, 4, 2, PAL["r"])
    return s


@ic("ic_i_diario")
def _():
    s = surf(16, 16)
    rect(s, 3, 2, 10, 12, PAL["b"]); rect(s, 5, 3, 7, 10, PAL["w"]); line(s, (5, 3), (12, 3), PAL["y"])
    line(s, (7, 6), (11, 6), PAL["d"]); line(s, (7, 8), (11, 8), PAL["d"]); line(s, (7, 10), (10, 10), PAL["d"])
    return s


# ============================================================ STATS (8x8)
def _stat_base():
    return surf(10, 10)


@ic("ic_s_dmg")
def _():
    s = _stat_base()
    rect(s, 4, 1, 2, 8, PAL["A"]); rect(s, 1, 4, 8, 2, PAL["A"])
    return s


@ic("ic_s_atk")
def _():
    s = _stat_base()
    poly(s, [(1, 6), (5, 2), (9, 6)], PAL["R"]); rect(s, 1, 7, 8, 2, PAL["r"])
    return s


@ic("ic_s_speed")
def _():
    s = _stat_base()
    poly(s, [(5, 1), (9, 6), (6, 6), (6, 9), (1, 5), (4, 5), (4, 1)], PAL["T"])
    return s


@ic("ic_s_hp")
def _():
    s = _stat_base()
    circ(s, 3, 4, 2, PAL["r"]); circ(s, 6, 4, 2, PAL["r"]); poly(s, [(1, 4), (8, 4), (5, 9)], PAL["r"])
    return s


@ic("ic_s_regen")
def _():
    s = _stat_base()
    rect(s, 4, 1, 2, 8, PAL["e"]); rect(s, 1, 4, 8, 2, PAL["e"])
    return s


@ic("ic_s_armor")
def _():
    s = _stat_base()
    poly(s, [(5, 0), (9, 2), (9, 6), (5, 9), (1, 6), (1, 2)], PAL["U"])
    return s


@ic("ic_s_dodge")
def _():
    s = _stat_base()
    poly(s, [(1, 3), (5, 1), (5, 8), (1, 6)], PAL["T"]); poly(s, [(6, 3), (9, 2), (9, 7), (6, 6)], PAL["t"])
    return s


@ic("ic_s_crit")
def _():
    s = _stat_base()
    circ(s, 5, 5, 4, PAL["r"], 1); circ(s, 5, 5, 1, PAL["r"])
    return s


@ic("ic_s_critdmg")
def _():
    s = _stat_base()
    circ(s, 5, 5, 4, PAL["r"], 1); rect(s, 2, 2, 6, 6, PAL["r"], )
    return s


@ic("ic_s_pickup")
def _():
    s = _stat_base()
    poly(s, [(2, 2), (2, 6), (4, 8), (6, 8), (8, 6), (8, 2)], PAL["t"]); rect(s, 3, 2, 4, 2, PAL["T"])
    return s


@ic("ic_s_luck")
def _():
    s = _stat_base()
    circ(s, 4, 4, 2, PAL["V"]); circ(s, 6, 4, 2, PAL["V"]); circ(s, 5, 6, 2, PAL["V"]); rect(s, 4, 7, 2, 3, PAL["v"])
    return s


@ic("ic_s_coin")
def _():
    s = _stat_base()
    circ(s, 5, 5, 4, PAL["a"]); circ(s, 5, 5, 3, PAL["A"]); rect(s, 4, 3, 1, 5, PAL["b"])
    return s


@ic("ic_s_xp")
def _():
    s = _stat_base()
    poly(s, [(5, 0), (8, 5), (5, 10), (2, 5)], PAL["T"])
    return s


@ic("ic_s_light")
def _():
    s = _stat_base()
    circ(s, 5, 4, 3, PAL["y"]); rect(s, 4, 7, 2, 3, PAL["g"]); rect(s, 3, 3, 1, 1, PAL["w"])
    return s


@ic("ic_s_kb")
def _():
    s = _stat_base()
    poly(s, [(1, 3), (6, 3), (6, 1), (9, 5), (6, 9), (6, 7), (1, 7)], PAL["A"])
    return s


@ic("ic_s_thorn")
def _():
    s = _stat_base()
    line(s, (1, 1), (9, 9), PAL["R"], 2); line(s, (5, 1), (9, 5), PAL["R"], 1); line(s, (1, 5), (5, 9), PAL["R"], 1)
    return s


@ic("ic_s_lifesteal")
def _():
    s = _stat_base()
    poly(s, [(5, 0), (8, 5), (5, 10), (2, 5)], PAL["r"]); circ(s, 4, 4, 1, PAL["R"])
    return s


@ic("ic_s_pierce")
def _():
    s = _stat_base()
    poly(s, [(2, 1), (8, 5), (2, 9)], PAL["l"]); rect(s, 1, 4, 3, 2, PAL["y"])
    return s


@ic("ic_s_proj")
def _():
    s = _stat_base()
    circ(s, 2, 5, 1, PAL["A"]); circ(s, 5, 5, 1, PAL["A"]); circ(s, 8, 5, 1, PAL["A"])
    return s


# ============================================================ UI
@ic("ic_ui_chispa")
def _():
    s = surf(12, 16)
    poly(s, [(7, 0), (2, 9), (6, 9), (4, 15), (10, 6), (6, 6), (9, 0)], PAL["A"])
    return s


@ic("ic_ui_sello")
def _():
    s = surf(14, 14)
    circ(s, 7, 7, 6, PAL["a"]); circ(s, 7, 7, 4, PAL["A"]); circ(s, 7, 7, 2, PAL["b"])
    return s


@ic("ic_ui_lock")
def _():
    s = surf(12, 12)
    circ(s, 6, 5, 3, PAL["g"], 1); rect(s, 3, 5, 6, 6, PAL["g"]); rect(s, 5, 7, 2, 3, PAL["k"])
    return s


@ic("ic_ui_check")
def _():
    s = surf(12, 12)
    poly(s, [(2, 6), (5, 9), (10, 2), (9, 1), (5, 7), (3, 5)], PAL["V"])
    return s


@ic("ic_ui_fogonazo")
def _():
    s = surf(14, 14)
    rect(s, 6, 0, 2, 14, PAL["A"]); rect(s, 0, 6, 14, 2, PAL["A"])
    poly(s, [(2, 2), (6, 6), (4, 8)], PAL["A"]); poly(s, [(12, 2), (8, 6), (10, 8)], PAL["A"])
    return s


@ic("ic_ui_dash")
def _():
    s = surf(14, 14)
    poly(s, [(2, 2), (7, 7), (2, 12)], PAL["T"]); poly(s, [(7, 2), (12, 7), (7, 12)], PAL["t"])
    return s
