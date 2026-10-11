"""Vigila la sonda del navegador: lee títulos por /json/list (independiente del
renderer) y, cuando termina, lee la terminal del runtime vía CDP."""
from __future__ import annotations

import json
import time
import urllib.request

import websocket

import os
DEBUG = os.environ.get("NAPL_CDP", "http://127.0.0.1:9223")


def pages():
    with urllib.request.urlopen(DEBUG + "/json/list", timeout=3) as r:
        data = json.load(r)
    return [t for t in data if t.get("type") == "page"]


def main() -> None:
    last = None
    deadline = time.time() + 320
    while time.time() < deadline:
        try:
            ts = [(t.get("url", "")[:36], t.get("title", "")) for t in pages()]
            s = " | ".join(f"{u}::{t}" for u, t in ts)
        except Exception as e:
            s = f"sin CDP: {e}"
        if s != last:
            print(f"[{time.strftime('%H:%M:%S')}] {s}", flush=True)
            last = s
        if any("FIN ok" in t or "ERR" in t for _u, t in ts):
            break
        time.sleep(6)

    for _ in range(24):
        try:
            ps = [t for t in pages() if "8000" in t.get("url", "")]
            if not ps:
                time.sleep(2)
                continue
            ws = websocket.create_connection(ps[0]["webSocketDebuggerUrl"], timeout=10,
                                             suppress_origin=True)
            ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate",
                                "params": {"expression":
                                           "((document.querySelector('.xterm-rows')||{}).innerText||'').slice(-3000)",
                                           "returnByValue": True}}))
            ws.settimeout(25)
            while True:
                m = json.loads(ws.recv())
                if m.get("id") == 1:
                    print("=== TERMINAL DEL RUNTIME ===")
                    print(m["result"]["result"].get("value"))
                    return
        except Exception as e:
            print("terminal no legible aún:", str(e)[:90], flush=True)
            time.sleep(5)


if __name__ == "__main__":
    main()
