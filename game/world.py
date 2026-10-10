"""RunWorld: simulación completa de una noche.

Fases: intro → active ↔ (levelup) → shop → active … → boss_intro → … → dead/victory.
"""
from __future__ import annotations

import math
import random

import pygame

from . import const as K
from . import sprites as S
from .core import ARENA_H, ARENA_W, Camera, Hash, Particles, Texts, clamp
from .entities import Enemy, Pickup, Player, Prop, Proj, Puddle, WeaponInst, make_boss, make_enemy
from .content import ach, chars as CC, enemies as CE, items as CI, metaup
from .content import mutators as CM, perks as CP, strings as ST, waves
from .content import weapons as CW

ENEMY_CAP = 230
PICKUP_CAP = 320


class RunWorld:
    def __init__(self, app, char_id: str, guardia: int, mut_ids: list[str], seed: int | None = None):
        self.app = app
        self.save = app.save
        self.settings = app.settings
        self.rng = random.Random(seed)
        self.char = CC.BY_ID[char_id]
        self.char_id = char_id
        self.guardia = int(guardia)
        self.mut_ids = list(mut_ids)
        self.mods = CM.aggregate(self.mut_ids)
        self.assist = bool(self.settings["assist"])

        # --- carga y estadísticas
        self.meta_adds, self.meta_special = metaup.aggregate_ranks(self.save.data["ranks"])
        weapons = [WeaponInst(w) for w in self.char["weapons"]]
        for _ in range(int(self.meta_special.get("start_weapon", 0))):
            weapons.append(WeaponInst(self.rng.choice(CW.STARTING_WEAPONS)))
        self.stats = self._compute_stats()
        self.player = Player(self.char, self.stats, weapons)
        self.player.revives = int(self.meta_special.get("revive", 0))
        self.player.x, self.player.y = ARENA_W / 2.0, ARENA_H / 2.0

        # --- mundo
        self.enemies: list[Enemy] = []
        self.projs: list[Proj] = []
        self.pickups: list[Pickup] = []
        self.props: list[Prop] = []
        self.puddles: list[Puddle] = []
        self.zaps: list[dict] = []
        self.slams: list[dict] = []
        self.beam_fx = None
        self.particles = Particles()
        self.texts = Texts()
        self.cam = Camera()
        self.cam.follow(self.player.x, self.player.y, snap=True)
        self.hash = Hash(44)
        self.floor = S.bake_floor(self.rng.randrange(1000))
        self._make_props()

        # --- estado del run
        self.time = 0.0
        self.wave = 1
        self.wave_t = 0.0
        self.wave_total = waves.wave_len(1, self.mods)
        self.phase = "intro"
        self.intro_t = 2.1
        self.coins = 0.0
        self.xp = 0.0
        self.level = 1
        self.xp_next = float((self.level + 3) ** 2)
        self.pending_levels = 0
        self.kills = 0
        self.boss: Enemy | None = None
        self.boss_def: dict | None = None
        self.shop: list[dict] = []
        self.rerolls = 0
        self.extra_rerolls = int(self.meta_special.get("extra_reroll", 0))
        self.shop_slots = 4 + int(self.meta_special.get("shop_slot", 0))
        self.discount = float(self.meta_special.get("discount", 0.0))
        self.spawn_acc = 0.0
        self.surge_left = 0.0
        self.surge_done = False
        self.incident_t = self.rng.uniform(35, 55)
        self.dark_bonus = 0.0
        self.dark_bonus_t = 0.0
        self.reveal_t = 0.0
        self.endless = False
        self.events: list[dict] = []
        self.rs: dict = {
            "best_wave": 1, "best_combo": 0, "kills": 0, "crits": 0, "dashes": 0, "fogonazos": 0,
            "crates": 0, "coins": 0, "merges": 0, "rerolls": 0, "heals_bought": 0, "levelups": 0,
            "dark_kills": 0, "lit_kills": 0, "endless": 0, "time": 0.0, "heal_used": 0,
        }
        self._ach_t = 0.0
        self.banner(waves.wave_intro(1))
        self.notify("ESPACIO: Fogonazo · SHIFT: Dash")
        self.particles.add(self.player.x, self.player.y, K.C["ambar"], n=10, speed=(10, 60), life=(0.4, 0.9), glow=True)

    # ================================================================ stats
    def _compute_stats(self) -> dict:
        stats = dict(K.BASE)
        for k, v in self.char.get("add", {}).items():
            stats[k] = stats.get(k, 0) + v
        for k, m in self.char.get("mult", {}).items():
            stats[k] = stats.get(k, 1) * m
        for k, v in self.meta_adds.items():
            stats[k] = stats.get(k, 0) + v
        for iid in getattr(self, "player", None).items if getattr(self, "player", None) else []:
            for k, v in CI.BY_ID[iid]["stats"].items():
                stats[k] = stats.get(k, 0) + v
        if getattr(self, "player", None):
            for pid, count in self.player.perks.items():
                for k, v in CP.BY_ID[pid].get("stats", {}).items():
                    stats[k] = stats.get(k, 0) + v * count
        stats["dodge"] = min(0.6, stats["dodge"])
        stats["crit"] = min(0.9, stats["crit"])
        stats["atk_speed"] = max(0.25, stats["atk_speed"])
        stats["speed"] = max(50.0, stats["speed"])
        stats["hp"] = max(20.0, stats["hp"])
        return stats

    def recompute(self):
        p = self.player
        old_max = p.max_hp
        self.stats = self._compute_stats()
        p.stats = self.stats
        p.max_hp = self.stats["hp"]
        if p.max_hp > old_max:
            p.hp += p.max_hp - old_max
        p.hp = min(p.hp, p.max_hp)

    def _rebuild_wmods(self):
        p = self.player
        p.wmods = {}
        for pid, count in p.perks.items():
            wmod = CP.BY_ID[pid].get("wmod")
            if not wmod:
                continue
            wid = wmod["weapon"]
            slot = p.wmods.setdefault(wid, {"dmg": 0.0, "cd": 0.0, "dot": 0.0, "param": {}, "param_pct": {}})
            slot["dmg"] += wmod.get("dmg", 0.0) * count
            slot["cd"] += wmod.get("cd", 0.0) * count
            slot["dot"] += wmod.get("dot", 0.0) * count
            for k, v in wmod.get("param", {}).items():
                slot["param"][k] = slot["param"].get(k, 0) + v * count
            for k, v in wmod.get("param_pct", {}).items():
                slot["param_pct"][k] = slot["param_pct"].get(k, 0) + v * count

    # ================================================================ utilidades
    def notify(self, text: str, kind="msg"):
        self.events.append({"type": kind, "text": text})

    def banner(self, text: str):
        self.events.append({"type": "banner", "text": text})

    def toast(self, text: str, kind="info"):
        self.events.append({"type": "toast", "text": text, "kind": kind})

    def light_radius(self) -> float:
        base = self.stats["light"]
        drain = 1.0 - min(0.6, 0.22 * self.player.drains)
        r = base * drain
        if self.reveal_t > 0:
            r *= 1.55
        return r

    def in_light(self, x: float, y: float) -> bool:
        r = self.light_radius()
        dx, dy = x - self.player.x, y - self.player.y
        return dx * dx + dy * dy <= r * r

    def depht_enemies(self):  # compat
        return self.enemies

    def nearest_enemy(self, x: float, y: float, max_r: float = 1e9):
        best, bd = None, max_r * max_r
        for e in self.enemies:
            if e.dead:
                continue
            dx, dy = e.x - x, e.y - y
            d2 = dx * dx + dy * dy
            if d2 < bd:
                best, bd = e, d2
        return best

    def query_enemies(self, x, y, r):
        r2 = r * r
        out = []
        for e in self.hash.query(x, y, r):
            if e.dead:
                continue
            dx, dy = e.x - x, e.y - y
            if dx * dx + dy * dy <= r2:
                out.append(e)
        return out

    # ================================================================ props
    def _make_props(self):
        rng = self.rng
        spots = [
            ("desk", 8), ("chair", 6), ("plant", 5), ("cooler", 2), ("cabinet", 6), ("box", 10), ("lamp", 6),
        ]
        for kind, n in spots:
            for _ in range(n):
                x = rng.uniform(50, ARENA_W - 50)
                y = rng.uniform(50, ARENA_H - 50)
                if math.hypot(x - ARENA_W / 2, y - ARENA_H / 2) < 130:
                    x += 160
                if kind == "box":
                    p = Prop("box", x, y, r=9, solid=False, hp=3)
                elif kind in ("plant", "lamp"):
                    p = Prop(kind, x, y, r=7, solid=False)
                else:
                    p = Prop(kind, x, y, r=16 if kind == "desk" else 13, solid=True)
                self.props.append(p)

    # ================================================================ ciclo
    def update(self, dt):
        if dt <= 0:
            return
        self.time += dt
        self.particles.update(dt)
        self.texts.update(dt)
        self.cam.update(dt)
        for z in self.zaps:
            z["t"] -= dt
        self.zaps = [z for z in self.zaps if z["t"] > 0]

        if self.phase == "intro":
            self.intro_t -= dt
            if self.intro_t <= 0:
                self.phase = "active"
        elif self.phase == "active":
            self._update_active(dt)
        elif self.phase in ("shop", "levelup", "boss_intro", "dead", "victory"):
            if self.phase == "boss_intro":
                self.intro_t -= dt
                if self.intro_t <= 0:
                    self._spawn_boss()

    def _update_active(self, dt):
        p = self.player
        self.rs["time"] = self.time

        # --- temporizadores globales
        if self.reveal_t > 0:
            self.reveal_t -= dt
        if self.dark_bonus_t > 0:
            self.dark_bonus_t -= dt
            if self.dark_bonus_t <= 0:
                self.dark_bonus = 0.0

        # --- oleada
        self.wave_t += dt
        boss_hora = waves.is_boss_hora(self.wave)
        if not boss_hora and self.wave_t >= self.wave_total:
            self._end_wave()
            return
        if boss_hora and self.boss is not None and self.wave_t >= self.wave_total:
            # el jefe se retira si no lo has matado a tiempo (estilo Brotato)
            b = self.boss
            self.particles.add(b.x, b.y, K.C["morado"], n=24, speed=(40, 160), life=(0.3, 0.8), glow=True)
            if b in self.enemies:
                self.enemies.remove(b)
            b.dead = True
            self.boss = None
            self.banner("El jefe se retira a su despacho… por ahora.")
            self.app.audio.play("boss_die", 0.5)
            self._end_wave()
            return
        if boss_hora and self.boss is not None and self.wave_t > 75 and not self.boss.hit_seen.get("enraged"):
            self.boss.hit_seen["enraged"] = 1
            self.boss.spd *= 1.4
            self.banner("¡EL JEFE SE IMPACIENTA!")
        if not self.surge_done and self.wave_t > self.wave_total * 0.62:
            self.surge_done = True
            self.surge_left = 4.0
            self.banner("¡AVALANCHA!")
            self.app.audio.play("boss_spawn", 0.5)
        if self.surge_left > 0:
            self.surge_left -= dt

        # --- spawn
        rate = waves.spawn_rate(self.wave, self.mods)
        if self.surge_left > 0:
            rate *= 3.2
        self.spawn_acc += rate * dt
        while self.spawn_acc >= 1.0:
            self.spawn_acc -= 1.0
            if len(self.enemies) < ENEMY_CAP:
                self._spawn_random()

        self._update_incidents(dt)
        self._update_player(dt)
        for inst in p.weapons:
            self._update_weapon(inst, dt)
        self._update_slams(dt)
        self._kick_boxes()
        self._update_enemies(dt)
        if self.boss is not None:
            self._update_boss(self.boss, dt)
        self._update_projs(dt)
        self._update_pickups(dt)
        self._update_puddles(dt)

        # --- logros cada pocos segundos
        self._ach_t += dt
        if self._ach_t > 3.0:
            self._ach_t = 0.0
            self._check_achievements()

        # --- subida de nivel pendiente
        if self.pending_levels > 0 and self.phase == "active":
            self.phase = "levelup"
            self.events.append({"type": "levelup"})

    # ================================================================ incidencias / oleadas
    def _update_incidents(self, dt):
        self.incident_t -= dt
        if self.incident_t > 0:
            return
        self.incident_t = self.rng.uniform(38, 62)
        p = self.player
        choices = ["flicker", "surge", "coffee"]
        if self.wave >= 6:
            choices.append("boss_call")
        kind = self.rng.choice(choices)
        if kind == "flicker":
            self.dark_bonus = 55.0
            self.dark_bonus_t = 5.0
            self.banner(ST.VARITA["flicker"])
            self.app.audio.play("ui_deny", 0.4)
        elif kind == "surge":
            for e in self.enemies:
                e.spd *= 1.25
            self.banner(ST.VARITA["surge"])
        elif kind == "coffee":
            self.notify(ST.VARITA["coffee"])
            for _ in range(3):
                self.spawn_drop(p.x + self.rng.uniform(-40, 40), p.y + self.rng.uniform(-40, 40), "heal", 4)
            for _ in range(6):
                self.spawn_drop(p.x + self.rng.uniform(-60, 60), p.y + self.rng.uniform(-60, 60), "coin", 1)
        elif kind == "boss_call":
            self.notify(ST.VARITA["boss_call"])
            for _ in range(2):
                self._spawn_at(self.rng.choice(["clip", "raton", "pila"]),
                               p.x + self.rng.uniform(-260, 260), p.y + self.rng.uniform(-260, 260), elite=True)

    def _end_wave(self):
        bonus = waves.wave_bonus_coins(self.wave)
        self.coins += bonus * self.stats["coin_gain"] * (1 + self.mods.get("coin_gain", 0))
        self.rs["coins"] = int(self.coins)
        self.rs["best_wave"] = max(self.rs["best_wave"], self.wave)
        self._check_achievements()
        self._open_shop()

    def next_wave(self):
        self.wave += 1
        if self.wave > K.HORAS_NOCHE:
            if not self.endless:
                self.endless = True
            self.rs["endless"] = max(self.rs.get("endless", 0), self.wave - K.HORAS_NOCHE)
        self.rs["best_wave"] = max(self.rs["best_wave"], self.wave)
        self.wave_t = 0.0
        self.wave_total = waves.wave_len(self.wave, self.mods)
        self.surge_done = False
        self.spawn_acc = 0.0
        if waves.is_boss_hora(self.wave) and (self.boss is None):
            self.boss_def = CE.boss_by_hora(self.wave)
            self.phase = "boss_intro"
            self.intro_t = 2.4
            self.events.append({"type": "boss_intro", "name": self.boss_def["name"], "line": self.boss_def["intro"]})
            self.app.audio.play("boss_spawn")
            self.app.audio.duck(0.4, 2.0)
        else:
            self.phase = "active"
            self._pending_intro_msg()

    def _pending_intro_msg(self):
        if self.wave > K.HORAS_NOCHE:
            self.banner(f"HORA EXTRA {self.wave - K.HORAS_NOCHE}")
        elif self.wave in waves.WAVE_INTROS:
            self.banner(waves.wave_intro(self.wave))

    def _spawn_boss(self):
        b = self.boss_def
        p = self.player
        x = ARENA_W / 2 + self.rng.uniform(-200, 200)
        y = max(60.0, p.y - 300)
        e = make_boss(b, x, y, 1.0, 1.0)
        scaled = waves.boss_scaled(b, self.wave, self.guardia, self.mods, self.assist)
        e.hp = e.max_hp = scaled["hp"]
        e.dmg = scaled["dmg"]
        e.pat_cd = 2.5
        self.boss = e
        self.enemies.append(e)
        self.save.see_enemy(b["id"])
        self.phase = "active"
        self.cam.add_shake(3)
        self.particles.add(x, y, K.C["morado_claro"], n=22, speed=(40, 180), life=(0.3, 0.8), glow=True)

    def _boss_died(self):
        b = self.boss
        self.boss = None
        self.rs[f"boss_{b.defn['id']}"] = 1
        self.save.slay_boss(b.defn["id"])
        self.toast(f"JEFE DERROTADO: {b.defn['name']}", "boss")
        self.app.audio.play("boss_die")
        self.app.audio.duck(0.4, 2.0)
        self.cam.add_shake(8)
        for _ in range(26):
            self.spawn_drop(b.x + self.rng.uniform(-30, 30), b.y + self.rng.uniform(-30, 30),
                            "coin", self.rng.randint(1, 3))
        for _ in range(8):
            self.spawn_drop(b.x + self.rng.uniform(-30, 30), b.y + self.rng.uniform(-30, 30), "heal", 5)
        self.particles.add(b.x, b.y, K.C["ambar"], n=40, speed=(40, 220), life=(0.4, 1.1), glow=True, size=(2, 4))
        self.particles.add(b.x, b.y, K.C["rojo"], n=26, speed=(30, 160), life=(0.4, 1.0), size=(1, 3))
        if self.wave >= K.HORAS_NOCHE and b.defn["id"] == "olvido" and not self.endless:
            self._finish(victory=True)
            return
        self._check_achievements()
        self._end_wave()

    # ================================================================ jugador
    def _update_player(self, dt):
        p = self.player
        inp = self.app.input
        move = inp.move_vector()
        if move.length_squared() > 0:
            p.facing = move.x < 0
            p.walk_t += dt
            p.mvx, p.mvy = move.x, move.y
        aim_e = self.nearest_enemy(p.x, p.y)
        if aim_e is not None:
            p.aim = math.atan2(aim_e.y - p.y, aim_e.x - p.x)

        # dash
        p.dash_cd = max(0.0, p.dash_cd - dt)
        p.rafaga_cd = max(0.0, p.rafaga_cd - dt)
        if p.dash_t > 0:
            p.dash_t -= dt
            p.x += p.dash_vx * dt
            p.y += p.dash_vy * dt
            self.particles.add(p.x, p.y, K.C["teal_claro"], n=1, speed=(4, 20), life=(0.15, 0.3), glow=True)
        else:
            spd = self.stats["speed"] * p.buff_mult
            p.x += move.x * spd * dt
            p.y += move.y * spd * dt
        if inp.held(pygame.K_LSHIFT) or inp.held(pygame.K_RSHIFT):
            if p.dash_cd <= 0 and p.iframe <= 0 and move.length_squared() > 0:
                self._do_dash(move)
        # fogonazo
        p.abl_cd = max(0.0, p.abl_cd - dt)
        if inp.just_pressed(pygame.K_SPACE) and p.abl_cd <= 0:
            self._do_fogonazo()
        # timers
        p.iframe = max(0.0, p.iframe - dt)
        p.hurt_flash = max(0.0, p.hurt_flash - dt)
        if p.buff_t > 0:
            p.buff_t -= dt
            if p.buff_t <= 0:
                p.buff_mult = 1.0
        if p.combo_t > 0:
            p.combo_t -= dt
            if p.combo_t <= 0:
                p.combo = 0
        if self.stats["regen"] > 0 and p.hp < p.max_hp:
            p.hp = min(p.max_hp, p.hp + self.stats["regen"] * dt)
        # límites arena
        m = 12
        p.x = clamp(p.x, m, ARENA_W - m)
        p.y = clamp(p.y, m, ARENA_H - m)
        self.cam.follow(p.x, p.y)

    def _do_dash(self, move):
        p = self.player
        v = move.normalize()
        p.dash_vx, p.dash_vy = v.x * 540, v.y * 540
        p.dash_t = 0.15
        p.iframe = max(p.iframe, 0.34)
        perk = self.char["perk"]
        mult = 0.5 if perk == "doble_clic" else 1.0
        p.dash_cd = 1.0 * mult
        self.rs["dashes"] += 1
        self.app.audio.play("player_dash", 0.7)
        self.particles.add(p.x, p.y, K.C["teal_claro"], n=6, speed=(30, 90), life=(0.15, 0.35),
                           angle=math.atan2(-v.y, -v.x), spread=60, glow=True)

    def _do_fogonazo(self):
        p = self.player
        r = self.light_radius() * 1.9
        dmg = 26 + 2.2 * self.wave
        hits = self.query_enemies(p.x, p.y, r)
        for e in hits:
            self.damage(e, dmg, crit_ok=False, status={"stun": 1.6}, kb=90)
        self.reveal_t = 1.3
        p.abl_cd = max(3.5, 14.0 * (1 + self.stats["abl_cd"]))
        self.rs["fogonazos"] += 1
        self.app.audio.play("fogonazo")
        self.cam.add_shake(4)
        self.particles.ring(p.x, p.y, K.C["ambar_claro"], r0=10, r1=r, life=0.4, width=3)
        self.particles.add(p.x, p.y, K.C["ambar"], n=22, speed=(60, 260), life=(0.25, 0.6), glow=True, size=(1, 3))
        self.app.freeze = max(self.app.freeze, 0.06)

    # ================================================================ daño
    def damage(self, e: Enemy, base: float, crit_ok=True, status: dict | None = None, kb=0.0,
               dx=0.0, dy=0.0) -> tuple[float, bool]:
        if e.dead:
            return 0.0, False
        lit = self.in_light(e.x, e.y)
        mult = 1.0 if lit else K.LIGHT_DMG_DARK
        crit = crit_ok and self.rng.random() < self.stats["crit"]
        dmg = base * mult * self.stats["dmg"]
        if crit:
            dmg *= self.stats["crit_dmg"]
            self.rs["crits"] += 1
            if self.char["perk"] == "perforado":
                st = e.st.setdefault("bleed", [0.0, 0.0])
                st[0] = max(st[0], 2.0)
                st[1] = max(st[1], 5.0)
        if status:
            for k, v in status.items():
                if k in ("burn", "poison", "bleed"):
                    st = e.st.setdefault(k, [0.0, 0.0])
                    st[0] = max(st[0], 2.0)
                    st[1] = max(st[1], float(v))
                elif k == "slow":
                    pct, dur = v
                    st = e.st.setdefault("slow", [0.0, 0.0])
                    st[0] = max(st[0], float(dur))
                    st[1] = max(st[1], float(pct))
                elif k == "stun":
                    st = e.st.setdefault("stun", [0.0, 0.0])
                    st[0] = max(st[0], float(v))
        if self.char["perk"] == "quemadura" and status is None and crit_ok:
            st = e.st.setdefault("burn", [0.0, 0.0])
            st[0] = max(st[0], 2.5)
            st[1] = max(st[1], 4.0)
        e.hp -= dmg
        e.flash_t = 0.09
        if kb:
            kbv = kb * self.stats["kb"] * (1 - e.kb_r)
            l = math.hypot(dx, dy) or 1.0
            e.x += dx / l * kbv * 0.6
            e.y += dy / l * kbv * 0.6
            e.vx += dx / l * kbv * 2
            e.vy += dy / l * kbv * 2
        col = K.C["ambar"] if crit else K.C["crema"]
        if not lit:
            col = K.C["gris"]
        self.texts.add(e.x, e.y - e.r - 4, str(int(dmg)), col, size=10 if crit else 9, crit=crit)
        leech = self.stats["lifesteal"]
        if leech > 0:
            p = self.player
            p.life_steal_acc += dmg * leech
            if p.life_steal_acc >= 1.0:
                heal = int(p.life_steal_acc)
                p.life_steal_acc -= heal
                p.hp = min(p.max_hp, p.hp + heal)
        if e.hp <= 0:
            self._kill_enemy(e, lit)
        return dmg, crit

    def _kill_enemy(self, e: Enemy, lit=True):
        e.dead = True
        self.kills += 1
        self.rs["kills"] += 1
        if lit:
            self.rs["lit_kills"] += 1
        else:
            self.rs["dark_kills"] += 1
        p = self.player
        p.combo += 1
        p.combo_t = 3.0
        self.rs["best_combo"] = max(self.rs["best_combo"], p.combo)
        self.app.audio.play("enemy_die_big" if (e.elite or e.boss) else "enemy_die")
        # fx de muerte
        sp = S.get(e.defn["sprite"])
        self.particles.add(e.x, e.y, K.C["crema"], n=6, speed=(20, 90), life=(0.2, 0.5), size=(1, 2))
        if not e.boss:
            self.particles.add(e.x, e.y - 5, K.C["crema"], n=1, speed=(0, 10), life=(0.5, 0.7), image=sp.small)
        xp_val = max(1, int(e.xp))
        self.spawn_drop(e.x, e.y, "xp", xp_val)
        coin = e.coin
        n_coins = 1 + int(coin > 1.5) + int(coin > 3.0)
        for i in range(n_coins):
            if self.rng.random() < min(1.0, coin / max(1, n_coins)):
                self.spawn_drop(e.x, e.y, "coin", 1 + int(coin > 2.5))
        if self.rng.random() < 0.034:
            self.spawn_drop(e.x, e.y, "heal", 6)
        # perk cafeína
        if self.char["perk"] == "cafeina" and self.rng.random() < 0.15:
            p.buff_mult = 1.2
            p.buff_t = 2.5
            self.texts.add(p.x, p.y - 20, "¡CAFEÍNA!", K.C["ambar_claro"], size=10)
        # habilidades al morir
        kind = e.defn.get("kind")
        if kind == "poison":
            self.puddle_add(e.x, e.y, e.defn.get("cloud_r", 40), e.defn.get("cloud_dot", 6), 0.0,
                            e.defn.get("cloud_t", 3.0), friendly=False)
        if e.elite:
            for _ in range(4):
                self.spawn_drop(e.x + self.rng.uniform(-14, 14), e.y + self.rng.uniform(-14, 14), "coin", 2)
        if e.boss:
            self._boss_died()

    def player_hurt(self, dmg, src_e: Enemy | None = None):
        p = self.player
        if p.iframe > 0 or not p.alive or self.phase in ("dead", "victory"):
            return
        if self.rng.random() < self.stats["dodge"]:
            self.texts.add(p.x, p.y - 22, "¡esquiva!", K.C["teal_claro"], size=9)
            p.iframe = 0.2
            return
        dr = self.stats["armor"] / (self.stats["armor"] + 15.0)
        dmg *= (1.0 - dr)
        p.hp -= dmg
        p.iframe = 0.55
        p.hurt_flash = 0.25
        # empujón de escape: te separa del enemigo que te golpeó
        if src_e is not None:
            dx, dy = p.x - src_e.x, p.y - src_e.y
            d = math.hypot(dx, dy) or 1.0
            p.x = clamp(p.x + dx / d * 7, 12, ARENA_W - 12)
            p.y = clamp(p.y + dy / d * 7, 12, ARENA_H - 12)
        self.cam.add_shake(3.4)
        self.app.freeze = max(self.app.freeze, 0.045)
        self.app.audio.play("player_hurt")
        self.particles.add(p.x, p.y, K.C["rojo_claro"], n=10, speed=(40, 140), life=(0.2, 0.5))
        if src_e is not None and self.stats["thorn"] > 0:
            self.damage_silent(src_e, self.stats["thorn"], lit_ok=True)
        if self.char["perk"] == "rafaga" and src_e is not None:
            if getattr(p, "rafaga_cd", 0) <= 0:
                p.rafaga_cd = 4.0
                for e in self.query_enemies(p.x, p.y, 120):
                    self.damage(e, 8, crit_ok=False, kb=140, dx=e.x - p.x, dy=e.y - p.y)
                self.particles.ring(p.x, p.y, K.C["teal_claro"], 8, 120, 0.35, 2)
        if p.hp <= 0:
            if p.revives > 0:
                p.revives -= 1
                p.hp = p.max_hp * 0.5
                p.iframe = 2.0
                self.reveal_t = 2.0
                self.banner("¡FUSIBLE DE REPUESTO! Sigues encendida.")
                self.app.audio.play("levelup")
                return
            p.alive = False
            self._finish(victory=False)

    def damage_silent(self, e: Enemy, dmg, lit_ok=False):
        if e.dead:
            return
        mult = 1.0 if (not lit_ok or self.in_light(e.x, e.y)) else K.LIGHT_DMG_DARK
        e.hp -= dmg * mult
        e.flash_t = 0.07
        if e.hp <= 0:
            self._kill_enemy(e, lit=lit_ok and self.in_light(e.x, e.y))

    def heal_player(self, amount):
        p = self.player
        p.hp = min(p.max_hp, p.hp + amount)
        self.texts.add(p.x, p.y - 24, f"+{int(amount)}", K.C["verde_claro"], size=10)

    # ================================================================ drops
    def spawn_drop(self, x, y, kind, value):
        if len(self.pickups) >= PICKUP_CAP:
            # fusionar con el más cercano
            if self.pickups:
                q = min(self.pickups, key=lambda it: (it.x - x) ** 2 + (it.y - y) ** 2)
                if q.kind == kind:
                    q.value += value
                    return
                q.life = max(q.life, 8)
            return
        self.pickups.append(Pickup(kind, value, x, y))

    def _update_pickups(self, dt):
        p = self.player
        pr = self.stats["pickup"]
        pr2 = pr * pr
        alive = []
        for it in self.pickups:
            it.life -= dt
            if it.life <= 0:
                continue
            dx, dy = p.x - it.x, p.y - it.y
            d2 = dx * dx + dy * dy
            if d2 < pr2:
                it.magnet = True
            if it.magnet:
                d = math.sqrt(d2) or 1.0
                pull = 620.0
                it.vx += dx / d * pull * dt
                it.vy += dy / d * pull * dt
            it.x += it.vx * dt
            it.y += it.vy * dt
            it.vx *= 0.92 ** (dt * 60)
            it.vy *= 0.92 ** (dt * 60)
            if d2 < 225:
                self._collect(it)
                continue
            alive.append(it)
        self.pickups = alive

    def _collect(self, it: Pickup):
        if it.kind == "xp":
            val = it.value * self.stats["xp_gain"] * (1 + self.mods.get("xp_gain", 0))
            self._add_xp(val)
            self.app.audio.play_xp(self.player.combo)
        elif it.kind == "coin":
            val = it.value * self.stats["coin_gain"] * (1 + self.mods.get("coin_gain", 0))
            self.coins += val
            self.rs["coins"] = int(self.coins)
            self.app.audio.play("pickup_coin", 0.8)
        elif it.kind == "heal":
            self.heal_player(it.value)
            self.app.audio.play("pickup_heal")

    def _add_xp(self, val):
        self.xp += val
        while self.xp >= self.xp_next:
            self.xp -= self.xp_next
            self.level += 1
            self.xp_next = float(int((self.level + 2.6) ** 2))
            self.pending_levels += 1
            self.rs["levelups"] += 1
            self.app.audio.play("levelup")
            self.particles.ring(self.player.x, self.player.y, K.C["teal_claro"], 6, 60, 0.3)

    def apply_levelup(self, card: dict):
        p = self.player
        p.perks[card["id"]] = p.perks.get(card["id"], 0) + 1
        self._rebuild_wmods()
        self.recompute()
        self.pending_levels -= 1
        self.toast(f"MEJORA: {card['name']}", "perk")
        if self.pending_levels <= 0:
            self.phase = "active"

    # ================================================================ enemigos
    def _spawn_random(self):
        comp = waves.composition(self.wave, self.rng, self.mods)
        if not comp:
            return
        eid = self.rng.choice(comp)
        r = 360 + self.rng.uniform(0, 90)
        p = self.player
        if abs(p.mvx) + abs(p.mvy) > 0.1:
            # sesgo trasero: aparecen sobre todo por detrás y los flancos del movimiento
            base = math.atan2(-p.mvy, -p.mvx)
            ang = base + self.rng.uniform(-1.85, 1.85)
        else:
            ang = self.rng.uniform(0, math.tau)
        x = clamp(p.x + math.cos(ang) * r, 20, ARENA_W - 20)
        y = clamp(p.y + math.sin(ang) * r, 20, ARENA_H - 20)
        elite = self.rng.random() < waves.elite_chance(self.wave, self.stats["luck"])
        self._spawn_at(eid, x, y, elite=elite)

    def _spawn_at(self, eid, x, y, elite=False):
        hp_m = waves.hp_scale(self.wave, self.guardia, self.mods, self.assist)
        dmg_m = waves.dmg_scale(self.wave, self.guardia, self.mods)
        spd_m = waves.spd_scale(self.mods)
        d = CE.BY_ID[eid]
        if d.get("always_elite"):
            elite = True
        e = make_enemy(eid, x, y, hp_m, dmg_m, spd_m, elite=elite)
        self.enemies.append(e)
        self.particles.add(x, y, K.C["morado_claro"], n=5, speed=(10, 50), life=(0.2, 0.5))
        self.save.see_enemy(eid)

    def _update_enemies(self, dt):
        p = self.player
        prev = self.hash
        prev.clear()
        prev.insert_all(self.enemies)
        drains = 0.0
        for e in self.enemies:
            if e.dead:
                continue
            e.flash_t = max(0.0, e.flash_t - dt)
            self._tick_enemy_status(e, dt)
            if e.st.get("stun"):
                st = e.st["stun"]
                st[0] -= dt
                if st[0] <= 0:
                    e.st.pop("stun", None)
                continue
            d = e.defn
            dx, dy = p.x - e.x, p.y - e.y
            dist = math.hypot(dx, dy) or 1.0
            ux, uy = dx / dist, dy / dist
            spd = e.spd
            slow = e.st.get("slow")
            if slow and slow[0] > 0:
                spd *= (1 - slow[1] * 0.8)
            kind = d.get("kind", "chase")
            if kind == "wanderdark":
                lit = self.in_light(e.x, e.y)
                spd *= d.get("lit_spd", 0.5) if lit else d.get("dark_spd", 1.3)
                e.dmg = d["dmg"] * (waves.dmg_scale(self.wave, self.guardia, self.mods)) * (
                    d.get("dark_dmg", 1.0) if not lit else 1.0)
            if kind == "zigzag":
                e.zig_t += dt
                perp_x, perp_y = -uy, ux
                osc = math.sin(e.zig_t * d.get("zig_f", 6.0)) * d.get("zig", 150)
                vx = ux * spd + perp_x * osc
                vy = uy * spd + perp_y * osc
                e.x += vx * dt
                e.y += vy * dt
            elif kind == "shooter":
                if dist > d.get("shoot_range", 250) * 0.8:
                    e.x += ux * spd * dt
                    e.y += uy * spd * dt
                elif dist < 150:
                    e.x -= ux * spd * 0.7 * dt
                    e.y -= uy * spd * 0.7 * dt
                e.shoot_t -= dt
                if e.shoot_t <= 0 and dist < d.get("shoot_range", 250):
                    e.shoot_t = d.get("shoot_cd", 2.0) * self.rng.uniform(0.85, 1.2)
                    self._enemy_shoot(e, ux, uy, d.get("proj", "pr_staple"), d.get("proj_dmg", 7),
                                      d.get("proj_spd", 250))
            elif kind == "exploder":
                e.x += ux * spd * dt
                e.y += uy * spd * dt
                if dist < e.r + p.r + 12:
                    self._explode_enemy(e)
                    continue
            elif kind == "puddle":
                e.x += ux * spd * dt
                e.y += uy * spd * dt
                e.puddle_t -= dt
                if e.puddle_t <= 0:
                    e.puddle_t = d.get("puddle_cd", 2.6)
                    self.puddle_add(e.x, e.y, 34, 3, 0.35, 5.0, friendly=False)
            elif kind == "spawner":
                e.x += ux * spd * dt
                e.y += uy * spd * dt
                e.spawn_t -= dt
                if e.spawn_t <= 0:
                    e.spawn_t = d.get("spawn_cd", 4.0)
                    for _ in range(d.get("spawn_n", 1)):
                        sx = clamp(e.x + self.rng.uniform(-30, 30), 20, ARENA_W - 20)
                        sy = clamp(e.y + self.rng.uniform(-30, 30), 20, ARENA_H - 20)
                        self._spawn_at(d.get("spawn_eid", "clip"), sx, sy)
            elif kind == "charger":
                if e.state_i == 0:
                    e.x += ux * spd * dt
                    e.y += uy * spd * dt
                    e.charge_t -= dt
                    if dist < d.get("charge_range", 190) and e.charge_t <= 0:
                        e.state_i = 1
                        e.teleg_t = d.get("tele", 0.5)
                        e.dirx, e.diry = ux, uy
                        e.dash_v = d.get("charge_spd", 330)
                elif e.state_i == 1:
                    e.teleg_t -= dt
                    if e.teleg_t <= 0:
                        e.state_i = 2
                        e.teleg_t = 0.34
                        self.app.audio.play("shoot_throw", 0.5)
                else:
                    e.x += e.dirx * e.dash_v * dt
                    e.y += e.diry * e.dash_v * dt
                    e.teleg_t -= dt
                    if e.teleg_t <= 0:
                        e.state_i = 0
                        e.charge_t = d.get("charge_cd", 2.8)
            elif kind == "dasher":
                if e.state_i == 0:
                    e.x += ux * spd * dt
                    e.y += uy * spd * dt
                    e.charge_t -= dt
                    if e.charge_t <= 0 and dist < 240:
                        e.state_i = 1
                        e.teleg_t = d.get("dash_t", 0.32)
                        e.dirx, e.diry = ux, uy
                        self.particles.add(e.x, e.y, K.C["rojo_claro"], n=4, speed=(10, 50), life=(0.2, 0.4))
                else:
                    e.x += e.dirx * d.get("dash_spd", 420) * dt
                    e.y += e.diry * d.get("dash_spd", 420) * dt
                    e.teleg_t -= dt
                    if e.teleg_t <= 0:
                        e.state_i = 0
                        e.charge_t = d.get("dash_cd", 3.0)
            else:  # chase (incluye bombilla/drainer)
                e.x += ux * spd * dt
                e.y += uy * spd * dt
            if kind == "drainer" and dist < d.get("drain_r", 130):
                drains += d.get("drain", 0.16)
            # contacto con el jugador (cooldown por enemigo + iframe global)
            rr = e.r + p.r - 2
            if dist < rr and p.alive:
                last = e.hit_seen.get("touch", -9.0)
                if p.iframe <= 0 and self.time - last >= 1.0:
                    e.hit_seen["touch"] = self.time
                    lit = self.in_light(e.x, e.y)
                    dmg = e.dmg * (K.LIGHT_TAKEN_DARK if not lit else 1.0)
                    self.player_hurt(dmg, src_e=e)
            e.x = clamp(e.x, 10, ARENA_W - 10)
            e.y = clamp(e.y, 10, ARENA_H - 10)
        self.player.drains = drains
        self._separate_enemies()
        self.enemies = [e for e in self.enemies if not e.dead]

    def _separate_enemies(self):
        cell = 22
        grid: dict[tuple, list] = {}
        for e in self.enemies:
            if e.dead or e.boss:
                continue
            key = (int(e.x) // cell, int(e.y) // cell)
            grid.setdefault(key, []).append(e)
        for e in self.enemies:
            if e.dead or e.boss:
                continue
            key = (int(e.x) // cell, int(e.y) // cell)
            near = []
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    near.extend(grid.get((key[0] + dx, key[1] + dy), ()))
            c = 0
            for o in near:
                if o is e or o.dead:
                    continue
                ddx, ddy = e.x - o.x, e.y - o.y
                d2 = ddx * ddx + ddy * ddy
                mr = (e.r + o.r) * 0.75
                if 0 < d2 < mr * mr:
                    d = math.sqrt(d2)
                    push = (mr - d) * 0.4
                    ox, oy = ddx / d, ddy / d
                    e.x += ox * push
                    e.y += oy * push
                    c += 1
                    if c > 6:
                        break

    def _tick_enemy_status(self, e, dt):
        for k in ("burn", "poison", "bleed"):
            st = e.st.get(k)
            if st and st[0] > 0:
                st[0] -= dt
                if st[0] > 0:
                    e.hp -= st[1] * dt
                    if self.rng.random() < dt * 6:
                        col = {"burn": K.C["ambar"], "poison": K.C["morado_claro"], "bleed": K.C["rojo_claro"]}[k]
                        self.particles.add(e.x, e.y - e.r * 0.5, col, n=1, speed=(5, 25), life=(0.2, 0.4), glow=True)
                if e.hp <= 0 and not e.dead:
                    self._kill_enemy(e, lit=self.in_light(e.x, e.y))
        st = e.st.get("slow")
        if st and st[0] > 0:
            st[0] -= dt

    def _enemy_shoot(self, e, ux, uy, sprite, dmg, spd):
        ang = math.atan2(uy, ux) + self.rng.uniform(-0.12, 0.12)
        vx, vy = math.cos(ang) * spd, math.sin(ang) * spd
        dmg = dmg * waves.dmg_scale(self.wave, self.guardia, self.mods)
        self.projs.append(Proj(e.x, e.y, vx, vy, dmg, friendly=False, sprite=sprite, r=4, life=2.6))
        self.app.audio.play("shoot_tack", 0.4)

    def _explode_enemy(self, e):
        r = e.defn.get("boom_r", 44)
        self.enemies.remove(e)
        e.dead = True
        self.particles.ring(e.x, e.y, K.C["verde_claro"], 4, r, 0.3, 2)
        self.particles.add(e.x, e.y, K.C["verde"], n=14, speed=(40, 160), life=(0.2, 0.5))
        self.app.audio.play("explosion_small")
        p = self.player
        dd = math.hypot(p.x - e.x, p.y - e.y)
        if dd < r + p.r:
            self.player_hurt(e.defn.get("boom_dmg", 22) * waves.dmg_scale(self.wave, self.guardia, self.mods))
        # daña también a otros enemigos (¡las pilas no distinguen!)
        for o in self.query_enemies(e.x, e.y, r):
            if o is not e:
                self.damage_silent(o, e.defn.get("boom_dmg", 22) * 0.5)
        self.spawn_drop(e.x, e.y, "xp", max(1, int(e.xp)))

    # ================================================================ puddles
    def puddle_add(self, x, y, r, dps, slow, t, friendly=True):
        self.puddles.append(Puddle(x, y, r, dps, slow, t, friendly=friendly))

    def _update_puddles(self, dt):
        p = self.player
        alive = []
        for pu in self.puddles:
            pu.t -= dt
            if pu.t <= 0:
                continue
            if pu.friendly:
                if pu.dps > 0:
                    for e in self.query_enemies(pu.x, pu.y, pu.r):
                        dmg = pu.dps * dt * self.stats["dmg"]
                        if not self.in_light(e.x, e.y):
                            dmg *= K.LIGHT_DMG_DARK
                        e.hp -= dmg
                        if e.hp <= 0 and not e.dead:
                            self._kill_enemy(e, self.in_light(e.x, e.y))
            else:
                if pu.dps > 0 and p.iframe <= 0:
                    if math.hypot(p.x - pu.x, p.y - pu.y) < pu.r + p.r * 0.4:
                        self.player_hurt(max(2.0, pu.dps) * 1.2)
            alive.append(pu)
        self.puddles = alive

    # ================================================================ armas
    def _update_weapon(self, inst: WeaponInst, dt):
        from . import weapons as WZ
        WZ.update_weapon(self, inst, dt)

    # ================================================================ jefes
    def _update_boss(self, b: Enemy, dt):
        if b.dead:
            return
        self._update_boss_pattern(b, dt)

    # ================================================================ fin
    def _check_achievements(self):
        newly = ach.evaluate(self.save, self.rs)
        for (aid, chispas, unlock) in newly:
            a = ach.BY_ID[aid]
            self.save.earn(chispas)
            self.toast(f"SELLO: {a['name']} (+{chispas} chispas)", "ach")
            if unlock:
                self._toast_unlock(unlock)

    def _toast_unlock(self, unlock_id: str):
        kind, _, name = unlock_id.partition(":")
        label = {"char": "CACHARRO", "weapon": "ARMA", "item": "ÍTEM", "mutator": "MARCA"}.get(kind, "NUEVO")
        self.toast(f"{label} DESBLOQUEADO: {name}", "unlock")

    def chispas_earned(self, victory: bool) -> int:
        base = self.rs["best_wave"] * 3 + self.kills * 0.06
        if victory:
            base += 60
        base += 20 * len([1 for bid in ("despertador", "reunion", "deadline", "olvido") if self._boss_slain_this_run(bid)])
        base *= self.stats["chispas"] * self.mods.get("reward", 1.0)
        return max(5, int(base))

    def _boss_slain_this_run(self, bid):
        return self.rs.get(f"boss_{bid}", 0) > 0

    def _finish(self, victory: bool):
        if self.phase in ("dead", "victory"):
            return
        self.phase = "victory" if victory else "dead"
        # fusionar estadísticas del run en el save
        s = self.save
        for key in ("kills", "crits", "dashes", "fogonazos", "crates", "merges", "rerolls", "heals_bought"):
            s.stat_add(key, self.rs.get(key, 0))
        s.stat_add("coins", self.rs["coins"])
        s.stat_add("levelups", self.rs.get("levelups", 0))
        s.stat_add("dark_kills", self.rs.get("dark_kills", 0))
        s.stat_add("lit_kills", self.rs.get("lit_kills", 0))
        s.stat_add("time", self.time)
        s.stat_add("runs", 1)
        s.stat_max("best_wave", self.rs["best_wave"])
        s.stat_max("best_combo", self.rs["best_combo"])
        s.stat_max("endless_best", self.rs.get("endless", 0))
        if victory:
            s.stat_add("wins", 1)
            s.stat_max("guardia_best", self.guardia)
            s.set_guardia(self.char_id, self.guardia)
            won = s.data["stats"].setdefault("won_chars", [])
            if self.char_id not in won:
                won.append(self.char_id)
        chispas = self.chispas_earned(victory)
        s.earn(chispas)
        # logros finales (stats ya fusionadas)
        self._check_achievements()
        summary = {
            "char": self.char_id, "char_name": self.char["name"], "guardia": self.guardia,
            "wave": self.rs["best_wave"], "hora": K.fmt_hora(min(self.wave, 24)),
            "victory": victory, "time": self.time, "kills": self.kills, "level": self.level,
            "coins": int(self.coins), "chispas": chispas, "mutators": list(self.mut_ids),
            "block": self._best_wave_label(),
        }
        s.add_history(summary)
        s.flush()
        self.events.append({"type": "run_end", "summary": summary})
        self.app.audio.play("victory" if victory else "game_over")

    def _best_wave_label(self):
        return f"hora {self.rs['best_wave']}"

    def continue_endless(self):
        self.endless = True
        self.phase = "active"
        self.next_wave()

    # ================================================================ sello (slam) y cajas
    def _update_slams(self, dt):
        alive = []
        for s in self.slams:
            s["t"] += dt
            if s["t"] >= s["delay"]:
                for e in self.query_enemies(s["x"], s["y"], s["r"]):
                    self.damage(e, s["dmg"], kb=s["kb"], dx=e.x - s["x"], dy=e.y - s["y"])
                self.particles.ring(s["x"], s["y"], K.C["rojo_claro"], 10, s["r"], 0.4, 3)
                self.particles.add(s["x"], s["y"], K.C["rojo"], n=14, speed=(40, 180), life=(0.2, 0.5))
                self.cam.add_shake(4)
                self.app.audio.play("explosion_big", 0.55)
                continue
            alive.append(s)
        self.slams = alive

    def _kick_boxes(self):
        p = self.player
        for pr in self.props:
            if pr.dead or pr.kind != "box":
                continue
            if (pr.x - p.x) ** 2 + (pr.y - p.y) ** 2 < (p.r + pr.r + 4) ** 2:
                pr.hp -= 1
                if pr.hp <= 0:
                    pr.dead = True
                    self.rs["crates"] += 1
                    self.app.audio.play("crate_break")
                    self.app.audio.play("crate_break", 0.8)
                    self.particles.add(pr.x, pr.y, K.C["ambar_osc"], n=12, speed=(30, 140), life=(0.2, 0.5))
                    for _ in range(self.rng.randint(2, 4)):
                        self.spawn_drop(pr.x, pr.y, "coin", 1)
                    if self.rng.random() < 0.22:
                        self.spawn_drop(pr.x, pr.y, "heal", 4)
                    if self.rng.random() < 0.10:
                        self.spawn_drop(pr.x, pr.y, "xp", 8)
                else:
                    self.app.audio.play("hit_enemy", 0.4)
                    self.particles.add(pr.x, pr.y - 4, K.C["ambar_osc"], n=4, speed=(20, 80), life=(0.15, 0.3))

    # ================================================================ cartas de subida
    def roll_levelup_cards(self, n=3):
        from .content import perks as CP2
        owned = {inst.wid for inst in self.player.weapons}
        pool = []
        for card in CP2.PERKS:
            if self.player.perks.get(card["id"], 0) >= card.get("max", 1):
                continue
            req = card.get("req")
            if req and req not in owned:
                continue
            weight = card.get("weight", 5) + (4 if req else 0)
            pool.append((card, weight))
        picks = []
        for _ in range(min(n, len(pool))):
            total = sum(wt for (_c, wt) in pool)
            if total <= 0:
                break
            r = self.rng.uniform(0, total)
            acc = 0.0
            for i, (card, wt) in enumerate(pool):
                acc += wt
                if r <= acc:
                    picks.append(card)
                    pool.pop(i)
                    break
        return picks

    # ================================================================ proyectiles
    def _update_projs(self, dt):
        p = self.player
        alive = []
        for pr in self.projs:
            pr.life -= dt
            if pr.life <= 0:
                continue
            if pr.kind == "lob":
                pr.t_air -= dt
                if pr.t_air <= 0:
                    self._lob_land(pr)
                    continue
            if pr.kind == "boom":
                dist0 = math.hypot(pr.x - pr.ox, pr.y - pr.oy)
                if pr.phase == 0 and dist0 > pr.range:
                    pr.phase = 1
                if pr.phase == 1:
                    dx, dy = p.x - pr.x, p.y - pr.y
                    d = math.hypot(dx, dy) or 1.0
                    sp = math.hypot(pr.vx, pr.vy)
                    pr.vx, pr.vy = dx / d * sp, dy / d * sp
                    if d < 18:
                        continue
            if pr.kind == "missile" and pr.homing:
                tgt = self.nearest_enemy(pr.x, pr.y, 340)
                if tgt is not None:
                    dx, dy = tgt.x - pr.x, tgt.y - pr.y
                    d = math.hypot(dx, dy) or 1.0
                    sp = math.hypot(pr.vx, pr.vy)
                    k = min(1.0, 7.0 * dt)
                    pr.vx += (dx / d * sp - pr.vx) * k
                    pr.vy += (dy / d * sp - pr.vy) * k
            pr.x += pr.vx * dt
            pr.y += pr.vy * dt
            if pr.x < 8 or pr.x > ARENA_W - 8 or pr.y < 8 or pr.y > ARENA_H - 8:
                if pr.kind == "bounce" and pr.bounces > 0:
                    pr.bounces -= 1
                    if pr.x < 8 or pr.x > ARENA_W - 8:
                        pr.vx = -pr.vx
                    if pr.y < 8 or pr.y > ARENA_H - 8:
                        pr.vy = -pr.vy
                    pr.x = clamp(pr.x, 8, ARENA_W - 8)
                    pr.y = clamp(pr.y, 8, ARENA_H - 8)
                else:
                    continue
            if pr.friendly:
                hit = None
                for e in self.hash.query(pr.x, pr.y, pr.r + 26):
                    if e.dead:
                        continue
                    dx, dy = e.x - pr.x, e.y - pr.y
                    rr = e.r + pr.r
                    if dx * dx + dy * dy <= rr * rr:
                        if pr.hit_cd.get(id(e), 0.0) > 0:
                            continue
                        hit = (e, dx, dy)
                        break
                if hit is not None:
                    e, dx, dy = hit
                    _dmg, crit = self.damage(e, pr.dmg, status=pr.status, kb=pr.kb, dx=dx, dy=dy)
                    self.app.audio.play("hit_crit" if crit else "hit_enemy")
                    if pr.kind == "bounce":
                        pr.hit_cd[id(e)] = 0.22
                        pr.bounces -= 1
                        if pr.bounces < 0:
                            continue
                        nx = self.nearest_enemy(pr.x, pr.y, 220)
                        if nx is not None and nx is not e:
                            dx2, dy2 = nx.x - pr.x, nx.y - pr.y
                            d2 = math.hypot(dx2, dy2) or 1.0
                            sp = math.hypot(pr.vx, pr.vy)
                            pr.vx, pr.vy = dx2 / d2 * sp, dy2 / d2 * sp
                        else:
                            pr.vx, pr.vy = -pr.vx, -pr.vy
                    elif pr.kind == "boom":
                        pr.hit_cd[id(e)] = 0.35
                    else:
                        pr.pierce -= 1
                        if pr.pierce < 0:
                            self.particles.add(pr.x, pr.y, K.C["crema"], n=4, speed=(20, 70), life=(0.15, 0.3))
                            continue
            else:
                dx, dy = p.x - pr.x, p.y - pr.y
                rr = pr.r + p.r
                if dx * dx + dy * dy <= rr * rr:
                    self.player_hurt(pr.dmg)
                    continue
            for k in list(pr.hit_cd):
                pr.hit_cd[k] -= dt
                if pr.hit_cd[k] <= 0:
                    del pr.hit_cd[k]
            alive.append(pr)
        self.projs = alive

    def _lob_land(self, pr):
        if pr.friendly:
            for e in self.query_enemies(pr.tx, pr.ty, pr.r):
                self.damage(e, pr.dmg, status=pr.status, kb=pr.kb, dx=e.x - pr.tx, dy=e.y - pr.ty)
            if pr.status.get("puddle_dot", 0) > 0:
                self.puddle_add(pr.tx, pr.ty, pr.r * 0.85, pr.status["puddle_dot"], 0.3,
                                pr.status.get("puddle_t", 3.0), friendly=True)
            self.particles.ring(pr.tx, pr.ty, K.C["ambar"], 6, pr.r, 0.35, 2)
            self.particles.add(pr.tx, pr.ty, K.C["ambar"], n=12, speed=(30, 140), life=(0.2, 0.5), glow=True)
            self.app.audio.play("explosion_small", 0.8)
        else:
            p = self.player
            if math.hypot(p.x - pr.tx, p.y - pr.ty) < pr.r + p.r:
                self.player_hurt(pr.dmg)
            self.puddle_add(pr.tx, pr.ty, pr.r * 0.8, 4, 0.3, 3.5, friendly=False)
            self.particles.ring(pr.tx, pr.ty, K.C["rojo_claro"], 6, pr.r, 0.35, 2)

    # ================================================================ patrones de jefe
    def _update_boss_pattern(self, b: Enemy, dt):
        d = b.defn
        if b.dash_t > 0:
            b.dash_t -= dt
            b.x = clamp(b.x + b.dirx * b.dash_v * dt, 30, ARENA_W - 30)
            b.y = clamp(b.y + b.diry * b.dash_v * dt, 30, ARENA_H - 30)
        # wind-up de shockwave (telegrafiado, evitable)
        if b.state_i == 77:
            b.teleg_t -= dt
            self.particles.add(b.x, b.y, K.C["ambar"], n=2, speed=(30, 90), life=(0.15, 0.3), glow=True)
            if b.teleg_t <= 0:
                b.state_i = 0
                r = float(b.hit_seen.get("shock_arg", 150))
                p = self.player
                self.particles.ring(b.x, b.y, K.C["ambar"], 8, r, 0.5, 3)
                self.app.audio.play("explosion_big", 0.8)
                self.cam.add_shake(3)
                if math.hypot(p.x - b.x, p.y - b.y) < r + p.r:
                    self.player_hurt(b.dmg * 0.8)
            return
        b.pat_cd -= dt
        if b.pat_cd > 0:
            return
        p = self.player
        pat = d["pattern"]
        cd, act, arg = pat[b.pat_i % len(pat)]
        b.pat_i += 1
        b.pat_cd = cd
        if act == "shockwave":
            b.state_i = 77
            b.teleg_t = 0.6
            b.hit_seen["shock_arg"] = float(arg)
            return
        elif act == "summon":
            eid, n = arg
            for _ in range(int(n)):
                self._spawn_at(eid, clamp(b.x + self.rng.uniform(-80, 80), 20, ARENA_W - 20),
                               clamp(b.y + self.rng.uniform(-80, 80), 20, ARENA_H - 20))
            self.particles.add(b.x, b.y, K.C["morado_claro"], n=10, speed=(20, 100), life=(0.2, 0.5))
        elif act == "charge":
            dx, dy = p.x - b.x, p.y - b.y
            dn = math.hypot(dx, dy) or 1.0
            b.dirx, b.diry = dx / dn, dy / dn
            b.dash_v = float(arg)
            b.dash_t = 1.2
            self.particles.add(b.x, b.y, K.C["rojo_claro"], n=8, speed=(20, 90), life=(0.2, 0.5))
        elif act == "dashplayer":
            dx, dy = p.x - b.x, p.y - b.y
            dn = math.hypot(dx, dy) or 1.0
            b.dirx, b.diry = dx / dn, dy / dn
            b.dash_v = float(arg)
            b.dash_t = 0.5
        elif act == "lob_player":
            for i in range(int(arg)):
                tx = clamp(p.x + self.rng.uniform(-30, 30), 20, ARENA_W - 20)
                ty = clamp(p.y + self.rng.uniform(-30, 30), 20, ARENA_H - 20)
                dx, dy = tx - b.x, ty - b.y
                dn = math.hypot(dx, dy) or 1.0
                pl = Proj(b.x, b.y, dx / dn * 220, dy / dn * 220, b.dmg * 0.7, friendly=False,
                          sprite="pr_coffee", r=30, kind="lob", tx=tx, ty=ty, t_air=0.8 + i * 0.15)
                self.projs.append(pl)
        elif act == "spray":
            base = math.atan2(p.y - b.y, p.x - b.x)
            for i in range(int(arg)):
                ang = base + (i - int(arg) / 2) * 0.16
                vx, vy = math.cos(ang) * 230, math.sin(ang) * 230
                self.projs.append(Proj(b.x, b.y, vx, vy, b.dmg * 0.5, friendly=False, sprite="pr_toner",
                                       r=5, life=3.0))
            self.app.audio.play("shoot_spread" if False else "shoot_heavy", 0.6)
        elif act == "burst":
            base = self.rng.uniform(0, 6.28)
            for i in range(int(arg)):
                ang = base + i * (6.283 / int(arg))
                vx, vy = math.cos(ang) * 210, math.sin(ang) * 210
                self.projs.append(Proj(b.x, b.y, vx, vy, b.dmg * 0.45, friendly=False, sprite="pr_toner",
                                       r=5, life=3.4))
            self.app.audio.play("nova", 0.7)
        elif act == "dark":
            self.dark_bonus = max(self.dark_bonus, float(arg))
            self.dark_bonus_t = 6.5
            self.banner("LA OSCURIDAD SE ESPESA...")
            self.app.audio.play("ui_deny", 0.7)
        elif act == "blink":
            ang = self.rng.uniform(0, 6.28)
            b.x = clamp(p.x + math.cos(ang) * 210, 40, ARENA_W - 40)
            b.y = clamp(p.y + math.sin(ang) * 210, 40, ARENA_H - 40)
            self.particles.add(b.x, b.y, K.C["morado"], n=16, speed=(30, 140), life=(0.2, 0.6), glow=True)

    # ================================================================ tienda
    def _open_shop(self):
        self.phase = "shop"
        self.rerolls = 0
        self._roll_shop()
        self.events.append({"type": "shop_open"})
        self.app.audio.play("wave_start")

    def _tier_ok(self, tier: int) -> bool:
        w = self.wave
        return {1: True, 2: w >= 2, 3: w >= 5, 4: w >= 9}[tier]

    def _weapon_pool(self):
        out = []
        for wid, w in CW.BY_ID.items():
            if not self._tier_ok(w["tier"]):
                continue
            if w.get("unlock") and not self.save.has(w["unlock"]):
                continue
            out.append(wid)
        return out or ["grapadora"]

    def _item_pool(self):
        out = []
        for iid, it in CI.BY_ID.items():
            if not self._tier_ok(it["tier"]):
                continue
            if it.get("unlock") and not self.save.has(it["unlock"]):
                continue
            out.append(iid)
        return out

    def _roll_shop(self):
        rng = self.rng
        luck = self.stats["luck"]
        self.shop = []
        n = self.shop_slots
        wpool = self._weapon_pool()
        ipool = self._item_pool()
        for i in range(n):
            want_weapon = (i < 2) if self.wave <= 3 else (rng.random() < 0.45)
            if want_weapon and wpool:
                wid = rng.choice(wpool)
                self.shop.append(self._make_offer("weapon", wid))
            elif ipool:
                iid = rng.choice(ipool)
                self.shop.append(self._make_offer("item", iid))
            else:
                wid = rng.choice(wpool)
                self.shop.append(self._make_offer("weapon", wid))

    def _make_offer(self, kind, cid) -> dict:
        if kind == "weapon":
            tier = CW.BY_ID[cid]["tier"]
            base = {1: 16, 2: 26, 3: 38, 4: 52}[tier]
        else:
            tier = CI.BY_ID[cid]["tier"]
            base = CI.price(CI.BY_ID[cid])
        price = base + self.rng.randint(0, 3)
        price = max(1, int(round(price * (1 - self.discount))))
        return {"kind": kind, "id": cid, "price": price, "sold": False}

    def reroll_cost(self) -> int:
        paid = max(0, self.rerolls - self.extra_rerolls)
        if paid == 0 and self.rerolls < self.extra_rerolls:
            return 0
        RI = max(1, int(0.35 * self.wave))
        FRP = int(0.6 * self.wave) + RI
        cost = FRP + paid * RI
        return max(1, int(round(cost * (1 - self.discount))))

    def shop_reroll(self) -> bool:
        if self.mods.get("no_reroll") and self.rerolls >= self.extra_rerolls:
            self.notify("La máquina no se deja sacudir (AUSTERIDAD).")
            return False
        cost = self.reroll_cost()
        if cost > int(self.coins):
            return False
        self.coins -= cost
        self.rerolls += 1
        self.rs["rerolls"] += 1
        self._roll_shop()
        self.app.audio.play("shop_reroll")
        self.cam.add_shake(1.6)
        return True

    def shop_heal_price(self) -> int:
        return max(2, int(round((8 + 2 * self.wave) * (1 - self.discount))))

    def shop_heal(self) -> bool:
        price = self.shop_heal_price()
        if int(self.coins) < price:
            return False
        self.coins -= price
        self.rs["heals_bought"] += 1
        self.heal_player(self.player.max_hp * 0.30)
        self.app.audio.play("pickup_heal")
        return True

    def shop_buy(self, i: int) -> bool:
        if i < 0 or i >= len(self.shop):
            return False
        off = self.shop[i]
        if off["sold"] or int(self.coins) < off["price"]:
            return False
        p = self.player
        if off["kind"] == "weapon":
            wid = off["id"]
            if len(p.weapons) >= CW.MAX_WEAPON_SLOTS:
                # intentar fusión automática con misma arma y nivel
                cand = next((w for w in p.weapons if w.wid == wid and w.level < CW.MAX_WEAPON_LEVEL), None)
                if cand is None:
                    self.notify("Sin huecos: necesitas 6 armas o una fusión posible.")
                    return False
                cand.level += 1
                self.rs["merges"] += 1
                self.app.audio.play("merge")
                self.toast(f"FUSIÓN: {CW.BY_ID[wid]['name']} nivel {cand.level}", "perk")
            else:
                p.weapons.append(WeaponInst(wid))
        else:
            p.items.append(off["id"])
            self.recompute()
        self.coins -= off["price"]
        off["sold"] = True
        self.app.audio.play("shop_buy")
        return True

    def shop_sell(self, idx: int) -> bool:
        p = self.player
        if idx < 0 or idx >= len(p.weapons):
            return False
        if len(p.weapons) <= 1:
            self.notify("No puedes quedarte sin armas.")
            return False
        w = p.weapons.pop(idx)
        price = {1: 16, 2: 26, 3: 38, 4: 52}[CW.BY_ID[w.wid]["tier"]]
        self.coins += price * 0.5
        self.app.audio.play("shop_buy", 0.6)
        return True

    def shop_merge(self, i: int, j: int) -> bool:
        p = self.player
        if i == j or not (0 <= i < len(p.weapons) and 0 <= j < len(p.weapons)):
            return False
        a, b = p.weapons[i], p.weapons[j]
        if a.wid != b.wid or a.level != b.level or a.level >= CW.MAX_WEAPON_LEVEL:
            return False
        a.level += 1
        p.weapons.pop(j)
        self.rs["merges"] += 1
        self.app.audio.play("merge")
        self.toast(f"FUSIÓN: {CW.BY_ID[a.wid]['name']} nivel {a.level}", "perk")
        return True

    def merge_pairs(self) -> list[tuple[int, int]]:
        pairs = []
        ws = self.player.weapons
        for i in range(len(ws)):
            for j in range(i + 1, len(ws)):
                if ws[i].wid == ws[j].wid and ws[i].level == ws[j].level and ws[i].level < CW.MAX_WEAPON_LEVEL:
                    pairs.append((i, j))
        return pairs

    def leave_shop(self):
        if self.pending_levels > 0:
            self.phase = "levelup"
            self.events.append({"type": "levelup"})
            return
        self.next_wave()

    # ================================================================ render
    def draw(self, surf):
        cam = self.cam
        fx, fy = cam.to_screen(0, 0)
        surf.blit(self.floor, (int(fx), int(fy)))
        # charcos
        for pu in self.puddles:
            x, y = cam.to_screen(pu.x, pu.y)
            col = (140, 90, 40, 90) if pu.friendly else (60, 70, 80, 90)
            alpha = int(80 * min(1.0, pu.t / 1.5))
            r = int(pu.r)
            pygame.draw.ellipse(surf, col, (x - r, y - r * 0.55, r * 2, r * 1.1))
            pygame.draw.ellipse(surf, (col[0] // 2, col[1] // 2, col[2] // 2, alpha),
                                (x - r, y - r * 0.55, r * 2, r * 1.1), 1)
        # profundidad: props, enemigos y jugador ordenados por Y
        items = [(pr.y, 0, pr) for pr in self.props]
        items += [(e.y, 1, e) for e in self.enemies]
        items.append((self.player.y, 2, self.player))
        items.sort(key=lambda t: t[0])
        for (_y, kind, obj) in items:
            if kind == 0:
                self._draw_prop(surf, obj)
            elif kind == 1:
                self._draw_enemy(surf, obj)
            else:
                self._draw_player(surf, obj)
        # proyectiles
        for pr in self.projs:
            sp = S.get(pr.sprite)
            x, y = cam.to_screen(pr.x, pr.y)
            if pr.kind == "lob":
                t = 1.0 - max(0.0, pr.t_air / max(0.001, pr.t_tot))
                x = x + (cam.to_screen(pr.tx, pr.ty)[0] - x) * t
                y = y + (cam.to_screen(pr.tx, pr.ty)[1] - y) * t - math.sin(math.pi * t) * 34
            sp.draw(surf, x, y + sp.h // 2, flip=pr.vx < 0)
        # rayos (cadenas)
        for z in self.zaps:
            a = z["t"] / z["max"]
            x1, y1 = cam.to_screen(z["x1"], z["y1"])
            x2, y2 = cam.to_screen(z["x2"], z["y2"])
            col = (int(255 * a), int(220 * a), int(140 * a))
            pygame.draw.line(surf, col, (x1, y1), (x2, y2), 2)
            for i in range(1, 4):
                t = i / 4
                jx = x1 + (x2 - x1) * t + self.rng.uniform(-3, 3)
                jy = y1 + (y2 - y1) * t + self.rng.uniform(-3, 3)
                surf.fill(col, (int(jx), int(jy), 2, 2), special_flags=pygame.BLEND_RGB_ADD)
        # sello: telegrafiado
        for s in self.slams:
            x, y = cam.to_screen(s["x"], s["y"])
            prog = min(1.0, s["t"] / max(0.01, s["delay"]))
            r = int(s["r"] * (0.5 + 0.5 * prog))
            pygame.draw.circle(surf, (255, 140, 90), (int(x), int(y)), r, 1)
            pygame.draw.circle(surf, (255, 90, 60), (int(x), int(y)), max(2, int(r * prog)), 1)
        # haz láser
        if self.beam_fx is not None and self.time - self.beam_fx[4] < 0.1:
            x1, y1, x2, y2, _t = self.beam_fx
            a = cam.to_screen(x1, y1)
            b = cam.to_screen(x2, y2)
            pygame.draw.line(surf, (120, 40, 40), a, b, 5)
            pygame.draw.line(surf, (255, 120, 120), a, b, 2)
            pygame.draw.line(surf, (255, 230, 200), a, b, 1)
            surf.fill((255, 200, 160), (int(b[0]) - 2, int(b[1]) - 2, 4, 4), special_flags=pygame.BLEND_RGB_ADD)
        # partículas + números
        self.particles.draw(surf, cam)
        self.texts.draw(surf, cam, self.app.fonts)
        # oscuridad y viñeta
        self._draw_darkness(surf)

    def _draw_prop(self, surf, pr: Prop):
        if pr.dead:
            return
        sp = S.get(pr.sprite)
        x, y = self.cam.to_screen(pr.x, pr.y)
        if pr.solid:
            S.draw_shadow(surf, x, y + 2, sp.w)
        sp.draw(surf, x, y)

    def _draw_enemy(self, surf, e: Enemy):
        sp = S.get(e.defn["sprite"])
        x, y = self.cam.to_screen(e.x, e.y)
        S.draw_shadow(surf, x, y + 2, max(10, int(e.r * 2)))
        bob = math.sin(self.time * 6 + e.x * 0.13) * (1.2 if not e.boss else 0)
        flash = e.flash_t > 0
        if e.elite and not flash:
            # aura dorada para élites
            glow = S.glow(int(e.r * 2.2), (255, 190, 90), 70)
            surf.blit(glow, (int(x - glow.get_width() / 2), int(y - glow.get_height() / 2)),
                      special_flags=pygame.BLEND_RGB_ADD)
            surf.blit(sp.elite, (int(x - sp.w // 2), int(y - sp.h + 1 + bob)))
        else:
            sp.draw(surf, x, y + bob, flash=flash)
        if e.boss and e.state_i == 77:
            # aviso de golpe sísmico
            prog = 1.0 - max(0.0, e.teleg_t / 0.6)
            rr = int(e.defn and 150 * (0.4 + 0.6 * prog))
            pygame.draw.circle(surf, (255, 170, 90), (int(x), int(y)), rr, 1)

    def _draw_player(self, surf, p: Player):
        sp = S.get(self.char["sprite"])
        x, y = self.cam.to_screen(p.x, p.y)
        S.draw_shadow(surf, x, y + 2, 20)
        bob = math.sin(self.time * 8) * (1.2 if p.walk_t else 0.5)
        flash = p.hurt_flash > 0.12
        sp.draw(surf, x, y + bob, flip=p.facing, flash=flash)
        # halo cálido de la lámpara
        r = int(self.light_radius() * 0.5)
        g = S.glow(max(20, r), (255, 190, 110), 60)
        surf.blit(g, (int(x - g.get_width() / 2), int(y - g.get_height() / 2) - 4),
                  special_flags=pygame.BLEND_RGB_ADD)
        if p.iframe > 0 and int(self.time * 12) % 2 == 0:
            pygame.draw.circle(surf, K.C["teal_claro"], (int(x), int(y) - 6), 12, 1)

    def _draw_darkness(self, surf):
        alpha = waves.amb_dark(self.wave, self.mods) + int(self.dark_bonus)
        alpha = int(clamp(alpha, 0, 232))
        if self.reveal_t > 0:
            alpha = int(alpha * 0.35)
        if alpha <= 4:
            return
        if getattr(self, "_dark_surf", None) is None:
            self._dark_surf = pygame.Surface((K.W, K.H), pygame.SRCALPHA)
        ds = self._dark_surf
        ds.fill((6, 8, 18, alpha))
        r = int(self.light_radius())
        if r > 4:
            mask = S.radial_mask(r)
            x, y = self.cam.to_screen(self.player.x, self.player.y)
            ds.blit(mask, (int(x - r), int(y - r - 4)), special_flags=pygame.BLEND_RGBA_SUB)
        surf.blit(ds, (0, 0))
        # viñeta
        if getattr(self, "_vignette", None) is None:
            v = pygame.Surface((K.W, K.H), pygame.SRCALPHA)
            for i in range(26):
                a = int(90 * (1 - i / 26) ** 1.8)
                pygame.draw.rect(v, (4, 5, 12, a), (i, i, K.W - i * 2, K.H - i * 2), 1)
            self._vignette = v
        surf.blit(self._vignette, (0, 0))


def wave_hp_mult(world: RunWorld) -> float:
    return waves.hp_scale(world.wave, world.guardia, world.mods, world.assist)
