"""Sincroniza los assets del APK independiente (apk_app) con el build web de pygbag.

Uso:
    .venv/Scripts/python.exe tools/sync_apk_assets.py

Toma el resultado de `tools/build_web.py --build` (build/web_src/build/web/) y lo
copia a apk_app/app/src/main/assets/ con los ajustes que exige el WebView:

  - index.html: URLs del CDN oficial -> https://appassets.androidplatform.net/cdn/
  - web_src.tar.gz -> web_src.gz.bin  (el aapt de Android descomprime y renombra
    los assets .gz; con extension neutra el archivo llega intacto y el
    interceptor de MainActivity lo sirve para la ruta /web_src.tar.gz)
  - fonts/, iconos, manifest, sw.js y favicon se copian tal cual

La carpeta assets/cdn/ (runtime pygbag + wheel, descargados del CDN publico) se
conserva; solo se comprueba que exista.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BUILD = RAIZ / "build" / "web_src" / "build" / "web"
DEST = RAIZ / "apk_app" / "app" / "src" / "main" / "assets"

URL_CDN_OFICIAL = "https://pygame-web.github.io/cdn/"
URL_CDN_LOCAL = "https://appassets.androidplatform.net/cdn/"

COPIAR_TAL_CUAL = [
    "fonts",
    "favicon.png",
    "icon_192.png",
    "icon_512.png",
    "icon_maskable.png",
    "icon_napal.png",
    "manifest.webmanifest",
    "sw.js",
]


def main() -> int:
    if not (BUILD / "index.html").exists():
        print(f"No hay build web en {BUILD}. Ejecuta antes: tools/build_web.py --build")
        return 1
    DEST.mkdir(parents=True, exist_ok=True)

    # 1) index.html con las URLs del CDN reescritas al origen local del WebView
    idx = (BUILD / "index.html").read_text(encoding="utf-8")
    n = idx.count(URL_CDN_OFICIAL)
    idx = idx.replace(URL_CDN_OFICIAL, URL_CDN_LOCAL)
    (DEST / "index.html").write_text(idx, encoding="utf-8")
    print(f"index.html: {n} URLs del CDN reescritas a appassets")

    # 2) archivo del juego con extension neutra (aapt descomprime los .gz)
    shutil.copy2(BUILD / "web_src.tar.gz", DEST / "web_src.gz.bin")
    kb = (DEST / "web_src.gz.bin").stat().st_size // 1024
    print(f"web_src.tar.gz -> web_src.gz.bin ({kb} KB)")

    # 3) resto de archivos del sitio
    for nombre in COPIAR_TAL_CUAL:
        origen = BUILD / nombre
        if origen.is_dir():
            shutil.copytree(origen, DEST / nombre, dirs_exist_ok=True)
        elif origen.exists():
            shutil.copy2(origen, DEST / nombre)
        else:
            print(f"AVISO: falta {origen}")
        print(f"copiado: {nombre}")

    # 4) el runtime del CDN debe seguir empaquetado; si falta, se descarga
    if not (DEST / "cdn" / "0.9.3" / "pythons.js").exists():
        print("assets/cdn/ no esta: descargando runtime del CDN publico...")
        descargar_cdn(DEST / "cdn")
    print("assets/cdn/ presente (runtime + wheel)")
    print("OK — ahora: cd apk_app && JAVA_HOME=<jdk21> ./gradlew assembleRelease")
    return 0


ARCHIVOS_CDN = [
    "0.9.3/pythons.js",
    "0.9.3/empty.html",
    "0.9.3/empty.ogg",
    "0.9.3/cpythonrc.py",
    "0.9.3/cpython312/main.js",
    "0.9.3/cpython312/main.data",
    "0.9.3/cpython312/main.wasm",
    "vt/xterm.js",
    "vt/xterm.css",
    "vt/xterm-addon-image.js",
    "vtx.js",
    "cp312/pygame_ce-2.5.7-cp312-cp312-wasm32_bi_emscripten.whl",
    "index-0.9.3-cp312.json",
]


def descargar_cdn(destino: Path) -> None:
    import urllib.request

    base = "https://pygame-web.github.io/cdn/"
    for rel in ARCHIVOS_CDN:
        out = destino / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(base + rel, timeout=180) as r:
            out.write_bytes(r.read())
        print(f"  descargado cdn/{rel} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    sys.exit(main())
