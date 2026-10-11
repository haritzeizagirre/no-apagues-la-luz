"""Captura de pantalla del juego corriendo en el navegador + análisis ASCII."""
from __future__ import annotations

import base64
import json
import sys
import time
import urllib.request

import websocket

import os
DEBUG = os.environ.get("NAPL_CDP", "http://127.0.0.1:9223")
OUT = sys.argv[1] if len(sys.argv) > 1 else "web_game.png"


def main() -> None:
    with urllib.request.urlopen(DEBUG + "/json/list", timeout=4) as r:
        pages = [t for t in json.load(r) if t.get("type") == "page" and "8000" in t.get("url", "")]
    if not pages:
        print("sin pestaña del juego")
        return
    ws = websocket.create_connection(pages[0]["webSocketDebuggerUrl"], timeout=15,
                                     suppress_origin=True)

    def send(mid, method, params=None, timeout=30):
        ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        ws.settimeout(timeout)
        t0 = time.time()
        while time.time() - t0 < timeout:
            try:
                m = json.loads(ws.recv())
            except Exception:
                return None
            if m.get("id") == mid:
                return m
        return None

    r = send(1, "Runtime.evaluate",
             {"expression": "((document.querySelector('.xterm-rows')||{}).innerText||'').slice(-600)",
              "returnByValue": True})
    if r:
        print("TERMINAL (últimas líneas):")
        print(r["result"]["result"].get("value"))
    r = send(2, "Page.captureScreenshot", {"format": "png"}, timeout=60)
    data = (r or {}).get("result", {}).get("data")
    if not data:
        print("sin captura")
        return
    with open(OUT, "wb") as f:
        f.write(base64.b64decode(data))
    print("screenshot ->", OUT)
    # rect real del canvas (el template lo redimensiona al vuelo)
    r = send(3, "Runtime.evaluate", {"expression": "(() => {const c=document.querySelector('canvas.emscripten'); if(!c) return null; const r=c.getBoundingClientRect(); return JSON.stringify([r.x,r.y,r.width,r.height]);})()", "returnByValue": True})
    rect = json.loads(r["result"]["result"]["value"]) if r else None
    ws.close()

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
    if rect:
        rx, ry, rw, rh = (int(v) for v in rect)
        crop = pygame.Surface((rw, rh))
        crop.blit(img, (0, 0), (rx, ry, rw, rh))
        img = pygame.transform.smoothscale(crop, (640, 360))
        print(f"recorte del canvas: {rect}")
        w, h = img.get_size()
    step = max(1, w // 110)
    for y in range(0, h, step * 2):
        row = "".join("#" if sum(img.get_at((x, y))[:3]) > 380 else
                      ("+" if sum(img.get_at((x, y))[:3]) > 150 else
                       ("." if sum(img.get_at((x, y))[:3]) > 40 else " "))
                      for x in range(0, w, step))
        print("|" + row + "|")


if __name__ == "__main__":
    main()
