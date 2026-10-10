"""Core del motor: input, cámara, hash espacial, partículas, textos, fuentes,
escenas y bucle de aplicación con escalado entero y capturas."""
from __future__ import annotations

import math
import random

import pygame

from . import const as K
from . import sprites as S

V = pygame.math.Vector2

ARENA_W, ARENA_H = K.ARENA_W, K.ARENA_H


def clamp(v, a, b):
    return a if v < a else (b if v > b else v)


def lerp(a, b, t):
    return a + (b - a) * t


def approach(a, b, d):
    if a < b:
        return min(b, a + d)
    return max(b, a - d)


def ang_to(v: V) -> float:
    return math.atan2(v.y, v.x)


# ==========================================================================
class Input:
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

    def handle(self, ev: pygame.event.Event):
        if ev.type == pygame.KEYDOWN:
            self.keys[ev.key] = True
            self.just.add(ev.key)
            self.any_key = True
            self.text += ev.unicode if ev.unicode and ev.unicode.isprintable() else ""
        elif ev.type == pygame.KEYUP:
            self.keys[ev.key] = False
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.mouse_down = True
            self.mouse_clicked = True
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            self.mouse_down = False
            self.mouse_released = True

    def held(self, key: int) -> bool:
        return self.keys.get(key, False)

    def just_pressed(self, key: int) -> bool:
        return key in self.just

    def move_vector(self) -> V:
        x = (self.held(pygame.K_d) or self.held(pygame.K_RIGHT)) - (self.held(pygame.K_a) or self.held(pygame.K_LEFT))
        y = (self.held(pygame.K_s) or self.held(pygame.K_DOWN)) - (self.held(pygame.K_w) or self.held(pygame.K_UP))
        v = V(x, y)
        if v.length_squared() > 1:
            v = v.normalize()
        return v


# ==========================================================================
class Camera:
    def __init__(self):
        self.pos = V(0, 0)
        self.shake = 0.0
        self.off = V(0, 0)
        self.target = V(0, 0)

    def follow(self, tx, ty, snap=False):
        self.target = V(clamp(tx - K.W / 2, 0, ARENA_W - K.W), clamp(ty - K.H / 2, 0, ARENA_H - K.H))
        if snap:
            self.pos = self.target.copy()

    def add_shake(self, amount):
        self.shake = min(9.0, self.shake + amount)

    def update(self, dt):
        self.pos += (self.target - self.pos) * min(1.0, dt * 9)
        self.shake *= max(0.0, 1 - dt * 7)
        if self.shake > 0.2:
            self.off = V(random.uniform(-self.shake, self.shake), random.uniform(-self.shake, self.shake) * 0.6)
        else:
            self.off = V(0, 0)

    def to_screen(self, x, y):
        return x - self.pos.x + self.off.x, y - self.pos.y + self.off.y


# ==========================================================================
class Hash:
    def __init__(self, cell=48):
        self.cell = cell
        self.grid: dict[tuple, list] = {}

    def clear(self):
        self.grid.clear()

    def insert_all(self, items):
        self.clear()
        c = self.cell
        for it in items:
            key = (int(it.x) // c, int(it.y) // c)
            self.grid.setdefault(key, []).append(it)

    def query(self, x, y, r):
        c = self.cell
        out = []
        x0, x1 = int(x - r) // c, int(x + r) // c
        y0, y1 = int(y - r) // c, int(y + r) // c
        for cx in range(x0, x1 + 1):
            for cy in range(y0, y1 + 1):
                cell = self.grid.get((cx, cy))
                if cell:
                    out.extend(cell)
        return out


# ==========================================================================
class Particles:
    """Partículas + flashes aditivos. Cada partícula es un dict ligero."""

    def __init__(self, cap=560):
        self.items: list[dict] = []
        self.cap = cap

    def add(self, x, y, color, n=1, speed=(20, 90), life=(0.25, 0.6), size=(1, 3),
            kind="spark", grav=0.0, drag=0.9, glow=False, image=None, spread=360, angle=None):
        for _ in range(n):
            if len(self.items) >= self.cap:
                return
            if angle is None:
                a = random.uniform(0, math.tau) if spread >= 360 else random.uniform(-spread / 2, spread / 2) - math.pi / 2
            else:
                a = angle + (random.uniform(-spread / 2, spread / 2) if spread < 360 else 0)
            sp = random.uniform(*speed)
            self.items.append({
                "x": x, "y": y, "vx": math.cos(a) * sp, "vy": math.sin(a) * sp,
                "life": random.uniform(*life), "max": 0.0,
                "color": color, "size": random.uniform(*size),
                "kind": kind, "grav": grav, "drag": drag, "glow": glow, "img": image,
            })
            self.items[-1]["max"] = self.items[-1]["life"]

    def ring(self, x, y, color, r0=6, r1=26, life=0.3, width=2, glow=True):
        if len(self.items) >= self.cap:
            return
        self.items.append({"x": x, "y": y, "vx": 0, "vy": 0, "life": life, "max": life,
                           "color": color, "size": width, "kind": "ring", "r0": r0, "r1": r1,
                           "grav": 0, "drag": 1, "glow": glow, "img": None})

    def update(self, dt):
        alive = []
        for p in self.items:
            p["life"] -= dt
            if p["life"] <= 0:
                continue
            if p["kind"] in ("spark", "puff", "shard"):
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                sp = p["drag"] ** (dt * 60)
                p["vx"] *= sp
                p["vy"] *= sp
                p["vy"] += p["grav"] * dt
            alive.append(p)
        self.items = alive

    def draw(self, target, cam: Camera, additive=True):
        for p in self.items:
            x, y = cam.to_screen(p["x"], p["y"])
            if x < -40 or x > K.W + 40 or y < -40 or y > K.H + 40:
                continue
            t = p["life"] / p["max"]
            if p["kind"] == "ring":
                r = lerp(p["r0"], p["r1"], 1 - t)
                if additive:
                    pygame.draw.circle(target, p["color"] + (int(180 * t),), (int(x), int(y)), int(r), int(p["size"]))
                else:
                    pygame.draw.circle(target, p["color"], (int(x), int(y)), int(r), int(p["size"]))
                continue
            size = max(1, int(p["size"] * (0.4 + 0.6 * t)))
            if p["img"] is not None:
                img = p["img"]
                alpha = int(255 * min(1.0, t * 1.6))
                img.set_alpha(alpha)
                target.blit(img, (int(x - img.get_width() / 2), int(y - img.get_height() / 2)))
            elif p["glow"]:
                target.fill(p["color"] + (0,), (int(x), int(y), size, size), special_flags=pygame.BLEND_RGB_ADD)
            else:
                target.fill(p["color"], (int(x), int(y), size, size))


class Texts:
    def __init__(self):
        self.items: list[dict] = []

    def add(self, x, y, text, color, size=9, crit=False, life=0.7):
        if len(self.items) > 90:
            return
        self.items.append({"x": x + random.uniform(-4, 4), "y": y, "vy": -34 if not crit else -46,
                           "text": text, "color": color, "life": life, "max": life,
                           "size": size, "crit": crit})

    def update(self, dt):
        alive = []
        for t in self.items:
            t["life"] -= dt
            if t["life"] <= 0:
                continue
            t["y"] += t["vy"] * dt
            t["vy"] *= (0.9) ** (dt * 60)
            alive.append(t)
        self.items = alive

    def draw(self, target, cam, fonts):
        for t in self.items:
            x, y = cam.to_screen(t["x"], t["y"])
            a = clamp(t["life"] / t["max"], 0, 1)
            col = t["color"]
            fonts.text(target, t["text"], (x, y), size=t["size"], color=col, shadow=True,
                       anchor="center", alpha=int(200 + 55 * a), bold_shadow=True)


# ==========================================================================
class Fonts:
    def __init__(self):
        self.cache: dict[tuple, pygame.font.Font] = {}
        self.files = {
            "psp": K.FONTS / "PressStart2P-Regular.ttf",
            "vt": K.FONTS / "VT323-Regular.ttf",
            "silk": K.FONTS / "Silkscreen-Regular.ttf",
            "silkb": K.FONTS / "Silkscreen-Bold.ttf",
        }
        self.ok = all(p.exists() for p in self.files.values())

    def font(self, kind="vt", size=14) -> pygame.font.Font:
        key = (kind, size)
        if key not in self.cache:
            path = self.files.get(kind, self.files["vt"])
            try:
                self.cache[key] = pygame.font.Font(str(path), size)
            except Exception:
                self.cache[key] = pygame.font.Font(None, size + 2)
        return self.cache[key]

    def text(self, target, text, pos, kind="vt", size=14, color=K.C["crema"],
             anchor="topleft", shadow=False, alpha=255, shadow_col=(8, 9, 15), bold_shadow=False):
        f = self.font(kind, size)
        img = f.render(str(text), False, color)
        if alpha < 255:
            img = img.copy()
            img.set_alpha(alpha)
        x, y = pos
        if anchor == "center":
            r = img.get_rect(center=(int(x), int(y)))
        elif anchor == "topright":
            r = img.get_rect(topright=(int(x), int(y)))
        elif anchor == "midtop":
            r = img.get_rect(midtop=(int(x), int(y)))
        elif anchor == "midbottom":
            r = img.get_rect(midbottom=(int(x), int(y)))
        elif anchor == "bottomright":
            r = img.get_rect(bottomright=(int(x), int(y)))
        else:
            r = img.get_rect(topleft=(int(x), int(y)))
        if shadow:
            sh = f.render(str(text), False, shadow_col)
            if alpha < 255:
                sh = sh.copy()
                sh.set_alpha(alpha)
            target.blit(sh, (r.x + 1, r.y + 1))
            if bold_shadow:
                target.blit(sh, (r.x - 1, r.y + 1))
                target.blit(sh, (r.x + 1, r.y - 1))
        target.blit(img, r)
        return r

    def wrap(self, text, kind, size, width):
        f = self.font(kind, size)
        words = text.split()
        lines, cur = [], ""
        for w in words:
            probe = (cur + " " + w).strip()
            if f.size(probe)[0] <= width:
                cur = probe
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines


# ==========================================================================
class Scene:
    def __init__(self, app):
        self.app = app

    def enter(self, **kw):
        pass

    def leave(self):
        pass

    def handle(self, ev):
        pass

    def update(self, dt):
        pass

    def draw(self, surf):
        pass


# ==========================================================================
class App:
    def __init__(self, settings, save, audio, headless=False):
        self.settings = settings
        self.save = save
        self.audio = audio
        self.headless = headless
        pygame.init()
        pygame.display.set_caption(f"{K.TITLE} — {K.SUBTITLE}")
        self.fonts = Fonts()
        self.input = Input()
        self.window = None
        self.scale = 1
        self.off = (0, 0)
        self.view = (K.W, K.H)
        self._create_window()
        self.screen = pygame.Surface((K.W, K.H)).convert()
        self.scenes: dict[str, Scene] = {}
        self.scene: Scene | None = None
        self.running = True
        self.fps = 0.0
        self.fps_acc = 0.0
        self.fps_n = 0
        self.debug = False
        self.freeze = 0.0
        self.clock = pygame.time.Clock()
        self.time = 0.0
        self.shot_n = 0

    # ------------------------------------------------------------- ventana
    def _create_window(self):
        info = pygame.display.get_desktop_sizes()[0] if pygame.display.get_desktop_sizes() else (1920, 1080)
        if self.headless:
            self.window = pygame.display.set_mode((K.W * 2, K.H * 2))
            self.scale, self.off, self.view = 2, (0, 0), (K.W * 2, K.H * 2)
            return
        if self.settings["fullscreen"]:
            self.window = pygame.display.set_mode(info, pygame.FULLSCREEN)
            sw, sh = info
        else:
            sc = self.settings["scale"] or 2
            sc = clamp(sc, 1, 4)
            self.window = pygame.display.set_mode((K.W * sc, K.H * sc))
            sw, sh = K.W * sc, K.H * sc
        self.scale = max(1, min(sw // K.W, sh // K.H))
        self.view = (K.W * self.scale, K.H * self.scale)
        self.off = ((sw - self.view[0]) // 2, (sh - self.view[1]) // 2)

    def toggle_fullscreen(self):
        self.settings["fullscreen"] = not self.settings["fullscreen"]
        self.settings.flush()
        self._create_window()

    def mouse(self):
        mx, my = pygame.mouse.get_pos()
        return ((mx - self.off[0]) / self.scale, (my - self.off[1]) / self.scale)

    # ------------------------------------------------------------- escenas
    def set_scene(self, name: str, **kw):
        if self.scene is not None:
            self.scene.leave()
        self.scene = self.scenes[name]
        self.scene.enter(**kw)

    def sfx(self, name, vol=1.0):
        self.audio.play(name, vol)

    # ------------------------------------------------------------- frame
    def frame(self) -> bool:
        dt = min(self.clock.tick(K.FPS) / 1000.0, K.DT_CLAMP)
        self.time += dt
        evs = pygame.event.get()
        self.input.begin()
        for ev in evs:
            if ev.type == pygame.QUIT:
                self.running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
                self.toggle_fullscreen()
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_F3:
                self.debug = not self.debug
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_F12:
                self.screenshot()
            self.input.handle(ev)
            if self.scene:
                self.scene.handle(ev)
        self.input.mouse = self.mouse()
        if not self.running:
            return False
        sim_dt = dt
        if self.freeze > 0:
            self.freeze -= dt
            sim_dt = 0.0
        if self.scene:
            self.scene.update(sim_dt)
            self.screen.fill(K.C["negro"])
            self.scene.draw(self.screen)
        self.audio.update(dt)
        if self.settings["show_fps"] or self.debug:
            self.fps_acc += dt
            self.fps_n += 1
            if self.fps_acc >= 0.5:
                self.fps = self.fps_n / self.fps_acc
                self.fps_acc, self.fps_n = 0.0, 0
            self.fonts.text(self.screen, f"{self.fps:.0f} fps", (K.W - 4, 4), size=10, anchor="topright",
                            color=K.C["ambar"] if self.fps > 50 else K.C["rojo_claro"], shadow=True)
        self._present()
        return True

    def _present(self):
        vw, vh = self.view
        if vw > K.W:
            pygame.transform.scale(self.screen, (vw, vh), self.window.subsurface(pygame.Rect(self.off, (vw, vh))))
        else:
            self.window.fill((0, 0, 0))
            self.window.blit(self.screen, self.off)
        pygame.display.flip()

    def screenshot(self):
        K.ensure_app_dir()
        d = K.APP_DIR / "capturas"
        d.mkdir(exist_ok=True)
        self.shot_n += 1
        path = d / f"captura_{self.shot_n:03d}.png"
        pygame.image.save(self.screen, str(path))
        print(f"[captura] {path}")
        return path

    def quit(self):
        self.running = False
