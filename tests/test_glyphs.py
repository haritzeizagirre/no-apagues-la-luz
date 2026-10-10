"""Cobertura de glifos: ningún carácter usado en el juego debe renderizarse como 'tofu'.

Las fuentes pixel (VT323, Silkscreen, Press Start 2P) no traen muchos símbolos
(▶ ✦ ✔ ↑ ↓ ✓ ◀ ✕ ★ …). core.Fonts.san() los sustituye por equivalentes soportados;
este test escanea TODO el código fuente y comprueba, en cada fuente y tamaño que usa
el juego, que ningún carácter sale idéntico al glifo 'notdef'.
"""
import pathlib

import pygame
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
NOTDEF = "\ue001"  # área privada Unicode: seguro que no existe en estas fuentes

FONT_FILES = {
    "psp": "PressStart2P-Regular.ttf",
    "vt": "VT323-Regular.ttf",
    "silk": "Silkscreen-Regular.ttf",
    "silkb": "Silkscreen-Bold.ttf",
}


def _used_chars() -> set:
    chars = set()
    for p in list((ROOT / "game").rglob("*.py")) + [ROOT / "main.py"]:
        chars |= {c for c in p.read_text(encoding="utf-8") if ord(c) > 127}
    return chars


def _blob(font, s):
    img = font.render(s, False, (255, 255, 255))
    return (img.get_size(), pygame.image.tobytes(img, "RGBA"))


@pytest.mark.parametrize("kind,fname", sorted(FONT_FILES.items()))
def test_no_tofu_glyphs(kind, fname):
    pygame.font.init()
    from game.core import Fonts
    path = ROOT / "assets" / "fonts" / fname
    used = sorted(_used_chars())
    for size in (9, 11, 13, 16, 18, 24):
        f = pygame.font.Font(str(path), size)
        notdef = _blob(f, NOTDEF)
        for ch in used:
            s = Fonts.san(ch)
            got = _blob(f, s)
            assert got != notdef, f"{fname}@{size}: {ch!r} sale como tofu (fallback {s!r} también falla)"


def test_glyph_fallback_covers_used_symbols():
    """Cada símbolo problemático del inventario debe tener sustituto en el mapa."""
    from game.core import Fonts
    problematic = "▶►◀◄✕✓✔✦★◆↔→↑↓🗡"
    for ch in problematic:
        assert ch in Fonts.GLYPH_FALLBACK, f"falta fallback para {ch!r}"
        assert Fonts.san(ch) != ch or ord(ch) < 128
