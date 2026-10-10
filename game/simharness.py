"""Arnés de simulación: un bot juega noches completas sin render, para balance y QA."""
from __future__ import annotations

import math
import random

import pygame

from . import const as K
from .world import RunWorld


class FakeAppInput:
    def __init__(self):
        self.keys: dict[int, bool] = {}
        self.just: set[int] = set()
        self.mouse = (0, 0)
        self.mouse_down = False
        self.mouse_clicked = False
        self.mouse_released = False
        self.any_key = False
        self.text = ""

    def begin(self):
        self.just = set()
        self.mouse_clicked = False
        self.mouse_released = False
        self.any_key = False
        self.text = ""

    def handle(self, ev):
        pass

    def held(self, key):
        return self.keys.get(key, False)

    def just_pressed(self, key):
        return key in self.just

    def move_vector(self):
        from .core import V
        x = (self.held(pygame.K_d) or self.held(pygame.K_RIGHT)) - (self.held(pygame.K_a) or self.held(pygame.K_LEFT))
        y = (self.held(pygame.K_s) or self.held(pygame.K_DOWN)) - (self.held(pygame.K_w) or self.held(pygame.K_UP))
        v = V(x, y)
        if v.length_squared() > 1:
            v = v.normalize()
        return v


def bot_step(world: RunWorld, inp: FakeAppInput, t: float):
    """Bot que kites: elige la dirección con más espacio libre y recoge cerca."""
    p = world.player
    inp.just = set()
    inp.keys = {}
    best_score = -1e9
    best = (1.0, 0.0)
    for k in range(12):
        a = k * math.tau / 12
        dx, dy = math.cos(a), math.sin(a)
        score = 0.0
        for e in world.enemies:
            ex, ey = e.x - p.x, e.y - p.y
            d2 = ex * ex + ey * ey
            if d2 > 200 * 200 or d2 == 0:
                continue
            d = math.sqrt(d2)
            dot = (ex * dx + ey * dy) / d
            if dot > 0:
                score -= (200 - d) / 200 * (dot ** 2) * 3.0
        # acercarse a pickups solo si no hay penalización grande
        if score > -1.2:
            for it in world.pickups[:60]:
                ix, iy = it.x - p.x, it.y - p.y
                d2 = ix * ix + iy * iy
                if 40 < d2 < 180 * 180:
                    d = math.sqrt(d2)
                    dot = (ix * dx + iy * dy) / d
                    if dot > 0:
                        score += 4.0 / d
        # evitar paredes
        nx, ny = p.x + dx * 90, p.y + dy * 90
        if nx < 40 or nx > K.ARENA_W - 40 or ny < 40 or ny > K.ARENA_H - 40:
            score -= 1.5
        if score > best_score:
            best_score = score
            best = (dx, dy)
    mx, my = best
    if mx > 0.35:
        inp.keys[pygame.K_d] = True
    if mx < -0.35:
        inp.keys[pygame.K_a] = True
    if my > 0.35:
        inp.keys[pygame.K_s] = True
    if my < -0.35:
        inp.keys[pygame.K_w] = True
    near = world.nearest_enemy(p.x, p.y, 185)
    # fogonazo si hay mucha densidad alrededor
    if p.abl_cd <= 0 and len(world.query_enemies(p.x, p.y, 95)) >= 4:
        inp.just.add(pygame.K_SPACE)
    # dash si está muy cerca
    if near is not None:
        d = math.hypot(p.x - near.x, p.y - near.y)
        if d < 60 and p.dash_cd <= 0:
            inp.keys[pygame.K_LSHIFT] = True


def auto_shop(world: RunWorld):
    """Compra lo que pueda (prioriza armas y fusiona) y sigue."""
    for i, off in enumerate(world.shop):
        if not off["sold"] and off["price"] <= int(world.coins):
            world.shop_buy(i)
    # fusionar pares disponibles
    pairs = world.merge_pairs()
    if pairs:
        i, j = pairs[0]
        world.shop_merge(i, j)
    # sacudir la máquina si va sobrado
    if world.coins > 34 and world.reroll_cost() <= world.coins:
        world.shop_reroll()
        for i, off in enumerate(world.shop):
            if not off["sold"] and off["price"] <= int(world.coins):
                world.shop_buy(i)
    if world.player.hp < world.player.max_hp * 0.5:
        world.shop_heal()
    world.leave_shop()


def auto_levelup(world: RunWorld):
    cards = world.roll_levelup_cards()
    if cards:
        world.apply_levelup(cards[0])
    else:
        world.pending_levels = 0
        if world.phase == "levelup":
            world.phase = "active"


def fast_run(app, char_id="lia", guardia=1, mut_ids=None, seed=1, max_time=1500.0, dt=1 / 60,
             bot=True, max_steps=None):
    """Simula una noche entera. Devuelve un resumen dict."""
    world = RunWorld(app, char_id, guardia, mut_ids or [], seed=seed)
    inp = FakeAppInput()
    app.input = inp
    steps = int(max_time / dt)
    if max_steps:
        steps = min(steps, max_steps)
    events_log = []
    for i in range(steps):
        t = i * dt
        if world.phase in ("dead", "victory"):
            break
        if bot and world.phase == "active":
            bot_step(world, inp, t)
        world.update(dt)
        if world.phase == "levelup":
            auto_levelup(world)
        elif world.phase == "shop":
            auto_shop(world)
    return {
        "char": char_id, "guardia": guardia, "muts": list(mut_ids or []), "seed": seed,
        "phase": world.phase, "wave": world.wave, "best_wave": world.rs["best_wave"],
        "kills": world.kills, "level": world.level, "time": round(world.time, 1),
        "coins": int(world.coins), "hp_frac": round(world.player.hp / world.player.max_hp, 2),
        "enemies_left": len(world.enemies), "victory": world.phase == "victory",
        "endless": world.rs.get("endless", 0), "merges": world.rs.get("merges", 0),
        "rerolls": world.rs.get("rerolls", 0), "combo": world.rs.get("best_combo", 0),
        "weapons": [f"{w.wid}:{w.level}" for w in world.player.weapons],
        "items": len(world.player.items),
        "chispas": world.chispas_earned(world.phase == "victory"),
    }
