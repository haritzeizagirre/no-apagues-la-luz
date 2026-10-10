# NO APAGUES LA LUZ 🔆
**el turno de las sombras** — un roguelike de oleadas ("survivor-like") de oficina nocturna, en español, para PC y offline.

> Eres **LÍA**, una lámpara de escritorio que se niega a apagarse.
> Cuando la oficina cierra, despierta **el OLVIDO** y solo tu luz lo contiene:
> en penumbra haces mucho menos daño… y los que acechan en la oscuridad pegan más fuerte.

![pill](tools/_no_pill.png)

## Cómo se juega
- **WASD / flechas** mover · **ESPACIO** Fogonazo (pulso de luz que aturde y daña) · **SHIFT** Dash (esquiva con invulnerabilidad) · **ESC** pausa · **F11** pantalla completa · **F12** captura.
- Las armas **disparan solas** (14 armas con comportamientos distintos). Sube de nivel y elige **cartas**; entre horas compra en **LA EXPENDEDORA** (sacude la máquina para reroll, fusiona armas repetidas, vende lo que no uses).
- **La noche dura 20 horas** (18:00 → 13:00). Horas 5/10/15/20 tienen **jefe**. Si lo superas: **HORA EXTRA** (endless).
- En penumbra haces un 65% de daño: mantén a los enemigos **dentro de tu luz**. Las **Bombillas Fundidas** te roban el radio de luz; las **Sombras** corren rápido en la oscuridad.
- Meta-progresión: gana **CHISPAS**, gástalas en **EL CAJÓN DE LOS RECUERDOS**, supera **GUARDIAS 1–5**, completa **29 SELLOS** que desbloquean 8 cacharros jugables, armas, ítems y **MARCAS DEL TURNO** (riesgo ↔ recompensa).

## Jugarlo ya
1. **Windows**: ejecuta `dist\NoApaguesLaLuz.exe` (doble clic). No instala nada, no necesita conexión.
   *(Si el SmartScreen te avisa por ser un .exe recién creado y sin firma: Más información → Ejecutar de todas formas.)*
2. **Desde el código**: `\.venv\Scripts\python.exe main.py`

## Compilar el .exe
```bat
.venv\Scripts\python.exe tools\build_exe.py
```
Genera `dist\NoApaguesLaLuz.exe` (onefile, con icono y metadatos de versión) e `dist\informe_build.json`.

## Modos de diagnóstico
```bat
.venv\Scripts\python.exe main.py --selftest     :: integridad + sims + rendimiento (headless)
.venv\Scripts\python.exe main.py --simulate --char lia --guardia 2 --muts apagon --seed 7 --minutes 25
.venv\Scripts\python.exe main.py --screenshot   :: capturas de las pantallas clave
.venv\Scripts\python.exe tools\simbatch.py 12 lia 1   :: lote de balance con bot
.venv\Scripts\python.exe tools\gen_audio.py     :: regenera los SFX/música sintetizados
.venv\Scripts\python.exe tools\curate_audio.py  :: re-cura el audio real (Kenney/OGA) → audio_map.json
```

## Tests
```bat
.venv\Scripts\python.exe -m pytest tests/ -q    :: 284 tests (contenido, sprites, economía, mundo, save, audio)
```

## Estructura
```
main.py                punto de entrada + modos de diagnóstico
game/
  const.py             paleta, stats base, rutas, constantes de diseño
  core.py              motor: input, cámara(shake), partículas, textos, hash, fuentes, App
  gui.py               UI inmediata (teclas, notas adhesivas, sliders, tooltips)
  sprites.py           TODO el arte se dibuja por código (51 sprites + suelo + helpers)
  icons.py             iconos de armas/ítems/stats/UI (dibujados por código)
  audio.py             SFX + música (mapa Kenney/OGA con fallback sintetizado)
  save.py              guardado atómico en %APPDATA%\NoApaguesLaLuz
  entities.py          jugador, enemigos, proyectiles, pickups, props
  weapons.py           disparo de los 13 tipos de arma
  world.py             la noche entera: oleadas, IA, luz/oscuridad, tienda, jefes, render
  run_ui.py            HUD + cartas + tienda + pausa + resumen
  screens.py           portada, historia, selección, El Cajón, Sellos, Archivo, Ajustes
  simharness.py        bot + simulación rápida (balance y QA)
  content/             datos: armas, ítems, enemigos/jefes, cacharros, sellos, marcas, textos
tests/                 284 tests
tools/                 gen_audio, curate_audio, build_exe, make_icon, simbatch
docs/referencias.md    dossier de diseño del género (con fuentes)
```

## Créditos y licencias
- Código y arte por código: generados para este proyecto.
- Fuentes: **Press Start 2P**, **VT323**, **Silkscreen** (Google Fonts, OFL).
- Audio: set sintetizado propio + **Kenney.nl** (CC0) + **OpenGameArt** CC0 — detalle en `assets/LICENCIAS.md`.
- Gracias por no apagar la luz.
