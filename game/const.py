"""NO APAGUES LA LUZ — constantes globales, paleta y rutas.

Todo el juego usa resolución interna 640x360 y escala por enteros.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

TITLE = "NO APAGUES LA LUZ"
SUBTITLE = "el turno de las sombras"
VERSION = "1.0.0"

W, H = 640, 360
ARENA_W, ARENA_H = 1024, 576
FPS = 60
DT_CLAMP = 1 / 30.0

# --------------------------------------------------------------------------
# Paleta: "papelería nocturna" — azul noche, ámbar de lámpara, crema de papel
# --------------------------------------------------------------------------
C = {
    "negro": (11, 14, 26),
    "fondo": (20, 26, 46),
    "marino": (28, 36, 64),
    "azul": (44, 58, 99),
    "azul_claro": (70, 89, 140),
    "teal": (46, 143, 131),
    "teal_claro": (79, 196, 168),
    "ambar": (255, 179, 71),
    "ambar_claro": (255, 217, 138),
    "ambar_osc": (196, 122, 31),
    "crema": (242, 233, 216),
    "papel": (232, 220, 192),
    "papel2": (214, 199, 164),
    "rojo": (201, 79, 61),
    "rojo_claro": (255, 122, 102),
    "verde": (91, 140, 74),
    "verde_claro": (140, 190, 110),
    "gris": (107, 114, 128),
    "gris_osc": (58, 65, 82),
    "morado": (107, 74, 140),
    "morado_claro": (163, 124, 201),
    "blanco": (255, 255, 255),
    "negro_puro": (8, 9, 15),
}


def col(name: str):
    return C[name]


def mix(c1, c2, t: float):
    """Mezcla lineal entre dos colores (tuplas RGB)."""
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def shade(c, f: float):
    """Oscurece (f<1) o aclara (f>1) un color."""
    if f <= 1:
        return (int(c[0] * f), int(c[1] * f), int(c[2] * f))
    return mix(c, (255, 255, 255), min(1.0, f - 1))


# --------------------------------------------------------------------------
# Stats del jugador
# --------------------------------------------------------------------------
# (etiqueta ES, tipo)  tipo: "pct" (fracción, se muestra x100), "flat" (número), "mult"
STATS = {
    "dmg": ("Daño", "pct"),
    "atk_speed": ("Vel. ataque", "pct"),
    "crit": ("Crítico", "pct"),
    "crit_dmg": ("Daño crítico", "pct"),
    "speed": ("Velocidad", "pct"),
    "hp": ("Vida máx.", "flat"),
    "regen": ("Regeneración", "flat"),
    "armor": ("Armadura", "flat"),
    "dodge": ("Esquiva", "pct"),
    "pickup": ("Imán", "pct"),
    "luck": ("Suerte", "pct"),
    "xp_gain": ("Recuerdos +", "pct"),
    "coin_gain": ("Monedas +", "pct"),
    "light": ("Luz", "pct"),
    "thorn": ("Espinas", "flat"),
    "lifesteal": ("Robo de vida", "pct"),
    "kb": ("Empuje", "pct"),
    "proj_add": ("Proyectiles +", "flat"),
    "pierce_add": ("Perforación +", "flat"),
    "abl_cd": ("Fogonazo -CD", "pct"),
    "chispas": ("Chispas +", "pct"),
    "elite_lure": ("Élites +", "pct"),
}

# Base del jugador (unidades "naturales": pct como fracción)
BASE = {
    "hp": 115.0,
    "regen": 0.0,
    "armor": 0.0,
    "dodge": 0.0,
    "speed": 175.0,
    "dmg": 1.0,
    "atk_speed": 1.0,
    "crit": 0.05,
    "crit_dmg": 1.8,
    "pickup": 54.0,
    "luck": 0.0,
    "xp_gain": 1.0,
    "coin_gain": 1.0,
    "light": 112.0,
    "thorn": 0.0,
    "lifesteal": 0.0,
    "kb": 1.0,
    "proj_add": 0,
    "pierce_add": 0,
    "abl_cd": 1.0,
    "chispas": 1.0,
    "elite_lure": 1.0,
}

# stats aditivos "flat" y stats "multiplicadores" para recomputar
STAT_PCT_KEYS = [k for k, (_, t) in STATS.items() if t == "pct"]
STAT_FLAT_KEYS = [k for k, (_, t) in STATS.items() if t == "flat"]


def fmt_stat(key: str, value: float) -> str:
    label, kind = STATS.get(key, (key, "flat"))
    if kind == "pct":
        v = value * 100
        sign = "+" if v >= 0 else ""
        return f"{sign}{v:.0f}%"
    sign = "+" if value >= 0 else ""
    if isinstance(value, float) and value != int(value):
        return f"{sign}{value:.1f}"
    return f"{sign}{int(value)}"


def fmt_num(n) -> str:
    n = int(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 10_000:
        return f"{n/1000:.0f}k"
    if n >= 1_000:
        return f"{n/1000:.1f}k"
    return str(n)


def fmt_time(s: float) -> str:
    s = max(0, int(s))
    return f"{s//60}:{s%60:02d}"


def fmt_hora(hora: int) -> str:
    """Hora de la noche: oleada 1 = 18:00, cada oleada +1 h."""
    return f"{(18 + hora - 1) % 24:02d}:00"


# --------------------------------------------------------------------------
# Rutas
# --------------------------------------------------------------------------
def resource_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent


RES = resource_dir()
ASSETS = RES / "assets"
FONTS = ASSETS / "fonts"
SFX_DIR = ASSETS / "sfx"
MUSIC_DIR = ASSETS / "music"
AUDIO_MAP_PATH = ASSETS / "audio_map.json"

APP_NAME = "NoApaguesLaLuz"
APP_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / APP_NAME
SAVE_PATH = APP_DIR / "meta.json"
SETTINGS_PATH = APP_DIR / "settings.json"
HISTORY_PATH = APP_DIR / "history.json"


def ensure_app_dir() -> Path:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    return APP_DIR

# --------------------------------------------------------------------------
# Controles
# --------------------------------------------------------------------------
MOVE_KEYS = None  # se resuelve en core.py (depende de pygame)

KEY_ABILITY = "space"
KEY_DASH = "lshift"
KEY_PAUSE = "escape"
KEY_FULLSCREEN = "f11"
KEY_DEBUG = "f3"
KEY_SHOT = "f12"

# --------------------------------------------------------------------------
# Modos de juego
# --------------------------------------------------------------------------
GUARDIA_NAMES = {
    1: "Guardia 1 — turno normal",
    2: "Guardia 2 — refuerzos",
    3: "Guardia 3 — inspección",
    4: "Guardia 4 — auditoría",
    5: "Guardia 5 — final de trimestre",
}
MAX_GUARDIA = 5

HORAS_NOCHE = 20  # oleadas de una noche completa
BOSSS_HORAS = (5, 10, 15, 20)

DARK_BASE = 52        # alfa de oscuridad ambiental en la hora 1
DARK_PER_HORA = 6.8   # incremento por hora
DARK_MAX = 206

LIGHT_DMG_DARK = 0.65    # daño que haces a enemigos en penumbra
LIGHT_TAKEN_DARK = 1.15  # daño extra que recibes en penumbra
