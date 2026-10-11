"""Construye la version web (pygbag) en build/web_src y empaqueta con pygbag.

Uso:
    ./.venv/Scripts/python.exe tools/build_web.py            # monta y sirve en :8000 (dev)
    ./.venv/Scripts/python.exe tools/build_web.py --build    # solo empaqueta

Reglas aprendidas (detalle en docs/WEB-MOVIL.md):
- pygbag SIEMPRE ejecuta build/web_src/main.py -> debe ser la entrada ASYNC (main_web.py).
  La entrada de escritorio se conserva como desktop_entry.py (main_web importa build_app de ahi).
- Todo el audio debe ser OGG (pygbag rechaza WAV/MP3).
- El bucle del juego debe usar `await asyncio.sleep(0)`: los sleeps con temporizador
  NO resuelven en el modo "main thread" de pygbag.
- El servidor de desarrollo de pygbag debe correr en el puerto 8000 (el runtime pide
  ahi el wheel de pygame-ce).
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "build" / "web_src"


def stage() -> None:
    WEB.mkdir(parents=True, exist_ok=True)
    # entrada de escritorio (para importar build_app) y entrada web como main.py
    shutil.copy2(ROOT / "main.py", WEB / "desktop_entry.py")
    shutil.copy2(ROOT / "main_web.py", WEB / "main.py")
    # codigo del juego
    dst = WEB / "game"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(ROOT / "game", dst, ignore=shutil.ignore_patterns("__pycache__"))
    # assets (una vez; las siguientes builds reutilizan)
    assets_dst = WEB / "assets"
    if not assets_dst.exists():
        shutil.copytree(ROOT / "assets", assets_dst,
                        ignore=shutil.ignore_patterns("raw_downloads"))
    # convertir WAV/MP3 -> OGG si quedara alguno (pygbag los rechaza).
    # la musica en 44100 q6 (el 22050 mono sonaba "saturado"); los sfx en 22050 q4
    for w in list(assets_dst.rglob("*.wav")) + list(assets_dst.rglob("*.mp3")):
        ogg = w.with_suffix(".ogg")
        print(f"[web] convirtiendo {w.name} -> ogg")
        if "music" in w.parts:
            enc = ["-ac", "1", "-ar", "44100", "-c:a", "libvorbis", "-q:a", "6"]
        else:
            enc = ["-ac", "1", "-ar", "22050", "-c:a", "libvorbis", "-q:a", "4"]
        subprocess.run(["ffmpeg", "-y", "-i", str(w)] + enc + [str(ogg)],
                       check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if ogg.exists():
            w.unlink()
    # favicon web = lampara del juego (la plantilla de pygbag trae el icono por
    # defecto de pygame-ce, la "rana"; se sustituye favicon.png de la raiz servida)
    web_icon = ROOT / "assets" / "icon_web.png"
    if not web_icon.exists():
        subprocess.call([sys.executable, str(ROOT / "tools" / "make_icon.py")])
    out_dir = WEB / "build" / "web"
    out_dir.mkdir(parents=True, exist_ok=True)
    if web_icon.exists():
        # icon_napal.png = el que usa NUESTRA plantilla (pygbag re-escribe favicon.png
        # en cada build con el suyo por defecto, asi que no podemos usar ese nombre)
        shutil.copy2(web_icon, out_dir / "icon_napal.png")
        shutil.copy2(web_icon, out_dir / "favicon.png")
        print("[web] favicon = lampara del juego (icon_napal.png)")
    # fuentes para la pantalla de carga del template
    fonts_dir = out_dir / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    for ttf in ("PressStart2P-Regular.ttf", "Silkscreen-Regular.ttf"):
        src = ROOT / "assets" / "fonts" / ttf
        if src.exists():
            shutil.copy2(src, fonts_dir / ttf)
    print(f"[web] montaje listo en {WEB}")


def main() -> int:
    args = sys.argv[1:]
    stage()
    tmpl = ROOT / "tools" / "web_template.tmpl"
    # SIN --ume_block 0: el runtime espera al primer gesto (MM.UME) antes de
    # arrancar; asi el AudioContext se crea DESPUES del toque y el audio suena
    # en movil (con ume_block 0 nace suspendido y el movil se queda mudo).
    cmd = [sys.executable, "-m", "pygbag"]
    if tmpl.is_file():
        cmd += ["--template", str(tmpl)]
    if "--lan" in args:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            lan_ip = s.getsockname()[0]
        finally:
            s.close()
        cmd += ["--bind", lan_ip]
        print(f"[web] servidor accesible en la red local: http://{lan_ip}:8000/")
        print("[web] (abrelo desde el movil conectado a la misma wifi)")
    if "--port" in args:
        i = args.index("--port")
        if i + 1 < len(args):
            cmd += ["--port", args[i + 1]]
    if "--build" in args:
        cmd.append("--build")
    cmd.append(".")
    print("[web] pygbag:", " ".join(cmd[2:]))
    rc = subprocess.call(cmd, cwd=WEB)
    # pygbag --build re-escribe favicon.png con su rana por defecto DESPUES de
    # nuestra copia: reponer la lampara al terminar el build
    web_icon = ROOT / "assets" / "icon_web.png"
    out_dir = WEB / "build" / "web"
    if web_icon.exists() and out_dir.is_dir():
        shutil.copy2(web_icon, out_dir / "favicon.png")
        shutil.copy2(web_icon, out_dir / "icon_napal.png")
        print("[web] favicon restaurado (lampara) tras el build")
    # PWA: manifest + iconos de app + service worker (version de cache por build)
    if out_dir.is_dir():
        for name in ("icon_192.png", "icon_512.png", "icon_maskable.png"):
            src = ROOT / "assets" / name
            if src.exists():
                shutil.copy2(src, out_dir / name)
        man = ROOT / "tools" / "manifest.webmanifest"
        if man.is_file():
            shutil.copy2(man, out_dir / "manifest.webmanifest")
        sw = ROOT / "tools" / "sw.js"
        if sw.is_file():
            stamp = str(int(__import__("time").time()))
            txt = sw.read_text(encoding="utf-8").replace("__V__", stamp)
            (out_dir / "sw.js").write_text(txt, encoding="utf-8")
        print("[web] PWA lista: manifest + iconos + sw.js (cache v" + stamp + ")" if sw.is_file() else "[web] PWA: manifest + iconos")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
