"""
Simple helper to inspect plans.db

Usage:
    python scripts\inspect_db.py list
    python scripts\inspect_db.py show <id>

Prints a list of saved plans or JSON data for a single plan id.
"""
import sqlite3
import json
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / 'plans.db'


def list_plans(limit=50):
    if not DB_PATH.exists():
        print(f"No database found at {DB_PATH}")
        return
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, project_name, created_at FROM plans ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        print("No plans saved yet.")
        return
    for r in rows:
        print(f"{r['id']:>4} | {r['created_at']} | {r['project_name']}")


def show_plan(plan_id):
    if not DB_PATH.exists():
        print(f"No database found at {DB_PATH}")
        return
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT plan_data FROM plans WHERE id = ?", (plan_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        print(f"Plan with id {plan_id} not found.")
        return
    try:
        plan = json.loads(row['plan_data'])
        print(json.dumps(plan, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Failed to parse plan JSON: {e}")
        print("Raw data:\n")
        print(row['plan_data'])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == 'list':
        list_plans()
    elif cmd == 'show' and len(sys.argv) == 3:
        show_plan(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)
