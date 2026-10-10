"""QA del .exe: selftest del binario + arranque real de ventana + limpieza."""
from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "dist", "NoApaguesLaLuz.exe")


def find_window_with(substr: str):
    user32 = ctypes.windll.user32
    found = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def cb(hwnd, _lp):
        n = user32.GetWindowTextLengthW(hwnd)
        if n:
            buf = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(hwnd, buf, n + 1)
            if substr.lower() in buf.value.lower():
                found.append((hwnd, buf.value))
        return True

    user32.EnumWindows(cb, None)
    return found


def main() -> int:
    if not os.path.exists(EXE):
        print(json.dumps({"ok": False, "error": "no existe el exe"}))
        return 1
    report = {"exe": EXE, "exe_bytes": os.path.getsize(EXE)}

    # 1) selftest headless del binario
    rep_path = os.path.join(os.environ.get("TEMP", "."), "napal_selftest_report.json")
    try:
        os.remove(rep_path)
    except OSError:
        pass
    t0 = time.time()
    p = subprocess.run([EXE, "--selftest"], timeout=420)
    report["selftest"] = {"rc": p.returncode, "s": round(time.time() - t0, 1)}
    try:
        with open(rep_path, "r", encoding="utf-8") as f:
            rp = json.load(f)
        report["selftest"]["ok"] = rp.get("ok")
        report["selftest"]["checks"] = [{"name": c["name"], "ok": c["ok"]} for c in rp.get("checks", [])]
        report["selftest"]["sims_ok"] = all("error" not in s for s in rp.get("sims", []))
        report["selftest"]["sims"] = rp.get("sims", [])
    except Exception as e:
        report["selftest"]["ok"] = False
        report["selftest"]["error"] = f"{type(e).__name__}: {e}"

    # 2) arranque real de ventana
    t_start = time.time() - 2
    subprocess.run(["taskkill", "/F", "/IM", os.path.basename(EXE)], capture_output=True)
    proc = subprocess.Popen([EXE])
    time.sleep(11)
    wins_check = find_window_with("APAGUES")
    alive = bool(wins_check)
    wins = wins_check
    report["ventana"] = {"proceso_vivo": alive, "ventanas": [w[1] for w in wins]}
    # matar TODAS las instancias (el onefile deja vivo al hijo si matas al padre)
    subprocess.run(["taskkill", "/F", "/IM", os.path.basename(EXE)], capture_output=True)
    try:
        proc.wait(timeout=10)
    except Exception:
        pass

    # 3) crash log: solo cuenta como fallo si es NUEVO (posterior al arranque de esta verificación)
    crash = os.path.join(os.environ.get("APPDATA", ""), "NoApaguesLaLuz", "crash.txt")
    crash_nuevo = False
    if os.path.exists(crash):
        crash_nuevo = os.path.getmtime(crash) >= t_start
    report["crash_txt"] = os.path.exists(crash)
    report["crash_nuevo"] = crash_nuevo
    ok = bool(report["selftest"].get("ok")) and report["ventana"]["proceso_vivo"] and bool(report["ventana"]["ventanas"]) and not crash_nuevo
    report["ok"] = ok
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
