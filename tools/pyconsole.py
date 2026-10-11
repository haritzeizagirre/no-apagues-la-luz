"""Inyecta comandos Python en la consola interactiva de pygbag (xterm de la página)."""
from __future__ import annotations

import json
import sys
import time
import urllib.request

import websocket

import os
DEBUG = os.environ.get("NAPL_CDP", "http://127.0.0.1:9223")


def send(ws, mid, method, params=None, timeout=30):
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


def main() -> None:
    code = sys.argv[1] if len(sys.argv) > 1 else "print('hola')"
    with urllib.request.urlopen(DEBUG + "/json/list", timeout=4) as r:
        pages = [t for t in json.load(r) if t.get("type") == "page" and "8000" in t.get("url", "")]
    ws = websocket.create_connection(pages[0]["webSocketDebuggerUrl"], timeout=20,
                                     suppress_origin=True)
    send(ws, 1, "Runtime.evaluate", {"expression":
         "document.querySelector('.xterm-helper-textarea')?.focus()"})
    time.sleep(0.3)
    send(ws, 2, "Input.insertText", {"text": code})
    time.sleep(0.3)
    send(ws, 3, "Input.dispatchKeyEvent", {"type": "keyDown", "key": "Enter",
                                           "code": "Enter", "windowsVirtualKeyCode": 13})
    send(ws, 4, "Input.dispatchKeyEvent", {"type": "keyUp", "key": "Enter",
                                           "code": "Enter", "windowsVirtualKeyCode": 13})
    time.sleep(2.5)
    r = send(ws, 5, "Runtime.evaluate",
             {"expression": "((document.querySelector('.xterm-rows')||{}).innerText||'').slice(-1500)",
              "returnByValue": True})
    print("=== CONSOLA ===")
    print(r["result"]["result"].get("value"))
    ws.close()


if __name__ == "__main__":
    main()
