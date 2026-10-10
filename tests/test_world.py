"""Mundo: invariantes, mecánica de luz, subida de nivel y una noche corta real."""
import os
import tempfile

import pytest

from game import const as K


@pytest.fixture(scope="module")
def app():
    from main import build_app
    tmp = tempfile.mkdtemp(prefix="napal_world_")
    return build_app(headless=True, save_path=os.path.join(tmp, "m.json"), settings_path=os.path.join(tmp, "s.json"))


def _world(app, char="lia", guardia=1, muts=None, seed=1):
    from game.world import RunWorld
    return RunWorld(app, char, guardia, muts or [], seed=seed)


def test_spawning_invariants(app):
    w = _world(app)
    w.intro_t = 0
    w.phase = "active"
    for _ in range(60 * 40):
        w.update(1 / 60)
        if w.phase in ("dead", "levelup"):
            break
        if w.phase == "levelup":
            w.pending_levels = 0
            w.phase = "active"
    assert len(w.enemies) <= 230
    assert len(w.pickups) <= 320
    for e in w.enemies[:50]:
        assert 0 <= e.x <= K.ARENA_W and 0 <= e.y <= K.ARENA_H
        assert e.hp > 0 or e.dead  # los muertos del último frame esperan barrido
    assert w.kills > 0


def test_light_damage_multiplier(app):
    w = _world(app)
    w.intro_t = 0
    w.phase = "active"
    w.enemies.clear()
    lit = w._spawn_at("posti", w.player.x + 10, w.player.y)
    e_lit = w.enemies[-1]
    dark = w._spawn_at("posti", w.player.x + w.light_radius() + 120, w.player.y)
    e_dark = w.enemies[-1]
    hp0 = e_lit.hp
    w.damage(e_lit, 10.0, crit_ok=False)
    dmg_lit = hp0 - e_lit.hp
    hp0d = e_dark.hp
    w.damage(e_dark, 10.0, crit_ok=False)
    dmg_dark = hp0d - e_dark.hp
    assert dmg_lit > 0 and dmg_dark > 0
    assert abs(dmg_dark / dmg_lit - K.LIGHT_DMG_DARK) < 0.01


def test_levelup_flow(app):
    w = _world(app)
    w.intro_t = 0
    w.phase = "active"
    w._add_xp(w.xp_next)
    assert w.level == 2 and w.pending_levels == 1
    w.update(1 / 60)
    assert w.phase == "levelup"
    cards = w.roll_levelup_cards()
    assert len(cards) == 3
    w.apply_levelup(cards[0])
    assert w.phase == "active" and w.pending_levels == 0


def test_wave_flow_and_shop(app):
    w = _world(app)
    w.intro_t = 0
    w.phase = "active"
    w.wave_t = w.wave_total  # fuerza fin de oleada
    w.update(1 / 60)
    assert w.phase == "shop"
    assert len(w.shop) == w.shop_slots
    w.coins = 500
    bought = 0
    for i in range(len(w.shop)):
        if w.shop_buy(i):
            bought += 1
    assert bought >= 1
    w.leave_shop()
    assert w.phase == "active"
    assert w.wave == 2


def test_fogonazo_and_dash(app):
    w = _world(app)
    w.intro_t = 0
    w.phase = "active"
    w._spawn_at("posti", w.player.x + 30, w.player.y)
    w.update(1 / 60)  # un frame para reconstruir el hash espacial
    e = w.enemies[-1]
    hp0 = e.hp
    w._do_fogonazo()
    assert e.hp < hp0  # dañado
    assert e.st.get("stun") is not None
    assert w.player.abl_cd > 0
    from game.core import V
    w._do_dash(V(1, 0))
    assert w.player.dash_t > 0
    assert w.rs["dashes"] == 1


def test_short_night_with_bot(app):
    """60 s de juego real con el bot: sin excepciones y con progreso."""
    from game.simharness import fast_run
    r = fast_run(app, "lia", 1, [], seed=42, max_time=60.0)
    assert r["phase"] in ("active", "shop", "levelup", "dead", "victory")
    assert r["kills"] >= 5
    assert r["level"] >= 1


def test_run_finish_merges_stats(app):
    w = _world(app)
    w.intro_t = 0
    w.phase = "active"
    w.kills = 50
    before_runs = app.save.data["stats"]["runs"]
    w._finish(victory=False)
    assert app.save.data["stats"]["runs"] == before_runs + 1
    assert app.save.chispas > 0
    assert len(app.save.data["history"]) >= 1


def test_drainer_reduces_light(app):
    w = _world(app)
    w.intro_t = 0
    w.phase = "active"
    base = w.light_radius()
    w._spawn_at("bombilla", w.player.x + 20, w.player.y)
    w.update(1 / 60)
    assert w.light_radius() < base
