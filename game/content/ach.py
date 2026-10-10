"""29 Sellos (logros). cond: ("stat",k,n) | ("run",k,n) | ("boss",id,n) | ("enemy",id,n)."""
from __future__ import annotations

ACHIEVEMENTS = [
    dict(id="off_primera", name="Primer turno", desc="Completa tu primera noche (como termine).",
         chispas=20, cond=("stat", "runs", 1)),
    dict(id="off_h5", name="Las 23:00", desc="Aguanta hasta la hora 5.", chispas=25,
         cond=("run", "best_wave", 5)),
    dict(id="off_h8", name="Cambio de guardia", desc="Aguanta hasta la hora 8.",
         chispas=30, cond=("run", "best_wave", 8)),
    dict(id="off_h10", name="Media noche", desc="Aguanta hasta la hora 10.",
         chispas=40, unlock="char:tosty", cond=("run", "best_wave", 10)),
    dict(id="off_h12", name="La hora del café malo", desc="Aguanta hasta la hora 12.",
         chispas=50, unlock="mutator:sobrecarga", cond=("run", "best_wave", 12)),
    dict(id="off_h15", name="Madrugada hostil", desc="Aguanta hasta la hora 15.",
         chispas=70, unlock="char:radio", cond=("run", "best_wave", 15)),
    dict(id="off_jefe1", name="Despertar", desc="Derrota a EL DESPERTADOR.", chispas=40,
         cond=("boss", "despertador", 1)),
    dict(id="off_jefe2", name="Reunión cerrada", desc="Derrota a LA REUNIÓN INTERMINABLE.",
         chispas=60, cond=("boss", "reunion", 1)),
    dict(id="off_jefe3", name="Deadline cumplido", desc="Derrota a EL DEADLINE.", chispas=90,
         cond=("boss", "deadline", 1)),
    dict(id="off_ganar", name="Se apaga el Olvido", desc="Derrota a EL OLVIDO y termina la noche.",
         chispas=120, unlock="char:taza", cond=("boss", "olvido", 1)),
    dict(id="off_endless3", name="Hora extra", desc="Llega a la hora extra 3.", chispas=100,
         unlock="mutator:turno_doble", cond=("run", "endless", 3)),
    dict(id="off_guardia2", name="Guardia 2 superada", desc="Gana una noche en Guardia 2.",
         chispas=80, unlock="mutator:apagon", cond=("stat", "guardia_best", 2)),
    dict(id="off_guardia3", name="Guardia 3 superada", desc="Gana una noche en Guardia 3.",
         chispas=120, unlock="char:alargador", cond=("stat", "guardia_best", 3)),
    dict(id="off_guardia4", name="Guardia 4 superada", desc="Gana una noche en Guardia 4.",
         chispas=160, unlock="mutator:jefe_furioso", cond=("stat", "guardia_best", 4)),
    dict(id="off_guardia5", name="Final de trimestre", desc="Gana una noche en Guardia 5. Nada más que decir.",
         chispas=300, cond=("stat", "guardia_best", 5)),
    dict(id="off_kills300", name="Pequeño caos", desc="Elimina 600 enemigos en total.",
         chispas=30, unlock="char:ventilin", cond=("stat", "kills", 600)),
    dict(id="off_kills1000", name="Exterminio de cubículos", desc="Elimina 2000 enemigos en total.",
         chispas=60, unlock="char:raton", cond=("stat", "kills", 2000)),
    dict(id="off_kills3000", name="Almacén vacío", desc="Elimina 3000 enemigos en total.",
         chispas=120, unlock="mutator:plaga", cond=("stat", "kills", 3000)),
    dict(id="off_crit200", name="Puntería de oficina", desc="Asesta 400 críticos.", chispas=50,
         unlock="char:grapa", cond=("stat", "crits", 400)),
    dict(id="off_crit500", name="Pulso de cirujano", desc="Asesta 500 críticos.", chispas=90,
         unlock="weapon:laser", cond=("stat", "crits", 500)),
    dict(id="off_monedas1000", name="Buchaca llena", desc="Consigue 1000 monedas en total.",
         chispas=80, unlock="item:tarjeta_plata", cond=("stat", "coins", 1000)),
    dict(id="off_merges5", name="Manitas", desc="Fusiona armas 5 veces.", chispas=60,
         unlock="item:alargador_pro", cond=("stat", "merges", 5)),
    dict(id="off_cables30", name="Cables pelados", desc="Elimina 30 cables escurridizos.",
         chispas=40, unlock="weapon:cable", cond=("enemy", "cable", 30)),
    dict(id="off_dashes100", name="Reflejos de gato de oficina", desc="Usa el Dash 100 veces.",
         chispas=70, unlock="weapon:movil", cond=("stat", "dashes", 100)),
    dict(id="off_combo50", name="En racha", desc="Alcanza un combo de 50 en una noche.",
         chispas=60, unlock="item:multipresa", cond=("run", "best_combo", 50)),
    dict(id="off_crates50", name="Reciclaje activo", desc="Rompe 50 cajas de cartón.",
         chispas=50, unlock="item:funda_antigolpe", cond=("stat", "crates", 50)),
    dict(id="off_grapas120", name="Grapas fuera", desc="Elimina 120 grapadoras salvajes.",
         chispas=70, unlock="item:grapadora_oro", cond=("enemy", "grapa_ranged", 120)),
    dict(id="off_ratones40", name="Control de plagas", desc="Elimina 40 ratones infectados.",
         chispas=40, unlock="item:usb3", cond=("enemy", "raton", 40)),
    dict(id="off_fogonazos30", name="Fogonazo profesional", desc="Usa el Fogonazo 30 veces.",
         chispas=50, unlock="item:diario", cond=("stat", "fogonazos", 30)),
]

BY_ID = {a["id"]: a for a in ACHIEVEMENTS}


def seal_for(unlock_id: str):
    """Sello (logro) que otorga este desbloqueo, si existe."""
    return next((a for a in ACHIEVEMENTS if a.get("unlock") == unlock_id), None)


def evaluate(save, runstats: dict | None = None) -> list[tuple[str, int, str | None]]:
    """Devuelve [(ach_id, chispas, unlock_id)] recién completados."""
    newly = []
    rs = runstats or {}
    for a in ACHIEVEMENTS:
        if save.ach_done(a["id"]):
            continue
        kind = a["cond"][0]
        done = False
        if kind == "stat":
            key, n = a["cond"][1], a["cond"][2]
            done = save.data["stats"].get(key, 0) >= n
        elif kind == "run":
            key, n = a["cond"][1], a["cond"][2]
            done = rs.get(key, 0) >= n
        elif kind == "boss":
            bid, n = a["cond"][1], a["cond"][2]
            done = save.data["bestiary_boss"].get(bid, 0) >= n
        elif kind == "enemy":
            eid, n = a["cond"][1], a["cond"][2]
            done = save.data["bestiary"].get(eid, 0) >= n
        if done:
            save.ach_complete(a["id"])
            if a.get("unlock"):
                save.unlock(a["unlock"])
            newly.append((a["id"], a.get("chispas", 0), a.get("unlock")))
    return newly


def n_done(save) -> int:
    return sum(1 for a in ACHIEVEMENTS if save.ach_done(a["id"]))
