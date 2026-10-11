"""Audio: SFX + música con crossfade.

Resolución de cada sonido lógico (por prioridad):
  1) assets/audio_map.json  {"sfx": {logico: "ruta/relativa/a/assets"}, "music": {...}}
  2) assets/sfx/<logico>.wav|.ogg     (set sintetizado; .ogg para el build web)
  3) assets/audio_kenney/<logico>.ogg (copia directa con el nombre lógico)
Si nada existe, el sonido queda en silencio (y se reporta en missing()).
"""
from __future__ import annotations

import json
from pathlib import Path

import pygame

from . import const as K

SFX_NAMES = [
    "shoot_tack", "shoot_marker", "shoot_heavy", "shoot_throw", "beam_loop",
    "chain_zap", "aura_pulse", "nova", "explosion_small", "explosion_big",
    "hit_enemy", "hit_crit", "enemy_die", "enemy_die_big", "player_hurt",
    "player_dash", "fogonazo", "pickup_xp1", "pickup_xp2", "pickup_xp3",
    "pickup_coin", "pickup_heal", "levelup", "wave_start", "boss_spawn",
    "boss_die", "victory", "game_over", "ui_click", "ui_hover", "ui_deny",
    "shop_buy", "shop_reroll", "merge", "crate_break", "tape_hit",
]

MUSIC_TRACKS = ["menu", "combat", "combat2", "combat3", "boss", "victory"]

# volumen base por efecto (se multiplica por vol_sfx y vol_master)
SFX_BASE_VOL = {
    "shoot_tack": 0.5, "shoot_marker": 0.5, "shoot_heavy": 0.65, "shoot_throw": 0.55,
    "hit_enemy": 0.55, "hit_crit": 0.75, "enemy_die": 0.5, "enemy_die_big": 0.7,
    "player_hurt": 0.9, "player_dash": 0.6, "fogonazo": 0.9, "nova": 0.8,
    "chain_zap": 0.6, "aura_pulse": 0.55, "explosion_small": 0.7, "explosion_big": 0.95,
    "pickup_xp1": 0.32, "pickup_xp2": 0.32, "pickup_xp3": 0.32, "pickup_coin": 0.5,
    "pickup_heal": 0.7, "levelup": 0.9, "wave_start": 0.8, "boss_spawn": 1.0,
    "boss_die": 1.0, "victory": 1.0, "game_over": 1.0, "ui_click": 0.6,
    "ui_hover": 0.35, "ui_deny": 0.6, "shop_buy": 0.8, "shop_reroll": 0.8,
    "merge": 0.85, "crate_break": 0.7, "tape_hit": 0.5,
}


class Audio:
    def __init__(self, settings):
        self.settings = settings
        self.enabled = False
        try:
            import pygame.mixer  # noqa: F401  (en WASM el submódulo se carga aquí)
        except Exception:
            pass
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.missing: list[str] = []
        self._map = {"sfx": {}, "music": {}}
        self._music_channels = [None, None]  # canal A/B para crossfade
        self._active_music = 1
        self._current_track: str | None = None
        self._duck_timer = 0.0
        self._duck_amount = 0.0
        self._now = 0.0
        self._last: dict[str, float] = {}
        try:
            # 44100 estéreo: es la frecuencia nativa de los OGG de Kenney; con
            # 22050 mono SDL_mixer se cuelga al reprocesar (access violation real).
            pygame.mixer.pre_init(44100, -16, 2, 256)
            pygame.mixer.init()
            pygame.mixer.set_num_channels(28)
            self.enabled = True
        except Exception as e:  # sin dispositivo de audio: seguimos en silencio
            print(f"[audio] mixer no disponible: {e}")
        if self.enabled:
            self._load_map()
            self._load_all()
            self._music_channels = [pygame.mixer.Channel(26), pygame.mixer.Channel(27)]

    # ------------------------------------------------------------------ carga
    def _load_map(self) -> None:
        p = K.AUDIO_MAP_PATH
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._map["sfx"] = data.get("sfx", {}) or {}
            self._map["music"] = data.get("music", {}) or {}
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"[audio] audio_map.json ilegible: {e}")

    def _candidates(self, kind: str, name: str):
        rel = self._map.get(kind, {}).get(name)
        if rel:
            yield K.ASSETS / rel
        if kind == "sfx":
            yield K.SFX_DIR / f"{name}.wav"
            yield K.SFX_DIR / f"{name}.ogg"   # build web (pygbag exige OGG)
            for ext in (".ogg", ".wav", ".mp3"):
                yield K.ASSETS / "audio_kenney" / f"{name}{ext}"
        else:
            yield K.MUSIC_DIR / f"{name}.wav"
            yield K.MUSIC_DIR / f"{name}.ogg"
            yield K.ASSETS / "music_ext" / f"{name}.ogg"

    def _load_all(self) -> None:
        for name in SFX_NAMES:
            snd = None
            for cand in self._candidates("sfx", name):
                if cand.exists():
                    try:
                        snd = pygame.mixer.Sound(str(cand))
                        break
                    except Exception as e:
                        print(f"[audio] fallo cargando {cand.name}: {e}")
            if snd is None:
                self.missing.append(name)
            else:
                self.sounds[name] = snd
        self._music_cache: dict[str, pygame.mixer.Sound] = {}
        for t in MUSIC_TRACKS:
            for cand in self._candidates("music", t):
                if cand.exists():
                    try:
                        self._music_cache[t] = pygame.mixer.Sound(str(cand))
                        break
                    except Exception as e:
                        print(f"[audio] música {cand.name}: {e}")
        self.refresh_volumes()

    # ------------------------------------------------------------------ volumen
    def refresh_volumes(self) -> None:
        if not self.enabled:
            return
        master = float(self.settings["vol_master"])
        vs = float(self.settings["vol_sfx"])
        vm = float(self.settings["vol_music"])
        for name, snd in self.sounds.items():
            base = SFX_BASE_VOL.get(name, 0.6)
            snd.set_volume(max(0.0, min(1.0, base * vs * master)))
        self._music_vol = max(0.0, min(1.0, vm * master))

    # ------------------------------------------------------------------ sfx
    def _cooldown(self, name: str) -> float:
        if name.startswith("ui_hover"):
            return 0.08
        if name in ("hit_enemy", "hit_crit", "enemy_die", "shoot_tack", "pickup_xp1"):
            return 0.03
        return 0.02

    def play(self, name: str, vol: float = 1.0, pitch: int = 0) -> None:
        if not self.enabled:
            return
        snd = self.sounds.get(name)
        if snd is None:
            return
        if self._now - self._last.get(name, -9.0) < self._cooldown(name):
            return
        self._last[name] = self._now
        try:
            base = SFX_BASE_VOL.get(name, 0.6)
            v = max(0.0, min(1.0, base * vol * float(self.settings["vol_sfx"]) * float(self.settings["vol_master"])))
            snd.set_volume(v)
            snd.play()
        except pygame.error:
            pass

    def play_xp(self, streak: int) -> None:
        """Blip de recuerdo con escalado por racha."""
        name = "pickup_xp1" if streak < 12 else ("pickup_xp2" if streak < 30 else "pickup_xp3")
        self.play(name)

    # ------------------------------------------------------------------ música
    def play_music(self, track: str, fade: float = 0.8) -> None:
        if not self.enabled:
            self._current_track = track
            return
        if track == self._current_track:
            return
        snd = self._music_cache.get(track)
        self._current_track = track
        if snd is None:
            return
        # canal activo -> pasivo, nueva pista en el otro canal
        old = self._music_channels[self._active_music]
        self._active_music = 1 - self._active_music
        new = self._music_channels[self._active_music]
        if old is not None:
            old.fadeout(int(fade * 1000))
        if new is not None:
            new.set_volume(0.0)
            new.play(snd, loops=-1)
        self._fade_in = fade
        self._fade_t = 0.0

    def stop_music(self, fade: float = 0.6) -> None:
        if not self.enabled:
            self._current_track = None
            return
        for ch in self._music_channels:
            if ch is not None:
                ch.fadeout(int(fade * 1000))
        self._current_track = None

    def duck(self, amount: float = 0.5, duration: float = 1.2) -> None:
        self._duck_timer = duration
        self._duck_amount = amount

    def update(self, dt: float) -> None:
        self._now += dt
        if not self.enabled:
            return
        vol = getattr(self, "_music_vol", 0.7)
        if self._duck_timer > 0:
            self._duck_timer -= dt
            vol *= 1.0 - self._duck_amount
        # fade-in de la pista activa
        fade = getattr(self, "_fade_in", 0.0)
        if fade > 0:
            self._fade_t = getattr(self, "_fade_t", 0.0) + dt
            prog = min(1.0, self._fade_t / fade)
            vol *= prog
            if prog >= 1.0:
                self._fade_in = 0.0
        ch = self._music_channels[self._active_music] if self._music_channels else None
        if ch is not None and ch.get_busy():
            ch.set_volume(max(0.0, min(1.0, vol)))

    def report(self) -> dict:
        return {
            "enabled": self.enabled,
            "sfx_loaded": len(self.sounds),
            "sfx_missing": list(self.missing),
            "music_loaded": list(getattr(self, "_music_cache", {}).keys()),
        }
