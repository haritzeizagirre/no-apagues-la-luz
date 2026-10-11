"""Prueba interactiva: hover + clic + diff de pantallas (¿llegan los eventos al juego?)."""
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
    gx, gy = int(sys.argv[1]), int(sys.argv[2])   # coords del JUEGO (640x360)
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

    def shot(mid, path):
        r = send(mid, "Page.captureScreenshot", {"format": "png"}, timeout=60)
        data = (r or {}).get("result", {}).get("data")
        if not data:
            return None
        with open(path, "wb") as f:
            f.write(base64.b64decode(data))
        return path

    # mapear coords de juego (640x360) a coords de página
    r = send(1, "Runtime.evaluate",
             {"expression": """(() => {const c=document.querySelector('canvas');
              const r=c.getBoundingClientRect(); return JSON.stringify({x:r.x,y:r.y,w:r.width,h:r.height,cw:c.width,ch:c.height});})()""",
              "returnByValue": True})
    geo = json.loads(r["result"]["result"]["value"])
    # el juego va centrado: escala = min(cw/640, ch/360) con canvas rectangular
    sc = min(geo["cw"] / 640.0, geo["ch"] / 360.0)
    offx = (geo["cw"] - 640 * sc) / 2
    offy = (geo["ch"] - 360 * sc) / 2
    bx = (gx * sc + offx) * geo["w"] / geo["cw"]
    by = (gy * sc + offy) * geo["h"] / geo["ch"]
    px, py = geo["x"] + bx, geo["y"] + by
    print(f"juego({gx},{gy}) -> pagina({px:.0f},{py:.0f})  [geo={geo}]")

    a = shot(2, "i_before.png")
    send(3, "Input.dispatchMouseEvent", {"type": "mouseMoved", "x": px, "y": py})
    time.sleep(1.5)
    b = shot(4, "i_hover.png")
    send(5, "Input.dispatchMouseEvent", {"type": "mousePressed", "x": px, "y": py,
                                         "button": "left", "clickCount": 1})
    time.sleep(0.12)
    send(6, "Input.dispatchMouseEvent", {"type": "mouseReleased", "x": px, "y": py,
                                         "button": "left", "clickCount": 1})
    time.sleep(3.0)
    c = shot(7, "i_click.png")

    import pygame
    pygame.display.init()
    pygame.display.set_mode((64, 64))
    imgs = {}
    for name, path in (("antes", a), ("hover", b), ("clic", c)):
        if path:
            imgs[name] = pygame.image.load(path)
    def diff(i1, i2):
        if not (i1 and i2):
            return -1
        w, h = i1.get_size()
        n = 0
        for yy in range(0, h, 3):
            for xx in range(0, w, 3):
                if i1.get_at((xx, yy))[:3] != i2.get_at((xx, yy))[:3]:
                    n += 1
        return n
    if len(imgs) == 3:
        print("pixeles distintos antes->hover:", diff(imgs["antes"], imgs["hover"]))
        print("pixeles distintos hover->clic:", diff(imgs["hover"], imgs["clic"]))
        print("pixeles distintos antes->clic:", diff(imgs["antes"], imgs["clic"]))
    if c:
        img = imgs.get("clic")
        w, h = img.get_size()
        step = max(1, w // 110)
        for yy in range(0, h, step * 2):
            row = "".join("#" if sum(img.get_at((xx, yy))[:3]) > 380 else
                          ("+" if sum(img.get_at((xx, yy))[:3]) > 150 else
                           ("." if sum(img.get_at((xx, yy))[:3]) > 40 else " "))
                          for xx in range(0, w, step))
            print("|" + row + "|")
    ws.close()


if __name__ == "__main__":
    main()
