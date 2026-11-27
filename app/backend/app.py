import os
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", "/app/data/app.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        if count == 0:
            conn.execute(
                "INSERT INTO items (title, completed) VALUES (?, ?)",
                ("Deploy 3-tier app to AWS ECS Fargate", 0),
            )
        conn.commit()


init_db()


@app.route("/api/health", methods=["GET"])
def health():
    try:
        with get_db() as conn:
            conn.execute("SELECT 1")
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as exc:
        return jsonify({"status": "unhealthy", "error": str(exc)}), 500


@app.route("/api/items", methods=["GET"])
def list_items():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, title, completed, created_at FROM items ORDER BY id DESC"
        ).fetchall()
    return jsonify([dict(r) for r in rows]), 200


@app.route("/api/items", methods=["POST"])
def create_item():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400
    with get_db() as conn:
        cur = conn.execute("INSERT INTO items (title) VALUES (?)", (title,))
        conn.commit()
        row = conn.execute(
            "SELECT id, title, completed, created_at FROM items WHERE id = ?",
            (cur.lastrowid,),
        ).fetchone()
    return jsonify(dict(row)), 201


@app.route("/api/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    data = request.get_json(silent=True) or {}
    completed = 1 if data.get("completed") else 0
    with get_db() as conn:
        cur = conn.execute(
            "UPDATE items SET completed = ? WHERE id = ?", (completed, item_id)
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "not found"}), 404
    return jsonify({"id": item_id, "completed": bool(completed)}), 200


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    with get_db() as conn:
        cur = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": item_id}), 200
