# NO APAGUES LA LUZ — Documento de diseño

Roguelike de oleadas ("survivor-like") 2D pixel, PC/Windows, offline, en español.
Protagonista: **LÍA**, una lámpara de escritorio que se niega a apagarse.

## Lore (mini)
Las oficinas del Edificio Möbius cierran a las 18:00. Cuando cae la última luz de
la planta, despierta **el OLVIDO**: todo lo que quisimos hacer y no hicimos cobra
cuerpo (post-its que exigen respuestas, clips que muerden, cables que estrangulan
y, al final de la noche, los Tres Jefes del calendario: El Despertador, La Reunión
Interminable y El Deadline). Solo **LÍA** se niega a apagarse. Cada noche aguanta
20 horas de turno; las monedas que roba a las sombras las guarda en **El Cajón de
los Recuerdos**, donde cada chispa comprada la hace un poco más inmortal.
Quien apaga la luz, alimenta al Olvido.

## Bucle de juego
- Run = **una noche = 20 horas-oleada** (~20 min con tiendas) + modo **Hora Extra** (endless).
- Oleadas de 28s(+3s/hora, cap 62s); las horas 5/10/15/20 son de JEFE (se acaba al matarlo).
- Combate **automático** (armas disparan solas), control total por movimiento + 2 activas:
  **Fogonazo** (Espacio): pulso de luz que daña/aturde todo lo iluminado; **Dash** (Shift): esquiva con i-frames.
- Al matar sueltan **Recuerdos** (XP) y **Monedas** (tienda). Subida de nivel → eliges 1 de 4 cartas
  (stats o mejoras especiales; algunas ligadas a tus armas). Fin de oleada → **Tienda**.

## Mecánica firma: la LUZ
- LÍA tiene un **radio de luz**. La oficina se oscurece conforme avanza la noche (alfa ambiental ↑ por hora).
- Enemigo **a la luz**: 100% daño recibido. **En penumbra**: recibe solo 65% y te hace 15% más de daño.
- Stats/ítems suben radio y potencia de luz. El Fogonazo disipa temporalmente la oscuridad.
- Alertas ambientales: **Incidencias del Turno** aleatorias (parpadeo/apagón, sobrecarga, cafés, llamada del jefe).
- Enemigos que **chupan luz** (Bombilla Fundida) reducen tu radio al acercarse. El jefe final ES la oscuridad.

## Sistemas de progresión
### Dentro de la run
- **Tienda "La Expendedora"** entre horas: 4 huecos (armas/ítems), pujar "Sacudir" (reroll), curita (cura), vender.
  - Garantía docente: horas 1–3 → mínimo 2 armas en tienda. Rarezas: T2 desde hora 2, T3 desde 5, T4 desde 9.
  - Reroll: `precio = piso(0.60*hora) + RI`, `RI = max(1, piso(0.35*hora))`, +RI por cada sacudida extra.
  - **Fusión**: dos armas iguales y mismo nivel → sube 1 nivel (max 4). Armas hasta 6 huecos; ítems ilimitados.
- **Nivel**: umbral cuadrático `XP = (nivel+3)^2` (≈14–18 niveles por noche). Cartas con downside frecuente.
### Meta (persistente)
- Moneda meta: **Chispas** (por noche jugada + sellos + multiplicadores de Marcas).
- **El Cajón de los Recuerdos**: ~20 mejoras permanentes multi-rango (vida, daño, luz, créditos, rerolls, revivir…).
- **Guardias 1–5** por cacharro: +22% PV / +15% daño enemigo por guardia; desbloquea la siguiente al ganar.
- **Desbloqueos**: 8 cacharros, ~14 armas, ~28 ítems, 6 Marcas y modo Hora Extra, vía 24 **Sellos** (logros).
- **Archivo** (bestiario) + estadísticas + historial de runs.

## Contenido
- **8 cacharros** jugables con perk única: Lía, Tosty, Ventilín, Taza, Grapón, Radio, Ratoncín, Alargador.
- **14 armas** con comportamiento distinto (disparo, escopeta, perforante, boomerang, cadena eléctrica,
  charco, rebote, arco melee, aura, nova, láser continuo, homing, pegajosa, lanzamiento AoE), 4 niveles + fusión.
- **~28 ítems** con stats +/- (mitad con downside). **~30 cartas** de subida (incl. especiales de arma).
- **16 enemigos** + **4 jefes** (El Despertador, La Reunión Interminable, El Deadline, EL OLVIDO) + élites.
- **Incidencias** del turno, **cajas de cartón** rompibles, props de oficina con colisión.

## Dirección artística y UI
- Resolución interna **640×360**. Ventana redimensionable libre como cualquier app de Windows (def. 1280×720, se abre centrada y recuerda el tamaño); escala entera cuando encaja (píxeles nítidos) y suave si no; **F11** pantalla completa y botón **RECENTRAR** de rescate en Ajustes.
- Paleta: azul noche + ámbar de lámpara + teal + papel crema. Sprites pixel generados por código (coherencia total).
- UI "papelería nocturna": notas adhesivas para cartas de subida, teclas para botones, máquina expendedora dibujada
  para la tienda, reloj de fichar para la hora/marcha de la oleada, barra de XP como cable. Fuentes OFL:
  Press Start 2P (títulos) + VT323 (texto) + Silkscreen (números).
- Juice: screenshake, hitstop, flash blanco, partículas, números de daño, banners de oleada/jefe, combo, glows aditivos,
  viñeta + oscuridad con máscara radial de luz, sonidos sintetizados + sample pack CC0 (Kenney), 4 temas musicales.

## Controles
WASD/flechas mover · Espacio Fogonazo · Shift Dash · Esc pausa · F11 pantalla completa · F3 debug · F12 captura.
Ratón para menús/tienda. Todo lo demás es automático.

## Tecnología
- Python 3.14 + pygame-ce. Código propio, datos en tablas Python (game/content/), guardado **atómico** en
  `%APPDATA%/NoApaguesLaLuz/` (meta + settings + historial). Sin red en runtime.
- Empaquetado: PyInstaller **onefile** → `dist/NoApaguesLaLuz.exe` (icono propio, versión, sin consola).
- Modos de diagnóstico integrados: `--selftest` (smoke headless + informe), `--simulate` (bot que juega noches
  enteras aceleradas y reporta balance), `--screenshot` (capturas PNG de menú/combate/tienda/jefe).

## Calidad (plan de pruebas)
1. pytest de lógica: contenido íntegro, economía, curva XP, guardado, fusión, multiplicador de luz, logros.
2. Simulación bot multi-personaje/multi-semilla: noches completas sin excepción, jefes matables, 0 NaN,
   caps respetados, compras viables; informe de balance (oleada media alcanzada, niveles, DPS).
3. Perf: paso de lógica <8 ms con 230 enemigos; render <8 ms; test de 10 min simulados.
4. Smoke de UI: cada pantalla renderiza 1 frame sin crash; clic en todos los botones.
5. Exe: `--selftest` sobre el binario + arranque real de ventana 10s + captura.
