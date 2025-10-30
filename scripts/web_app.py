#!/usr/bin/env python3
"""Small Flask app to serve the SQLite DB contents at '/'.

Run:
  python3 scripts/web_app.py

Then open http://127.0.0.1:5000/ in your browser.
"""
from flask import Flask, render_template, g, jsonify
import sqlite3
import os

APP_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(APP_DIR, 'best_sports_betting_odds.db')

app = Flask(__name__, template_folder=os.path.join(APP_DIR, 'templates'))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    if not os.path.exists(DB_PATH):
        return 'Database not found. Run the CSV->SQLite converter first.', 500
    db = get_db()
    cur = db.execute('SELECT id, section, entry_type, content FROM entries ORDER BY id')
    entries = cur.fetchall()
    return render_template('index.html', entries=entries)


@app.route('/api/entries')
def api_entries():
    if not os.path.exists(DB_PATH):
        return jsonify({'error':'DB not found'}), 500
    db = get_db()
    cur = db.execute('SELECT id, section, entry_type, content FROM entries ORDER BY id')
    rows = [dict(r) for r in cur.fetchall()]
    return jsonify(rows)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
