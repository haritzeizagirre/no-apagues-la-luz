"""Todos los textos del juego (ES) con algo de sal.""" 
from __future__ import annotations

TAGLINE = "una lámpara contra el turno de noche"

LORE = [
    "Edificio Möbius, planta 404. Son las 18:00. Uno a uno, todos fichan y se van.",
    "El último en salir apaga la luz principal... y sonríe mientras lo hace.",
    "Pero hoy alguien se quedó encendida. LÍA, una lámpara de escritorio con la bombilla algo suelta, una vocación enorme de molestar y cero intención de apagarse.",
    "Cuando cae la noche, la oficina sueña. Y sus sueños son el OLVIDO: los lunes no vividos, las reuniones que pudieron ser un correo, los deadlines que nadie cumplió. Si te apagan, lo recuerdan todo. Y vienen a por ti.",
    "Aguanta 20 horas de turno. Roba sus monedas. Compra en La Expendedora. Guarda tus Chispas en El Cajón de los Recuerdos. Y que nunca se haga la luz.",
]

TIPS = [
    "En penumbra haces un 35% menos de daño. Mantén a los enemigos dentro de tu círculo de luz.",
    "El Fogonazo aturde a todo lo iluminado. Guárdalo para las avalanchas.",
    "Dos armas iguales del mismo nivel se pueden fusionar en la tienda (doble clic en la segunda).",
    "La máquina se puede sacudir... pero cada sacudida encarece la siguiente.",
    "Las Bombillas Fundidas te roban radio de luz cuando se acercan. Prioridad alta.",
    "Las Sombras del Olvido son lentas en tu luz y rapidísimas en la oscuridad.",
    "Rompe cajas de cartón: sueltan monedas y, con suerte, algo más.",
    "Vender las armas que no uses te devuelve la mitad de su precio.",
    "Las Marcas del Turno dan más Chispas a cambio de dolor. Tú eliges.",
    "El Despertador avisa antes de sonar. Cuando se pare, aléjate.",
    "El Becario hace dash en línea recta: cambia de dirección justo cuando se agacha.",
    "Revisa El Cajón: una buena inversión temprana en Luz se nota desde la hora 6.",
    "Una taza de café caliente deja charco. No te quedes parada encima.",
    "Los Recuerdos (XP) también inflan la barra de la hora. Recógelos aunque estés lejos.",
]

SHOP_FLAVOR = [
    "La máquina tararea bajito.",
    "Un zumbido familiar. Casi hogareño.",
    "Hay un papel pegado: «NO SACUDIR». Ignóralo.",
    "La ranura de monedas brilla con malas intenciones.",
    "Huele a café rancio y a oportunidades.",
    "Detrás del cristal, todo parece más apetecible de lo que es.",
    "La máquina tiene un golpe abollado con forma de puño.",
    "Solo acepta monedas. Y secretos.",
]

CONTROLS = [
    ("WASD / Flechas", "Moverse"),
    ("ESPACIO", "Fogonazo (pulso de luz)"),
    ("SHIFT", "Dash (esquiva con invulnerabilidad)"),
    ("ESC", "Pausa"),
    ("F11", "Pantalla completa"),
    ("F12", "Captura de pantalla"),
    ("Ratón", "Menús y tienda"),
]

DEFEAT_TITLES = [
    "TE APAGARON",
    "BOMBILLA FUNDIDA",
    "SE HIZO LA LUZ",
    "FIN DEL TURNO",
]

DEFEAT_LINES = [
    "La oficina suspira aliviada. Tú no.",
    "El Olvido recuerda tu nombre ahora. Mala señal.",
    "Alguien fichó por ti. Con una sonrisa.",
    "No pasa nada: las lámparas nunca mueren del todo.",
]

VICTORY_TITLE = "SOBREVIVISTE AL TURNO"
VICTORY_LINES = [
    "El edificio entero bosteza. El Olvido se repliega entre los archivadores, derrotado.",
    "A las 14:00, la primera persona ficha de vuelta y encuentra la oficina intacta.",
    "Solo una lámpara sigue encendida. Con los ojos entrecerrados. Cansada. Invicta.",
    "Mañana vuelve a cerrarse la oficina. Y tú ya sabes lo que hay que hacer.",
]

ENDLESS_PROMPT = "El día no ha llegado todavía. ¿SIGUES EN EL TURNO?"

CAJON_BLURB = "Cada chispa es una promesa. Compra barato, apágate tarde."

ARCHIVO_BLURB = "Bestiario de lo que despierta cuando te apagan."

SELLOS_BLURB = "Cada sello es una noche que el Olvido no ganó."

GUARDIA_BLURB = "Más riesgo, más chispas"

NEW_RUN_HINT = "Pulsa ENTER o haz clic para empezar la noche."

SHOP_TITLE = "LA EXPENDEDORA"
SHOP_SHAKE = "SACUDIR (reroll)"
SHOP_HEAL = "CURITA  (+30% vida)"
SHOP_SELL = "VENDER (mitad de precio)"

VARITA = {  # frases para incidencias del turno
    "flicker": "INCIDENCIA: parpadeo en el alumbrado",
    "surge": "INCIDENCIA: sobretensión en la planta",
    "boss_call": "INCIDENCIA: llamada del jefe",
    "coffee": "INCIDENCIA: alguien dejó café",
}

CREDITS = [
    "NO APAGUES LA LUZ — un roguelike de oficina nocturna",
    "",
    "Diseño, código y arte: generado por código (pixel art procedural).",
    "Motor: Python + pygame-ce.",
    "Fuentes: Press Start 2P, VT323 y Silkscreen (Google Fonts, licencia OFL).",
    "Audio: sintetizado + packs CC0 (Kenney / OpenGameArt) — ver assets/LICENCIAS.md.",
    "",
    "Gracias por jugar. Y por no apagar la luz.",
]
