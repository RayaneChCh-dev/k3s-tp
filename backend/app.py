from flask import Flask, jsonify
import os
import psycopg2

app = Flask(__name__)


def get_db():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        database=os.environ.get("DB_NAME", "appdb"),
        user=os.environ.get("DB_USER", "appuser"),
        password=os.environ.get("DB_PASSWORD", "apppassword"),
        connect_timeout=3,
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "backend"}), 200


@app.route("/api/ready")
def ready():
    try:
        conn = get_db()
        conn.cursor().execute("SELECT 1;")
        conn.close()
        return jsonify({"status": "ready", "db": "up"}), 200
    except Exception as e:
        return jsonify({"status": "not-ready", "db": "down", "error": str(e)}), 503


@app.route("/api/users")
def users():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, name, role FROM users ORDER BY id;")
        rows = cur.fetchall()
        conn.close()
        return jsonify([{"id": r[0], "name": r[1], "role": r[2]} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/count")
def users_count():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users;")
        count = cur.fetchone()[0]
        conn.close()
        return jsonify({"count": count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
