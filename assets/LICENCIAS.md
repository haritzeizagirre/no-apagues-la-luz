# LICENCIAS — Assets externos ("No Apagues La Luz")

Fecha de descarga de todos los assets: **2026-10-10**.
Todo el contenido listado a continuación es **CC0 1.0 (dominio público)**; se indica por asset la fuente, autor y enlace a la página original.

---

## Aviso estándar de Kenney

> **License: (Creative Commons Zero, CC0)** — http://creativecommons.org/publicdomain/zero/1.0/
> This content is free to use in personal, educational and commercial projects.
> Support us by crediting Kenney or www.kenney.nl (this is not mandatory).
> — *License.txt, incluido en cada pack (assets/audio_kenney/<pack>/License.txt)*

Acreditar a Kenney **no es obligatorio** con CC0, pero se recomienda: `Audio: Kenney.nl (CC0)`.

---

## Audio — Kenney (CC0)

Fuente: https://kenney.nl — packs descargados desde la página oficial de cada pack.
Los zips originales fueron verificados (`zipfile.testzip`), extraídos planos (solo audio) y eliminados.
Índice máquina-legible: `assets/audio_kenney/manifest.json` (354 entradas con tags sugeridos).

| Pack | Archivos | Enlace de la página | License.txt |
|---|---|---|---|
| Impact Sounds v1.0 (2019) | 130 `.ogg` | https://kenney.nl/assets/impact-sounds | incluido |
| Interface Sounds v1.0 (2020) | 100 `.ogg` | https://kenney.nl/assets/interface-sounds | incluido |
| UI Audio v1.0 (2012) | 51 `.ogg` | https://kenney.nl/assets/ui-audio | incluido |
| Sci-Fi Sounds v1.0 | 73 `.ogg` | https://kenney.nl/assets/sci-fi-sounds | incluido |

- Autor: **Kenney** (www.kenney.nl) — Licencia: **CC0**.
- Ruta local: `assets/audio_kenney/<pack>/` (plano, sin subcarpetas).
- Nota: `Preview.ogg` del pack UI Audio (montaje de preview del pack, no un asset de juego) fue excluido.

---

## Música — OpenGameArt (CC0)

Licencia verificada en la página de cada asset (campo "License(s)"), no solo en el buscador.

### 1. EmptyCity: Background Music — uso: **menú / ambient oscuro**
- Autor: **yd** — Licencia: **CC0**
- Página: https://opengameart.org/content/emptycity-background-music
- Archivo: `assets/music_ext/EmptyCity.ogg` — soundtrack oscuro y loopable ("Exploring a devastated city").

### 2. 5 Chiptunes (Action) — uso: **combate / chiptune driving**
- Autor: **Juhani Junkala**, subido por **SubspaceAudio** — Licencia: **CC0**
- Página: https://opengameart.org/content/5-chiptunes-action
- Archivos en `assets/music_ext/`: `Juhani Junkala [Retro Game Music Pack] Level 1/2/3.ogg` (combate), `... Title Screen.ogg` (menú alternativo), `... Ending.ogg`.
- Nota: el zip original traía 5 WAV (~50 MB); fueron **convertidos localmente a OGG Vorbis** con ffmpeg (`-q:a 5`, ~6.4 MB) sin otra modificación. `junkala_INFO.txt` es el INFO.txt original del zip.

### 3. Boss Battle Theme (CleytonRX – Battle RPG Theme) — uso: **boss / tenso**
- Autor: **CleytonKauffman** — Licencia: **CC0**
- Página: https://opengameart.org/content/boss-battle-theme
- Archivo: `assets/music_ext/CleytonRX - Battle RPG Theme Var_0.ogg` — loop ("Looped: Yes").

### 4. Glorious victory fanfare NES — uso: **victoria / corto triunfal**
- Autor: **congusbongus** — Licencia: **CC0**
- Página: https://opengameart.org/content/glorious-victory-fanfare-nes
- Archivo: `assets/music_ext/victory2_0.ogg` — fanfarria estilo famicom/NES (famistudio).

### 5. Blackout — extra temático ("Lights Out")
- Autor: **SkyleTheFrench** — Licencia: **CC0** (el autor indica que acreditar no es obligatorio)
- Página: https://opengameart.org/content/blackout
- Archivo: `assets/music_ext/blackout_3mzut0qtwao.mp3` — música inspirada en *Lights Out*; encaja con el título del juego.

---

## Pixel art — OpenGameArt (CC0)

### 1. B&W SURREAL OFFICE RPG (1-bit sprites & tiles) — oficina, rejilla 16x16
- Autor: **SdiviHall** — Licencia: **CC0**
- Página: https://opengameart.org/content/bw-surreal-office-rpg-1-bit-sprites-and-tiles
- Ruta local: `assets/sprites_ext/bw_office_rpg/`
- Archivos: `tileset_58.png` (64×80, tiles de 16×16), `workers1.png` y `workers2.png` (384×256, sprites en rejilla de 16×16), `workerface1.png`, `workerface2.png` (128×64).
- Nota: estilo 1-bit (blanco y negro); temática de oficina corporativa surrealista.

### 2. indoor office appliances — decoración de oficina a color
- Autor: **semtex99** — Licencia: **CC0**
- Página: https://opengameart.org/content/indoor-office-appliances
- Ruta local: `assets/sprites_ext/office_appliances/`
- Archivos: `office-tilemap.png` y `office-tilemap_0.png` (160×160, tiles de 32×32; decoración de oficina/factory).

> **Nota honesta**: no se encontró ningún pack **CC0 de pixel art 16×16 a color** de objetos de oficina/escritorio.
> Los dos anteriores son los más cercanos y 100 % temáticos (uno 16×16 pero 1-bit B/N; otro a color pero 32×32).
> Se descartó, entre otros, *Interior Tileset 16x16* de Bonsaiheldin por ser **CC-BY-SA 3.0** (share-alike).

---

## Notas de proceso

- Kenney: los 5 packs candidatos existen; se descargaron 4 zips con `curl -fSL` desde los enlaces reales `kenney.nl/media/pages/assets/<slug>/<hash>/kenney_<slug>.zip`.
- OpenGameArt: la licencia de cada asset se comprobó en su página (campo `License(s): CC0`). Se prefirió CC0 siempre; no se usó ningún asset CC-BY+.
- Verificación final (magic bytes `OggS`/`RIFF`/`ID3`, tamaño >0, decodificación con ffprobe): ver informe de la tarea.
