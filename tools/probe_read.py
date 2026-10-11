"""Lectura rápida del estado de la sonda: títulos + terminal (con timeouts cortos)."""
from __future__ import annotations

import json
import sys
import urllib.request

import websocket

import os
DEBUG = os.environ.get("NAPL_CDP", "http://127.0.0.1:9223")


def main() -> None:
    with urllib.request.urlopen(DEBUG + "/json/list", timeout=4) as r:
        data = json.load(r)
    ps = [t for t in data if t.get("type") == "page"]
    for t in ps:
        print("TÍTULO:", repr(t.get("title", "")), "| URL:", t.get("url", "")[:50])
    game = [t for t in ps if "8000" in t.get("url", "")]
    if not game:
        print("(sin pestaña del juego)")
        return
    try:
        ws = websocket.create_connection(game[0]["webSocketDebuggerUrl"], timeout=10,
                                         suppress_origin=True)
        ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate",
                            "params": {"expression":
                                       "((document.querySelector('.xterm-rows')||{}).innerText||'').slice(-3500)",
                                       "returnByValue": True}}))
        ws.settimeout(30)
        while True:
            m = json.loads(ws.recv())
            if m.get("id") == 1:
                print("=== TERMINAL ===")
                print(m["result"]["result"].get("value"))
                break
    except Exception as e:
        print("terminal no legible:", str(e)[:120])


if __name__ == "__main__":
    sys.exit(main())
