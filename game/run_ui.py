"""RunScene: la pantalla de partida — HUD, cartas, tienda, pausa y resumen."""
from __future__ import annotations

import math
import random

import pygame

from . import const as K
from . import icons as I
from . import sprites as S
from .core import Scene, WEB, clamp
from .gui import GUI, bar
from .world import RunWorld
from .content import chars as CC
from .content import enemies as CE
from .content import items as CI
from .content import mutators as CM
from .content import perks as CP
from .content import strings as ST
from .content import waves
from .content import weapons as CW


class RunScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.gui = GUI(app)
        self.world: RunWorld | None = None
        self.paused = False
        self.pause_tab = 0
        self.cards: list[dict] | None = None
        self.card_rects: list[pygame.Rect] = []
        self.banner_txt = ""
        self.banner_t = 0.0
        self.toasts: list[dict] = []
        self.intro_t = 0.0
        self.flash_t = 0.0
        self.sel_weapon = None
        self.end_t = 0.0
        self.abandon_confirm = False
        self.shop_hover = None
        self._pend_fs = False
        self.tut_page = 0

    # ------------------------------------------------------------- entrada
    def enter(self, char_id="lia", guardia=1, mut_ids=None, seed=None, **kw):
        self.world = RunWorld(self.app, char_id, guardia, mut_ids or [], seed)
        self.paused = False
        self.cards = None
        self.toasts = []
        self.banner_t = 0
        self.intro_t = 2.6
        self.tut_page = 1 if not self.app.save.data.get("seen_tut") else 0
        self.sel_weapon = None
        self.end_t = 0.0
        self.abandon_confirm = False
        self.app.audio.play_music("combat")
        self.app.save.see_enemy("posti")

    # ------------------------------------------------------------- input
    def handle(self, ev):
        if self.tut_page > 0:
            return  # la guía consume el input; se avanza desde update()
        if ev.type == pygame.KEYDOWN:
            if self.world and self.world.phase in ("dead", "victory"):
                return
            if ev.key == pygame.K_ESCAPE:
                if self.world and self.world.phase == "shop":
                    self.world.leave_shop()
                else:
                    self.paused = not self.paused
            elif ev.key == pygame.K_TAB and self.paused:
                self.pause_tab = (self.pause_tab + 1) % 4
            elif self.paused and ev.key == pygame.K_TAB:
                pass
            elif ev.key == pygame.K_g and self.paused:
                self.tut_page = 1
        if self.paused and ev.type == pygame.KEYDOWN and ev.key == pygame.K_q:
            self.app.set_scene("menu")

    # ------------------------------------------------------------- update
    def update(self, dt):
        w = self.world
        g = self.gui
        g.begin()
        # controles tactiles (web): pausa + acciones, solo en partida activa
        if WEB and not self.paused and self.cards is None and self.tut_page == 0 and w.phase == "active":
            if g.button(pygame.Rect(K.W - 34, 6, 28, 20), "II", "t_pausa", size=10):
                self.paused = True
            if g.button(pygame.Rect(K.W - 178, K.H - 76, 58, 26), "DASH", "t_dash", size=9):
                self.app.input.press_virtual(pygame.K_LSHIFT)
            if g.button(pygame.Rect(K.W - 112, K.H - 76, 58, 26), "FOGO", "t_fogo", size=9):
                self.app.input.press_virtual(pygame.K_SPACE)
        if self._pend_fs:
            self._pend_fs = False
            self.app.toggle_fullscreen()
        if self.tut_page > 0:
            inp = self.app.input
            advance = (inp.just_pressed(pygame.K_RETURN) or inp.just_pressed(pygame.K_SPACE)
                       or inp.mouse_clicked)
            if advance or inp.just_pressed(pygame.K_ESCAPE):
                if advance:
                    self.tut_page += 1
                    self.app.audio.play("ui_click")
                if self.tut_page > 2 or not advance:
                    self.tut_page = 0
                if self.tut_page == 0:
                    self.app.save.data["seen_tut"] = True
                    self.app.save.flush()
            return
        # eventos del mundo
        for ev in w.events:
            t = ev["type"]
            if t == "banner":
                self.banner_txt = ev["text"]
                self.banner_t = 2.6
            elif t == "msg":
                self.banner_txt = self.banner_txt or ev["text"]
                self.push_toast(ev["text"], "info")
            elif t == "toast":
                self.push_toast(ev["text"], ev.get("kind", "info"))
            elif t == "levelup":
                if self.cards is None:
                    self.cards = self._roll_cards()
            elif t == "boss_intro":
                self.banner_txt = f"{ev['name']}  —  {ev['line']}"
                self.banner_t = 3.2
                self.flash_t = 0.3
                self.app.audio.duck(0.5, 2.5)
            elif t == "shop_open":
                self.sel_weapon = None
            elif t == "run_end":
                self.end_t = 0.001
        w.events.clear()

        if self.banner_t > 0:
            self.banner_t -= dt
        if self.flash_t > 0:
            self.flash_t -= dt
        for to in self.toasts:
            to["t"] -= dt
        self.toasts = [to for to in self.toasts if to["t"] > 0]
        if self.intro_t > 0:
            self.intro_t -= dt

        if not self.paused and self.end_t <= 0:
            w.update(dt)
        if self.end_t > 0:
            self.end_t += dt

        # música por estado
        if w.phase not in ("dead", "victory"):
            if w.boss is not None:
                want = "boss"
            elif w.wave <= 6:
                want = "combat"
            elif w.wave <= 12:
                want = "combat2"
            else:
                want = "combat3"
            self.app.audio.play_music(want)

    def push_toast(self, text, kind="info"):
        self.toasts.insert(0, {"text": text, "kind": kind, "t": 4.5})
        del self.toasts[7:]

    # ------------------------------------------------------------- cartas
    def _roll_cards(self) -> list[dict]:
        return self.world.roll_levelup_cards()

    def _ui_levelup(self):
        surf = self.app.screen
        g = self.gui
        ov = pygame.Surface((K.W, K.H), pygame.SRCALPHA)
        ov.fill((6, 8, 16, 130))
        surf.blit(ov, (0, 0))
        self.app.fonts.text(surf, "¡SUBE DE NIVEL!", (K.W // 2, 34), kind="psp", size=14,
                            color=K.C["ambar"], anchor="center", shadow=True, bold_shadow=True)
        self.app.fonts.text(surf, f"nivel {self.world.level} · elige una carta", (K.W // 2, 52),
                            size=13, color=K.C["crema"], anchor="center", shadow=True)
        n = len(self.cards)
        cw_, ch_ = 150, 132
        total = n * cw_ + (n - 1) * 14
        x0 = (K.W - total) // 2
        self.card_rects = []
        for i, card in enumerate(self.cards):
            r = pygame.Rect(x0 + i * (cw_ + 14), 84, cw_, ch_)
            rect = g.sticky_card(r, card["name"], self._wrap_card(card), accent_idx=i, en=True)
            self.card_rects.append(rect)
            icon = I.get_icon(card["icon"])
            icon_y = rect.y + 32 + len(self._wrap_card(card)) * 13
            surf.blit(icon, (rect.centerx - icon.get_width() // 2, icon_y))
            if g.click and r.collidepoint(g.mouse):
                self.world.apply_levelup(card)
                self.app.audio.play("ui_click")
                self.cards = self._roll_cards() if self.world.pending_levels > 0 else None
                break

    def _wrap_card(self, card) -> list[str]:
        desc = card.get("desc", "")
        return self.app.fonts.wrap(desc, "vt", 11, 128)

    # ------------------------------------------------------------- tienda
    def _ui_shop(self):
        w = self.world
        g = self.gui
        surf = self.app.screen
        ov = pygame.Surface((K.W, K.H), pygame.SRCALPHA)
        ov.fill((6, 8, 16, 165))
        surf.blit(ov, (0, 0))

        panel = g.panel((80, 26, 480, 268), "slab", ST.SHOP_TITLE)
        # máquina expendedora decorativa (abajo, sin pisar huecos ni textos)
        vm = S.get("pp_vending")
        surf.blit(vm.n, (88, 236))
        # ofertas (nombre + efecto visibles dentro del hueco, sin tooltip)
        slot_w = 90
        x0 = 180
        for i, off in enumerate(w.shop):
            r = pygame.Rect(x0 + i * 96, 62, slot_w, 104)
            if off["kind"] == "weapon":
                d = CW.BY_ID[off["id"]]
                short, res = CW.SHORT.get(off["id"], (d["name"], d["desc"]))
                border = K.C["azul_claro"]
                extra = "Arma · fusiona 2 iguales para subir de nivel"
            else:
                d = CI.BY_ID[off["id"]]
                short, res = CI.SHORT.get(off["id"], d["name"]), d["desc"]
                border = K.C["teal"]
                extra = "Ítem pasivo"
            icon = I.get_icon(d["icon"])
            afford = int(w.coins) >= off["price"]
            clicked = g.icon_slot(r, icon, short, price=off["price"], en=afford, border=border,
                                  tag=f"T{d['tier']}", sold=off["sold"], desc=res)
            if r.collidepoint(g.mouse):
                g.tooltip(r, d["name"], [extra] + self.app.fonts.wrap(d.get("desc", ""), "vt", 11, 200))
            if clicked and not off["sold"]:
                if not w.shop_buy(i):
                    self.app.audio.play("ui_deny")
        # servicios
        y = 172
        shake_r = pygame.Rect(190, y, 96, 26)
        cost = w.reroll_cost()
        free = w.rerolls < w.extra_rerolls
        if g.button(shake_r, f"SACUDIR {'libre' if free else str(cost) + '¢'}", "shake", size=10,
                    en=(free or int(w.coins) >= cost)):
            if not w.shop_reroll():
                self.app.audio.play("ui_deny")
        heal_r = pygame.Rect(296, y, 100, 26)
        hp = int(w.shop_heal_price())
        if g.button(heal_r, f"CURITA {hp}¢", "heal", size=10, en=(int(w.coins) >= hp)):
            if not w.shop_heal():
                self.app.audio.play("ui_deny")
        go_r = pygame.Rect(406, y, 96, 26)
        if g.button(go_r, "SEGUIR ▶", "go", size=11):
            w.leave_shop()
        # inventario armas
        self.app.fonts.text(surf, "TUS ARMAS (clic: fusionar/vender)", (190, 208), size=10, color=K.C["crema"], shadow=True)
        for i, inst in enumerate(w.player.weapons):
            r = pygame.Rect(190 + i * 46, 222, 42, 42)
            icon = I.get_icon(inst.defn["icon"])
            sel = (self.sel_weapon == i)
            clicked = g.icon_slot(r, icon, border=K.C["ambar"] if sel else None, count=inst.level)
            if r.collidepoint(g.mouse):
                g.tooltip(r, f"{inst.defn['name']} N{inst.level}", self.app.fonts.wrap(inst.defn["desc"], "vt", 11, 200))
            if clicked:
                if self.sel_weapon is None:
                    self.sel_weapon = i
                elif self.sel_weapon == i:
                    self.sel_weapon = None
                else:
                    j = self.sel_weapon
                    if not w.shop_merge(min(i, j), max(i, j)):
                        self.sel_weapon = i
                    else:
                        self.sel_weapon = None
        # vender seleccionada
        if self.sel_weapon is not None and self.sel_weapon < len(w.player.weapons):
            sr = pygame.Rect(486, 222, 62, 20)
            if g.button(sr, "VENDER", "sell", size=9):
                w.shop_sell(self.sel_weapon)
                self.sel_weapon = None
        # monedas y avance del turno (texto arriba, enemigos en rejilla compacta)
        surf.blit(I.get_icon("ic_s_coin"), (92, 32))
        self.app.fonts.text(surf, str(int(w.coins)), (106, 34), size=14, color=K.C["ambar"], shadow=True)
        nexth = w.wave + 1
        if nexth <= K.HORAS_NOCHE:
            self.app.fonts.text(surf, f"SIGUIENTE: hora {nexth} — {K.fmt_hora(nexth)}", (150, 38), size=10,
                                color=K.C["crema"], shadow=True)
            comp = sorted(set(waves.composition(nexth, w.rng, w.mods)))
            for k, eid in enumerate(comp[:8]):
                sp = S.get(CE.BY_ID[eid]["sprite"])
                surf.blit(sp.small, (92 + (k % 4) * 21, 54 + (k // 4) * 14))
        else:
            self.app.fonts.text(surf, "SIGUIENTE: HORA EXTRA", (150, 38), size=10, color=K.C["morado_claro"], shadow=True)

    # ------------------------------------------------------------- pausa
    def _ui_pause(self):
        surf = self.app.screen
        g = self.gui
        w = self.world
        ov = pygame.Surface((K.W, K.H), pygame.SRCALPHA)
        ov.fill((6, 8, 16, 170))
        surf.blit(ov, (0, 0))
        g.panel((80, 26, 480, 304), "slab", "TURNO EN PAUSA")
        tabs = ["ESTADO", "CONTROLES", "ARCHIVO", "AJUSTES"]
        for i, tname in enumerate(tabs):
            r = pygame.Rect(132 + i * 96, 52, 90, 20)
            if g.button(r, tname, f"tab{i}", style="key", size=9, en=(self.pause_tab != i)):
                self.pause_tab = i
        if self.pause_tab == 0:
            y = 80
            rows = [("Vida", f"{int(w.player.hp)}/{int(w.player.max_hp)}"),
                    ("Nivel", str(w.level)),
                    ("Daño", K.fmt_stat("dmg", w.stats["dmg"] - 1)),
                    ("Vel. ataque", K.fmt_stat("atk_speed", w.stats["atk_speed"] - 1)),
                    ("Crítico", f"{w.stats['crit']*100:.0f}% x{w.stats['crit_dmg']:.1f}"),
                    ("Armadura", str(int(w.stats["armor"]))),
                    ("Luz", f"{int(w.light_radius())} px"),
                    ("Velocidad", f"{int(w.stats['speed'])}"),
                    ("Bajas", str(w.kills)),
                    ("Racha máx.", str(w.rs["best_combo"]))]
            for k, (a, b) in enumerate(rows):
                col = K.C["crema"] if k % 2 == 0 else K.C["papel2"]
                self.app.fonts.text(surf, a, (140, y + k * 15), size=11, color=col)
                self.app.fonts.text(surf, str(b), (330, y + k * 15), size=11, color=K.C["ambar"], shadow=True)
            self.app.fonts.text(surf, "ARMAS (disparan solas · 2 iguales se fusionan)", (140, y + 10 * 15 + 4),
                                size=10, color=K.C["teal_claro"])
            for i, inst in enumerate(w.player.weapons):
                wid = inst.defn["id"]
                short = CW.SHORT.get(wid, (inst.defn["name"], ""))[0]
                xx = 140 + (i % 2) * 205
                yy = y + 10 * 15 + 18 + (i // 2) * 16
                icon = I.get_icon(inst.defn["icon"])
                surf.blit(icon, (xx, yy))
                self.app.fonts.text(surf, f"{short} N{inst.level}", (xx + 20, yy - 2), size=9, color=K.C["crema"])
        elif self.pause_tab == 1:
            y = 90
            for k, (a, b) in enumerate(ST.CONTROLS):
                self.app.fonts.text(surf, a, (140, y + k * 18), size=11, color=K.C["ambar"])
                self.app.fonts.text(surf, b, (250, y + k * 18), size=11, color=K.C["crema"])
            self.app.fonts.text(surf, "En penumbra haces 35% menos daño.", (140, y + 8 * 18 + 6), size=10,
                                color=K.C["gris"])
            self.app.fonts.text(surf, "G: volver a ver la GUÍA del turno.", (140, y + 8 * 18 + 20), size=10,
                                color=K.C["ambar_claro"])
        elif self.pause_tab == 2:
            y = 88
            i = 0
            for e in CE.ENEMIES + CE.BOSSES:
                seen = self.app.save.seen_enemy(e["id"])
                x = 136 + (i % 3) * 126
                yy = y + (i // 3) * 32
                if seen:
                    sp = S.get(e["sprite"])
                    surf.blit(sp.small, (x, yy + 8))
                    self.app.fonts.text(surf, e["name"][:16], (x + 18, yy + 2), size=9, color=K.C["crema"])
                    self.app.fonts.text(surf, f"x{self.app.save.data['bestiary'].get(e['id'],0)}", (x + 18, yy + 13),
                                        size=9, color=K.C["gris"])
                else:
                    surf.blit(I.get_icon("ic_ui_lock"), (x + 2, yy + 6))
                    self.app.fonts.text(surf, "———", (x + 18, yy + 2), size=9, color=K.C["gris_osc"])
                i += 1
        else:
            # ajustes en caliente: volúmenes y opciones sin salir de la partida
            s = self.app.settings
            s["vol_master"] = g.slider(pygame.Rect(215, 96, 215, 12), s["vol_master"], "p1", "Volumen general")
            s["vol_sfx"] = g.slider(pygame.Rect(215, 130, 215, 12), s["vol_sfx"], "p2", "Efectos")
            s["vol_music"] = g.slider(pygame.Rect(215, 164, 215, 12), s["vol_music"], "p3", "Música")
            s["shake"] = g.toggle(pygame.Rect(215, 178, 215, 22), "Vibración de pantalla", s["shake"], "p4")
            s["dmg_numbers"] = g.toggle(pygame.Rect(215, 202, 215, 22), "Números de daño", s["dmg_numbers"], "p5")
            s["flash"] = g.toggle(pygame.Rect(215, 226, 215, 22), "Destellos de pantalla", s["flash"], "p6")
            if g.button(pygame.Rect(215, 252, 215, 22),
                        f"PANTALLA COMPLETA: {'SÍ' if s['fullscreen'] else 'NO'}", "p7", size=10):
                self._pend_fs = True
            self.app.fonts.text(surf, "Los cambios se aplican al momento.", (215, 280), size=9, color=K.C["gris"])
            if self.app.input.mouse_released or self.app.input.mouse_clicked:
                self.app.audio.refresh_volumes()
                s.flush()
        # botones
        if g.button(pygame.Rect(132, 300, 120, 22), "CONTINUAR", "res", size=10):
            self.paused = False
        if not self.abandon_confirm:
            if g.button(pygame.Rect(262, 300, 120, 22), "ABANDONAR", "ab", size=10):
                self.abandon_confirm = True
        else:
            if g.button(pygame.Rect(262, 300, 120, 22), "¿SEGURO? SÍ", "ab2", size=9):
                self.paused = False
                self.world._finish(victory=False)
        if g.button(pygame.Rect(392, 300, 116, 22), "MENÚ", "menu", size=10):
            self.app.set_scene("menu")

    # ------------------------------------------------------------- fin de run
    def _unlock_icon(self, unlock_id: str):
        """Icono pequeño (hasta 14 px de alto) para un desbloqueo, o None."""
        kind, _, name = unlock_id.partition(":")
        ic = None
        try:
            if kind == "char":
                from .content import chars as _CC
                d = _CC.BY_ID.get(name)
                ic = S.get(d["sprite"]).small if d else None
            elif kind == "weapon":
                ic = I.get_icon(CW.BY_ID[name]["icon"])
            elif kind == "item":
                ic = I.get_icon(CI.BY_ID[name]["icon"])
        except Exception:
            return None
        if ic is not None and ic.get_height() > 14:
            w2 = max(1, ic.get_width() * 14 // ic.get_height())
            ic = pygame.transform.smoothscale(ic, (w2, 14))
        return ic

    def _ui_end(self):
        surf = self.app.screen
        g = self.gui
        w = self.world
        victory = w.phase == "victory"
        ov = pygame.Surface((K.W, K.H), pygame.SRCALPHA)
        ov.fill((6, 8, 16, 190))
        surf.blit(ov, (0, 0))
        # resumen del run (ya guardado en historial)
        hist = self.app.save.data["history"][0] if self.app.save.data["history"] else {}
        title = ST.VICTORY_TITLE if victory else random.choice(ST.DEFEAT_TITLES)
        col = K.C["ambar"] if victory else K.C["rojo_claro"]
        self.app.fonts.text(surf, title, (K.W // 2, 40), kind="psp", size=16, color=col, anchor="center",
                            shadow=True, bold_shadow=True)
        lines = ST.VICTORY_LINES if victory else ST.DEFEAT_LINES
        txt = lines[(int(self.end_t * 0.5)) % len(lines)]
        self.app.fonts.text(surf, txt, (K.W // 2, 64), size=12, color=K.C["crema"], anchor="center", shadow=True)
        # panel de resumen
        g.panel((110, 84, 420, 190), "paper")
        h = hist or {}
        rows = [
            ("Cacharro", f"{w.char['name']}  (guardia {w.guardia})"),
            ("Aguantaste hasta", K.fmt_hora(min(w.rs['best_wave'], 24))),
            ("Bajas", str(w.kills)),
            ("Nivel", str(w.level)),
            ("Monedas ganadas", str(int(h.get("coins", 0)))),
            ("Tiempo", K.fmt_time(w.time)),
            ("CHISPAS GANADAS", f"+{h.get('chispas', 0)}"),
        ]
        for k, (a, b) in enumerate(rows):
            y = 98 + k * 19
            col_t = (70, 52, 30)
            self.app.fonts.text(surf, a, (126, y), size=12, color=col_t)
            self.app.fonts.text(surf, str(b), (400, y), size=12, color=(140, 70, 10) if k == 6 else col_t,
                                anchor="topright", shadow=False)
        # desbloqueos de la noche (alertas claras al terminar la partida)
        rep = getattr(w, "unlock_report", [])
        if rep:
            g.panel((110, 230, 420, 58), "slab", "DESBLOQUEADO ESTA NOCHE")
            yy = 252
            shown = 0
            for (kind2, val) in rep:
                if shown >= 3:
                    break
                if kind2 == "guardia":
                    self.app.fonts.text(surf, f"NIVEL DE GUARDIA {val} — {K.GUARDIA_NAMES.get(val, '')}",
                                        (126, yy), size=10, color=K.C["ambar"], shadow=True)
                else:
                    lbl, disp, _k3, _nm3 = w.unlock_label(val)
                    icon = self._unlock_icon(val)
                    if icon is not None:
                        surf.blit(icon, (124, yy - 1))
                        self.app.fonts.text(surf, f"{lbl}: {disp}", (140, yy), size=10,
                                            color=K.C["teal_claro"], shadow=True)
                    else:
                        self.app.fonts.text(surf, f"{lbl}: {disp}", (126, yy), size=10,
                                            color=K.C["teal_claro"], shadow=True)
                shown += 1
                yy += 12
            if len(rep) > shown:
                self.app.fonts.text(surf, f"+{len(rep) - shown} más — míralo en SELLOS", (126, yy - 1), size=9,
                                    color=K.C["gris"])
        # habitat de botones
        if victory:
            if g.button(pygame.Rect(180, 292, 130, 26), "HORA EXTRA ▶", "endless", size=11):
                w.continue_endless()
            if g.button(pygame.Rect(330, 292, 130, 26), "TERMINAR", "endliving", size=11):
                self.app.set_scene("menu")
        else:
            if g.button(pygame.Rect(180, 292, 130, 26), "OTRA NOCHE", "retry", size=11):
                self.app.set_scene("run", char_id=w.char_id, guardia=w.guardia, mut_ids=w.mut_ids)
            if g.button(pygame.Rect(330, 292, 130, 26), "AL MENÚ", "tomenu", size=11):
                self.app.set_scene("menu")
        if g.button(pygame.Rect(264, 322, 112, 18), "VER SELLOS", "ver_sellos", size=9):
            self.app.set_scene("sellos")

    # ------------------------------------------------------------- HUD
    def draw(self, surf):
        w = self.world
        w.draw(surf)
        if WEB:
            w.draw_stick(surf)
        self._draw_hud(surf)
        if self.banner_t > 0 and self.banner_txt:
            a = min(1.0, self.banner_t / 0.5)
            size = 15 if len(self.banner_txt) < 40 else 12
            self.app.fonts.text(surf, self.banner_txt, (K.W // 2, 84), kind="psp", size=size,
                                color=K.C["ambar"], anchor="center", shadow=True, bold_shadow=True,
                                alpha=int(255 * a))
        if self.flash_t > 0:
            fl = pygame.Surface((K.W, K.H), pygame.SRCALPHA)
            fl.fill((255, 255, 255, int(120 * (self.flash_t / 0.3))))
            surf.blit(fl, (0, 0))
        # toasts
        y = 120
        for to in self.toasts:
            a = min(1.0, to["t"] / 0.6)
            col = {"info": K.C["papel2"], "ach": K.C["ambar"], "unlock": K.C["teal_claro"],
                   "perk": K.C["crema"], "boss": K.C["rojo_claro"]}.get(to["kind"], K.C["crema"])
            self.app.fonts.text(surf, to["text"], (K.W - 10, y), size=10, color=col, anchor="topright",
                                shadow=True, alpha=int(255 * a))
            y += 15
        if self.intro_t > 0:
            self._draw_intro(surf)
        # superposiciones interactivas (se dibujan AQUÍ, después del mundo)
        w = self.world
        if self.tut_page > 0:
            self._ui_tut()
        elif self.paused:
            self._ui_pause()
        elif self.cards is not None:
            self._ui_levelup()
        elif w.phase == "shop":
            self._ui_shop()
        elif w.phase in ("dead", "victory"):
            self._ui_end()
        self.gui.end(surf)

    def _draw_hud(self, surf):
        w = self.world
        f = self.app.fonts
        # reloj / hora
        f.text(surf, K.fmt_hora(min(w.wave, 24)), (8, 6), kind="silkb", size=15, color=K.C["ambar"], shadow=True)
        f.text(surf, f"HORA {w.wave}" + (f"/{K.HORAS_NOCHE}" if not w.endless else f" +{w.wave - K.HORAS_NOCHE}"),
               (9, 24), size=11, color=K.C["crema"], shadow=True)
        if not waves.is_boss_hora(w.wave) or w.boss is None:
            frac = clamp(w.wave_t / max(1, w.wave_total), 0, 1)
            bar(surf, (70, 9, 110, 8), frac, K.C["ambar_osc"])
            # marcas de avalancha
            pygame.draw.rect(surf, K.C["rojo_claro"], (70 + int(110 * 0.62), 9, 2, 8))
        # vida (bombilla): caja con barra y número grande, siempre legible
        hp = w.player.hp / max(1.0, w.player.max_hp)
        pygame.draw.rect(surf, (8, 10, 18), (8, K.H - 31, 166, 17), border_radius=3)
        pygame.draw.rect(surf, K.C["azul"], (8, K.H - 31, 166, 17), 1, border_radius=3)
        bar(surf, (12, K.H - 27, 158, 9), hp, K.C["rojo_claro"] if hp < 0.4 else K.C["teal_claro"])
        f.text(surf, f"{int(w.player.hp)}", (91, K.H - 22), kind="silkb", size=12,
               color=K.C["crema"], anchor="center", shadow=True)
        # xp
        nxt = max(1.0, w.xp_next)
        xp_frac = clamp(w.xp / nxt, 0, 1)
        bar(surf, (8, K.H - 12, K.W - 16, 8), xp_frac, K.C["teal"])
        f.text(surf, f"Nv {w.level}", (K.W - 45, K.H - 20), kind="silkb", size=11, color=K.C["teal_claro"],
               anchor="center", shadow=True)
        # monedas
        surf.blit(I.get_icon("ic_s_coin"), (K.W - 70, 6))
        f.text(surf, str(int(w.coins)), (K.W - 56, 8), size=13, color=K.C["ambar"], shadow=True)
        # combo
        if w.player.combo > 4:
            f.text(surf, f"x{w.player.combo}", (K.W - 8, 30), kind="silkb", size=14, color=K.C["ambar_claro"],
                   anchor="topright", shadow=True)
        # habilidades
        abl = 1.0 - clamp(w.player.abl_cd / max(0.01, 14.0 * (1 + w.stats["abl_cd"])), 0, 1)
        dash = 1.0 - clamp(w.player.dash_cd / 1.0, 0, 1)
        for (x, frac, ic, lab) in ((8, abl, "ic_ui_fogonazo", "ESPACIO"), (40, dash, "ic_ui_dash", "SHIFT")):
            pygame.draw.rect(surf, K.C["fondo"], (x, K.H - 58, 26, 26), border_radius=3)
            pygame.draw.rect(surf, K.C["azul"], (x, K.H - 58, 26, 26), 1, border_radius=3)
            icon = I.get_icon(ic)
            icon.set_alpha(255 if frac >= 1 else 90)
            surf.blit(icon, (x + 5, K.H - 55))
            bar(surf, (x, K.H - 32, 26, 4), frac, K.C["ambar"] if frac >= 1 else K.C["gris"], r=1)
        # armas
        for i, inst in enumerate(w.player.weapons):
            x = 76 + i * 30
            icon = I.get_icon(inst.defn["icon"])
            surf.blit(icon, (x, K.H - 60))
            for lv in range(inst.level):
                pygame.draw.rect(surf, K.C["ambar"], (x + 2 + lv * 5, K.H - 44, 3, 3))
        # ítems (crecen hacia arriba; nunca pisan "Nv" ni la barra de XP)
        for i, iid in enumerate(w.player.items[:27]):
            icon = I.get_icon(CI.BY_ID[iid]["icon"])
            surf.blit(icon, (K.W - 14 - (i % 9) * 15, K.H - 60 - (i // 9) * 16))
        # jefe
        if w.boss is not None:
            b = w.boss
            f.text(surf, b.defn["name"], (K.W // 2, 8), kind="psp", size=9, color=K.C["rojo_claro"],
                   anchor="center", shadow=True)
            bar(surf, (K.W // 2 - 130, 22, 260, 10), b.hp / max(1.0, b.max_hp), K.C["rojo"], r=2)
        # incidencias activas
        if w.dark_bonus_t > 0:
            f.text(surf, "¡APAGÓN!", (K.W // 2, 40), size=11, color=K.C["morado_claro"], anchor="center", shadow=True)

    # ------------------------------------------------------------- guía
    def _ui_tut(self):
        """Guía ilustrada del HUD y del equipo inicial (2 páginas)."""
        surf = self.app.screen
        f = self.app.fonts
        g = self.gui
        ov = pygame.Surface((K.W, K.H), pygame.SRCALPHA)
        ov.fill((6, 8, 16, 205))
        surf.blit(ov, (0, 0))
        if self.tut_page == 1:
            g.panel((60, 30, 520, 268), "slab", "¿QUÉ ESTOY VIENDO?")
            lines = [
                ("RELOJ (arriba izq.)", "hora del turno · barra naranja = lo que queda"),
                ("MONEDAS (arriba der.)", "se gastan en LA EXPENDEDORA entre horas"),
                ("VIDA (abajo izq.)", "tu bombilla · si llega a 0, te apagan"),
                ("RECUERDOS (barra verde)", "experiencia: llénala y eliges una mejora"),
                ("TUS ARMAS (iconos abajo)", "disparan solas · 2 iguales se fusionan"),
                ("FOGONAZO (ESPACIO)", "pulso de luz que aturde lo que te rodea"),
                ("DASH (SHIFT)", "esquiva rápida con un instante sin daño"),
                ("BOTÍN DEL SUELO", "chispas, monedas y vida: los recoges al pasar"),
                ("CAJAS DE CARTÓN", "chasquéalas: sueltan monedas y a veces curitas"),
            ]
            y = 52
            for a, b in lines:
                f.text(surf, f"· {a}:", (76, y), size=10, color=K.C["ambar_claro"])
                f.text(surf, b, (252, y), size=10, color=K.C["crema"])
                y += 24
            f.text(surf, "clic / ENTER para seguir >", (K.W // 2, K.H - 24), size=11, color=K.C["ambar"],
                   anchor="center", shadow=True)
        else:
            g.panel((60, 30, 520, 268), "slab", "¿POR QUÉ EMPIEZAS CON ESAS ARMAS?")
            cdef = self.world.char
            f.text(surf, f"{cdef['name']} trae su propio equipo de oficina:", (76, 54), size=11,
                   color=K.C["crema"])
            y = 80
            for wid in cdef.get("weapons", []):
                wd = CW.BY_ID.get(wid)
                if wd is None:
                    continue
                short, res = CW.SHORT.get(wid, (wd["name"], wd["desc"]))
                icon = I.get_icon(wd["icon"])
                surf.blit(icon, (80, y))
                f.text(surf, short, (112, y - 2), size=11, color=K.C["ambar_claro"])
                f.text(surf, res, (112, y + 11), size=10, color=K.C["crema"])
                y += 38
            y = max(y + 4, 170)
            for ln in ("Las armas disparan solas: tú te mueves y esquivas.",
                       "En la tienda puedes comprar más (hasta 6) y fusionar",
                       "dos iguales para subirles el nivel.",
                       "Cada cacharro empieza con armas distintas: pruébalos."):
                f.text(surf, ln, (76, y), size=10, color=K.C["papel2"])
                y += 15
            f.text(surf, "clic / ENTER para empezar el turno >", (K.W // 2, K.H - 24), size=11,
                   color=K.C["ambar"], anchor="center", shadow=True)

    def _draw_intro(self, surf):
        a = clamp(self.intro_t / 1.2, 0, 1)
        ov = pygame.Surface((K.W, K.H), pygame.SRCALPHA)
        ov.fill((6, 8, 16, int(150 * min(1.0, self.intro_t / 2.0))))
        surf.blit(ov, (0, 0))
        f = self.app.fonts
        f.text(surf, "EL TURNO COMIENZA", (K.W // 2, 120), kind="psp", size=13, color=K.C["ambar"],
               anchor="center", shadow=True, alpha=int(255 * a))
        f.text(surf, "Mantén a los enemigos dentro de tu luz: en penumbra les haces mucho menos daño.",
               (K.W // 2, 156), size=12, color=K.C["crema"], anchor="center", shadow=True, alpha=int(255 * a))
        f.text(surf, "WASD moverse · ESPACIO Fogonazo · SHIFT Dash · ESC pausa", (K.W // 2, 176), size=12,
               color=K.C["papel2"], anchor="center", shadow=True, alpha=int(255 * a))
