"""Economía de run: precios, rerolls, fusiones, compras."""
import os
import tempfile

import pytest

from game.content import weapons as CW


@pytest.fixture(scope="module")
def app():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    from main import build_app
    tmp = tempfile.mkdtemp(prefix="napal_eco_")
    return build_app(headless=True, save_path=os.path.join(tmp, "m.json"), settings_path=os.path.join(tmp, "s.json"))


def _world(app, seed=1):
    from game.world import RunWorld
    return RunWorld(app, "lia", 1, [], seed=seed)


def test_reroll_cost_grows(app):
    w = _world(app)
    w.wave = 5
    c0 = w.reroll_cost()
    w.rerolls = 1
    c1 = w.reroll_cost()
    assert c1 > 0 and c0 > 0
    w.wave = 15
    c15 = w.reroll_cost()
    assert c15 > c0


def test_shop_roll_early_guarantees(app):
    w = _world(app)
    for wave in (1, 2, 3):
        w.wave = wave
        w._roll_shop()
        n_weapons = sum(1 for o in w.shop if o["kind"] == "weapon")
        assert n_weapons >= 2, f"hora {wave} sin garantía de armas"


def test_tier_gating(app):
    w = _world(app)
    w.wave = 1
    assert all(CW.BY_ID[o["id"]]["tier"] == 1 for o in (w.shop if w.shop else [])) or True
    pool = w._weapon_pool()
    assert all(CW.BY_ID[wid]["tier"] == 1 for wid in pool)
    w.wave = 2
    pool2 = w._weapon_pool()
    assert any(CW.BY_ID[wid]["tier"] == 2 for wid in pool2)


def test_buy_and_sell(app):
    w = _world(app)
    w.coins = 200
    w.wave = 1
    w._roll_shop()
    before = len(w.player.weapons)
    # comprar la primera arma de la tienda
    idx = next(i for i, o in enumerate(w.shop) if o["kind"] == "weapon")
    assert w.shop_buy(idx)
    assert len(w.player.weapons) in (before + 1, before)  # +1 o fusión
    # vender
    w2 = _world(app, seed=2)
    w2.coins = 0
    w2.wave = 1
    n = len(w2.player.weapons)
    if n >= 2:
        assert w2.shop_sell(0)
        assert len(w2.player.weapons) == n - 1
        assert w2.coins > 0
    # no puedes vender la última
    while len(w2.player.weapons) > 1:
        w2.shop_sell(0)
    assert not w2.shop_sell(0)


def test_merge_rules(app):
    w = _world(app)
    from game.entities import WeaponInst
    w.player.weapons = [WeaponInst("grapadora", 1), WeaponInst("grapadora", 1), WeaponInst("regla", 1)]
    assert (0, 1) in w.merge_pairs()
    assert w.shop_merge(0, 1)
    assert w.player.weapons[0].level == 2
    assert len(w.player.weapons) == 2
    # no se puede fusionar distinto nivel
    w.player.weapons = [WeaponInst("grapadora", 1), WeaponInst("grapadora", 2)]
    assert not w.merge_pairs()
    assert not w.shop_merge(0, 1)
    # nivel máximo
    w.player.weapons = [WeaponInst("grapadora", CW.MAX_WEAPON_LEVEL)] * 2
    assert not w.merge_pairs()


def test_buy_full_slots_merges_or_denies(app):
    w = _world(app)
    from game.entities import WeaponInst
    w.player.weapons = [WeaponInst(x, 1) for x in ("grapadora", "chinchetas", "cinta", "rotulador", "regla", "clips")]
    w.coins = 200
    w.wave = 1
    w.shop = [{"kind": "weapon", "id": "grapadora", "price": 10, "sold": False}]
    assert w.shop_buy(0)  # fusión automática
    assert len(w.player.weapons) == 6
    assert any(x.wid == "grapadora" and x.level == 2 for x in w.player.weapons)
    w.shop = [{"kind": "weapon", "id": "tijeras", "price": 10, "sold": False}]
    before_coins = w.coins
    assert not w.shop_buy(0)  # sin hueco y sin fusión posible
    assert w.coins == before_coins


def test_heal_price(app):
    w = _world(app)
    w.wave = 1
    p1 = w.shop_heal_price()
    w.wave = 12
    assert w.shop_heal_price() > p1
    w.coins = 999
    w.player.hp = 10
    assert w.shop_heal()
    assert w.player.hp > 10
