"""Clic en el juego del navegador (coordenadas de página) + captura + terminal."""
from __future__ import annotations

import base64
import json
import sys
import time
import urllib.request

import websocket

import os
DEBUG = os.environ.get("NAPL_CDP", "http://127.0.0.1:9223")


def main() -> None:
    x, y = int(sys.argv[1]), int(sys.argv[2])
    out = sys.argv[3] if len(sys.argv) > 3 else "click.png"
    with urllib.request.urlopen(DEBUG + "/json/list", timeout=4) as r:
        pages = [t for t in json.load(r) if t.get("type") == "page" and "8000" in t.get("url", "")]
    ws = websocket.create_connection(pages[0]["webSocketDebuggerUrl"], timeout=20,
                                     suppress_origin=True)

    def send(mid, method, params=None, timeout=40):
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

    send(1, "Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y})
    time.sleep(0.2)
    send(2, "Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y,
                                         "button": "left", "clickCount": 1})
    time.sleep(0.1)
    send(3, "Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y,
                                         "button": "left", "clickCount": 1})
    print(f"clic en ({x},{y})")
    time.sleep(3)
    r = send(4, "Page.captureScreenshot", {"format": "png"}, timeout=60)
    data = (r or {}).get("result", {}).get("data")
    if not data:
        print("sin captura")
        return
    with open(out, "wb") as f:
        f.write(base64.b64decode(data))
    print("screenshot ->", out)
    r = send(5, "Runtime.evaluate",
             {"expression": "((document.querySelector('.xterm-rows')||{}).innerText||'').slice(-400)",
              "returnByValue": True})
    if r:
        print("TERMINAL:", r["result"]["result"].get("value"))
    ws.close()

    import pygame
    pygame.display.init()
    pygame.display.set_mode((64, 64))
    img = pygame.image.load(out)
    w, h = img.get_size()
    step = max(1, w // 110)
    for yy in range(0, h, step * 2):
        row = "".join("#" if sum(img.get_at((xx, yy))[:3]) > 380 else
                      ("+" if sum(img.get_at((xx, yy))[:3]) > 150 else
                       ("." if sum(img.get_at((xx, yy))[:3]) > 40 else " "))
                      for xx in range(0, w, step))
        print("|" + row + "|")


if __name__ == "__main__":
    main()
