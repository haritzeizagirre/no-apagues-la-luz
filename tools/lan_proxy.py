"""Proxy HTTP minimo para probar el juego desde el movil cuando el cortafuegos
no permite al python del venv escuchar en la red (perfil Publico de Windows).

El python de Hermes SI tiene permiso de entrada; este proxy escucha en 0.0.0.0:8000
y reenvia al servidor pygbag en 127.0.0.1:8001, reescribiendo las URLs del indice
para que apunten a la IP desde la que entra el movil.

Uso:  python tools/lan_proxy.py [--listen 0.0.0.0:8000] [--backend 127.0.0.1:8001]
"""
from __future__ import annotations

import argparse
import http.client
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BACKEND = "127.0.0.1:8001"


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _proxy(self, method: str) -> None:
        host, port = BACKEND.split(":")
        conn = http.client.HTTPConnection(host, int(port), timeout=90)
        try:
            conn.request(method, self.path, headers={"Host": f"{host}:{port}"})
            resp = conn.getresponse()
            body = resp.read()
            ctype = resp.getheader("Content-Type", "")
            if "text/html" in ctype:
                pub = self.headers.get("Host", "")
                body = re.sub(rb"http://(127\.0\.0\.1|localhost):8001",
                              f"http://{pub}".encode(), body)
            self.send_response(resp.status)
            for k, v in resp.getheaders():
                if k.lower() in ("content-length", "transfer-encoding", "connection"):
                    continue
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if method != "HEAD":
                self.wfile.write(body)
        except Exception as e:  # noqa: BLE001
            try:
                self.send_error(502, f"proxy: {e}")
            except Exception:
                pass
        finally:
            conn.close()

    def do_GET(self) -> None:  # noqa: N802
        self._proxy("GET")

    def do_HEAD(self) -> None:  # noqa: N802
        self._proxy("HEAD")

    def log_message(self, fmt, *args) -> None:  # silencio
        pass


def main() -> None:
    global BACKEND
    ap = argparse.ArgumentParser()
    ap.add_argument("--listen", default="0.0.0.0:8000")
    ap.add_argument("--backend", default=BACKEND)
    args = ap.parse_args()
    BACKEND = args.backend
    lh, lp = args.listen.split(":")
    print(f"[proxy] escuchando en http://{lh}:{lp}  ->  {BACKEND}", flush=True)
    ThreadingHTTPServer((lh, int(lp)), Handler).serve_forever()


if __name__ == "__main__":
    main()
