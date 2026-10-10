"""Cura el audio real (Kenney CC0 + OpenGameArt CC0) y escribe assets/audio_map.json.

Reglas con lista de candidatos por sonido lógico; usa el primero que exista.
Los sonidos no listados siguen usando el set sintetizado (assets/sfx/*.wav).
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

# sonido lógico -> [candidatos relativos a assets/ o a audio_kenney/]
SFX_RULES = {
    "hit_enemy": ["audio_kenney/impact-sounds/impactGeneric_light_001.ogg",
                  "audio_kenney/impact-sounds/impactGeneric_light_000.ogg"],
    "hit_crit": ["audio_kenney/impact-sounds/impactPunch_medium_001.ogg",
                 "audio_kenney/impact-sounds/impactPunch_medium_000.ogg",
                 "audio_kenney/impact-sounds/impactGeneric_heavy_001.ogg",
                 "audio_kenney/impact-sounds/impactMetal_medium_001.ogg"],
    "enemy_die": ["audio_kenney/impact-sounds/impactSoft_medium_001.ogg",
                  "audio_kenney/impact-sounds/impactSoft_medium_000.ogg"],
    "enemy_die_big": ["audio_kenney/impact-sounds/impactSoft_heavy_001.ogg",
                      "audio_kenney/impact-sounds/impactSoft_heavy_000.ogg"],
    "explosion_small": ["audio_kenney/sci-fi-sounds/explosionCrunch_001.ogg",
                        "audio_kenney/sci-fi-sounds/explosionCrunch_000.ogg"],
    "explosion_big": ["audio_kenney/sci-fi-sounds/lowFrequency_explosion_001.ogg",
                      "audio_kenney/sci-fi-sounds/lowFrequency_explosion_000.ogg"],
    "crate_break": ["audio_kenney/impact-sounds/impactWood_heavy_001.ogg",
                    "audio_kenney/impact-sounds/impactWood_heavy_000.ogg",
                    "audio_kenney/impact-sounds/impactPlank_medium_001.ogg",
                    "audio_kenney/impact-sounds/impactPlank_medium_000.ogg"],
    "tape_hit": ["audio_kenney/impact-sounds/impactSoft_light_001.ogg",
                 "audio_kenney/impact-sounds/impactSoft_light_000.ogg"],
    "ui_click": ["audio_kenney/interface-sounds/click_002.ogg",
                 "audio_kenney/interface-sounds/click_001.ogg"],
    "ui_hover": ["audio_kenney/interface-sounds/tick_001.ogg",
                 "audio_kenney/interface-sounds/tick_002.ogg"],
    "ui_deny": ["audio_kenney/interface-sounds/error_002.ogg",
                "audio_kenney/interface-sounds/error_001.ogg"],
    "shop_buy": ["audio_kenney/interface-sounds/confirmation_002.ogg",
                 "audio_kenney/interface-sounds/confirmation_001.ogg"],
    "shop_reroll": ["audio_kenney/interface-sounds/switch_003.ogg",
                    "audio_kenney/interface-sounds/switch_001.ogg"],
    "merge": ["audio_kenney/impact-sounds/impactMining_001.ogg",
              "audio_kenney/impact-sounds/impactMining_000.ogg",
              "audio_kenney/impact-sounds/impactPlank_medium_002.ogg"],
    "player_hurt": ["audio_kenney/impact-sounds/impactPunch_heavy_001.ogg",
                    "audio_kenney/impact-sounds/impactPunch_heavy_000.ogg"],
    "pickup_heal": ["audio_kenney/interface-sounds/confirmation_004.ogg"],
}

MUSIC_MAP = {
    "menu": "music_ext/EmptyCity.ogg",
    "combat": "music_ext/Juhani Junkala [Retro Game Music Pack] Level 1.ogg",
    "combat2": "music_ext/Juhani Junkala [Retro Game Music Pack] Level 2.ogg",
    "combat3": "music_ext/Juhani Junkala [Retro Game Music Pack] Level 3.ogg",
    "boss": "music_ext/CleytonRX - Battle RPG Theme Var_0.ogg",
    "victory": "music_ext/victory2_0.ogg",
}


def resolve(cands):
    for c in cands:
        p = os.path.join(ASSETS, c)
        if os.path.exists(p):
            return c
    # búsqueda laxa por nombre base en audio_kenney
    for c in cands:
        base = os.path.basename(c).lower()
        for root, _dirs, files in os.walk(os.path.join(ASSETS, "audio_kenney")):
            for f in files:
                if f.lower() == base:
                    return os.path.relpath(os.path.join(root, f), ASSETS).replace("\\", "/")
    return None


def main() -> int:
    sfx = {}
    missing = []
    for name, cands in SFX_RULES.items():
        got = resolve(cands)
        if got:
            sfx[name] = got
        else:
            missing.append(name)
    music = {}
    for name, rel in MUSIC_MAP.items():
        if os.path.exists(os.path.join(ASSETS, rel)):
            music[name] = rel
        else:
            missing.append(f"music:{name}")
    data = {"sfx": sfx, "music": music, "_nota": "Generado por tools/curate_audio.py — Kenney CC0 + OpenGameArt CC0"}
    out = os.path.join(ASSETS, "audio_map.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(json.dumps({"sfx_mapped": len(sfx), "music_mapped": len(music), "missing": missing}, ensure_ascii=False, indent=1))
    for k, v in sfx.items():
        print(f"  {k:>16} <- {v}")
    for k, v in music.items():
        print(f"  music/{k:>10} <- {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
