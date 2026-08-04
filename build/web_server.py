"""Zero-dependency local web host for AIsle.

The browser client and the desktop client both call the same Python simulation
core. The server binds to localhost by default and is not intended as a public
multi-user deployment.
"""
from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from core import generate_population, population_from_input, run_simulation, validate
from storage import load_last_result, load_project, save_last_result, save_project

ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"


class Handler(SimpleHTTPRequestHandler):
    server_version = "AIsle/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def _json(self, payload, status=HTTPStatus.OK):
        data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length > 12_000_000:
            raise ValueError("Request quá lớn")
        return json.loads(self.rfile.read(length).decode("utf-8")) if length else {}

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/project":
            layout, catalog = load_project()
            return self._json({"layout": layout, "catalog": catalog, "issues": validate(layout, catalog)})
        if path == "/api/last-result":
            return self._json({"result": load_last_result()})
        if path == "/health":
            return self._json({"ok": True})
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        try:
            path, body = urlparse(self.path).path, self._body()
            if path == "/api/project":
                issues = validate(body["layout"], body["catalog"])
                save_project(body["layout"], body["catalog"])
                return self._json({"ok": True, "issues": issues})
            if path == "/api/simulate":
                layout, catalog = body["layout"], body["catalog"]
                errors = [message for level, message in validate(layout, catalog) if level == "error"]
                if errors:
                    return self._json({"error": " · ".join(errors)}, HTTPStatus.BAD_REQUEST)
                seed = int(body.get("seed", 42))
                if body.get("population_mode") == "manual":
                    population = population_from_input(body.get("manual_npcs", []))
                    if not population:
                        raise ValueError("Cần ít nhất một NPC thủ công")
                else:
                    population = generate_population(catalog, int(body.get("npc_count", 180)), seed)
                result = run_simulation(layout, catalog, population, int(body.get("duration_minutes", 30)), seed,
                                        bool(body.get("crowd_avoidance", True)))
                result["name"] = str(body.get("name") or "Web simulation")
                save_project(layout, catalog)
                save_last_result(result)
                return self._json({"result": result})
            return self._json({"error": "API không tồn tại"}, HTTPStatus.NOT_FOUND)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            return self._json({"error": f"Simulation failed: {exc}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def log_message(self, fmt, *args):
        print(f"[AIsle] {self.address_string()} - {fmt % args}")


def main():
    parser = argparse.ArgumentParser(description="Run the AIsle local web app")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"AIsle Web: http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
