#!/usr/bin/env python3
"""Convert best_sports_betting_odds.csv into a SQLite database.

Creates best_sports_betting_odds.db with table `entries`:
  id INTEGER PRIMARY KEY,
  section TEXT,
  entry_type TEXT,
  content TEXT

Usage:
  python3 scripts/csv_to_sqlite.py
"""
import csv
import sqlite3
import os
import sys

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'best_sports_betting_odds.csv')
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'best_sports_betting_odds.db')


def main():
    if not os.path.exists(CSV_PATH):
        print(f"CSV not found: {CSV_PATH}")
        sys.exit(1)

    # Remove existing DB to make runs idempotent
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT,
            entry_type TEXT,
            content TEXT
        )
        """
    )

    inserted = 0
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            section = row.get('section')
            entry_type = row.get('entry_type')
            content = row.get('content')
            cur.execute(
                "INSERT INTO entries (section, entry_type, content) VALUES (?, ?, ?)",
                (section, entry_type, content),
            )
            inserted += 1

    conn.commit()
    conn.close()
    print(f"Wrote {DB_PATH} with {inserted} rows")


if __name__ == '__main__':
    main()
