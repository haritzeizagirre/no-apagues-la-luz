"""Integridad de mapas fijos por guardia, sellos de desbloqueo e icono."""
import os
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from game import const as K  # noqa: E402
from game.content import ach, chars as CC, items as CI, maps as CMP  # noqa: E402
from game.content import mutators as CM, weapons as CW  # noqa: E402


def test_maps_layout_valid():
    assert len(CMP.MAPS) == K.MAX_GUARDIA
    valid_kinds = {"desk", "chair", "plant", "cooler", "cabinet", "box", "lamp"}
    for m in CMP.MAPS:
        assert m["props"] and m["boxes"], m["id"]
        assert len(m["boxes"]) >= 6, f"{m['id']} necesita al menos 6 cajas"
        assert m.get("short") and m.get("name") and m.get("floor"), m["id"]
        for (kind, x, y) in m["props"]:
            assert kind in valid_kinds, (m["id"], kind)
            assert 40 <= x <= K.ARENA_W - 40 and 40 <= y <= K.ARENA_H - 40, (m["id"], kind, x, y)
            d = ((x - K.ARENA_W / 2) ** 2 + (y - K.ARENA_H / 2) ** 2) ** 0.5
            assert d >= 55, f"prop {kind} de {m['id']} demasiado cerca del spawn"
        for (x, y) in m["boxes"]:
            assert 40 <= x <= K.ARENA_W - 40 and 40 <= y <= K.ARENA_H - 40, (m["id"], x, y)


def test_for_guardia_clamps():
    assert CMP.for_guardia(1) is CMP.MAPS[0]
    assert CMP.for_guardia(5) is CMP.MAPS[4]
    assert CMP.for_guardia(9) is CMP.MAPS[4]


@pytest.fixture(scope="module")
def app():
    from main import build_app
    tmp = tempfile.mkdtemp(prefix="napal_maps_")
    return build_app(headless=True, save_path=os.path.join(tmp, "m.json"),
                     settings_path=os.path.join(tmp, "s.json"))


def test_world_uses_fixed_map(app):
    from game.world import RunWorld
    w1 = RunWorld(app, "lia", 1, [])
    w3 = RunWorld(app, "lia", 3, [])
    assert w1.map["id"] != w3.map["id"], "cada guardia debe usar una planta distinta"
    assert len(w1.props) == len(w1.map["props"]) + len(w1.map["boxes"])
    assert w1.floor.get_width() == K.ARENA_W
    # dos runs en la misma guardia comparten posiciones de muebles
    w1b = RunWorld(app, "lia", 1, [])
    pos_a = sorted((p.kind, p.x, p.y) for p in w1.props)
    pos_b = sorted((p.kind, p.x, p.y) for p in w1b.props)
    assert pos_a == pos_b, "el mapa debe ser FIJO (mismas posiciones)"


def test_every_char_unlock_has_seal():
    for c in CC.CHARS:
        u = c.get("unlock")
        if u:
            seal = ach.seal_for(u)
            assert seal is not None, f"{c['id']} sin sello de desbloqueo"
            assert seal["desc"], f"sello de {c['id']} sin descripción"


def test_seal_unlocks_are_valid_ids():
    table = {"char": CC.BY_ID, "weapon": CW.BY_ID, "item": CI.BY_ID, "mutator": CM.BY_ID}
    for a in ach.ACHIEVEMENTS:
        u = a.get("unlock")
        if not u:
            continue
        kind, _, name = u.partition(":")
        assert kind in table and name in table[kind], f"unlock roto: {u}"


def test_unlock_report_and_labels(app):
    from game.world import RunWorld
    w = RunWorld(app, "lia", 1, [])
    w.save.unlock("weapon:cafe")
    w._finish(victory=False)
    kinds = [k for (k, _v) in w.unlock_report]
    assert "unlock" in kinds, "el informe no recoge el desbloqueo de la noche"
    for k, u in w.unlock_report:
        if k == "unlock":
            lbl, disp, _k, _n = w.unlock_label(u)
            assert lbl and disp


def test_lamp_icon_has_bulb():
    from game import sprites as S
    pygame.display.init()
    pygame.display.set_mode((32, 32))
    ic = S.lamp_icon(32)
    bright = 0
    for x in range(8, 24):
        for y in range(12, 22):
            if sum(ic.get_at((x, y))[:3]) > 560:
                bright += 1
    assert bright >= 6, "el icono de la lámpara no destaca la bombilla"
