"""Entidades del run: jugador, enemigos, proyectiles, pickups, props."""
from __future__ import annotations

import math
import random

from .content import enemies as CE
from .content import weapons as CW


class WeaponInst:
    __slots__ = ("wid", "level", "timer", "mods", "beam_t", "orbit_a", "shots")

    def __init__(self, wid: str, level: int = 1):
        self.wid = wid
        self.level = level
        self.timer = random.uniform(0.0, 0.5)
        self.mods = {"dmg": 0.0, "cd": 0.0, "dot": 0.0, "param": {}, "param_pct": {}}
        self.beam_t = 0.0
        self.orbit_a = random.uniform(0.0, 6.28)
        self.shots = 0

    @property
    def defn(self) -> dict:
        return CW.BY_ID[self.wid]


class Player:
    __slots__ = ("char", "x", "y", "vx", "vy", "r", "hp", "max_hp", "stats", "weapons", "items",
                 "perks", "wmods", "aim", "facing", "iframe", "dash_t", "dash_cd", "abl_cd",
                 "buff_t", "buff_mult", "drains", "hurt_flash", "walk_t", "alive", "revives",
                 "combo", "combo_t", "life_steal_acc", "dash_vx", "dash_vy", "rafaga_cd", "mvx", "mvy")

    def __init__(self, char_def: dict, stats: dict, weapons: list):
        self.char = char_def
        self.x, self.y = 0.0, 0.0
        self.vx, self.vy = 0.0, 0.0
        self.r = 9
        self.stats = stats
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.weapons: list[WeaponInst] = weapons
        self.items: list[str] = []
        self.perks: dict[str, int] = {}
        self.wmods: dict[str, dict] = {}
        self.aim = random.uniform(0, 6.28)
        self.facing = False
        self.iframe = 0.0
        self.dash_t = 0.0
        self.dash_cd = 0.0
        self.abl_cd = 0.0
        self.buff_t = 0.0
        self.buff_mult = 1.0
        self.drains = 0
        self.hurt_flash = 0.0
        self.walk_t = 0.0
        self.alive = True
        self.revives = 0
        self.combo = 0
        self.combo_t = 0.0
        self.life_steal_acc = 0.0
        self.dash_vx = 0.0
        self.dash_vy = 0.0
        self.rafaga_cd = 0.0
        self.mvx = 0.0
        self.mvy = 0.0


class Enemy:
    __slots__ = ("eid", "defn", "x", "y", "vx", "vy", "hp", "max_hp", "r", "elite", "spd", "dmg",
                 "xp", "coin", "kb_r", "st", "flash_t", "shoot_t", "charge_t", "charge_v", "dash_t",
                 "dash_v", "spawn_t", "puddle_t", "zig_t", "zig_sign", "dead", "boss", "pat_i",
                 "pat_cd", "pat_t", "wander", "hit_seen", "teleg_t", "dirx", "diry", "state_i")

    def __init__(self, defn: dict, x: float, y: float, hp: float, dmg: float, spd: float,
                 elite: bool = False, boss: bool = False):
        self.eid = defn["id"]
        self.defn = defn
        self.x, self.y = x, y
        self.vx, self.vy = 0.0, 0.0
        self.hp = self.max_hp = hp
        self.r = defn["r"] * (1.15 if elite else 1.0)
        self.elite = elite
        self.spd = spd
        self.dmg = dmg
        self.xp = defn["xp"] * (2 if elite else 1)
        self.coin = defn.get("coin", 0.5) * (2.5 if elite else 1.0)
        self.kb_r = defn.get("kb_resist", 0.0)
        self.st = {}          # estados: burn/poison/slow/stun/bleed → (t, valor)
        self.flash_t = 0.0
        self.shoot_t = random.uniform(0.5, 1.5)
        self.charge_t = random.uniform(1.0, 2.0)
        self.charge_v = 0.0
        self.dash_t = 0.0
        self.dash_v = 0.0
        self.spawn_t = random.uniform(1.0, 2.5)
        self.puddle_t = random.uniform(1.0, 2.5)
        self.zig_t = random.uniform(0, 3)
        self.zig_sign = random.choice((-1, 1))
        self.dead = False
        self.boss = boss
        self.pat_i = 0
        self.pat_cd = 2.0
        self.pat_t = 0.0
        self.wander = random.uniform(0, 6.28)
        self.hit_seen = {}
        self.teleg_t = 0.0
        self.dirx = 1.0
        self.diry = 0.0
        self.state_i = 0


class Proj:
    __slots__ = ("x", "y", "vx", "vy", "dmg", "pierce", "life", "friendly", "sprite", "r", "kb",
                 "status", "kind", "bounces", "hit_cd", "ox", "oy", "dirx", "diry", "range", "phase",
                 "tx", "ty", "t_air", "t_tot", "homing", "gone", "spin", "rot")

    def __init__(self, x, y, vx, vy, dmg, friendly, sprite, r=4, pierce=0, life=2.0, kb=0.0,
                 kind="bullet", status=None, bounces=0, ox=None, oy=None, range_=0.0, tx=None, ty=None,
                 t_air=0.0, homing=False, spin=0.0):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.dmg = dmg
        self.pierce = pierce
        self.life = life
        self.friendly = friendly
        self.sprite = sprite
        self.r = r
        self.kb = kb
        self.status = status or {}
        self.kind = kind
        self.bounces = bounces
        self.hit_cd: dict[int, float] = {}
        self.ox, self.oy = (x if ox is None else ox), (y if oy is None else oy)
        self.tx, self.ty = tx, ty
        self.dirx, self.diry = vx, vy
        self.range = range_
        self.phase = 0
        self.t_air = t_air
        self.t_tot = t_air
        self.homing = homing
        self.gone = False
        self.spin = spin
        self.rot = 0.0


class Pickup:
    __slots__ = ("kind", "value", "x", "y", "vx", "vy", "life", "magnet")

    def __init__(self, kind, value, x, y):
        self.kind = kind
        self.value = value
        self.x, self.y = x, y
        a = random.uniform(0, 6.28)
        sp = random.uniform(20, 70)
        self.vx, self.vy = math.cos(a) * sp, math.sin(a) * sp
        self.life = 26.0
        self.magnet = False


class Prop:
    __slots__ = ("kind", "x", "y", "r", "solid", "hp", "sprite", "dead")

    def __init__(self, kind, x, y, r=14, solid=True, hp=0):
        self.kind = kind
        self.x, self.y = x, y
        self.r = r
        self.solid = solid
        self.hp = hp
        self.sprite = f"pp_{kind}"
        self.dead = False


class Puddle:
    __slots__ = ("x", "y", "r", "dps", "slow", "t", "friendly")

    def __init__(self, x, y, r, dps, slow, t, friendly=True):
        self.x, self.y = x, y
        self.r = r
        self.dps = dps
        self.slow = slow
        self.t = t
        self.friendly = friendly


def make_enemy(eid: str, x, y, hp_mult: float, dmg_mult: float, spd_mult: float, elite=False) -> Enemy:
    d = CE.BY_ID[eid]
    return Enemy(d, x, y, d["hp"] * hp_mult, d["dmg"] * dmg_mult, d["spd"] * spd_mult, elite=elite)


def make_boss(defn: dict, x, y, hp_mult: float, dmg_mult: float) -> Enemy:
    e = Enemy(defn, x, y, defn["hp"] * hp_mult, defn["dmg"] * dmg_mult, defn["spd"], boss=True)
    e.r = defn["r"]
    e.kb_r = 0.92
    return e
