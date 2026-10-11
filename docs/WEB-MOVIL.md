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

## Táctil en partida (móvil)

- **Movimiento = joystick virtual** abajo-izquierda (`game/world.py`: `STICK_BASE`,
  `STICK_ZONE`, `_stick_move`, `draw_stick`). El dedo dentro de la zona genera un
  vector (dx,dy); velocidad proporcional.
- **Botones táctiles** (`game/run_ui.py` `_ui_touch`): pausa (II, arriba-derecha),
  DASH y FOGO (abajo-derecha, 92×44). Se registran en `draw()`, NUNCA en `update()`
  (el GUI dibuja al instante y el draw del mundo los taparía).
- **Segundo dedo (crítico)**: SDL solo emula el ratón con el puntero primario — con
  el joystick sujeto, un segundo dedo en DASH/FOGO no genera clic. Los botones
  escuchan también FINGERDOWN directos (`Input.taps` + hit-test con coordenadas
  convertidas ventana→juego).
- **Teclas virtuales** (`Input.press_virtual`): limpiar DESPUÉS del update del
  frame siguiente (update → clear_virtual → draw); limpiarlas tras draw las mata.
- **Detección de dispositivo**: `has_touch` (True al primer FINGERDOWN) + ajuste
  TÁCTILES: AUTO/SÍ/NO → en navegador de PC no aparecen joystick ni botones. La
  guía de la primera ronda cambia el texto de controles según el modo.
- **Móvil en vertical**: aviso "GIRA EL MÓVIL PARA JUGAR" (al tocarlo → pantalla
  completa). En horizontal el juego llena la pantalla; si no, ajuste LLENAR.

## Trampas de audio/settings/staging (lecciones)

- **El staging se re-copia en CADA build**: `build_web.py` copia `main_web.py` de la
  RAÍZ a `build/web_src/main.py`. Los parches van SIEMPRE a la raíz.
- **Nunca dejes `vol_music`/`vol_sfx` a 0 en el prep de settings web** — deja el
  juego mudo. En web el prep solo toca lo imprescindible.
- **Audio móvil = gate del gesto (MM.UME)**: `--ume_block 0` arranca sin gesto →
  AudioContext suspendido → mudo en móvil. Con el default, el template espera al
  primer toque ("▶ TOCA PARA EMPEZAR" en el infobox) y el mixer nace tras el gesto.
- **Música "saturada"**: OGG 22050 mono q4 suena mal; música → 44100 q6 (los sfx
  cortos valen a 22050 q4). El staging NO re-convierte OGGs existentes: borrarlos y
  reponer los WAV originales.
- **Favicon**: `pygbag --build` re-escribe `favicon.png` (su rana) DESPUÉS de
  cualquier copia previa → `build_web.py` la repone tras el subprocess.
- Diagnóstico: `vol=... aud=... taps=...` en el log cada 300 frames.

## APK Android independiente (apk_app/) — sin navegador

La TWA (Bubblewrap) SIEMPRE abre Chrome por debajo. Para una app de verdad:
`apk_app/` = proyecto Android minimo con un **WebView** + `WebViewAssetLoader`
que sirve el juego entero desde dentro del APK. Sin permiso de INTERNET.

- **Sincronizar assets**: `.venv/Scripts/python.exe tools/sync_apk_assets.py`
  (copia `build/web_src/build/web/` → `apk_app/app/src/main/assets/`, reescribe
  las 6 URLs del CDN a `https://appassets.androidplatform.net/cdn/` y renombra
  `web_src.tar.gz` → `web_src.gz.bin`).
- **Compilar**: `cd apk_app && JAVA_HOME="/c/Program Files/Android/Android Studio/jbr" ./gradlew assembleRelease`
- **Trampas del empaquetado** (todas sufridas, ver skill pygbag-web-port):
  - El runtime lleva URLs del CDN oficial incrustadas (p.ej. `index-0.9.3-cp312.json`).
    `MainActivity` intercepta el host `pygame-web.github.io` y sirve `/cdn/...`
    desde los assets locales — **con CORS** (`Access-Control-Allow-Origin: *`),
    sin ello el fetch cross-origin muere con "Failed to fetch".
  - **El aapt de Android descomprime y renombra los assets `.gz`**: el runtime pide
    `web_src.tar.gz` y en el paquete llegaba como `web_src.tar` ya descomprimido
    (tarfile.ReadError). Solución: guardarlo como `web_src.gz.bin` (gzip intacto)
    y servirlo para esa ruta desde `MainActivity`.
  - Depurar el WebView: `WebView.setWebContentsDebuggingEnabled(true)` +
    `adb forward tcp:9224 localabstract:webview_devtools_remote_<pid>` + CDP
    (`Runtime.consoleAPICalled` tras `Page.reload` muestra los prints de Python).
- **OJO (emulador)**: con `-gpu swiftshader_indirect` el arranque es lentisimo;
  validar antes el conjunto de assets en Chrome de escritorio (http.server + CDP)
  para distinguir "assets mal montados" de "emulador lento".

## Pendiente (siguiente paso del port)

- **Guardado en web**: el FS del navegador no persiste; usar IDBFS/localStorage.
  (Consecuencia actual: la guía del primer turno sale en cada carga.)
- **APK**: falta confirmar el arranque completo en un movil real (en el emulador
  con swiftshader el boot es extremadamente lento) y publicarlo en el hub.
- **Rendimiento en móvil**: medido y confirmado bueno por el usuario.

(Resuelto en esta iteración: joystick táctil; botones de pausa/DASH/FOGO visibles;
música en web (vol a 0 fuera); mapas rediseñados con rejilla de oficina con sentido;
aviso de girar el móvil; favicon repuesto tras el build; APK independiente compilado
y con el arranque resuelto a nivel de assets.)
