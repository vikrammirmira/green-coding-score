import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "green_coding.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS events (
            event_id    TEXT PRIMARY KEY,
            user_id     TEXT NOT NULL,
            model       TEXT NOT NULL,
            input_tokens  INTEGER NOT NULL,
            output_tokens INTEGER NOT NULL,
            total_tokens  INTEGER NOT NULL,
            energy_kwh    REAL NOT NULL,
            carbon_gco2   REAL NOT NULL,
            timestamp   TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS scores (
            user_id          TEXT PRIMARY KEY,
            efficiency_score REAL NOT NULL DEFAULT 0,
            carbon_score     REAL NOT NULL DEFAULT 0,
            total_score      REAL NOT NULL DEFAULT 0,
            total_tokens     INTEGER NOT NULL DEFAULT 0,
            total_energy_kwh REAL NOT NULL DEFAULT 0,
            total_carbon_gco2 REAL NOT NULL DEFAULT 0,
            event_count      INTEGER NOT NULL DEFAULT 0,
            updated_at       TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS badges (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   TEXT NOT NULL,
            badge     TEXT NOT NULL,
            awarded_at TEXT NOT NULL,
            UNIQUE(user_id, badge)
        );

        CREATE TABLE IF NOT EXISTS optimizations (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          TEXT NOT NULL,
            baseline_tokens  INTEGER NOT NULL,
            optimized_tokens INTEGER NOT NULL,
            improvement_pct  REAL NOT NULL,
            tokens_saved     INTEGER NOT NULL,
            recorded_at      TEXT NOT NULL
        );
        """)
