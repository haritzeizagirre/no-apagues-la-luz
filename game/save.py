"""Persistencia: meta (Chispas, desbloqueos, sellos, archivo) y ajustes.

Escritura atómica (tmp + replace). Tolerante a ficheros corruptos.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from . import const as K

META_VERSION = 1


def default_meta() -> dict:
    return {
        "version": META_VERSION,
        "chispas": 0,
        "ranks": {},              # id de mejora del Cajón -> rango
        "unlocked": ["char:lia"], # ids "tipo:nombre"
        "ach": {},                # id -> {"done": bool, "n": int}
        "bestiary": {},           # id de enemigo -> veces visto
        "bestiary_boss": {},      # id de jefe -> veces derrotado
        "guardias": {},           # char id -> guardia más alta GANADA
        "stats": {
            "runs": 0, "wins": 0, "endless_best": 0,
            "kills": 0, "deaths": 0, "bosses": 0, "merges": 0,
            "time": 0.0, "best_wave": 0, "best_combo": 0,
            "coins": 0, "chispas_earned": 0, "levelups": 0,
            "crits": 0, "dashes": 0, "fogonazos": 0, "dark_kills": 0,
            "lit_kills": 0, "crates": 0, "heals_bought": 0,
            "rerolls": 0, "won_chars": [], "guardia_best": 0,
        },
        "history": [],  # últimas 30 runs resumidas
    }


def default_settings() -> dict:
    return {
        "vol_master": 0.9,
        "vol_sfx": 0.9,
        "vol_music": 0.75,
        "fullscreen": False,
        "win_w": 1280,        # tamaño de ventana recordado (se abre centrada)
        "win_h": 720,
        "shake": True,
        "dmg_numbers": True,
        "flash": True,
        "show_fps": False,
        "assist": False,      # modo becario: -25% PV enemigo
        "seen_intro": False,
    }


def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _load_json(path: Path, default_factory):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("formato inesperado")
        return data
    except FileNotFoundError:
        return default_factory()
    except Exception:
        # corrupto: apartar y empezar de cero
        try:
            path.rename(path.with_suffix(path.suffix + f".corrupto{int(time.time())}"))
        except Exception:
            pass
        return default_factory()


def _merge_defaults(data: dict, defaults: dict) -> dict:
    for k, v in defaults.items():
        if k not in data:
            data[k] = v
        elif isinstance(v, dict) and isinstance(data.get(k), dict):
            _merge_defaults(data[k], v)
    return data


class Save:
    """Meta-progresión persistente."""

    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else K.SAVE_PATH
        self.data = _merge_defaults(_load_json(self.path, default_meta), default_meta())

    # -- escritura ---------------------------------------------------------
    def flush(self) -> None:
        atomic_write_json(self.path, self.data)

    # -- chispas -----------------------------------------------------------
    @property
    def chispas(self) -> int:
        return int(self.data.get("chispas", 0))

    def earn(self, amount: int) -> None:
        amount = int(amount)
        self.data["chispas"] = self.chispas + amount
        self.data["stats"]["chispas_earned"] = self.data["stats"].get("chispas_earned", 0) + amount

    def spend(self, amount: int) -> bool:
        if self.chispas >= amount:
            self.data["chispas"] = self.chispas - amount
            return True
        return False

    # -- desbloqueos ---------------------------------------------------------
    def has(self, item_id: str) -> bool:
        return item_id in self.data["unlocked"]

    def unlock(self, item_id: str) -> bool:
        if item_id not in self.data["unlocked"]:
            self.data["unlocked"].append(item_id)
            return True
        return False

    # -- Cajón (mejoras permanentes) -----------------------------------------
    def rank(self, up_id: str) -> int:
        return int(self.data["ranks"].get(up_id, 0))

    def set_rank(self, up_id: str, rank: int) -> None:
        self.data["ranks"][up_id] = int(rank)

    # -- sellos --------------------------------------------------------------
    def ach_state(self, ach_id: str) -> dict:
        return self.data["ach"].setdefault(ach_id, {"done": False, "n": 0})

    def ach_done(self, ach_id: str) -> bool:
        return bool(self.ach_state(ach_id)["done"])

    def ach_bump(self, ach_id: str, n: int = 1) -> None:
        st = self.ach_state(ach_id)
        if not st["done"]:
            st["n"] = st.get("n", 0) + n

    def ach_complete(self, ach_id: str) -> None:
        st = self.ach_state(ach_id)
        st["done"] = True
        st["n"] = max(1, st.get("n", 0))

    # -- archivo / guardias ---------------------------------------------------
    def see_enemy(self, eid: str) -> None:
        self.data["bestiary"][eid] = self.data["bestiary"].get(eid, 0) + 1

    def slay_boss(self, bid: str) -> None:
        self.data["bestiary_boss"][bid] = self.data["bestiary_boss"].get(bid, 0) + 1
        self.data["stats"]["bosses"] = self.data["stats"].get("bosses", 0) + 1

    def guardia_max(self, cid: str) -> int:
        return int(self.data["guardias"].get(cid, 0))

    def set_guardia(self, cid: str, g: int) -> None:
        self.data["guardias"][cid] = max(int(g), self.guardia_max(cid))

    # -- estadísticas / historia ----------------------------------------------
    def stat_add(self, key: str, n) -> None:
        self.data["stats"][key] = self.data["stats"].get(key, 0) + n

    def stat_max(self, key: str, n) -> None:
        self.data["stats"][key] = max(self.data["stats"].get(key, 0), n)

    def seen_enemy(self, eid: str) -> bool:
        return self.data["bestiary"].get(eid, 0) > 0

    def slayed_boss(self, bid: str) -> bool:
        return self.data["bestiary_boss"].get(bid, 0) > 0

    def add_history(self, entry: dict) -> None:
        h = self.data["history"]
        h.insert(0, entry)
        del h[30:]


class Settings:
    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else K.SETTINGS_PATH
        self.data = _merge_defaults(_load_json(self.path, default_settings), default_settings())

    def flush(self) -> None:
        atomic_write_json(self.path, self.data)

    def __getitem__(self, k):
        return self.data[k]

    def __setitem__(self, k, v):
        self.data[k] = v
