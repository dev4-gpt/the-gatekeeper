import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


DB_PATH = Path(__file__).resolve().parent.parent / "gatekeeper.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                need_text TEXT,
                authority_text TEXT,
                budget_text TEXT,
                timeline_text TEXT,
                need_score INTEGER,
                authority_score INTEGER,
                budget_score INTEGER,
                timeline_score INTEGER,
                outcome TEXT,
                reason TEXT,
                lead_score INTEGER,
                confidence_band TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_lead(
    answers: Dict[str, str],
    scores: Dict[str, int],
    outcome: str,
    reason: str,
    lead_score: int,
    confidence_band: str,
) -> int:
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO leads (
                created_at,
                need_text,
                authority_text,
                budget_text,
                timeline_text,
                need_score,
                authority_score,
                budget_score,
                timeline_score,
                outcome,
                reason,
                lead_score,
                confidence_band
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(timespec="seconds"),
                answers.get("need") or "",
                answers.get("authority") or "",
                answers.get("budget") or "",
                answers.get("timeline") or "",
                scores.get("need", 1),
                scores.get("authority", 1),
                scores.get("budget", 1),
                scores.get("timeline", 1),
                outcome,
                reason,
                lead_score,
                confidence_band,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def list_leads() -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT
                id,
                created_at,
                need_text,
                authority_text,
                budget_text,
                timeline_text,
                need_score,
                authority_score,
                budget_score,
                timeline_score,
                outcome,
                lead_score,
                confidence_band
            FROM leads
            ORDER BY created_at DESC
            """
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_lead(lead_id: int) -> Dict[str, Any] | None:
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT *
            FROM leads
            WHERE id = ?
            """,
            (lead_id,),
        )
        row = cur.fetchone()
        return dict(row) if row is not None else None
    finally:
        conn.close()

