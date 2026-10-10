"""Genera assets/icon.ico (lámpara sobre fondo noche) sin dependencias externas."""
from __future__ import annotations

import os
import struct
import sys
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from game import const as K  # noqa: E402
from game import sprites as S  # noqa: E402


def build_icon_png(size: int) -> bytes:
    pygame.display.init()
    pygame.display.set_mode((64, 64))
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    # fondo redondeado
    pygame.draw.rect(surf, (16, 20, 38), (0, 0, size, size), border_radius=max(4, size // 6))
    pygame.draw.rect(surf, (44, 58, 99), (0, 0, size, size), max(1, size // 48), border_radius=max(4, size // 6))
    # lámpara escalada
    lamp = S.get("char_lia").n
    scale = max(1, int(size * 0.72 / lamp.get_width()))
    big = pygame.transform.scale(lamp, (lamp.get_width() * scale, lamp.get_height() * scale))
    surf.blit(big, ((size - big.get_width()) // 2, (size - big.get_height()) // 2 + size // 14))
    # halo
    g = S.glow(max(8, size // 3), (255, 190, 110), 90)
    surf.blit(g, (size // 2 - g.get_width() // 2, size // 2 - g.get_height() // 2),
              special_flags=pygame.BLEND_RGB_ADD)
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.close()
    pygame.image.save(surf, tmp.name)
    with open(tmp.name, "rb") as fh:
        data = fh.read()
    os.unlink(tmp.name)
    return data


def write_ico(path: str, sizes=(256, 64, 32, 16)) -> None:
    images = [(sz, build_icon_png(sz)) for sz in sizes]
    header = struct.pack("<HHH", 0, 1, len(images))
    entries = b""
    offset = 6 + 16 * len(images)
    payload = b""
    for sz, data in images:
        w = 0 if sz >= 256 else sz
        entries += struct.pack("<BBBBHHII", w, w, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
        payload += data
    with open(path, "wb") as f:
        f.write(header + entries + payload)


if __name__ == "__main__":
    out = os.path.join(K.RES, "assets", "icon.ico")
    write_ico(out)
    print(f"[icono] {out} ({os.path.getsize(out)} bytes)")
