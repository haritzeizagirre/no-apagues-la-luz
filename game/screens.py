"""Pantallas de menú: portada, lore, selección, El Cajón, Sellos, Archivo, Ajustes."""
from __future__ import annotations

import math
import random

import pygame

from . import const as K
from . import icons as I
from . import sprites as S
from .core import Scene, clamp, WEB
from .gui import GUI, bar
from .content import ach as ACH
from .content import chars as CC
from .content import enemies as CE
from .content import items as CI
from .content import metaup as MU
from .content import mutators as CM
from .content import strings as ST
from .content import weapons as CW
from .content import maps as CMP


def _seal_progress(save, seal) -> str | None:
    """Progreso actual hacia un sello (o None si no aplica)."""
    kind, key, n = seal["cond"][0], seal["cond"][1], seal["cond"][2]
    cur = 0
    if kind in ("stat", "run"):
        cur = save.data["stats"].get(key, 0)
    elif kind == "enemy":
        cur = save.data["bestiary"].get(key, 0)
    elif kind == "boss":
        cur = save.data["bestiary_boss"].get(key, 0)
    if 0 < int(cur) < n:
        return f"Progreso: {int(cur)}/{n}"
    return None


# ---------------------------------------------------------------- fondo común
_bg_cache = {}


def draw_bg(app, surf, t):
    if "bg" not in _bg_cache:
        bg = pygame.Surface((K.W, K.H))
        for y in range(K.H):
            f = y / K.H
            col = (int(16 + 10 * (1 - f)), int(20 + 12 * (1 - f)), int(40 + 16 * (1 - f)))
            pygame.draw.line(bg, col, (0, y), (K.W, y))
        # luna
        pygame.draw.circle(bg, (222, 226, 235), (540, 66), 34)
        pygame.draw.circle(bg, (200, 205, 220), (548, 60), 8)
        pygame.draw.circle(bg, (208, 214, 228), (530, 78), 5)
        glow = S.glow(90, (190, 200, 230), 40)
        bg.blit(glow, (540 - 90, 66 - 90), special_flags=pygame.BLEND_RGB_ADD)
        # edificios
        skyline = [(0, 210, 70, 150), (60, 170, 90, 190), (140, 230, 60, 130), (195, 150, 80, 210),
                   (270, 200, 70, 160), (335, 240, 90, 120), (420, 180, 66, 180), (480, 220, 80, 140),
                   (555, 160, 85, 200)]
        for (x, y, w_, h_) in skyline:
            pygame.draw.rect(bg, (14, 17, 30), (x, y, w_, h_))
            for wy in range(y + 8, K.H, 16):
                for wx in range(x + 6, x + w_ - 6, 12):
                    if random.Random(wx * 7 + wy * 13).random() < 0.22:
                        pygame.draw.rect(bg, (56, 60, 46), (wx, wy, 3, 4))
                    elif random.Random(wx * 3 + wy * 5).random() < 0.06:
                        pygame.draw.rect(bg, (150, 130, 70), (wx, wy, 3, 4))
        # suelo
        pygame.draw.rect(bg, (24, 29, 46), (0, 300, K.W, 60))
        pygame.draw.rect(bg, (19, 23, 38), (0, 336, K.W, 24))
        # mesa y flexo silueta con glow
        pygame.draw.rect(bg, (30, 24, 20), (150, 292, 150, 10))
        pygame.draw.rect(bg, (26, 21, 18), (162, 302, 8, 52))
        pygame.draw.rect(bg, (35, 28, 22), (280, 302, 8, 52))
        lamp = S.get("char_lia")
        bg.blit(lamp.n, (196, 246))
        g2 = S.glow(120, (255, 190, 110), 70)
        bg.blit(g2, (206 - 120, 258 - 120), special_flags=pygame.BLEND_RGB_ADD)
        _bg_cache["bg"] = bg
    surf.blit(_bg_cache["bg"], (0, 0))
    # polvo flotante
    rnd = random.Random(7)
    for i in range(26):
        x = (rnd.randrange(K.W) + t * (6 + i % 5)) % K.W
        y = (rnd.randrange(220, K.H) + t * (2 + i % 3)) % K.H
        a = 70
        pygame.draw.rect(surf, (90, 96, 120), (int(x), int(y), 1, 1))
    # parpadeo de lámpara
    flick = 0.85 + 0.15 * abs(math.cos(math.radians(t * 90)))
    if random.Random(int(t * 3)).random() < 0.06:
        flick *= 0.55
    ve = pygame.Surface((K.W, K.H), pygame.SRCALPHA)
    ve.fill((4, 5, 12, int(70 * flick)))
    surf.blit(ve, (0, 0))


class BaseScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.gui = GUI(app)

    def back_button(self, surf):
        return self.gui.button(pygame.Rect(K.W - 74, K.H - 30, 66, 22), "◀ VOLVER", "back", size=10)

    def title(self, surf, text, sub=None, size=18):
        self.app.fonts.text(surf, text, (K.W // 2, 22), kind="psp", size=size, color=K.C["ambar"],
                            anchor="center", shadow=True, bold_shadow=True)
        if sub:
            self.app.fonts.text(surf, sub, (K.W // 2, 22 + size + 8), size=12, color=K.C["crema"],
                                anchor="center", shadow=True)

    def chispas_counter(self, surf):
        icon = I.get_icon("ic_ui_chispa")
        surf.blit(icon, (K.W - 96, 10))
        self.app.fonts.text(surf, str(self.app.save.chispas), (K.W - 80, 12), size=13, color=K.C["ambar_claro"],
                            shadow=True)


# ---------------------------------------------------------------- portada
class MenuScene(BaseScene):
    def enter(self, **kw):
        self.app.audio.play_music("menu")

    def update(self, dt):
        self.gui.begin()

    def draw(self, surf):
        draw_bg(self.app, surf, self.app.time)
        f = self.app.fonts
        f.text(surf, K.TITLE, (K.W // 2, 58), kind="psp", size=24, color=K.C["ambar"], anchor="center",
               shadow=True, bold_shadow=True)
        f.text(surf, K.SUBTITLE, (K.W // 2, 90), size=13, color=K.C["crema"], anchor="center", shadow=True)
        g = self.gui
        # botón principal, fila propia a lo ancho
        if g.button(pygame.Rect(36, 126, 308, 30), "JUGAR ▶", "menu_jugar", size=12, kind="silk"):
            self.app.set_scene("charsel")
        # rejilla 2×3
        pairs = [("HISTORIA", "lore"), ("EL CAJÓN", "cajon"),
                 ("SELLOS", "sellos"), ("ARCHIVO", "archivo"),
                 ("AJUSTES", "ajustes"), ("CRÉDITOS", "creditos")]
        for i, (label, key) in enumerate(pairs):
            r = pygame.Rect(36 + (i % 2) * 158, 162 + (i // 2) * 32, 150, 26)
            if g.button(r, label, f"menu_{key}", size=11):
                self.app.set_scene(key)
        self.chispas_counter(surf)
        if g.button(pygame.Rect(K.W - 74, K.H - 34, 66, 22), "✕ SALIR", "menu_quit", size=10):
            self.app.quit()
        # pie
        f.text(surf, ST.TAGLINE, (K.W // 2, K.H - 44), size=12, color=K.C["papel2"], anchor="center", shadow=True)
        f.text(surf, f"v{K.VERSION} · hecha con pygame · todo el arte se dibuja por código", (K.W // 2, K.H - 22),
               size=10, color=K.C["gris"], anchor="center")
        self.gui.end(surf)


# ---------------------------------------------------------------- lore
class LoreScene(BaseScene):
    def enter(self, first=False, **kw):
        self.first = first
        self.page = 0
        self.t = 0.0

    def update(self, dt):
        g = self.gui
        g.begin()
        self.t += dt
        if self.app.input.just_pressed(pygame.K_ESCAPE):
            self.app.settings["seen_intro"] = True
            self.app.settings.flush()
            self.app.set_scene("charsel" if self.first else "menu")
            return
        if self.app.input.just_pressed(pygame.K_RETURN) or self.app.input.just_pressed(pygame.K_SPACE):
            self._next()
        if g.click:
            self._next()

    def _next(self):
        self.page += 1
        self.app.audio.play("ui_click")
        if self.page >= len(ST.LORE):
            self.app.settings["seen_intro"] = True
            self.app.settings.flush()
            self.app.set_scene("charsel" if self.first else "menu")

    def draw(self, surf):
        draw_bg(self.app, surf, self.app.time)
        f = self.app.fonts
        panel = self.gui.panel((70, 60, 500, 230), "paper", "EL TURNO DE NOCHE")
        y = 100
        for i in range(self.page + 1):
            if i >= len(ST.LORE):
                break
            color = (60, 48, 30) if i < self.page else (34, 30, 24)
            for line in f.wrap(ST.LORE[i], "vt", 13, 460):
                f.text(surf, line, (92, y), size=13, color=color)
                y += 17
            y += 6
        hint = "clic o ENTER para continuar ▶" if self.page < len(ST.LORE) - 1 else "clic o ENTER para empezar ▶"
        f.text(surf, hint, (K.W // 2, K.H - 40), size=12, color=K.C["ambar"], anchor="center", shadow=True)
        self.gui.end(surf)


# ---------------------------------------------------------------- selección de cacharro
class CharSelectScene(BaseScene):
    def enter(self, **kw):
        self.sel = next((c["id"] for c in CC.CHARS if self.app.save.has(f"char:{c['id']}")), "lia")
        self.guardia = 1
        self.mut_sel: list[str] = []
        self._refresh_guardia()
        self.app.audio.play_music("menu")

    def _refresh_guardia(self):
        saw = self.app.save.guardia_max(self.sel)
        self.guardia = min(self.guardia, min(K.MAX_GUARDIA, saw + 1))

    def update(self, dt):
        self.gui.begin()
        if self.app.input.just_pressed(pygame.K_ESCAPE):
            self.app.set_scene("menu")
            return
        # flechas: cambia entre cacharros desbloqueados
        paso = 0
        if self.app.input.just_pressed(pygame.K_RIGHT):
            paso = 1
        elif self.app.input.just_pressed(pygame.K_LEFT):
            paso = -1
        if paso:
            ids = [c["id"] for c in CC.CHARS if self.app.save.has(f"char:{c['id']}")]
            if ids:
                i = ids.index(self.sel) if self.sel in ids else 0
                self.sel = ids[(i + paso) % len(ids)]
                self._refresh_guardia()
                self.app.audio.play("ui_hover")

    def _contenido(self, surf):
        g = self.gui
        save = self.app.save
        # rejilla de cacharros
        for i, c in enumerate(CC.CHARS):
            r = pygame.Rect(24 + (i % 4) * 74, 52 + (i // 4) * 60, 68, 54)
            unlocked = save.has(f"char:{c['id']}")
            hov = r.collidepoint(g.mouse)
            pygame.draw.rect(self.app.screen, K.C["marino"] if unlocked else K.C["fondo"], r, border_radius=3)
            border = K.C["ambar"] if self.sel == c["id"] else (K.C["azul"] if unlocked else K.C["gris_osc"])
            pygame.draw.rect(self.app.screen, border, r, 1, border_radius=3)
            sp = S.get(c["sprite"])
            if unlocked:
                rect = pygame.Rect(r.x, r.y + 16, r.w, 34)
                self.app.screen.blit(sp.n, (r.centerx - sp.w // 2, r.y + 22))
            else:
                self.app.screen.blit(I.get_icon("ic_ui_lock"), (r.centerx - 6, r.y + 20))
            self.app.fonts.text(self.app.screen, c["name"], (r.centerx, r.y + 4), size=8,
                                color=K.C["crema"] if unlocked else K.C["gris"], anchor="midtop", shadow=True)
            if hov and g.click and unlocked:
                self.sel = c["id"]
                self._refresh_guardia()
                self.app.audio.play("ui_click")
            if hov and not unlocked:
                lines = ["Bloqueado."]
                seal = ACH.seal_for(f"char:{c['id']}")
                if seal:
                    lines.append(f"Sello «{seal['name']}»: {seal['desc']}")
                    prog = _seal_progress(self.app.save, seal)
                    if prog:
                        lines.append(prog)
                else:
                    lines.append("Se desbloquea con el sello correspondiente.")
                g.tooltip(r, c["name"], lines)
        # detalle
        c = CC.BY_ID[self.sel]
        panel = pygame.Rect(330, 52, 288, 240)
        g.panel(panel, "slab")
        sp = S.get(c["sprite"])
        self.app.screen.blit(pygame.transform.scale(sp.n, (sp.w * 2, sp.h * 2)), (panel.x + 10, panel.y + 12))
        f = self.app.fonts
        f.text(self.app.screen, c["name"], (panel.x + 60, panel.y + 12), kind="silkb", size=13,
               color=K.C["ambar"], shadow=True)
        f.text(self.app.screen, c["title"], (panel.x + 60, panel.y + 28), size=10, color=K.C["papel2"])
        y = panel.y + 58
        for line in f.wrap(c["desc"], "vt", 11, 260):
            f.text(self.app.screen, line, (panel.x + 12, y), size=11, color=K.C["crema"])
            y += 13
        y += 4
        for pl in f.wrap(f"★ {c['perk_desc']}", "vt", 11, panel.w - 26):
            f.text(self.app.screen, pl, (panel.x + 12, y), size=11, color=K.C["teal_claro"])
            y += 13
        # stats con meta
        adds, _ = MU.aggregate_ranks(self.app.save.data["ranks"])
        stats = dict(K.BASE)
        for k2, v in c.get("add", {}).items():
            stats[k2] += v
        for k2, m in c.get("mult", {}).items():
            stats[k2] *= m
        for k2, v in adds.items():
            stats[k2] += v
        y += 5
        row = [("Vida", f"{int(stats['hp'])}"), ("Vel", f"{int(stats['speed'])}"),
               ("Daño", f"{stats['dmg']*100:.0f}%"), ("Ataque", f"{stats['atk_speed']*100:.0f}%"),
               ("Luz", f"{int(stats['light'])}"), ("Crítico", f"{stats['crit']*100:.0f}%")]
        for k2, (a, b) in enumerate(row):
            x = panel.x + 12 + (k2 % 3) * 92
            yy = y + (k2 // 3) * 16
            f.text(self.app.screen, f"{a}: ", (x, yy), size=10, color=K.C["gris"])
            f.text(self.app.screen, b, (x + 58, yy), size=10, color=K.C["crema"])
        # equipo inicial (transparencia: con qué armas sales)
        yq = y + 2 * 16 + 6
        f.text(self.app.screen, "EQUIPO INICIAL:", (panel.x + 12, yq), size=10, color=K.C["papel2"])
        for wi, wid in enumerate(c.get("weapons", [])[:3]):
            wd = CW.BY_ID.get(wid)
            if wd is None:
                continue
            xx = panel.x + 12 + wi * 128
            self.app.screen.blit(I.get_icon(wd["icon"]), (xx, yq + 14))
            f.text(self.app.screen, CW.SHORT.get(wid, (wd["name"], ""))[0], (xx + 24, yq + 16), size=9,
                   color=K.C["crema"])
        # guardia (debajo de la rejilla de cacharros, sin solapes)
        gy = 186
        f.text(self.app.screen, f"NIVEL DE GUARDIA  ({ST.GUARDIA_BLURB})", (24, 172), size=10, color=K.C["papel2"])
        saw = self.app.save.guardia_max(self.sel)
        for gnum in range(1, K.MAX_GUARDIA + 1):
            r = pygame.Rect(24 + (gnum - 1) * 42, gy, 38, 20)
            locked = gnum > min(K.MAX_GUARDIA, saw + 1)
            if g.button(r, str(gnum), f"g{gnum}", size=11, en=not locked):
                self.guardia = gnum
            if locked:
                self.app.screen.blit(I.get_icon("ic_ui_lock"), (r.x + 2, r.y + 2))
            if self.guardia == gnum:
                pygame.draw.rect(self.app.screen, K.C["ambar"], r, 2, border_radius=4)
        f.text(self.app.screen, f"Mejor: guardia {saw}" if saw else "Sin victorias todavía", (24, gy + 24),
               size=10, color=K.C["gris"])
        # planta del edificio según la guardia elegida
        mp = CMP.for_guardia(self.guardia)
        f.text(self.app.screen, f"MAPA: {mp.get('short', mp['name'])}", (328, 188), size=10,
               color=K.C["crema"], shadow=True, anchor="topright")
        f.text(self.app.screen, "otra planta cada guardia", (328, 207), size=9,
               color=K.C["gris"], anchor="topright")
        # marcas
        my = 248
        f.text(self.app.screen, "MARCAS DEL TURNO (riesgo ↔ chispas)", (24, my - 16), size=10, color=K.C["papel2"])
        for i, m in enumerate(CM.MUTATORS):
            r = pygame.Rect(24 + (i % 3) * 100, my + (i // 3) * 24, 94, 20)
            unlocked = self.app.save.has(f"mutator:{m['id']}")
            active = m["id"] in self.mut_sel
            if g.button(r, ("• " if active else "") + m["name"], f"m{i}", size=9, en=unlocked):
                if m["id"] in self.mut_sel:
                    self.mut_sel.remove(m["id"])
                else:
                    self.mut_sel.append(m["id"])
            if not unlocked:
                self.app.screen.blit(I.get_icon("ic_ui_lock"), (r.x + 2, r.y + 3))
            if r.collidepoint(g.mouse):
                lines = f.wrap(m["desc"], "vt", 11, 190)
                if m.get("unlock") and not unlocked:
                    seal = next((a["name"] for a in ACH.ACHIEVEMENTS if a.get("unlock") == m["unlock"]), None)
                    if seal:
                        lines.append(f"Sello: {seal}")
                g.tooltip(r, m["name"], lines)
        # empezar
        start = pygame.Rect(24, K.H - 44, 200, 30)
        if g.button(start, "▶ EMPEZAR LA NOCHE", "start", size=12):
            self.app.set_scene("run", char_id=self.sel, guardia=self.guardia, mut_ids=list(self.mut_sel))
        if self.back_button(self.app.screen):
            self.app.set_scene("menu")
        self.gui.end(self.app.screen)

    def draw(self, surf):
        draw_bg(self.app, surf, self.app.time)
        self.title(surf, "ELIGE TU CACHARRO")
        self._contenido(surf)


# ---------------------------------------------------------------- El Cajón
class CajonScene(BaseScene):
    def enter(self, **kw):
        self.msg = ""
        self.msg_t = 0.0

    def update(self, dt):
        self.gui.begin()
        self.msg_t = max(0.0, self.msg_t - dt)
        if self.app.input.just_pressed(pygame.K_ESCAPE):
            self.app.set_scene("menu")

    def _contenido(self, surf):
        g = self.gui
        save = self.app.save
        for i, up in enumerate(MU.META_UPGRADES):
            r = pygame.Rect(40 + (i % 2) * 290, 60 + (i // 2) * 28, 280, 24)
            rank = save.rank(up["id"])
            maxr = up["max_rank"]
            cost = MU.cost(up, rank)
            full = rank >= maxr
            afford = save.chispas >= cost and not full
            hov = r.collidepoint(g.mouse)
            pygame.draw.rect(surf, K.C["marino"] if hov else K.C["fondo"], r, border_radius=3)
            pygame.draw.rect(surf, K.C["azul"] if not full else K.C["ambar_osc"], r, 1, border_radius=3)
            self.app.fonts.text(surf, self.app.fonts.fit(up["name"], "vt", 11, r.w - 78), (r.x + 6, r.y + 2), size=11,
                                color=K.C["crema"] if not full else K.C["ambar_claro"], shadow=True)
            self.app.fonts.text(surf, self.app.fonts.fit(up["desc"], "vt", 9, r.w - 14), (r.x + 6, r.y + 13), size=9, color=K.C["papel2"])
            # pips de rango
            for k in range(maxr):
                col = K.C["ambar"] if k < rank else K.C["gris_osc"]
                pygame.draw.rect(surf, col, (r.right - 10 - (maxr - k) * 7, r.y + 4, 5, 5))
            price = "MÁX" if full else f"{cost}✦"
            self.app.fonts.text(surf, price, (r.right - 6, r.y + 12), size=11,
                                color=K.C["ambar"] if afford else K.C["gris"], anchor="topright", shadow=True)
            if hov and g.click:
                if full:
                    self.app.audio.play("ui_deny")
                elif save.spend(cost):
                    save.set_rank(up["id"], rank + 1)
                    save.flush()
                    self.app.audio.play("shop_buy")
                    self.msg = f"{up['name']} → rango {rank + 1}"
                    self.msg_t = 2.0
                else:
                    self.app.audio.play("ui_deny")
                    self.msg = "No te alcanzan las chispas."
                    self.msg_t = 2.0
        if self.msg_t > 0:
            self.app.fonts.text(surf, self.msg, (K.W // 2, K.H - 40), size=12, color=K.C["ambar"],
                                anchor="center", shadow=True)
        if self.back_button(surf):
            self.app.set_scene("menu")
        self.gui.end(surf)

    def draw(self, surf):
        draw_bg(self.app, surf, self.app.time)
        self.title(surf, "EL CAJÓN DE LOS RECUERDOS", ST.CAJON_BLURB)
        self.chispas_counter(surf)
        self._contenido(surf)


# ---------------------------------------------------------------- Sellos
class SellosScene(BaseScene):
    def enter(self, **kw):
        self.scroll = 0
        self.total = ACH.n_done(self.app.save)

    def _progress(self, save, cond):
        kind = cond[0]
        if kind == "stat":
            return save.data["stats"].get(cond[1], 0), cond[2]
        if kind == "run":
            return None, cond[2]
        if kind == "boss":
            return save.data["bestiary_boss"].get(cond[1], 0), cond[2]
        if kind == "enemy":
            return save.data["bestiary"].get(cond[1], 0), cond[2]
        return None, 0

    def update(self, dt):
        self.gui.begin()
        if self.app.input.just_pressed(pygame.K_ESCAPE):
            self.app.set_scene("menu")
        rows = len(ACH.ACHIEVEMENTS) // 2 + 1
        if self.app.input.just_pressed(pygame.K_DOWN):
            self.scroll = min(self.scroll + 1, max(0, rows - 12))
        if self.app.input.just_pressed(pygame.K_UP):
            self.scroll = max(0, self.scroll - 1)

    def _contenido(self, surf):
        g = self.gui
        save = self.app.save
        for i, a in enumerate(ACH.ACHIEVEMENTS):
            col_i = i % 2
            row_i = i // 2 - self.scroll
            if row_i < 0 or row_i > 11:
                continue
            r = pygame.Rect(30 + col_i * 295, 62 + row_i * 23, 285, 21)
            done = save.ach_done(a["id"])
            hov = r.collidepoint(g.mouse)
            pygame.draw.rect(surf, K.C["marino"] if hov else K.C["fondo"], r, border_radius=3)
            pygame.draw.rect(surf, K.C["ambar"] if done else K.C["gris_osc"], r, 1, border_radius=3)
            ic = I.get_icon("ic_ui_sello")
            ic2 = ic.copy()
            ic2.set_alpha(255 if done else 70)
            surf.blit(ic2, (r.x + 3, r.y + 3))
            self.app.fonts.text(surf, self.app.fonts.fit(a["name"], "vt", 10, 205), (r.x + 20, r.y + 1), size=10,
                                color=K.C["crema"] if done else K.C["gris"], shadow=True)
            cur, target = self._progress(save, a["cond"])
            if target:
                prog = "✔" if done else (f"{min(cur, target)}/{target}" if cur is not None else f"–/{target}")
            else:
                prog = "✔" if done else ""
            self.app.fonts.text(surf, prog, (r.right - 5, r.y + 10), size=9,
                                color=K.C["verde_claro"] if done else K.C["papel2"], anchor="midright", shadow=True)
            if hov:
                g.tooltip(r, a["name"], self.app.fonts.wrap(a["desc"], "vt", 11, 190) + [f"Recompensa: {a['chispas']} ✦"])
        self.app.fonts.text(surf, f"SELLOS: {self.total}/{len(ACH.ACHIEVEMENTS)}   (ARRIBA/ABAJO para mover)", (K.W // 2, K.H - 40),
                            size=11, color=K.C["crema"], anchor="center", shadow=True)
        if self.back_button(surf):
            self.app.set_scene("menu")
        self.gui.end(surf)

    def draw(self, surf):
        draw_bg(self.app, surf, self.app.time)
        self.title(surf, "SELLOS", ST.SELLOS_BLURB)
        self._contenido(surf)


# ---------------------------------------------------------------- Archivo
class ArchivoScene(BaseScene):
    def enter(self, **kw):
        self.scroll = 0

    def update(self, dt):
        self.gui.begin()
        if self.app.input.just_pressed(pygame.K_ESCAPE):
            self.app.set_scene("menu")
        entries = list(CE.ENEMIES) + list(CE.BOSSES)
        cols = 3
        rows = len(entries) // cols + 1
        if self.app.input.just_pressed(pygame.K_DOWN):
            self.scroll = min(self.scroll + 1, max(0, rows - 8))
        if self.app.input.just_pressed(pygame.K_UP):
            self.scroll = max(0, self.scroll - 1)

    def _contenido(self, surf):
        g = self.gui
        save = self.app.save
        entries = list(CE.ENEMIES) + list(CE.BOSSES)
        cols = 3
        seen_n = 0
        for i, e in enumerate(entries):
            col_i = i % cols
            row_i = i // cols - self.scroll
            if row_i < 0 or row_i > 7:
                continue
            r = pygame.Rect(26 + col_i * 198, 66 + row_i * 34, 192, 32)
            seen = save.seen_enemy(e["id"])
            if seen:
                seen_n += 1
            hov = r.collidepoint(g.mouse)
            pygame.draw.rect(surf, K.C["marino"] if hov else K.C["fondo"], r, border_radius=3)
            pygame.draw.rect(surf, K.C["azul"] if seen else K.C["gris_osc"], r, 1, border_radius=3)
            if seen:
                sp = S.get(e["sprite"])
                surf.blit(sp.small, (r.x + 6, r.y + 8))
                isboss = any(b["id"] == e["id"] for b in CE.BOSSES)
                n = save.data["bestiary_boss"].get(e["id"], 0) if isboss else save.data["bestiary"].get(e["id"], 0)
                self.app.fonts.text(surf, self.app.fonts.fit(e["name"], "vt", 10, 160), (r.x + 24, r.y + 4), size=10,
                                    color=K.C["rojo_claro"] if isboss else K.C["crema"], shadow=True)
                self.app.fonts.text(surf, f"{'X' if isboss else 'x'}{n}", (r.x + 24, r.y + 15), size=9,
                                    color=K.C["ambar"],)
                if hov:
                    g.tooltip(r, e["name"], self.app.fonts.wrap(e.get("flavor", ""), "vt", 11, 190))
            else:
                surf.blit(I.get_icon("ic_ui_lock"), (r.x + 8, r.y + 9))
                self.app.fonts.text(surf, "?", (r.x + 28, r.y + 8), size=12, color=K.C["gris_osc"])
        self.app.fonts.text(surf, f"ARCHIVO: {seen_n}/{len(entries)}   (ARRIBA/ABAJO para mover)", (K.W // 2, K.H - 40),
                            size=11, color=K.C["crema"], anchor="center", shadow=True)
        if self.back_button(surf):
            self.app.set_scene("menu")
        self.gui.end(surf)

    def draw(self, surf):
        draw_bg(self.app, surf, self.app.time)
        self.title(surf, "ARCHIVO", ST.ARCHIVO_BLURB)
        self._contenido(surf)


# ---------------------------------------------------------------- Ajustes
class AjustesScene(BaseScene):
    def enter(self, **kw):
        self._pend_fs = False

    def update(self, dt):
        self.gui.begin()
        if self._pend_fs:
            self._pend_fs = False
            self.app.toggle_fullscreen()
        elif self.app.input.just_pressed(pygame.K_ESCAPE):
            self.app.set_scene("menu")

    def _contenido(self, surf):
        g = self.gui
        s = self.app.settings
        changed = False
        y = 70
        s["vol_master"] = g.slider(pygame.Rect(160, y, 220, 12), s["vol_master"], "vm", "Volumen general")
        s["vol_sfx"] = g.slider(pygame.Rect(160, y + 40, 220, 12), s["vol_sfx"], "vs", "Efectos")
        s["vol_music"] = g.slider(pygame.Rect(160, y + 80, 220, 12), s["vol_music"], "vm2", "Música")
        s["shake"] = g.toggle(pygame.Rect(160, y + 110, 200, 22), "Vibración de pantalla", s["shake"], "shk")
        s["dmg_numbers"] = g.toggle(pygame.Rect(160, y + 138, 200, 22), "Números de daño", s["dmg_numbers"], "dmg")
        s["flash"] = g.toggle(pygame.Rect(160, y + 166, 200, 22), "Destellos de pantalla", s["flash"], "fla")
        s["show_fps"] = g.toggle(pygame.Rect(160, y + 194, 200, 22), "Mostrar FPS", s["show_fps"], "fps")
        s["assist"] = g.toggle(pygame.Rect(160, y + 222, 300, 22), "Modo becario (-25% vida enemiga)", s["assist"], "ass")
        if WEB:
            # ajustes solo-web: controles tactiles (auto/si/no) y estirar pantalla
            tmode = str(s.data.get("touch_ui", "auto"))
            if g.button(pygame.Rect(466, y + 222, 152, 22), f"TÁCTILES: {tmode.upper()}", "tch", size=10):
                s["touch_ui"] = {"auto": "si", "si": "no", "no": "auto"}.get(tmode, "auto")
                changed = True
            flabel = "LLENAR: " + ("SÍ" if s.data.get("fill_screen") else "NO")
            if g.button(pygame.Rect(514, y + 246, 104, 22), flabel, "fil", size=10):
                s["fill_screen"] = not bool(s.data.get("fill_screen"))
                self.app.apply_fill()
                changed = True
        if self.app.input.mouse_released or self.app.input.mouse_clicked:
            changed = True
        # ventana: pantalla completa + rescate (la ventana se redimensiona con el marco, como cualquier app)
        self.app.fonts.text(surf, "Ventana:", (160, y + 250), size=11, color=K.C["crema"])
        fs_label = f"PANTALLA COMPLETA: {'SÍ' if s['fullscreen'] else 'NO'}"
        if g.button(pygame.Rect(222, y + 246, 168, 22), fs_label, "fs", size=10):
            self._pend_fs = True
        if g.button(pygame.Rect(398, y + 246, 108, 22), "RECENTRAR", "rc", size=10):
            self.app.reset_window()
        if changed:
            self.app.audio.refresh_volumes()
            s.flush()
        if self.back_button(surf):
            self.app.set_scene("menu")
        self.gui.end(surf)

    def draw(self, surf):
        draw_bg(self.app, surf, self.app.time)
        self.title(surf, "AJUSTES")
        self._contenido(surf)


# ---------------------------------------------------------------- Créditos
class CreditosScene(BaseScene):
    def update(self, dt):
        self.gui.begin()
        if self.app.input.just_pressed(pygame.K_ESCAPE):
            self.app.set_scene("menu")

    def draw(self, surf):
        draw_bg(self.app, surf, self.app.time)
        self.title(surf, "CRÉDITOS")
        y = 70
        for line in ST.CREDITS:
            self.app.fonts.text(surf, line, (K.W // 2, y), size=12 if line else 8, color=K.C["crema"],
                                anchor="center", shadow=True)
            y += 18
        if self.back_button(surf):
            self.app.set_scene("menu")
        self.gui.end(surf)
