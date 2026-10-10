"""Disparo de armas: interpreta cada 'kind' sobre el mundo."""
from __future__ import annotations

import math

from . import const as K
from .core import ARENA_H, ARENA_W, clamp
from .content import weapons as CW
from .entities import Proj

FIRERS = {}


def firer(kind):
    def deco(fn):
        FIRERS[kind] = fn
        return fn
    return deco


def effective(inst, world):
    """Params efectivos del arma (nivel + stats + mods de perks)."""
    w = inst.defn
    p = CW.effective(w, inst.level)
    stats = world.stats
    m = inst.mods
    extra = world.player.wmods.get(inst.wid)
    dmg_add = m.get("dmg", 0.0) + (extra["dmg"] if extra else 0.0)
    cd_red = m.get("cd", 0.0) + (extra["cd"] if extra else 0.0)
    dot_add = m.get("dot", 0.0) + (extra["dot"] if extra else 0.0)
    if "dmg" in p:
        p["dmg"] *= (1 + dmg_add) * stats["dmg"]
    if "dps" in p:
        p["dps"] *= (1 + dmg_add) * stats["dmg"]
    if "dot" in p:
        p["dot"] *= (1 + dot_add) * (1 + stats["dmg"] * 0.5)
    adds = dict(extra["param"]) if extra else {}
    for k, v in m.get("param", {}).items():
        adds[k] = adds.get(k, 0) + v
    p["count"] = p.get("count", 0) + stats["proj_add"] + adds.pop("count", 0)
    p["pierce"] = p.get("pierce", 0) + stats["pierce_add"] + adds.pop("pierce", 0)
    for k, v in adds.items():
        p[k] = p.get(k, 0) + v
    pcts = dict(extra["param_pct"]) if extra else {}
    for k, v in m.get("param_pct", {}).items():
        pcts[k] = pcts.get(k, 0) + v
    for k, v in pcts.items():
        if k in p:
            p[k] *= (1 + v)
    return p, cd_red


def update_weapon(world, inst, dt):
    w = inst.defn
    kind = w["kind"]
    pl = world.player
    p, cd_red = effective(inst, world)
    if kind == "beam":
        _beam(world, inst, pl, p, dt)
        return
    inst.timer -= dt
    if inst.timer > 0:
        return
    base_cd = w["cd"]
    inst.timer = max(0.12, base_cd / world.stats["atk_speed"] * (1 - min(0.7, cd_red)))
    inst.timer *= world.rng.uniform(0.93, 1.07)
    inst.shots += 1
    fn = FIRERS.get(kind)
    if fn:
        fn(world, inst, pl, p)
    if world.char["perk"] == "sobrecarga" and inst.shots % 6 == 0 and kind != "beam":
        _chain_zap(world, pl, 10 * world.stats["dmg"], 2, 95)


def _status_from(inst, p):
    st = {}
    if "slow" in p and p.get("slow", 0) > 0:
        st["slow"] = (p["slow"], p.get("slow_t", 2.0))
    if p.get("dot", 0) > 0:
        st["burn" if inst.wid in ("cinta", "cafe") else "poison"] = p["dot"]
    return st


@firer("shot")
def _f_shot(world, inst, pl, p):
    n = int(max(1, p.get("count", 1)))
    spread = math.radians(p.get("spread", 10))
    status = _status_from(inst, p)
    for i in range(n):
        ang = pl.aim + (i - (n - 1) / 2) * spread
        vx, vy = math.cos(ang) * p["speed"], math.sin(ang) * p["speed"]
        world.projs.append(Proj(pl.x, pl.y - 6, vx, vy, p["dmg"], True, p["proj"], r=5,
                                pierce=int(p.get("pierce", 0)), life=p.get("life", 0.6),
                                kb=p.get("kb", 0.4), status=status))
    snd = {"pr_staple": "shoot_tack", "pr_tack": "shoot_tack", "pr_marker": "shoot_marker"}.get(p["proj"], "shoot_throw")
    world.app.audio.play(snd, 0.6)


@firer("melee")
def _f_melee(world, inst, pl, p):
    r = p["radius"]
    half = math.radians(p.get("arc", 100)) / 2
    for e in world.query_enemies(pl.x, pl.y, r + 16):
        dx, dy = e.x - pl.x, e.y - pl.y
        ang = math.atan2(dy, dx)
        diff = abs((ang - pl.aim + math.pi) % (2 * math.pi) - math.pi)
        if diff <= half:
            world.damage(e, p["dmg"], kb=p.get("kb", 1.0), dx=dx, dy=dy)
    hx = pl.x + math.cos(pl.aim) * r * 0.6
    hy = pl.y + math.sin(pl.aim) * r * 0.6
    world.particles.add(hx, hy, (218, 226, 240), n=7, speed=(50, 150), life=(0.1, 0.28),
                        angle=pl.aim, spread=80)
    world.app.audio.play("shoot_throw", 0.55)


def _chain_zap(world, pl, dmg, hops, rng, falloff=0.85):
    src = (pl.x, pl.y)
    hit = set()
    cur = dmg
    for _hop in range(int(hops) + 1):
        best, bd = None, rng * rng
        for e in world.enemies:
            if e.dead or id(e) in hit:
                continue
            dx, dy = e.x - src[0], e.y - src[1]
            d2 = dx * dx + dy * dy
            if d2 < bd:
                best, bd = e, d2
        if best is None:
            break
        world.damage(best, cur)
        hit.add(id(best))
        world.zaps.append({"x1": src[0], "y1": src[1], "x2": best.x, "y2": best.y, "t": 0.18, "max": 0.18})
        src = (best.x, best.y)
        cur *= falloff
    world.app.audio.play("chain_zap", 0.7)


@firer("chain")
def _f_chain(world, inst, pl, p):
    _chain_zap(world, pl, p["dmg"], p.get("hops", 3), p.get("hop_range", 95), p.get("falloff", 0.85))


@firer("lob")
def _f_lob(world, inst, pl, p):
    n = int(p.get("count", 1))
    status = dict(_status_from(inst, p))
    if p.get("dot", 0) > 0:
        status["puddle_dot"] = p["dot"]
        status["puddle_t"] = p.get("puddle_t", 3.0)
    for i in range(n):
        tgt = world.nearest_enemy(pl.x, pl.y, 320)
        if tgt is not None:
            tx, ty = tgt.x, tgt.y
        else:
            tx, ty = pl.x + math.cos(pl.aim) * 150, pl.y + math.sin(pl.aim) * 150
        tx = clamp(tx + world.rng.uniform(-14, 14), 20, ARENA_W - 20)
        ty = clamp(ty + world.rng.uniform(-14, 14), 20, ARENA_H - 20)
        dx, dy = tx - pl.x, ty - pl.y
        dist = math.hypot(dx, dy) or 1.0
        spd = p.get("speed", 260)
        world.projs.append(Proj(pl.x, pl.y - 6, dx / dist * 100, dy / dist * 100, p["dmg"], True,
                                p["proj"], r=p.get("aoe", 46), kind="lob", tx=tx, ty=ty,
                                t_air=max(0.28, dist / spd), status=status))
    world.app.audio.play("shoot_heavy", 0.7)


@firer("boomerang")
def _f_boom(world, inst, pl, p):
    n = int(p.get("count", 1))
    spread = math.radians(p.get("spread", 20))
    for i in range(n):
        ang = pl.aim + (i - (n - 1) / 2) * spread
        vx, vy = math.cos(ang) * p["speed"], math.sin(ang) * p["speed"]
        world.projs.append(Proj(pl.x, pl.y - 6, vx, vy, p["dmg"], True, p["proj"], r=7, kind="boom",
                                ox=pl.x, oy=pl.y, range_=p.get("range", 160), life=4.0,
                                kb=p.get("kb", 0.6), spin=12.0))
    world.app.audio.play("shoot_throw", 0.6)


@firer("bounce")
def _f_bounce(world, inst, pl, p):
    n = int(p.get("count", 1))
    spread = math.radians(p.get("spread", 25))
    for i in range(n):
        ang = pl.aim + (i - (n - 1) / 2) * spread
        vx, vy = math.cos(ang) * p["speed"], math.sin(ang) * p["speed"]
        world.projs.append(Proj(pl.x, pl.y - 6, vx, vy, p["dmg"], True, p["proj"], r=5, kind="bounce",
                                bounces=int(p.get("bounces", 3)), life=p.get("life", 2.6),
                                kb=p.get("kb", 0.3), spin=10.0))
    world.app.audio.play("shoot_tack", 0.5)


@firer("aura")
def _f_aura(world, inst, pl, p):
    r = p["radius"]
    for e in world.query_enemies(pl.x, pl.y, r):
        dx, dy = e.x - pl.x, e.y - pl.y
        world.damage(e, p["dmg"], kb=p.get("kb", 0.6), dx=dx, dy=dy)
    world.particles.ring(pl.x, pl.y, K.C["teal_claro"], 12, r, 0.3, 2)
    world.app.audio.play("aura_pulse", 0.65)
    world.cam.add_shake(0.8)


@firer("nova")
def _f_nova(world, inst, pl, p):
    r = p["radius"]
    for e in world.query_enemies(pl.x, pl.y, r):
        dx, dy = e.x - pl.x, e.y - pl.y
        world.damage(e, p["dmg"], kb=p.get("kb", 1.6), dx=dx, dy=dy)
    world.particles.ring(pl.x, pl.y, K.C["ambar_claro"], 10, r, 0.42, 3)
    world.particles.add(pl.x, pl.y, K.C["ambar"], n=16, speed=(60, 220), life=(0.2, 0.5), glow=True)
    world.app.audio.play("nova", 0.8)
    world.cam.add_shake(2.6)


@firer("slam")
def _f_slam(world, inst, pl, p):
    world.slams.append({"x": pl.x, "y": pl.y, "r": p["radius"], "dmg": p["dmg"],
                        "kb": p.get("kb", 2.0), "t": 0.0, "delay": p.get("tarea", 0.35)})
    world.app.audio.play("shoot_heavy", 0.5)


@firer("homing")
def _f_homing(world, inst, pl, p):
    n = int(p.get("count", 1))
    for i in range(n):
        ang = pl.aim + (i - (n - 1) / 2) * 0.5
        vx, vy = math.cos(ang) * p["speed"], math.sin(ang) * p["speed"]
        world.projs.append(Proj(pl.x, pl.y - 6, vx, vy, p["dmg"], True, "pr_missile", r=5,
                                kind="missile", homing=True, life=3.0))
    world.app.audio.play("shoot_marker", 0.5)


@firer("tape")
def _f_tape(world, inst, pl, p):
    n = int(max(1, p.get("count", 1)))
    spread = math.radians(p.get("spread", 10))
    status = _status_from(inst, p)
    for i in range(n):
        ang = pl.aim + (i - (n - 1) / 2) * spread
        vx, vy = math.cos(ang) * p["speed"], math.sin(ang) * p["speed"]
        world.projs.append(Proj(pl.x, pl.y - 6, vx, vy, p["dmg"], True, p["proj"], r=5,
                                pierce=int(p.get("pierce", 0)), life=p.get("life", 0.7),
                                kb=p.get("kb", 0.3), status=status))
    world.app.audio.play("tape_hit" if inst.wid == "cinta" else "shoot_marker", 0.55)


def _beam(world, inst, pl, p, dt):
    length = p["length"]
    width = p.get("width", 3)
    dps = p["dps"]
    tick = p.get("tick", 0.12)
    ang = pl.aim
    ex = pl.x + math.cos(ang) * length
    ey = pl.y + math.sin(ang) * length
    inst.beam_t += dt
    if inst.beam_t >= tick:
        inst.beam_t = 0.0
        mid_x, mid_y = (pl.x + ex) / 2, (pl.y + ey) / 2
        for e in world.query_enemies(mid_x, mid_y, length / 2 + 30):
            t = clamp(((e.x - pl.x) * (ex - pl.x) + (e.y - pl.y) * (ey - pl.y)) / (length * length), 0, 1)
            px = pl.x + (ex - pl.x) * t
            py = pl.y + (ey - pl.y) * t
            if math.hypot(e.x - px, e.y - py) <= e.r + width + 3:
                world.damage(e, dps * tick)
    world.beam_fx = (pl.x, pl.y - 6, ex, ey, world.time)
    if int(world.time * 3) % 2 == 0:
        world.app.audio.play("beam_loop", 0.35)
