# Dossier de referencia — Survivor-likes
### Documento de diseño comparativo para «No Apagues La Luz» (survivor-like 2D pixel, runs ~20 min, luz/oscuridad como mecánica, oficina nocturna, tienda tipo máquina expendedora, dificultad «guardias»)

> **Cómo leer este documento.** Cada juego tiene una ficha con: loop central, estructura de sesión, progresión in-run, progresión meta, motivación para rejugar, patrones de UI y twist único, con URLs de fuentes. La sección 2 destila los patrones numéricos comunes; la 3 recoge las críticas conocidas del género; la 4 («LECCIONES APLICABLES») traduce todo a 20 decisiones concretas para nuestro juego. Última verificación de fuentes: octubre de 2026.

---

## 1. Análisis por juego

### Tabla resumen

| Juego | Run típica | Recurso in-run | Meta-moneda | Twist clave |
|---|---|---|---|---|
| Vampire Survivors | 15–30 min | XP + oro | Oro (PowerUps) | Oleadas guionizadas por minuto + cofres-evolución |
| Brotato | 20 oleadas (≈25 min) | Materials (XP+dinero en uno) | Desbloqueos por retos (sin stats permanentes) | Tienda entre oleadas con reroll/lock |
| 20 Minutes Till Dawn | 20 min (10 en Quickplay) | XP + Souls | Souls (runas/personajes/armas) | Apuntado y disparo manuales |
| Halls of Torment | 30 min | XP + oro (ítems) | Oro (Blessings) + equipo extraído | Estructura ARPG (equipo, habilidades, campamento) |
| Death Must Die | 20 min | Bendiciones + botín | Equipo persistente (stash) | Dioses estilo Hades + loot estilo Diablo + dash |
| Nordic Ashes | ~30 min | XP + semillas | Hojas (árbol Yggdrasil) | Constelaciones deterministas por personaje |
| Rogue: Genesia | Varias fases por run | Cartas + almas | Almas (soul shop enorme) | Mapa tipo Slay the Spire + build de cartas |
| Megabonk | 10 min + enjambre final | XP + oro | Plata (desbloqueos) | 3D + teleporter de jefe estilo Risk of Rain 2 |
| DRG: Survivor | 5 etapas (dive) | Oro/Nitra/Red Sugar | Créditos (Meta Upgrades) | Minería con riesgo (cavar quieto entre hordas) |
| Yet Another Zombie Survivors | Run estándar ~15-20 min | XP + dinero | Árbol general + por superviviente | Escuadrón de hasta 3 personajes |

---

### 1.1 Vampire Survivors (poncle, 2022)

- **Loop central:** solo te mueves; las armas disparan solas. Sobrevives oleadas que escalan hasta un límite de tiempo que cierra la run. «Bullet heaven»: tú eres el jefe aplastando hormigas, no David contra Goliat.
- **Sesión:** etapas de 30:00 (algunas 20:00/15:00). A 30:00 aparece Death/Reaper y luego uno por minuto: el final está forzado por diseño (https://vampire.survivors.wiki/w/Stages).
- **In-run:** 6 ranuras de armas + 6 de pasivos; armas hasta nivel 8, pasivos hasta 5 (https://jboger.substack.com/p/the-secret-sauce-of-vampire-survivors). Subida de nivel: pausa el juego y ofrece 3–4 opciones (la 4.ª depende de Luck); curva de XP: 5 XP a nivel 2, +10 por nivel hasta el 20, +13 hasta el 40, +16 después; Rerolls/Skips/Banish comprables en la grid de PowerUps (https://vampire.survivors.wiki/w/Level_up).
- **Cadencia observada:** con 8 niveles por arma el juego logra «una recompensa cada ~23 segundos» en una run de 30 min, en vez de una cada 2:30 (https://jboger.substack.com/p/the-secret-sauce-of-vampire-survivors).
- **Oleadas:** guionizadas por minuto; la lista de la Inlaid Library introduce enemigos nuevos cada 2–3 min y sube el mínimo de enemigos en pantalla (50 → 110 → 200 → 300) mientras baja el intervalo de spawn (0.5 s → 0.1 s); jefes a los minutos 3, 8, 10, 11, 15, 18, 20 y 25 (https://games.gg/vampire-crawlers-the-turbo-wildcard-from-vampire-survivors/guides/vampire-survivors-inlaid-library-stage-guide/).
- **Meta:** oro persistente gastado en PowerUps (mejoras de stats base); el conjunto total supone ~2,5x daño y ~x2 salud, pero repartidas en incrementos pequeños que no se sienten grindy (https://jboger.substack.com/p/the-secret-sauce-of-vampire-survivors).
- **Cofres/evoluciones:** cofres de 1/3/5 ítems con animación tipo tragaperras; los seis primeros cofres están *hardcodeados* con 1-1-3-1-5 ítems para enganchar antes de bajar la probabilidad real (https://jboger.substack.com/p/the-secret-sauce-of-vampire-survivors). Evolución: arma a nivel máximo + pasivo concreto + cofre de jefe ≥ minuto 10 (https://vampire.survivors.wiki/w/Evolution). Arcanas: elección extra de 4 opciones en cofres de los minutos 11:00 y 21:00 (https://rogueranker.com/vampire-survivors-arcanas).
- **Rejugar:** logros masivos como objetivos secundarios constantes, desbloqueos continuos (personajes/mapas/armas), retos de dificultad (Hyper/Inverse) y modo Endless (cada ciclo: +100% HP, +50% frecuencia y cantidad de spawns, +25% daño enemigo) (https://vampire.survivors.wiki/w/Stages).
- **UI destacable:** barra de XP y temporizador como HUD mínimo; modal de subida de nivel que pausa el juego; apertura de cofre con tratamiento de «slot machine»; pantalla final con recuento de oro y stats.
- **Twist:** oleadas-reloj (eventos, jefes, cofres y Arcanas atados a minutos exactos) + evoluciones por receta.
- **Fuentes:** https://jboger.substack.com/p/the-secret-sauce-of-vampire-survivors · https://vampire.survivors.wiki/w/Level_up · https://vampire.survivors.wiki/w/Stages

### 1.2 Brotato (Blobfish, 2022)

- **Loop central:** micro = oleadas de 20–90 s con objetivo «matar eficiente»; meso = tienda entre oleadas (comprar, reroll, lock, reciclar, banear); macro = 20 oleadas fijas con jefe final (DPS check: ~30k de daño en ráfaga para matarlo en <15 s) (https://teemo.dev/game-design/brotato/systems/teardown).
- **Sesión:** escalera de duración publicada: oleada 1 = 20 s, +5 s por oleada hasta 60 s en la 9; oleadas 9–19 = 60 s; oleada 20 (jefe) = 90 s (https://teemo.dev/game-design/brotato/systems/shop-economy-and-run-structure-reference).
- **In-run:** Materials = XP y dinero a la vez (un solo recurso: matar rápido = subir nivel = comprar antes). Arranque garantizado: oleadas 1–2 dan exactamente 2 armas + 2 ítems en tienda; oleadas 3–5 garantizan ≥1 arma; desde la 6 nada garantizado. Rarezas bloqueadas por oleada (Tier II desde oleada 2, III desde 4, IV desde 8). Hasta 6 armas; fusionar 2 copias sube de tier (https://teemo.dev/game-design/brotato/systems/onboarding-and-first-session).
- **Caps de rendimiento:** máx. 50 blobs de material en el suelo (los extra se fusionan) y máx. 100 enemigos en pantalla (spawn nuevo desbanea uno y no suelta nada): premia matar rápido y acota el coste (https://teemo.dev/game-design/brotato/systems/overview-ii).
- **Tienda:** 4 ofertas aleatorias; reroll con precio elástico: RI = max(1, floor(0.40×Oleada)); precio del reroll n = floor(0.75×Oleada) + RI + (n−1)×RI → 1.er reroll oleada 1 = 1, oleada 20 = 23; 5 rerolls en oleada 20 cuestan 195. Lock gratuito congela precio (contrarresta la inflación); comprar las 4 ofertas da un reroll gratis. Los precios de ítems suben ×(1+0.1×oleada) + oleada fija (https://teemo.dev/game-design/brotato/systems/shop-economy-and-run-structure-reference).
- **Meta:** Danger 0–5 elegido antes de la run (D5 = +40% stats enemigas y segundo jefe). El meta NO da poder: desbloquea personajes e ítems, es decir, amplía el menú de opciones; un fallo en Danger 0 no hace la siguiente run estadísticamente más fácil (https://teemo.dev/game-design/brotato/systems/teardown). Stat Harvesting compone +5% por oleada (pago en materiales y XP al cerrar oleada) (https://teemo.dev/game-design/brotato/systems/overview-ii).
- **Rejugar:** decenas de personajes con reglas propias, récords por Danger, builds basadas en trade-offs (casi todo ítem tiene un defecto declarado).
- **UI destacable:** pantalla de tienda con 4 cartas + precios dinámicos visibles; panel de stats lateral; contador de oleada y avisos de oleadas élite/horda; secuencia fija de fin de oleada (bag → harvest → cofres → subidas de nivel encoladas → tienda) (https://teemo.dev/game-design/brotato/systems/shop-economy-and-run-structure-reference).
- **Twist:** la decisión recurrente no es esquivar, es *comprar* (densidad de decisión en tienda) + personajes como modificadores de run.
- **Fuentes:** https://teemo.dev/game-design/brotato · https://teemo.dev/game-design/brotato/systems/shop-economy-and-run-structure-reference

### 1.3 20 Minutes Till Dawn (flanne, 2022)

- **Loop central:** VS con una diferencia clave: apuntas y disparas manualmente (además de moverte). Sobrevive de noche hasta el amanecer.
- **Sesión:** modos Standard (20 min), Quickplay (10 min) y Endless; el marketing del juego vende «sesiones casuales de 10–20 minutos» (https://en.wikipedia.org/wiki/20_Minutes_Till_Dawn).
- **In-run:** subida de nivel → eliges 1 de 4 mejoras aleatorias; ~80–100 mejoras agrupadas en 25 árboles (p. ej. Cadencia, Fuego, Artes Oscuras, Escudo Sagrado); el HP máximo está capado en 11 puntos; los jefes sueltan cofres con mejoras especiales (https://en.wikipedia.org/wiki/20_Minutes_Till_Dawn, https://store.epicgames.com/news/20-minutes-till-dawn-guide-how-to-survive-and-thrive-at-the-highest-difficulties).
- **Meta:** moneda Souls ganada en cada run (éxito o fracaso) para comprar Runas, personajes y armas; las runas son mejoras de arranque seleccionables por personaje/arma (https://20-minutes-till-dawn.fandom.com/wiki/Souls).
- **Dificultad escalable:** sistema «Darkness» 0–15; cada nivel añade modificadores acumulativos (D15 = los jefes atacan un 80% más a menudo); hay que superar cada nivel para desbloquear el siguiente; «terminar» el juego = completar D15 con todos los personajes y armas (https://store.epicgames.com/news/20-minutes-till-dawn-guide-how-to-survive-and-thrive-at-the-highest-difficulties).
- **Rejugar:** combinaciones personaje×arma×runas cambian el gameplay; experimentar builds entre runs fue lo más elogiado por prensa (https://en.wikipedia.org/wiki/20_Minutes_Till_Dawn).
- **UI destacable:** temporizador de cuenta atrás protagonista (noche→amanecer); pantalla de elección de personaje/arma con runas; subida de nivel con 4 cartas.
- **Twist:** apuntado manual (más agencia mecánica que VS) sobre esqueleto de survivor.
- **Fuentes:** https://en.wikipedia.org/wiki/20_Minutes_Till_Dawn · https://store.epicgames.com/news/20-minutes-till-dawn-guide-how-to-survive-and-thrive-at-the-highest-difficulties

### 1.4 Halls of Torment (Chasing Carrots, 2024)

- **Loop central:** survivor con piel de ARPG clásico (Diablo): aguantas 30 minutos en una sala y derrotas al Lord final (https://www.ign.com/wikis/halls-of-torment/Beginner's_Guide).
- **Sesión:** 30 min por run; el artefacto opcional «Hastening Sands» la recorta −10 min a cambio de +30% spawn y +20% velocidad (https://hot.fandom.com/wiki/Artifact).
- **In-run:** subir de nivel → eliges 1 de 4 Traits (mejoran el arma principal o atributos), con rangos I–V por trait; las habilidades extra vienen de Scrolls of Mastery soltados por mini-jefes (eliges 1 de 3 al cogerlas) y se mejoran aparte; equipo con hasta 7 piezas. La XP requerida por nivel tiene fórmula propia por sala (https://www.ign.com/wikis/halls-of-torment/Beginner's_Guide, https://rogueliker.com/halls-of-torment-review/).
- **Oleadas/jefes:** jefes atados a umbrales de tiempo restante (p. ej. Imp Chieftain a los 24:00 restantes, Lich a 8:00, Wyrm Queen a 5:50); los mini-jefes sueltan scrolls con frecuencia (https://gamerant.com/halls-of-torment-how-unlock-all-characters/).
- **Meta:** oro → «Blessings» permanentes (p. ej. regeneración +0,75 HP/s, o +50% oro); el Wellkeeper permite extraer equipo de la run y conservarlo para siempre; 11 héroes desbloqueables por quests/bosses (https://primagames.com/tips/best-blessings-in-halls-of-torment-ranked, https://gamerant.com/halls-of-torment-how-unlock-all-characters/).
- **Dificultad escalable:** capas Agony y Torment; «Hall Strength» interpola el HP enemigo de mínimo a máximo según el progreso de la sala (p. ej. Haunted Caverns: 500→19.000); artefactos opcionales como modificadores de dificultad con recompensa (https://hot.fandom.com/wiki/Hall).
- **Rejugar:** quest board (objetivos con recompensas: oro, personajes, ítems, traits), marcas personales por héroe, builds con sinergias de elemento (fuego, hielo...).
- **UI destacable:** campamento-hub con Shrine of Blessings, piedra de quests, Wellkeeper; inventario tipo paper-doll; iconos de habilidad con cooldown; fuente/estética CRPG con fuentes «arcaicas» deliberadas (https://rogueliker.com/halls-of-torment-review/).
- **Twist:** convertir el survivor en un ARPG con equipo extraíble entre runs y quests que dan dirección (31.000+ reviews, 96% positivas: el «meta bien hecho» del género) (https://www.youtube.com/watch?v=NkiwYG1xQ3M).
- **Fuentes:** https://www.ign.com/wikis/halls-of-torment/Beginner's_Guide · https://rogueliker.com/halls-of-torment-review/ · https://hot.fandom.com/wiki/Hall

### 1.5 Death Must Die (Realm Archive, 2023)

- **Loop central:** survivors + Hades + Diablo: desciendes por los círculos del Inframundo matando hordas, eligiendo bendiciones de dioses y recogiendo botín con rarezas.
- **Sesión:** runs de ~20 minutos (https://bullethaven.com/review/death-must-die); combate entre auto-battler y acción: mueves y haces dash (con i-frames) mientras los ataques salen solos.
- **In-run:** al subir de nivel eliges bendiciones de dioses (8 dioses con estilos: fuego, hielo, maldición, rayo...); fijas ~3 dioses por run, lo que orienta la build; el dash con invulnerabilidad fue una de sus señas frente a VS (https://steamcommunity.com/app/2334730/discussions/0/4036977035349902927).
- **Meta:** equipo persistente estilo Diablo (rarezas, sets, stash que se llena de «rojos»), árboles de talento por héroe y maestría de bendiciones; 7 héroes con kits distintos (https://bullethaven.com/review/death-must-die).
- **Dificultad escalable:** opción de «aumentar las odds de reliquias perdidas a costa de potenciar las legiones de Death» (modificador de riesgo/recompensa declarado en la página de tienda) (https://store.steampowered.com/app/2334730/Death_Must_Die).
- **Rejugar:** farmear equipo para el stash, subir maestrías, probar hero×dios; 91% positivas con 19.600+ reviews y 500.000 propietarios (https://bullethaven.com/review/death-must-die).
- **UI destacable:** elección de bendición con la cara del dios y diálogo (estilo Hades); stash/rejilla de inventario; árbol de talentos por héroe.
- **Crítica conocida:** el RNG de dioses puede desbaratar builds planeadas (https://bullethaven.com/review/death-must-die).
- **Twist:** las bendiciones vienen de personajes con voz y personalidad (capa narrativa ligera) + dash activo + economía de loot persistente.
- **Fuentes:** https://bullethaven.com/review/death-must-die · https://store.steampowered.com/app/2334730/Death_Must_Die

### 1.6 Nordic Ashes: Survivors of Ragnarok (Noxfall, 2023)

- **Loop central:** fórmula VS (mover = única entrada directa) con mitología nórdica; runs de ~30 minutos (https://opencritic.com/game/16904/nordic-ashes-survivors-of-ragnarok).
- **In-run:** cada personaje tiene un árbol de Constelaciones propio; a diferencia del género, **el subir de nivel en run no es RNG: recorres ramas deterministas** que cambian cómo funciona tu arma principal (p. ej. hachas que pasan de girar a misiles guiados); 150+ reliquias como capa de build; tienda tras las oleadas (https://opencritic.com/game/16904/nordic-ashes-survivors-of-ragnarok, https://rich.report/nordic-ashes-survivors-ragnarok).
- **Meta:** árbol Yggdrasil entre runs: semillas recogidas → hojas → bonus permanentes, personajes y nodos nuevos; «incluso las runs fallidas contribuyen» (https://bullethaven.com/review/nordic-ashes-survivors-of-ragnarok).
- **Contenido:** 9 mapas (un reino cada uno), 10+ personajes, 5 modos (Adventure, Ragnarok, Daily, Custom, Nightmare) (https://store.steampowered.com/app/2068280/Nordic_Ashes_Survivors_of_Ragnarok).
- **Dificultad escalable:** Ragnarok no solo sube HP: cambia el comportamiento de enemigos, más élites y jefes con ataques nuevos; los jefes se leen como puzles de arena (https://rich.report/nordic-ashes-survivors-ragnarok).
- **Rejugar:** 89% positivas (5.800+ reviews); lo más citado en reviews de Steam es el meta fuerte (32/117) y las mecánicas únicas por personaje (25/117) (https://steamstat.io/app/2068280).
- **UI destacable:** constelaciones como pantalla de progreso in-run (no una lista); árbol Yggdrasil como hub de meta; alta legibilidad visual con paleta clara.
- **Críticas:** al final pesa el grind; variedad de build limitada porque las armas están atadas a personajes; el rol del azar (https://bullethaven.com/review/nordic-ashes-survivors-of-ragnarok).
- **Twist:** progresión in-run determinista por constelaciones (menos RNG frustrante) + identidad temática fuerte.
- **Fuentes:** https://bullethaven.com/review/nordic-ashes-survivors-of-ragnarok · https://opencritic.com/game/16904/nordic-ashes-survivors-of-ragnarok

### 1.7 Rogue: Genesia (Ouadi Huard, 2025)

- **Loop central:** bullet heaven con estructura de Slay the Spire: en vez de una run-contra-reloj, un mapa de mundo ramificado donde eliges tu camino entre nodos/etapas con modificadores (https://steamstat.io/app/2067920); dentro de cada etapa: mueves, matas, subes nivel eligiendo cartas.
- **In-run:** mejoras como **cartas** (build de mazo): 200+ mejoras y 60+ armas; podemos banear cartas/nodos para controlar el pool (https://bullethaven.com/review/rogue-genesia).
- **Meta:** «soul shop» masivo: 45 de 120 reviews analizadas destacan desbloqueos, talentos pasivos y mejoras permanentes como su mayor atractivo (https://steamstat.io/app/2067920).
- **Dificultad escalable:** dificultad multiplicada por modificadores de ruta/nodos; los críticos señalan tanto snowball trivial (matar fuera de pantalla) como tramos tediosos según el camino (https://steamstat.io/app/2067920).
- **Rejugar:** elección de ruta (estructura) + sinergias de cartas; 91% positivas (8.000+ reviews) (https://steamstat.io/app/2067920).
- **UI destacable:** mapa de nodos con recompensas visibles (antes de entrar sabes qué te juegas); pantalla de deck/cartas; tienda de mejora con banishes; comparativa clara de stats.
- **Críticas:** rendimiento (frame drops con miles de entidades), snowball/estanqueidad del ritmo tardío, y **clutter visual** que impide leer ataques (https://steamstat.io/app/2067920).
- **Twist:** la run no es «un cronómetro», es una *ruta con decisiones* entre fases.
- **Fuentes:** https://steamstat.io/app/2067920 · https://bullethaven.com/review/rogue-genesia

### 1.8 Megabonk (Vedinad, 2025)

- **Loop central:** survivors en 3D + estructura Risk of Rain 2: tienes 10 minutos para encontrar el teleporter de jefe y matarlo; en el mapa hay cofres, santuarios y vendedores; cuando el cronómetro llega a 0 aparece un enjambre final con enemigos de muerte garantizada (el juego «sabe cuándo terminar») (https://www.pcgamer.com/games/roguelike/megabonk-review/, https://www.destructoid.com/reviews/megabonk-review-an-absurd-charming-yet-potent-evolution-of-the-survivors-like-formula/).
- **In-run:** build de 4 armas + 4 tomos; los ítems apilan (estilo RoR, no hay fusiones tipo VS); armas por subida de nivel; cofres con animación de tragaperras; santuarios que dan buffs a cambio de quedarte quieto dentro; vendedor («thanks idiot») con precios crecientes (https://fullcleared.com/reviews/megabonk-review/).
- **Meta:** Plata + quests + logros (108) desbloquean personajes (20 en total), armas, tomos e ítems; los propios desbloqueos *aumentan el pool* (más variedad pero peor consistencia: dilución), y el juego da toggles para desactivar ítems del pool (https://www.pcgamer.com/games/roguelike/megabonk-review/).
- **Dificultad escalable:** tiers de dificultad por nivel + modificadores «Hyper» (más enemigos, menos coste de cofres...) y desafíos extremos (terminar una run sin poder moverte); los jefes finales exigen builds fuertes, con abanicos de recompensa incluso por probar armas raras (https://www.pcgamer.com/games/roguelike/megabonk-review/).
- **Rejugar:** con solo 3 niveles, la retención viene de desafíos y desbloqueos: récords de 45+ horas documentados (https://www.pcgamer.com/games/roguelike/megabonk-review/).
- **UI destacable:** HUD mínimo (salud + XP); cofre-slot-machine; el teleporter como objetivo físico en el mapa (exploras, no kites en círculos); pantalla de resultados con Plata.
- **Críticas:** pool dilution al desbloquear más ítems; algún jefe tardío con instakill «adivinación»; ir a 3D complica el acceso que VS lograba con solo ratón (https://www.pcgamer.com/games/roguelike/megabonk-review/, https://www.destructoid.com/reviews/megabonk-review-an-absurd-charming-yet-potent-evolution-of-the-survivors-like-formula/).
- **Twist:** 10 min + objetivo espacial (encontrar el portal) + físicas/juventud 3D.
- **Fuentes:** https://www.pcgamer.com/games/roguelike/megabonk-review/ · https://fullcleared.com/reviews/megabonk-review/

### 1.9 Deep Rock Galactic: Survivor (Funday Games, 2024/1.0 2025)

- **Loop central:** hacer un «dive» = 5 etapas seguidas, cada una con Supply Drop (mejoras) y un Elite; la 5.ª termina con un Dreadnought. Todo el rato alternas moverte disparando automático con **cavar** (Nitra, Oro, Red Sugar como objetivos físicos en la pared) (https://earlyguides.com/deep-rock-galactic-survivor).
- **Sesión:** el dive encadena 5 etapas (≈15–25 min); decisión constante «¿me paro a cavar 2-3 s con la horda acercándose?» — tensión que el género no tenía (https://playwanderer.online/game-reviews/deep-rock-galactic-survivor).
- **In-run:** subes armas con cartas; overclocks en niveles de arma 6, 12 y 18 (equilibrados; el de nivel 18 es «Unstable», extremo: p. ej. The Favourite dobla daño/cadencia de un arma y −30% al resto); 4 (hoy 5) clases × 3 variantes con armas iniciales y pasivas distintas; 10 armas por clase (https://earlyguides.com/deep-rock-galactic-survivor/weapons).
- **Meta:** oro/nitra/red sugar no persisten; créditos y recursos meta → Meta Upgrades (buffs de stats para todas las clases); Milestones desbloquean armas; el meta se siente como una segunda escalera de power (https://earlyguides.com/deep-rock-galactic-survivor/combat).
- **Dificultad escalable:** Hazard 1–5 por bioma; el bioma define peligros propios (https://earlyguides.com/deep-rock-galactic-survivor).
- **Rejugar:** clases/variantes con aperturas distintas + recetas de overclocks largas de descubrir.
- **UI destacable:** selección de overclock como mini árbol de decisión del arma; entre etapas, pantalla de Supply Drop; hazard selector antes del dive.
- **Críticas (14% negativas convergen):** el meta-progreso «gatea» las builds divertidas tras horas de grind; la pantalla de subida de nivel se llena de buffs porcentuales planos; runs intercambiables tras ~12 horas (https://playwanderer.online/game-reviews/deep-rock-galactic-survivor).
- **Twist:** minería con riesgo = segunda decisión constante (loot activamente en tensión con «jugar seguro»).
- **Fuentes:** https://playwanderer.online/game-reviews/deep-rock-galactic-survivor · https://earlyguides.com/deep-rock-galactic-survivor

### 1.10 Yet Another Zombie Survivors (Awesome Games Studio, 2023/1.0 2026)

- **Loop central:** survivors 3D con escuadrón: empiezas con 1 superviviente y respondes llamadas SOS para incorporar hasta 2 más (dúo o trío); cada uno aporta armas/habilidades/stats propios y sinergias de pareja (https://www.xbox.com/en-US/games/store/yet-another-zombie-survivors-game-preview/9NCK0FXQL38F).
- **Sesión:** runs estándar + modos variados (Extermination por oleadas, Endurance, Infinite, One Hit, Boss Rush); auto-aim por defecto con apuntado manual opcional (https://www.xbox.com/en-US/games/store/yet-another-zombie-survivors-game-preview/9NCK0FXQL38F).
- **In-run:** armas y habilidades evolucionan en direcciones distintas; ítems y badges apilables; builds alrededor de tipos de daño (fuego/eléctrico/hielo/químico) y rangos (https://www.xbox.com/en-US/games/store/yet-another-zombie-survivors-game-preview/9NCK0FXQL38F).
- **Meta:** árbol general compartido + progresión separada por superviviente; desbloqueo de armas, habilidades, evoluciones, ítems y badges; sistema de prestigio; dificultad «virus strength» (más fuerte y rápido a cambio de más recompensas) (https://rawg.io/games/yet-another-zombie-survivors).
- **Mecánica original:** Fatigue: el daño máximo por golpe enemigo sube de 1000 a 5000 según avanza la fatiga de la horda (reloj de presión integrado en el lore) (https://yetanotherzombie.wiki.gg/wiki/Stats_(Survivors)).
- **Rejugar:** probar tríos y sinergias; 147 logros; críticas: la progresión puede volverse grind y algunos builds dominan; identidad visual genérica; la repetición aparece con el tiempo (Metacritic: 70–80 críticos) (https://www.metacritic.com/game/yet-another-zombie-survivors).
- **UI destacable:** HUD de escuadrón con 3 columnas de cooldowns; menú de base entre runs; selector de modo explícito («¿de qué tienes ganas hoy?»).
- **Twist:** construir un equipo de 3 en vez de un solo héroe (decisiones de composición como capa adicional).
- **Fuentes:** https://www.xbox.com/en-US/games/store/yet-another-zombie-survivors-game-preview/9NCK0FXQL38F · https://yetanotherzombie.wiki.gg/wiki/Stats_(Survivors)

---

## 2. Patrones comunes de diseño

### 2.1 Cadencia de recompensas
- **Regla del género: nunca más de ~60 s sin una decisión.** VS reparte una subida cada ~23 s gracias a 8 niveles por arma; Brotato da subida + tienda cada 20–90 s; HoT pausa con 1-de-4 cada pocos minutos. (https://jboger.substack.com/p/the-secret-sauce-of-vampire-survivors, https://teemo.dev/game-design/brotato/systems/teardown)
- **La subida de nivel pausa el juego** (VS) o abre fase (tienda de Brotato): sirven de respiro entre picos de atención.
- **Primeras recompensas regaladas:** los 6 primeros cofres de VS están hardcodeados 1-1-3-1-5; Brotato garantiza 2 armas+2 ítems en oleadas 1–2. El estándar de la industria es un onboarding «generoso a propósito». (https://jboger.substack.com/p/the-secret-sauce-of-vampire-survivors)

### 2.2 Economía: moneda in-run vs moneda meta
- **Convergencia in-run:** un solo recurso dual (Brotato: Materials = XP + dinero) fuerza tensión «matar vs comprar»; dos recursos separados (oro + XP) es lo más común (VS, HoT).
- **Persistencia:** VS: oro 100% persistente → PowerUps (≈2,5x daño acumulado, x2 vida, en migajas). Brotato: **cero poder persistente** — el meta amplía el menú (ítems/personajes) y la dificultad la eliges tú (Danger 0–5). DRG:S: créditos → Meta Upgrades (crítica: gatea lo divertido). 20MTD: Souls → runas/personajes/armas. RG: soul shop gigante. (https://teemo.dev/game-design/brotato/systems/teardown, https://store.epicgames.com/news/20-minutes-till-dawn-guide-how-to-survive-and-thrive-at-the-highest-difficulties)
- **Inflación controlada:** precios de tienda y rerolls escalan con la oleada (Brotato ×(1+0.1×oleada)+oleada; tabla completa con 1.er reroll=1 → 23). Los **locks gratuitos** congelan precio y son el contrapeso clave. (https://teemo.dev/game-design/brotato/systems/shop-economy-and-run-structure-reference)

### 2.3 Escalado de enemigos por oleada
- **Por tiempo guionizado** (VS): evento cada minuto, nuevo tipo cada 2–3 min; mínimo en pantalla 50→110→200→300 y spawn 0.5 s→0.1 s en 30 min. (https://games.gg/vampire-crawlers-the-turbo-wildcard-from-vampire-survivors/guides/vampire-survivors-inlaid-library-stage-guide/)
- **Aditivo por oleada + multiplicador de dificultad** (Brotato): stats aditivos por oleada; Danger 5 = +40% global; Endless cuadrático (EndlessFactor: HP ×(1+EF×2.25)...). (https://teemo.dev/game-design/brotato)
- **Interpolación por progreso de sala** (HoT): Hall Strength 500→19.000 (sala I) según avance; capas Agony/Torment encima. (https://hot.fandom.com/wiki/Hall)
- **Capas opt-in como escalera de contenido:** Darkness 0–15 (20MTD), Agony/Torment (HoT), Hazard 1–5 (DRG:S), Danger 0–5 (Brotato), virus strength (YAZS), Ragnarok (NA). La subida de dificultad añade **comportamientos**, no solo números (NA: jefes con ataques nuevos; D15: +80% frecuencia de ataque de jefes).

### 2.4 Cuántos upgrades suele haber por run
- Ranuras típicas: 6 armas + 6 pasivos (VS); 6 armas (Brotato); 4 armas + 4 tomos (Megabonk); 7 piezas de equipo + 4–5 habilidades (HoT).
- Opciones por elección: **3–4 cartas** es el estándar (VS 3–4 con Luck; Brotato 4; HoT 4; 20MTD 4). Reroll/Skip/Banish como válvulas anti-RNG (VS) o Lock/Ban (Brotato, Megabonk).
- Catálogos totales: ~30 ítems base (VS, jboger) hasta 100 (20MTD), 150+ relics (NA), 200+ upgrades (RG), 80+ (20MTD).

### 2.5 Longitud de oleada / run óptima
- Oleadas cortas tipo «chunk»: 20 s → 60 s (+5 s/oleada; Brotato) + 90 s de jefe final.
- Runs: el cluster del género es **10–30 min**; éxitos recientes bajaron a 10 (Megabonk) y 20 (20MTD, DMD); los 30 (VS, HoT, NA) arrastran más críticas de ritmo («mirando el reloj»). (https://www.reddit.com/r/roguelites/comments/1kur1vd/anyone_else_tired_of_survivorlikes/)
- Hurry/Quickplay como variante oficial (VS x2; 20MTD 10 min): la duración es un parámetro de diseño exponible.

### 2.6 Jefes y telegrafía
- **Citas fijas:** jefes a minutos concretos (VS: 3/8/10/11/15/18/20/25; HoT: a umbrales de tiempo restante). El jugador aprende el calendario y construye hacia él.
- **Señales:** silueta única + barra de vida + eventos de «parade»; élites de Brotato con indicadores de oleada; el objetivo espacial (teleporter de Megabonk) convierte la búsqueda del jefe en gameplay.
- **Respuesta activa:** el dash con i-frames de DMD fue un diferenciador celebrado; los ataques «con wind-up» y patrones evitables son obligatorios — el instakill sorpresa de un jefe tardío de Megabonk se cita como fallo (https://www.pcgamer.com/games/roguelike/megabonk-review/).
- **Forcing function del final:** Reaper al expirar el tiempo (VS), enjambre final a 0:00 (Megabonk): la run no se eterniza.

---

## 3. Críticas y fatiga del género

1. **Saturación y precio.** Solo en 2022 se lanzaron 174 «action roguelike + bullet hell»; el precio ancla (~5 €) presiona a los clones a competir sin margen; hay fatiga explícita de jugadores («me cansé tras 3 títulos») y streamers. La conclusión de los análisis: sobrevivir hoy exige un gancho propio fuerte (20–30% de variación basta para ser reconocible pero distinto). (https://howtomarketagame.com/2023/01/09/are-vampire-survivor-likes-dead/, https://www.reddit.com/r/gamedev/comments/1sl3sd8/are_survivorslikes_finally_out_of_fashion/)
2. **Grind meta que gatea lo divertido.** La queja nº1 en DRG:S: «el progreso depende más de horas acumuladas que de jugar bien», con la pantalla de subida llena de buffs % planos tras las elecciones obvias; NA también recibe «grind tardío»; YAZS «la progresión puede hacerse grind». **Cómo lo evitan los buenos:** Brotato no vende poder permanente; VS fragmenta el poder en migajas «que no se sienten grindy»; HoT convierte el grind en quests con recompensas visibles. (https://playwanderer.online/game-reviews/deep-rock-galactic-survivor, https://bullethaven.com/review/nordic-ashes-survivors-of-ragnarok)
3. **RNG frustrante.** DMD: «planeas una build de rayo y Leigong no aparece nunca»; en VS muchas armas son «trampas» frente a las meta (Clock Lancet imprescindible para retos duros: señal de mal balance interno); en Megabonk, cada desbloqueo diluye el pool. **Antídotos del género:** rerolls/skips/banishes (VS), lock/ban (Brotato), árboles deterministas (NA), toggles de pool (Megabonk), fijar 2–3 Dioses por run (DMD). (https://bottomfeeder.substack.com/p/the-fast-life-and-fiery-death-of, https://bullethaven.com/review/death-must-die)
4. **Falta de decisión / pasividad.** «Es un género para apagar el cerebro: eliges mejoras y a moverte»; la solución de los buenos: añadir una segunda capa activa — apuntar (20MTD), dash (DMD), cavar arriesgando (DRG:S), buscar el portal (Megabonk) — o densidad de decisión en tienda (Brotato). (https://www.reddit.com/r/roguelites/comments/1kur1vd/anyone_else_tired_of_survivorlikes/) (https://teemo.dev/game-design/brotato/systems/teardown)
5. **Runs largas que se estancan.** «30 minutos de mirar el reloj»; picos de poder sin enemigos que los justifiquen («vuelves intocable y paseas esperando que vuelva el reto»). VS lo corrige con el Reaper; Megabonk con el enjambre final; los buenos terminan la run *a tiempo*. (https://www.reddit.com/r/roguelites/comments/1kur1vd/anyone_else_tired_of_survivorlikes/, https://www.pcgamer.com/games/roguelike/megabonk-review/)
6. **Poca variedad de enemigos y repetición.** «Veinte minutos de los mismos enemigos, en el mismo orden, con los mismos comportamientos»: se pide más diseño de enemigos tipo Robotron (olas de cerebros con misiles teledirigidos) y no solo sacos de HP. (https://bottomfeeder.substack.com/p/the-fast-life-and-fiery-death-of)
7. **Legibilidad y rendimiento.** Rogue: Genesia: frame drops y «caos ilegible que impide ver ataques»; NA: invulnerabilidades y curas superpuestas como «fallo de diseño»; 20MTD Endless: enjambres injugables (~20 min). Con miles de sprites, la claridad es una feature. (https://steamstat.io/app/2067920, https://steamstat.io/app/2068280)
8. **Balance de personajes/armas.** VS (pocos personajes realmente distintos), 20MTD (brecha entre builds con y sin sinergia), DMD (RNG de dioses). Los buenos priorizan kits que cambian el cómo se juega (Brotato, HoT, NA) y trade-offs declarados en cada ítem. (https://bottomfeeder.substack.com/p/the-fast-life-and-fiery-death-of, https://teemo.dev/game-design/brotato/systems/teardown)

---

## 4. LECCIONES APLICABLES (para «No Apagues La Luz»)

1. **Run de ~20 minutos con final forzado.** Sitúate en el cluster 10–20 min (20MTD, DMD, Megabonk); garantiza cierre dramático a los 20:00 (analogía Reaper/enjambre final: p. ej. «la ronda de guardias de cierre» o el turno termina y algo entra). Nunca una run eterna. *(VS: Reaper a los 30:00 — vampire.survivors.wiki/w/Stages; Megabonk: enjambre a 0:00 — pcgamer.com/games/roguelike/megabonk-review/)*
2. **Cadencia de recompensa ≤30 s.** Con ~8 niveles de mejora por arma se logra 1 decisión cada ~23 s; en 20 min apunta a una subida cada 20–30 s (≈40–50 subidas) dividiendo upgrades en escalones pequeños. Nunca dejes >60 s sin decisión. *(jboger.substack.com/p/the-secret-sauce-of-vampire-survivors)*
3. **Curva de XP replicable y transparente.** Usa una progresión por tramos (VS: 5 XP→nivel 2, +10 hasta nivel 20, +13 hasta 40); documentarla permite balancear el ritmo por minutos. *(vampire.survivors.wiki/w/Level_up)*
4. **Ofrece siempre 3–4 opciones y añade válvulas anti-RNG:** reroll (con precio creciente), banish y skip; lock gratuito en tienda. El lock es el contrapeso estándar a la inflación de precios. *(Brotato: RI=max(1,floor(0.40×oleada)) — teemo.dev/game-design/brotato/systems/shop-economy-and-run-structure-reference)*
5. **Define 5–6 ranuras de armas/objetos y 5–8 niveles por arma** (no 8 niveles solo si tu run es de 30 min; en 20 min, 5–6 niveles por arma mantienen la densidad de VS). Reserva 2–3 pasivos «clave» por arma para evoluciones. *(VS: 6+6 ranuras, armas nivel 8, pasivos nivel 5 — jboger.substack.com)*
6. **Máquina expendedora = fase de respiro con 4 ranuras.** Tras ciertos hitos temporales (p. ej. cada ~4 min de turno), abre la tienda con 4 ofertas: 2 objetos + 2 armas al principio (como Brotato en oleadas 1–2), precios ×(1+0.1×hito)+hito, y reroll encareciéndose; reciclar/bannear como en Brotato. *(teemo.dev/game-design/brotato/systems/shop-economy-and-run-structure-reference)*
7. **Dos monedas con roles distintos:** monedas de run (solo en la run, para la expendedora) y una meta-moneda («tickets de nómina») que compre **desbloqueos de opciones** (armas, personajes, modificadores) más que poder puro. Si haces stats meta, limítalos a migajas tipo VS (total acumulado ≤ +20–30% para no trivializar). Modelo de referencia: Brotato (0 poder permanente). *(teemo.dev/game-design/brotato/systems/teardown)*
8. **Luz/oscuridad como segunda capa activa (apuntar/cavar del género).** Convierte «apagar la luz» en la tensión de DRG:S: quedarte en oscuridad da bonus (daño/crítico) pero los enemigos nocturnos se activan; encender consumibles de luz te salva pero cuesta recursos. Es tu «cavar quieto»: una decisión cada pocos segundos, no cada nivel. *(playwanderer.online/game-reviews/deep-rock-galactic-survivor)*
9. **Jefes = «guardias» con calendario fijo y señales.** Programa jefes a minutos exactos (p. ej. 10:00 y 19:00, guardia de seguridad con linterna; 20:00 final), con silueta única + barra de vida + aviso 2–3 s antes. Telegrafía con wind-up; prohibido el instakill sorpresa. *(VS calendar — games.gg/.../vampire-survivors-inlaid-library-stage-guide/; Megabonk crítica — pcgamer.com)*
10. **Oleadas como chunks cortos de 20–90 s con respiro entre ellas.** Estructura tipo Brotato en la oficina: «rondas de trabajo» de duración creciente (+5 s), tienda cada X, y la última ronda = jefe. Escala spawn (intervalo 0.5 s→0.1 s) y mínimo enemigos (50→200→300) como VS. *(games.gg/.../inlaid-library; teemo.dev/game-design/brotato/systems/shop-economy-and-run-structure-reference)*
11. **Introduce un enemigo nuevo cada 2–3 minutos.** VS mantiene la escalada legible así; evita el «mismo orden de enemigos durante 20 min» que se critica al género. Guardias con comportamientos distintos (patrulla con cono de linterna, perro de seguridad, supervisor con radio...) = la lección Robotron. *(bottomfeeder.substack.com/p/the-fast-life-and-fiery-death-of)*
12. **Caps de rendimiento desde el diseño:** máx. ~100–150 enemigos vivos y ~50 pickups en suelo (desvanecer/fusionar los extra); en pixel art 2D esto protege el frame rate y la legibilidad. *(Brotato: 100/50 — teemo.dev/game-design/brotato/systems/overview-ii)*
13. **Pantalla pausada en cada elección** (subida de nivel) y en la expendedora: el género usa estas pausas como respiro anti-fatiga visual; con luz/oscuridad y partículas, es imprescindible. *(jboger.substack.com)*
14. **Dificultad «guardias» como escalera opt-in.** Dificultad elegida antes de la run (Danger 0–5 de Brotato, Darkness 0–15): cada nivel añade modificadores de comportamiento (jefes más agresivos, +80% frecuencia de ataque en D15) además de stats; desbloquea el siguiente al superarlo y recompensa con moneda/meta extra (modelo virus strength: más difícil = más recompensa). *(store.epicgames.com/news/20-minutes-till-dawn-guide...)*
15. **Meta con misiones visibles, no solo tienda.** Quest board estilo HoT: «sobrevive 5 min sin encender ninguna luz», «mata al guardia X con la grapadora» → recompensas concretas (personajes, ítems), y logros/challenges como objetivos secundarios constantes. Esto elimina la «orilla sin rumbo» del post-run. *(rogueliker.com/halls-of-torment-review/, gamerant.com/halls-of-torment-how-unlock-all-characters/)*
16. **Primera sesión guionada y generosa.** Primeras recompensas garantizadas (cofres hardcodeados 1-1-3-1-5 de VS; 2 armas+2 ítems en las primeras tiendas); los primeros 10 minutos deben regalar 2–3 momentos «rotos» de poder. *(jboger.substack.com; teemo.dev/game-design/brotato/systems/onboarding-and-first-session)*
17. **Trade-offs en vez de buffs planos.** Critica DRG:S: la pantalla de nivel se llena de +% aburridos. Casi cada ítem/oficina-item debería tener bonus + coste declarado (Brotato), y las grandes decisiones deben alterar el *cómo* (mecánicas de armas) no solo el cuánto. *(playwanderer.../deep-rock-galactic-survivor; teemo.dev/game-design/brotato/systems/teardown)*
18. **Evita la dilución de pool al desbloquear.** Megabonk lo sufre; antídotos: toggles para desactivar ítems del pool, banishes, y garantías por tipo en tiendas tempranas. En nuestro caso: separa armas/objetos/traumas en pools y da control de tuning al jugador. *(pcgamer.com/games/roguelike/megabonk-review/)*
19. **Claridad visual = feature de diseño.** Paleta con buen contraste (elogio a NA), evitar el «caos ilegible» de RG: máximo de 2–3 capas de efectos simultáneos por zona, siluetas enemigas distinguibles, y prioridad absoluta a telegrafías (flash de ataque) por encima de partículas. *(steamstat.io/app/2067920 vs bullethaven.com/review/nordic-ashes-survivors-of-ragnarok)*
20. **Diseña el «hook de la tercera run».** Con poco contenido (3 niveles bastan: Megabonk) la retención sale de desafíos variados + desbloqueos + un objetivo espacial por nivel. En No Apagues La Luz: cada planta de oficina debe tener secretos/objetivos físicos (sala de servidores, caja fuerte, el jefe en la sala de reuniones) y desafíos semanales. Evita que todos los retos sean «más difícil»: varía condiciones. *(pcgamer.com/games/roguelike/megabonk-review/, gameshub.com/news/reviews/megabonk-review-2832477/)*

---

## Fuentes (índice)

- Vampire Survivors — análisis de diseño: https://jboger.substack.com/p/the-secret-sauce-of-vampire-survivors
- Vampire Survivors — wiki (niveles, etapas, evolución, Arcanas): https://vampire.survivors.wiki/w/Level_up · https://vampire.survivors.wiki/w/Stages · https://vampire.survivors.wiki/w/Evolution · https://rogueranker.com/vampire-survivors-arcanas
- Vampire Survivors — oleadas de Inlaid Library: https://games.gg/vampire-crawlers-the-turbo-wildcard-from-vampire-survivors/guides/vampire-survivors-inlaid-library-stage-guide/
- Brotato — teardown y referencia de economía: https://teemo.dev/game-design/brotato · https://teemo.dev/game-design/brotato/systems/shop-economy-and-run-structure-reference · https://teemo.dev/game-design/brotato/systems/overview-ii
- 20 Minutes Till Dawn — Wikipedia y guía Epic: https://en.wikipedia.org/wiki/20_Minutes_Till_Dawn · https://store.epicgames.com/news/20-minutes-till-dawn-guide-how-to-survive-and-thrive-at-the-highest-difficulties · https://20-minutes-till-dawn.fandom.com/wiki/Souls
- Halls of Torment — IGN, rogueliker, wiki: https://www.ign.com/wikis/halls-of-torment/Beginner's_Guide · https://rogueliker.com/halls-of-torment-review/ · https://hot.fandom.com/wiki/Hall · https://hot.fandom.com/wiki/Artifact · https://gamerant.com/halls-of-torment-how-unlock-all-characters/
- Death Must Die — review y tienda: https://bullethaven.com/review/death-must-die · https://store.steampowered.com/app/2334730/Death_Must_Die
- Nordic Ashes — review y Steam: https://bullethaven.com/review/nordic-ashes-survivors-of-ragnarok · https://opencritic.com/game/16904/nordic-ashes-survivors-of-ragnarok · https://steamstat.io/app/2068280
- Rogue: Genesia — steamstat y review: https://steamstat.io/app/2067920 · https://bullethaven.com/review/rogue-genesia
- Megabonk — PC Gamer, Destructoid, FullCleared, GamesHub: https://www.pcgamer.com/games/roguelike/megabonk-review/ · https://www.destructoid.com/reviews/megabonk-review-an-absurd-charming-yet-potent-evolution-of-the-survivors-like-formula/ · https://fullcleared.com/reviews/megabonk-review/ · https://www.gameshub.com/news/reviews/megabonk-review-2832477/
- DRG: Survivor — review y guías: https://playwanderer.online/game-reviews/deep-rock-galactic-survivor · https://earlyguides.com/deep-rock-galactic-survivor · https://earlyguides.com/deep-rock-galactic-survivor/combat
- Yet Another Zombie Survivors — Xbox/tienda, wiki, Metacritic: https://www.xbox.com/en-US/games/store/yet-another-zombie-survivors-game-preview/9NCK0FXQL38F · https://yetanotherzombie.wiki.gg/wiki/Stats_(Survivors) · https://www.metacritic.com/game/yet-another-zombie-survivors
- Género — saturación, fatiga y críticas: https://www.pcgamer.com/so-so-many-vampire-survivors-clones-came-out-this-year/ · https://howtomarketagame.com/2023/01/09/are-vampire-survivor-likes-dead/ · https://bottomfeeder.substack.com/p/the-fast-life-and-fiery-death-of · https://www.reddit.com/r/roguelites/comments/1kur1vd/anyone_else_tired_of_survivorlikes/ · https://www.reddit.com/r/gamedev/comments/1sl3sd8/are_survivorslikes_finally_out_of_fashion/
