"""Verificación del build web (pygbag) con Chrome headless vía CDP directo.

Uso:  python tools/web_check.py [url] [salida.png]
Requiere: Chrome en --remote-debugging-port=9222 con la página abierta.
Espera en TIEMPO REAL a que el juego arranque (canvas3d visible), recoge
consola/terminal del runtime, captura pantalla y analiza píxeles.
"""
from __future__ import annotations

import base64
import json
import sys
import time
import urllib.request

import websocket

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8130/"
OUT = sys.argv[2] if len(sys.argv) > 2 else "web_shot.png"
DEBUG = "http://127.0.0.1:9222"

EXPR = (
    "(() => {"
    " const c=document.querySelector('#canvas3d');"
    " const m=document.querySelector('#canvas');"
    " const t=(document.querySelector('.xterm-rows')||{}).innerText||'';"
    " return JSON.stringify({"
    "  t:document.title,"
    "  c3d:c?[c.width,c.height,c.hidden]:null,"
    "  m:m?[m.width,m.height]:null,"
    "  term:t.replace(/\\s+/g,' ').slice(-260),"
    "  body:document.body.innerText.replace(/\\s+/g,' ').slice(0,140)"
    " }); })()"
)


def find_target(tries=30):
    want = URL.split("//")[-1].split("/")[0]   # host:puerto objetivo
    for _ in range(tries):
        try:
            with urllib.request.urlopen(DEBUG + "/json/list", timeout=3) as r:
                data = json.load(r)
            for t in data:
                if t.get("type") == "page" and want in t.get("url", ""):
                    return t["webSocketDebuggerUrl"]
            for t in data:
                if t.get("type") == "page" and t.get("url", "").startswith("http"):
                    return t["webSocketDebuggerUrl"]
        except Exception:
            pass
        time.sleep(1)
    return None


def main() -> int:
    ws_url = find_target()
    if not ws_url:
        print("NO TARGET CDP")
        return 2
    ws = websocket.create_connection(ws_url, timeout=30, suppress_origin=True)
    n = [0]

    def send(method, params=None, timeout=25):
        n[0] += 1
        my = n[0]
        ws.send(json.dumps({"id": my, "method": method, "params": params or {}}))
        t0 = time.time()
        ws.settimeout(timeout)
        while time.time() - t0 < timeout:
            try:
                raw = ws.recv()
            except Exception:
                return None
            try:
                m = json.loads(raw)
            except Exception:
                continue
            if m.get("id") == my:
                return m
            meth = m.get("method")
            if meth == "Runtime.exceptionThrown":
                print("  EXC:", json.dumps(m["params"])[:280])
            elif meth == "Runtime.consoleAPICalled":
                args = [a.get("value") for a in m["params"].get("args", [])]
                print("  CONSOLE:", str(args)[:200])
        return None

    send("Runtime.enable")
    send("Page.enable")

    t0 = time.time()
    state = "?"
    last = None
    while time.time() - t0 < 210:
        r = send("Runtime.evaluate", {"expression": EXPR, "returnByValue": True}, timeout=18)
        if r is None:
            print(f"[{time.time()-t0:5.1f}s] (página ocupada, eval sin respuesta)")
            time.sleep(1)
            continue
        val = r.get("result", {}).get("result", {}).get("value")
        if val != last:
            print(f"[{time.time()-t0:5.1f}s] {val}")
            last = val
        try:
            d = json.loads(val) if val else {}
        except Exception:
            d = {}
        if d.get("term", "") and "Traceback" in d["term"]:
            state = "TRACEBACK"
            break
        c3d = d.get("c3d")
        if c3d and not c3d[2] and c3d[0] > 10:
            state = "CANVAS3D_VISIBLE"
            break
        if d.get("body") and "Loading" not in d["body"] and "Downloading" not in d["body"]:
            state = "SIN_OVERLAY"
        time.sleep(2)

    print("estado:", state)
    # ¿la página sigue viva? (los timers del bucle async avanzan)
    a = send("Runtime.evaluate", {"expression": "performance.now()", "returnByValue": True})
    time.sleep(3)
    b = send("Runtime.evaluate", {"expression": "performance.now()", "returnByValue": True})
    try:
        print("timers vivos:", round(b["result"]["result"]["value"] - a["result"]["result"]["value"], 1), "ms en 3 s")
    except Exception:
        print("timers: sin datos")

    r = send("Page.captureScreenshot", {"format": "png"}, timeout=60)
    data = (r or {}).get("result", {}).get("data")
    if data:
        with open(OUT, "wb") as f:
            f.write(base64.b64decode(data))
        print("screenshot ->", OUT)
    else:
        print("sin screenshot (la página quizá esté ocupada)")
    ws.close()

    # análisis de píxeles
    try:
        import pygame
        pygame.display.init()
        pygame.display.set_mode((64, 64))
        img = pygame.image.load(OUT)
        w, h = img.get_size()
        print(f"png {w}x{h}")
        colors = {}
        bright = 0
        for y in range(0, h, 4):
            for x in range(0, w, 4):
                c = img.get_at((x, y))[:3]
                colors[c] = colors.get(c, 0) + 1
                if sum(c) > 120:
                    bright += 1
        print("colores dominantes:", sorted(colors.items(), key=lambda kv: -kv[1])[:6])
        print("píxeles con luz:", bright)
        step = max(1, w // 96)
        for y in range(0, h, step * 2):
            row = "".join("#" if sum(img.get_at((x, y))[:3]) > 380 else
                          ("+" if sum(img.get_at((x, y))[:3]) > 150 else
                           ("." if sum(img.get_at((x, y))[:3]) > 40 else " "))
                          for x in range(0, w, step))
            print("|" + row + "|")
    except Exception as e:
        print("análisis png falló:", e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
