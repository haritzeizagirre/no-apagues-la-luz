# Build web / móvil (pygbag) — estado y hallazgos

Spike de viabilidad del puerto a navegador/móvil con **pygbag** (pygame-ce → WebAssembly),
**sin reescribir el juego**: la misma base de código corre en PC (exe) y en navegador/móvil.

## Lo que YA funciona (verificado con evidencia real)
- `pygbag --ume_block 0 --build main_web.py` empaqueta el juego completo: **454 archivos → `web_src.apk` (~22 MB)**.
- El pipeline arranca en Chrome: CPython 3.12 WASM → wheel **pygame-ce 2.5.7 WASM** (1,5 MB) → desempaquetado de la app (21 MB).
- **Nuestro código se ejecuta en el navegador**: la pestaña pasa a llamarse
  "NO APAGUES LA LUZ — el turno de las sombras" (lo hace `pygame.display.set_caption`) y se crea
  el canvas 1280×720 (lo hace `set_mode`).
- Audio: **pygbag rechaza WAV** (y MP3) → se convirtió todo a OGG con ffmpeg. `game/audio.py` ya acepta
  `.ogg` como candidato de `assets/sfx/<nombre>.ogg`.

## Bloqueo actual (lo que falta para que sea jugable en web)
Tras arrancar la app, el hilo principal queda saturado y **no devuelve el control al navegador**
(sin repintado, sin input, sin consola; CPU ~100% de un núcleo; CDP sin responder durante minutos).
Plan de ataque, por orden de probabilidad:
1. **Bucle**: pygbag ejecuta Python en el hilo principal; hay que encontrar el patrón de cesión correcto
   (`await asyncio.sleep(0)` y `sleep(0.016)` no bastaron). Revisar wiki de pygbag (main loop / onCustomMessage).
2. **Coste por frame**: render en software a 1280×720 (escala desde 640×360). En web: ventana 640×360,
   evitar `smoothscale` por frame, y **perfil de calidad** (menos partículas/enemigos, 30 fps opcional).
3. Descartar trabajo pesado dentro de `build_app` (pantalla de carga + ceder entre fases).

Verificación: `tools/web_check.py` (controlador CDP propio: espera en tiempo real, consola del runtime,
screenshot y análisis de píxeles, sin depender de herramientas externas).

## Guardado en web
- `%APPDATA%` no existe en el navegador: `const.py` cae a `Path.home()` (FS virtual **volátil**).
- BrowserFS no está disponible (404 en el CDN de pygbag) → plan: persistir `meta.json`/`settings.json`
  en `localStorage`/IndexedDB vía `platform.window`, con detección de entorno web.

## Móvil (táctil)
- El input ya está centralizado (`core.Input`) → añadir capa táctil: joystick virtual + botones
  (fogonazo/dash) dibujados en pantalla; usar eventos `pygame.FINGER*` (SDL2 los soporta en móvil).
- Los tooltips (hover) pasan a "tap para mostrar". La UI ya escala por enteros y la ventana es redimensionable.

## Comandos del spike
```bash
# empaquetar (desde build/web_src: copia de main.py + game/ + assets/ + main_web.py + _beacon.py)
../../.venv/Scripts/python.exe -m pygbag --ume_block 0 --build main_web.py

# servidor de desarrollo — PUERTO 8000 IMPRESCINDIBLE: el wheel de pygame se pide a localhost:8000
../../.venv/Scripts/python.exe -m pygbag --ume_block 0 main_web.py

# verificación automatizada (Chrome headless con --remote-debugging-port=9222)
./.venv/Scripts/python.exe tools/web_check.py http://localhost:8000/ out.png
```

Notas: pygbag solo acepta OGG/OPUS; `--ume_block 0` evita la pantalla "clic para empezar"
(en Safari móvil, además, no reproducir sonido al inicio). El puerto nativo Android vía
`python-for-android` está descartado (Kivy eliminó el bootstrap de pygame): la vía realista
en móvil es **PWA** (instalar desde el navegador) o un port a otro motor si algún día se
quiere APK/tiendas.
