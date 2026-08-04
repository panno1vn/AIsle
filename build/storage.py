"""Local JSON + SQLite persistence for the desktop simulator."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from core import DEFAULT_CATALOG, DEFAULT_LAYOUT

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / "runtime"
RUNTIME.mkdir(exist_ok=True)
LAYOUT_FILE = RUNTIME / "layout.json"
CATALOG_FILE = RUNTIME / "catalog.json"
LAST_RESULT_FILE = RUNTIME / "last_result.json"
DATABASE = RUNTIME / "history.db"


def _load(path: Path, fallback):
    if not path.exists():
        return json.loads(json.dumps(fallback))
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return json.loads(json.dumps(fallback))


def load_project() -> tuple[dict, list[dict]]:
    return _load(LAYOUT_FILE, DEFAULT_LAYOUT), _load(CATALOG_FILE, DEFAULT_CATALOG)


def save_project(layout: dict, catalog: list[dict]) -> None:
    LAYOUT_FILE.write_text(json.dumps(layout, ensure_ascii=False, indent=2), encoding="utf-8")
    CATALOG_FILE.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")


def save_last_result(result: dict) -> None:
    LAST_RESULT_FILE.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS purchases (
            run_id TEXT, npc_id TEXT, product_id TEXT, purchase_type TEXT, tick INTEGER, price REAL
        )""")
        connection.execute("DELETE FROM purchases WHERE run_id = 'last'")
        connection.executemany(
            "INSERT INTO purchases VALUES ('last', ?, ?, ?, ?, ?)",
            [(p["npc_id"], p["product_id"], p["purchase_type"], p["tick"], p["price"]) for p in result["purchases"]],
        )


def load_last_result() -> dict | None:
    """Restore the latest completed simulation after the desktop app restarts."""
    if not LAST_RESULT_FILE.exists():
        return None
    try:
        result = json.loads(LAST_RESULT_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    required = {"layout", "agents", "purchases", "duration_minutes", "revenue"}
    return result if required.issubset(result) else None


def init_history() -> None:
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            seed INTEGER NOT NULL,
            npc_count INTEGER NOT NULL,
            duration_minutes INTEGER NOT NULL,
            revenue REAL NOT NULL,
            conversion_rate REAL NOT NULL,
            main_rate REAL NOT NULL,
            impulse_rate REAL NOT NULL,
            missing_rate REAL NOT NULL,
            result_path TEXT NOT NULL
        )""")


def save_history(name: str, result: dict) -> int:
    init_history()
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.execute(
            """INSERT INTO runs(name, created_at, seed, npc_count, duration_minutes,
               revenue, conversion_rate, main_rate, impulse_rate, missing_rate, result_path)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, result["created_at"], result["seed"], result["n"], result["duration_minutes"],
             result["revenue"], result["conversion_rate"], result["main_rate"],
             result["impulse_rate"], result["missing_rate"], str(LAST_RESULT_FILE)),
        )
        return int(cursor.lastrowid)


def list_history() -> list[dict]:
    init_history()
    with sqlite3.connect(DATABASE) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute("SELECT * FROM runs ORDER BY id DESC")]


def delete_history(run_id: int) -> None:
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("DELETE FROM runs WHERE id = ?", (run_id,))


def clear_history() -> None:
    init_history()
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("DELETE FROM runs")
