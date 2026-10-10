"""UI inmediata con estética "papelería nocturna": teclas, notas y paneles."""
from __future__ import annotations

import pygame

from . import const as K
from .core import clamp, lerp

PAPER = K.C["papel"]
PAPER2 = K.C["papel2"]
INK = (34, 31, 28)
NOTE_COLORS = [(255, 217, 138), (255, 170, 160), (168, 224, 210), (226, 214, 176), (200, 208, 240)]


class GUI:
    def __init__(self, app):
        self.app = app
        self.mouse = (0, 0)
        self.click = False
        self.down = False
        self._hot = None
        self._hover_snd = None
        self._hover_hit = False
        self._tooltip = None
        self._t = 0.0

    def begin(self):
        self.mouse = self.app.input.mouse
        self.click = self.app.input.mouse_clicked
        self.down = self.app.input.mouse_down
        self._hot = None
        if not self._hover_hit:
            self._hover_snd = None
        self._hover_hit = False
        self._tooltip = None
        self._t = self.app.time

    def end(self, surf):
        if self._tooltip:
            self._draw_tooltip(surf, self._tooltip)

    # ------------------------------------------------------------- helpers
    def hot_id(self, rect, key):
        r = pygame.Rect(rect)
        if r.collidepoint(self.mouse):
            self._hot = key
            return True
        return False

    def _sfx_click(self, ok=True):
        if ok:
            self.app.audio.play("ui_click")
        else:
            self.app.audio.play("ui_deny")

    def hover_enter(self, key):
        self._hover_hit = True
        if self._hover_snd != key:
            self._hover_snd = key
            self.app.audio.play("ui_hover")

    def tooltip(self, rect, title, lines, accent=None):
        r = pygame.Rect(rect)
        if r.collidepoint(self.mouse):
            self._tooltip = {"title": title, "lines": lines, "accent": accent or K.C["ambar"]}

    # ------------------------------------------------------------- widgets
    def button(self, rect, label, key=None, style="key", size=12, en=True, icon=None, sub=None, hotkey=None, kind="vt"):
        r = pygame.Rect(rect)
        hov = r.collidepoint(self.mouse)
        clicked = False
        if hov and en:
            self.hover_enter(key or label)
        if hov and self.click:
            self._sfx_click(en)
            clicked = en
        self.draw_key(r, label, style, size, en, hov, icon, sub, hotkey, kind)
        return clicked

    def draw_key(self, r, label, style="key", size=12, en=True, hov=False, icon=None, sub=None, hotkey=None, kind="vt"):
        s = self.app.screen
        if style == "key":
            base = K.C["marino"] if en else K.C["fondo"]
            top = K.C["azul"] if en else K.C["fondo"]
            if hov:
                base, top = K.C["azul_claro"], K.C["azul"]
            pygame.draw.rect(s, (12, 14, 24), (r.x, r.y + 2, r.w, r.h), border_radius=4)
            pygame.draw.rect(s, base, r, border_radius=4)
            pygame.draw.rect(s, top, (r.x + 1, r.y + 1, r.w - 2, r.h - 3), border_radius=3)
            col = K.C["crema"] if en else K.C["gris"]
            x = r.centerx
            if icon is not None:
                s.blit(icon, (r.x + 6, r.centery - icon.get_height() // 2))
                x = r.x + 14 + (r.w - 14) // 2
            self.app.fonts.text(s, label, (x, r.centery - (4 if sub else 0)), size=size, color=col,
                                shadow=True, anchor="center", kind=kind)
            if sub:
                self.app.fonts.text(s, sub, (x, r.centery + 9), size=9, color=K.C["gris"] if en else K.C["gris_osc"],
                                    shadow=False, anchor="center", kind=kind)
            if hotkey:
                self.app.fonts.text(s, hotkey, (r.right - 5, r.bottom - 4), size=8, color=K.C["gris"],
                                    anchor="bottomright")
        elif style == "note":
            col = NOTE_COLORS[0] if en else (120, 112, 96)
            if hov and en:
                col = K.mix(col, (255, 255, 255), 0.18)
            pygame.draw.rect(s, (10, 12, 20), (r.x + 2, r.y + 3, r.w, r.h), border_radius=2)
            pygame.draw.rect(s, col, r, border_radius=2)
            pygame.draw.rect(s, (60, 52, 40), r, 1, border_radius=2)
            col_t = INK if en else (90, 84, 70)
            self.app.fonts.text(s, label, r.center, size=size, color=col_t, anchor="center")

    def toggle(self, rect, label, value, key):
        r = pygame.Rect(rect)
        hov = r.collidepoint(self.mouse)
        val = value
        if hov and self.click:
            self._sfx_click(True)
            val = not value
        c = K.C["teal_claro"] if val else K.C["gris_osc"]
        self.draw_key(r, ("• " if val else "· ") + label, "key", 11, True, hov)
        pygame.draw.rect(self.app.screen, c, (r.right - 14, r.y + 5, 8, 8), border_radius=2)
        return val

    def slider(self, rect, value, key, label=None):
        r = pygame.Rect(rect)
        hov = r.collidepoint(self.mouse)
        if hov and self.down:
            value = clamp((self.mouse[0] - r.x) / max(1, r.w), 0.0, 1.0)
        pygame.draw.rect(self.app.screen, K.C["fondo"], r, border_radius=3)
        pygame.draw.rect(self.app.screen, K.C["gris_osc"], r, 1, border_radius=3)
        fill = pygame.Rect(r.x + 1, r.y + 1, int((r.w - 2) * value), r.h - 2)
        pygame.draw.rect(self.app.screen, K.C["teal"], fill, border_radius=3)
        knob_x = r.x + int((r.w - 8) * value) + 4
        pygame.draw.rect(self.app.screen, K.C["crema"] if (hov or self.down) else K.C["papel2"],
                         (knob_x - 3, r.y - 2, 6, r.h + 4), border_radius=2)
        if label:
            self.app.fonts.text(self.app.screen, label, (r.x, r.y - 12), size=10, color=K.C["crema"], shadow=True)
        return value

    def panel(self, rect, style="paper", title=None):
        s = self.app.screen
        r = pygame.Rect(rect)
        if style == "paper":
            pygame.draw.rect(s, (10, 12, 20), (r.x + 3, r.y + 4, r.w, r.h))
            pygame.draw.rect(s, PAPER, r)
            pygame.draw.rect(s, (90, 78, 58), r, 1)
            poly_t = [(r.centerx - 14, r.y - 2), (r.centerx + 14, r.y - 2), (r.centerx + 18, r.y + 8),
                      (r.centerx - 10, r.y + 8)]
            tape = pygame.Surface((40, 12), pygame.SRCALPHA)
            tape.fill((205, 205, 190, 130))
            s.blit(tape, (r.centerx - 20, r.y - 5))
            if title:
                self.app.fonts.text(s, title, (r.centerx, r.y + 8), size=12, color=(70, 52, 30),
                                    anchor="midtop")
        else:  # slab
            pygame.draw.rect(s, (10, 12, 20), (r.x + 3, r.y + 4, r.w, r.h), border_radius=3)
            pygame.draw.rect(s, K.C["marino"], r, border_radius=3)
            pygame.draw.rect(s, K.C["azul"], r, 1, border_radius=3)
            if title:
                self.app.fonts.text(s, title, (r.centerx, r.y + 6), size=13, color=K.C["ambar"],
                                    shadow=True, anchor="midtop")
        return r

    def icon_slot(self, rect, icon, label=None, price=None, en=True, border=None, count=None, tag=None,
                  sold=False, desc=None):
        """Hueco de tienda / inventario estilo máquina expendedora.

        con `desc`: nombre + efecto visibles dentro del hueco (sin tooltip).
        """
        s = self.app.screen
        r = pygame.Rect(rect)
        hov = r.collidepoint(self.mouse)
        clicked = False
        if hov and self.click and en and not sold:
            self._sfx_click(True)
            clicked = True
        elif hov and self.click:
            self._sfx_click(False)
        base = K.C["negro"] if not en else (K.C["fondo"] if not hov else K.C["marino"])
        pygame.draw.rect(s, (8, 10, 18), (r.x, r.y + 2, r.w, r.h), border_radius=3)
        pygame.draw.rect(s, base, r, border_radius=3)
        bc = border or (K.C["azul"] if en else K.C["gris_osc"])
        pygame.draw.rect(s, K.C["ambar"] if (hov and en) else bc, r, 1, border_radius=3)
        if icon is not None:
            iy = r.y + 12 if desc else r.y + 8
            s.blit(icon, (r.centerx - icon.get_width() // 2, iy))
        if label:
            label = self.app.fonts.fit(label, "vt", 9, r.w - 8)
            if desc:
                self.app.fonts.text(s, label, (r.centerx, r.y + 42), size=9,
                                    color=K.C["ambar_claro"] if en else K.C["gris"], anchor="midtop", shadow=True)
                dl = self.app.fonts.wrap(desc, "vt", 9, r.w - 8)
                if len(dl) > 2:
                    dl[1] = self.app.fonts.fit(" ".join(dl[1:]), "vt", 9, r.w - 8)
                yy = r.y + 60
                for ln in dl[:2]:
                    self.app.fonts.text(s, ln, (r.centerx, yy), size=9,
                                        color=K.C["crema"] if en else K.C["gris_osc"], anchor="midtop")
                    yy += 11
            else:
                self.app.fonts.text(s, label, (r.centerx, r.bottom - 22), size=9, color=K.C["crema"] if en else K.C["gris"],
                                    anchor="midtop", shadow=True)
        if price is not None:
            self.app.fonts.text(s, f"{price}¢", (r.centerx, r.bottom - (11 if desc else 9)), size=10,
                                color=K.C["ambar"] if en else K.C["rojo_claro"], anchor="midtop", shadow=True)
        if count is not None:
            self.app.fonts.text(s, f"x{count}", (r.right - 4, r.y + 3), size=9, color=K.C["teal_claro"],
                                anchor="topright", shadow=True)
        if tag:
            self.app.fonts.text(s, tag, (r.x + 4, r.y + 3), size=8, color=K.C["ambar_claro"],
                                anchor="topleft", shadow=True)
        if sold:
            pygame.draw.line(s, K.C["rojo"], (r.x + 4, r.y + 4), (r.right - 4, r.bottom - 4), 2)
        return clicked

    def sticky_card(self, rect, title, lines, accent_idx=0, en=True, hov_lift=2):
        """Nota adhesiva (cartas de subida de nivel)."""
        s = self.app.screen
        r = pygame.Rect(rect)
        hov = r.collidepoint(self.mouse) and en
        if hov:
            r = r.inflate(4, hov_lift * 2)
            r.y -= hov_lift * 2
        col = NOTE_COLORS[accent_idx % len(NOTE_COLORS)]
        if not en:
            col = tuple(int(c * 0.55) for c in col)
        if hov:
            col = K.mix(col, (255, 255, 255), 0.15)
        pygame.draw.rect(s, (8, 10, 18), (r.x + 3, r.y + 4, r.w, r.h))
        pygame.draw.rect(s, col, r)
        pygame.draw.rect(s, (70, 60, 44), r, 1)
        pygame.draw.rect(s, (150, 140, 120), (r.centerx - 10, r.y - 3, 20, 6))
        title = self.app.fonts.fit(title, "vt", 11, r.w - 10)
        self.app.fonts.text(s, title, (r.centerx, r.y + 9), size=11, color=INK, anchor="midtop")
        y = r.y + 26
        for ln in lines:
            self.app.fonts.text(s, ln, (r.centerx, y), size=10, color=(60, 50, 40), anchor="midtop")
            y += 13
        return r

    # ------------------------------------------------------------- tooltip
    def _draw_tooltip(self, surf, tt):
        fonts = self.app.fonts
        w = 0
        wrapped = []
        for ln in tt["lines"]:
            for sub in fonts.wrap(ln, "vt", 11, 190) or [""]:
                wrapped.append(sub)
                w = max(w, fonts.font("vt", 11).size(sub)[0])
        w = max(w, fonts.font("vt", 12).size(fonts.san(tt["title"]))[0]) + 16
        h = 20 + len(wrapped) * 12 + 8
        mx, my = self.mouse
        x = clamp(mx + 12, 4, K.W - w - 4)
        y = clamp(my + 14, 4, K.H - h - 4)
        box = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(box, (14, 16, 26, 240), (0, 0, w, h), border_radius=3)
        pygame.draw.rect(box, tt["accent"], (0, 0, w, h), 1, border_radius=3)
        surf.blit(box, (x, y))
        fonts.text(surf, tt["title"], (x + 8, y + 6), size=12, color=tt["accent"], shadow=False)
        yy = y + 20
        for ln in wrapped:
            fonts.text(surf, ln, (x + 8, yy), size=11, color=K.C["crema"])
            yy += 12


# ---------------------------------------------------------------- helpers
def bar(surf, rect, frac, color, bg=(20, 24, 40), border=(12, 14, 24), r=2):
    rct = pygame.Rect(rect)
    pygame.draw.rect(surf, bg, rct, border_radius=r)
    fw = int((rct.w) * clamp(frac, 0.0, 1.0))
    if fw > 0:
        pygame.draw.rect(surf, color, (rct.x, rct.y, fw, rct.h), border_radius=r)
    pygame.draw.rect(surf, border, rct, 1, border_radius=r)


def coin_icon():
    from . import sprites as S
    return S.get("pk_coin").n


def chispa_icon():
    from . import sprites as S
    return S.get("pr_spark").n
