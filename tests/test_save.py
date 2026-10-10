"""Guardado: roundtrip, corrupción, ajustes y sellos."""
import json
import os
import tempfile

from game import save as SV
from game.content import ach, mutators


def _tmp(name):
    d = tempfile.mkdtemp(prefix="napal_test_")
    return os.path.join(d, name)


def test_save_roundtrip():
    p = _tmp("meta.json")
    s = SV.Save(p)
    assert s.chispas == 0 and s.has("char:lia")
    s.earn(250)
    s.unlock("weapon:cable")
    s.set_rank("dmg", 2)
    s.stat_add("kills", 500)
    s.see_enemy("cable")
    s.flush()
    s2 = SV.Save(p)
    assert s2.chispas == 250
    assert s2.has("weapon:cable")
    assert s2.rank("dmg") == 2
    assert s2.data["stats"]["kills"] == 500
    assert s2.seen_enemy("cable")


def test_save_corrupt_recovery():
    p = _tmp("meta.json")
    with open(p, "w", encoding="utf-8") as f:
        f.write("{esto no es json!!!")
    s = SV.Save(p)
    assert s.chispas == 0
    assert any(fn.startswith("meta.json.corrupto") for fn in os.listdir(os.path.dirname(p)))


def test_settings_defaults_and_merge():
    p = _tmp("settings.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"vol_master": 0.1}, f)
    st = SV.Settings(p)
    assert st["vol_master"] == 0.1
    assert st["vol_sfx"] == 0.9  # default rellenado
    st["scale"] = 3
    st.flush()
    st2 = SV.Settings(p)
    assert st2["scale"] == 3


def test_achievement_evaluate_and_unlock():
    p = _tmp("meta.json")
    s = SV.Save(p)
    newly = ach.evaluate(s, {"best_wave": 8})
    ids = [n[0] for n in newly]
    assert "off_h5" in ids and "off_h8" in ids
    assert s.has("char:tosty")  # desbloqueo de off_h8
    # el premio en chispas lo acredita el llamador (RunWorld._check_achievements)
    total = sum(n[1] for n in newly)
    assert total >= 25
    delta = dict((n[0], n[1]) for n in newly)
    for aid, val in delta.items():
        s.earn(val)
    assert s.chispas == total


def test_boss_achievements():
    p = _tmp("meta.json")
    s = SV.Save(p)
    s.slay_boss("despertador")
    newly = ach.evaluate(s)
    ids = [n[0] for n in newly]
    assert "off_jefe1" in ids


def test_mutator_aggregate():
    mods = mutators.aggregate(["apagon", "sobrecarga"])
    assert abs(mods["light"] + 0.20) < 1e-9
    assert abs(mods["enemy_spd"] - 0.15) < 1e-9
    assert mods["reward"] > 1.0
