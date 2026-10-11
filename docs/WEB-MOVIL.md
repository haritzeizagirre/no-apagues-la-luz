# NO APAGUES LA LUZ — versión web/móvil (pygbag)

**Estado: JUGABLE EN EL NAVEGADOR** (verificado en Chrome real: menú → selección →
partida en marcha → movimiento con teclado a tiempo real; clics y táctil funcionan).

## Receta (lo que hace falta para que funcione)

1. **pygbag SIEMPRE ejecuta `main.py` del directorio que empaqueta** — ignora el
   argumento del script si existe `main.py`. Por eso el montaje usa:
   - `build/web_src/main.py` = **entrada web ASYNC** (copia de `main_web.py`).
   - `build/web_src/desktop_entry.py` = la entrada de escritorio (`main.py` del repo);
     `main_web.py` importa `build_app` de ahí.
   - Construir todo con: `tools/build_web.py` (monta + `pygbag --ume_block 0 [--build] .`).

2. **El bucle principal debe ser `await asyncio.sleep(0)`** (patrón canónico de pygbag).
   En el modo "main thread" del runtime, `asyncio.sleep(t)` **con temporizador nunca
   resuelve**: el bucle queda aparcado y solo avanza cuando llegan eventos del navegador
   (síntoma: la pantalla solo cambia al hacer clic).

3. **Reloj de tiempo real** (`_RealClock` en `main_web.py`): con `sleep(0)` el pump
   puede ir a >100 fps; el reloj debe devolver el tiempo real transcurrido para que
   `dt` sea correcto (si no, la partida corre acelerada). `Clock.tick` de pygame-ce es
   de solo lectura: se sustituye `app.clock` por un objeto propio.

4. **Compatibilidad WASM del código** (sin romper escritorio):
   - `pygame.math` no existe en el build → fallback mínimo de `Vector2` en `game/core.py`.
   - `pygame.init` / `display.init/quit` pueden faltar → guardas `hasattr`.
   - `pygame.mixer` se importa explícitamente (`import pygame.mixer`) antes de usarlo;
     si no está, el audio degrada con elegancia (sin sonido).
   - Fuentes TTF: `assets/fonts/*.ttf` cargan bien (verificado en WASM).

5. **Audio en OGG**: pygbag rechaza WAV/MP3 al empaquetar. `tools/build_web.py`
   convierte automáticamente con ffmpeg; `game/audio.py` ya acepta `.ogg` como
   candidato de sfx.

6. **Servidor en el puerto 8000**: el runtime pide el wheel de pygame-ce a
   `http://localhost:8000/cdn/...`. El servidor de desarrollo de pygbag ya sirve ahí
   (`tools/build_web.py` sin `--build`).

## Verificación (harness CDP)

- `tools/probe_read.py` — título de la pestaña + texto de la consola xterm. La terminal
  de la página es legible: `main_web.py` imprime `escena=<clase> pos=(x,y)` cada 300
  frames (navegación y movimiento verificables sin capturas).
- `tools/probe_interact.py GX GY` — clic en coordenadas del juego (640×360) + capturas
  before/hover/click + diff.
- `tools/shot.py OUT.png` — captura + volcado ASCII del juego (recorte del canvas).
- `tools/probe_watch.py` — vigila el título de la pestaña (útil en arranques).
- Chrome headless: `--headless=new --remote-debugging-port=9223 --remote-allow-origins=*`.
  **Matar Chrome en Windows: `powershell Stop-Process -Name chrome -Force`**
  (¡`taskkill //F` desde MSYS falla en silencio y las pestañas se acumulan!).
- El canvas en la página ocupa ~(259,0,765,765) con el juego letterboxed 16:9 dentro;
  ojo: la captura web sale con **alfa ~0.64** (colores ×0.64 sobre negro) al comparar
  con capturas de escritorio.

## Pendiente (siguiente paso del port)

- **Guardado en web**: el FS del navegador no persiste; usar IDBFS/localStorage.
- **Controles táctiles de juego** (joystick virtual): en móvil los menús ya funcionan
  con toques (touch→mouse); falta el movimiento en partida.
- **PWA/APK**: empaquetar `build/web` (service worker + manifest) y decidir TWA/WebView.
- **Rendimiento en móvil**: medir fps reales en un móvil; ajustar si hiciera falta.

(Resuelto en esta iteración: loader propio en la plantilla `tools/web_template.tmpl`;
canvas 16:9 estable con `napal_fit_canvas`; RECENTRAR/PANTALLA COMPLETA por JS del
navegador; favicon `icon_napal.png`; la atenuación de color del canvas desapareció al
pasar a backing 1280×720.)
