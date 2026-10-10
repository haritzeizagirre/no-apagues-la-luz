"""Integridad del contenido: ids, referencias cruzadas y sprites."""
from game import const as K
from game import sprites as S
from game import icons as I
from game.content import ach, chars, enemies, items, metaup, mutators, perks, waves, weapons


def test_counts():
    assert len(weapons.WEAPONS) == 14
    assert len(items.ITEMS) == 28
    assert len(enemies.ENEMIES) == 17
    assert len(enemies.BOSSES) == 4
    assert len(chars.CHARS) == 8
    assert len(metaup.META_UPGRADES) == 20
    assert len(ach.ACHIEVEMENTS) >= 24
    assert len(mutators.MUTATORS) == 6
    assert len(perks.PERKS) >= 30


def test_ids_unique():
    for coll in (weapons.WEAPONS, items.ITEMS, enemies.ENEMIES, enemies.BOSSES,
                 chars.CHARS, metaup.META_UPGRADES, ach.ACHIEVEMENTS, mutators.MUTATORS, perks.PERKS):
        ids = [c["id"] for c in coll]
        assert len(ids) == len(set(ids))


KINDS_REQUIRED = {
    "shot": {"count", "dmg", "speed", "proj"},
    "melee": {"dmg", "radius", "arc"},
    "beam": {"dps", "length"},
    "chain": {"dmg", "hops", "hop_range"},
    "lob": {"dmg", "aoe"},
    "boomerang": {"dmg", "speed", "range"},
    "bounce": {"dmg", "speed", "bounces"},
    "orbit": {"dmg", "radius"},
    "aura": {"dmg", "radius"},
    "nova": {"dmg", "radius"},
    "homing": {"dmg", "speed"},
    "slam": {"dmg", "radius"},
    "tape": {"dmg", "speed", "slow", "dot"},
}


def test_weapons_wellformed():
    for w in weapons.WEAPONS:
        assert w["kind"] in KINDS_REQUIRED, w["id"]
        missing = KINDS_REQUIRED[w["kind"]] - set(w["base"])
        assert not missing, f"{w['id']} le faltan {missing}"
        assert w["cd"] >= 0
        assert 1 <= w["tier"] <= 4
        eff = weapons.effective(w, 4)
        if "dmg" in w["base"]:
            assert eff["dmg"] > w["base"]["dmg"]


def test_items_stats_valid():
    for it in items.ITEMS:
        for k in it["stats"]:
            assert k in K.STATS, f"{it['id']}: stat {k}"
        assert 1 <= it["tier"] <= 4
        assert sum(1 for v in it["stats"].values() if v < 0) <= 1  # máximo un downside


def test_chars_valid():
    for c in chars.CHARS:
        for k in c["add"]:
            assert k in K.STATS, f"{c['id']}: {k}"
        for k in c["mult"]:
            assert k in K.STATS, f"{c['id']}: {k}"
        for wid in c["weapons"]:
            assert wid in weapons.BY_ID
        assert c["sprite"] in S.required_names(), c["id"]


def test_enemies_have_sprites():
    names = set(S.required_names())
    for e in enemies.ENEMIES + enemies.BOSSES:
        assert e["sprite"] in names, e["id"]
        assert e["hp"] > 0 and e["dmg"] > 0


def test_sprites_build_and_nonempty():
    lib = S.build_all()
    import pygame
    for name in S.required_names():
        sp = lib[name]
        assert sp.w > 3 and sp.h > 3
        mask = pygame.mask.from_surface(sp.n)
        assert mask.count() >= 8, f"{name} casi vacío"


def test_icons_exist_for_content():
    for w in weapons.WEAPONS:
        assert I.get_icon(w["icon"]).get_width() > 4, w["icon"]
    for it in items.ITEMS:
        assert I.get_icon(it["icon"]).get_width() > 4, it["icon"]
    for p in perks.PERKS:
        assert I.get_icon(p["icon"]).get_width() > 4, p["icon"]


def test_unlocks_reference_existing_content():
    valid = set()
    valid |= {f"char:{c['id']}" for c in chars.CHARS}
    valid |= {f"weapon:{w['id']}" for w in weapons.WEAPONS}
    valid |= {f"item:{i['id']}" for i in items.ITEMS}
    valid |= {f"mutator:{m['id']}" for m in mutators.MUTATORS}
    for a in ach.ACHIEVEMENTS:
        if a.get("unlock"):
            assert a["unlock"] in valid, f"{a['id']} -> {a['unlock']}"
    for w in weapons.WEAPONS:
        if w.get("unlock"):
            assert w["unlock"] in valid, w["id"]
    for it in items.ITEMS:
        if it.get("unlock"):
            assert it["unlock"] in valid, it["id"]


def test_waves_composition_all_hours():
    import random
    rng = random.Random(1)
    for hora in range(1, 26):
        comp = waves.composition(hora, rng, {})
        assert comp, f"hora {hora} sin enemigos"
        assert waves.wave_len(hora, {}) > 0


def test_boss_schedule():
    for h in (5, 10, 15, 20):
        b = enemies.boss_by_hora(h)
        assert b is not None
    scaled = waves.boss_scaled(enemies.BOSSES[0], 5, 1, {}, False)
    assert scaled["hp"] > 0


def test_meta_stats_valid():
    for m in metaup.META_UPGRADES:
        for k in m.get("add", {}):
            assert k in K.STATS, m["id"]
        assert m["max_rank"] >= 1
        c0, c1 = metaup.cost(m, 0), metaup.cost(m, 1)
        assert c1 > c0


def test_starting_weapons_are_starter_weapons():
    for wid in weapons.STARTING_WEAPONS:
        assert wid in weapons.BY_ID
