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
    surf = S.lamp_icon(size)  # lámpara clara (misma que en la ventana)
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
    # favicon web (lo copia tools/build_web.py a build/web/favicon.png)
    web = os.path.join(K.RES, "assets", "icon_web.png")
    with open(web, "wb") as f:
        f.write(build_icon_png(64))
    print(f"[icono] {web} ({os.path.getsize(web)} bytes)")
    # iconos PWA (192/512) + maskable (lampara al ~72% sobre fondo noche, zona
    # segura de las mascaras redondas de Android)
    for sz in (192, 512):
        p = os.path.join(K.RES, "assets", f"icon_{sz}.png")
        with open(p, "wb") as f:
            f.write(build_icon_png(sz))
        print(f"[icono] {p} ({os.path.getsize(p)} bytes)")
    mask = pygame.Surface((512, 512))
    mask.fill((14, 18, 31))
    inner = pygame.transform.smoothscale(S.lamp_icon(368), (368, 368))
    mask.blit(inner, (72, 72))
    p = os.path.join(K.RES, "assets", "icon_maskable.png")
    pygame.image.save(mask, p)
    print(f"[icono] {p} ({os.path.getsize(p)} bytes)")
