#!/usr/bin/env python3
"""Smart Bin AI backend (Flask + SQLite)

Run:
    python3 smwis.py

Requires:
    pip install flask

"""

import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, g, send_from_directory
from flask_cors import CORS

API_KEY = "smwis-key-2024"
DB_PATH = os.path.join(os.path.dirname(__file__), "smwis.db")
STATIC_DIR = os.path.dirname(__file__)

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")
CORS(app)

MEAL_SLOTS = [
    (5, 10, "breakfast"),
    (11, 15, "lunch"),
    (16, 21, "dinner"),
]


def get_db():
    db = getattr(g, "db", None)
    if db is None:
        exists = os.path.exists(DB_PATH)
        db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = sqlite3.Row
        g.db = db
        if not exists:
            init_db(db)
    return db


def init_db(db=None):
    if db is None:
        db = get_db()

    cursor = db.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            bin_id TEXT NOT NULL,
            dish TEXT NOT NULL,
            weight_kg REAL NOT NULL,
            battery_voltage REAL,
            wifi_rssi INTEGER,
            meal TEXT
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cooked (
            dish TEXT PRIMARY KEY,
            total_cooked_kg REAL NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
    )

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON readings(timestamp);"
    )

    db.commit()


@app.teardown_appcontext

def close_db(exception=None):
    db = getattr(g, "db", None)
    if db is not None:
        db.close()


def auth_required(req):
    key = req.headers.get("X-API-Key")
    if key != API_KEY:
        return False
    return True


def meal_for_time(dt: datetime):
    hour = dt.hour
    for start, end, meal in MEAL_SLOTS:
        if start <= hour <= end:
            return meal
    return "other"


def row_to_dict(row):
    return {k: row[k] for k in row.keys()}


@app.route("/health", methods=["GET"])
def health():
    if not auth_required(request):
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) as c FROM readings")
    readings = cursor.fetchone()["c"]

    cursor.execute("SELECT COUNT(DISTINCT bin_id) as c FROM readings")
    bins = cursor.fetchone()["c"]

    cursor.execute("SELECT COUNT(DISTINCT dish) as c FROM readings")
    dishes = cursor.fetchone()["c"]

    return jsonify({
        "status": "ok",
        "readings": readings,
        "bins": bins,
        "dishes": dishes,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })


@app.route("/data", methods=["POST"])
def add_reading():
    if not auth_required(request):
        return jsonify({"error": "Unauthorized"}), 401

    body = request.get_json() or {}
    bin_id = str(body.get("bin_id", "")).strip()
    dish = str(body.get("dish", "")).strip()
    weight = body.get("weight_kg")

    if not bin_id or not dish or weight is None:
        return jsonify({"error": "bin_id, dish and weight_kg are required"}), 400

    try:
        weight = float(weight)
    except Exception:
        return jsonify({"error": "weight_kg must be numeric"}), 400

    if weight < 0:
        return jsonify({"error": "weight_kg must be non-negative"}), 400

    battery = body.get("battery_voltage")
    rssi = body.get("wifi_rssi")

    now = datetime.utcnow()
    meal = meal_for_time(now)

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO readings (timestamp, bin_id, dish, weight_kg, battery_voltage, wifi_rssi, meal) VALUES (?, ?, ?, ?, ?, ?, ?);",
        (now.isoformat() + "Z", bin_id, dish, weight, battery, rssi, meal)
    )
    db.commit()

    return jsonify({"message": "Reading stored", "id": cursor.lastrowid}), 201


@app.route("/readings", methods=["GET"])
def get_readings():
    if not auth_required(request):
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 200")
    rows = cursor.fetchall()
    return jsonify({"readings": [row_to_dict(r) for r in rows]})


@app.route("/set-cooked", methods=["POST"])
def set_cooked():
    if not auth_required(request):
        return jsonify({"error": "Unauthorized"}), 401

    body = request.get_json() or {}
    dish = str(body.get("dish", "")).strip()
    cooked = body.get("total_cooked_kg")

    if not dish or cooked is None:
        return jsonify({"error": "dish and total_cooked_kg are required"}), 400

    try:
        cooked = float(cooked)
    except Exception:
        return jsonify({"error": "total_cooked_kg must be numeric"}), 400

    if cooked < 0:
        return jsonify({"error": "total_cooked_kg must be non-negative"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO cooked (dish, total_cooked_kg, updated_at) VALUES (?, ?, ?) ON CONFLICT(dish) DO UPDATE SET total_cooked_kg = excluded.total_cooked_kg, updated_at = excluded.updated_at;",
        (dish, cooked, datetime.utcnow().isoformat() + "Z")
    )
    db.commit()

    return jsonify({"message": "Cooked amount set", "dish": dish, "total_cooked_kg": cooked}), 201


@app.route("/analyzer", methods=["GET"])
def analyzer():
    if not auth_required(request):
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT dish, SUM(weight_kg) as total_waste FROM readings GROUP BY dish")
    waste_by_dish = {r["dish"]: round(r["total_waste"], 2) for r in cursor.fetchall()}

    cursor.execute("SELECT meal, SUM(weight_kg) as total_waste FROM readings GROUP BY meal")
    waste_by_meal = {r["meal"]: round(r["total_waste"], 2) for r in cursor.fetchall()}

    cursor.execute("SELECT SUM(weight_kg) as total_waste FROM readings")
    total_waste = float(cursor.fetchone()["total_waste"] or 0)

    cursor.execute("SELECT SUM(total_cooked_kg) as total_cooked FROM cooked")
    total_cooked = float(cursor.fetchone()["total_cooked"] or 0)

    waste_percent = round((total_waste / total_cooked * 100) if total_cooked > 0 else 0.0, 2)
    efficiency_score = max(0, round(100 - waste_percent, 2))

    return jsonify({
        "waste_by_dish": waste_by_dish,
        "waste_by_meal": waste_by_meal,
        "waste_percent": waste_percent,
        "efficiency_score": efficiency_score,
        "total_waste_kg": round(total_waste, 2),
        "total_cooked_kg": round(total_cooked, 2)
    })


@app.route("/patterns", methods=["GET"])
def patterns():
    if not auth_required(request):
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT bin_id, COUNT(*) as count, AVG(weight_kg) as avg_weight FROM readings GROUP BY bin_id")
    bins = cursor.fetchall()

    patterns = []
    for b in bins:
        if b["count"] >= 10 and b["avg_weight"] > 2.5:
            patterns.append({
                "type": "HighWasteBin",
                "severity": "warning",
                "message": f"Bin {b['bin_id']} has high average waste ({round(b['avg_weight'],2)}kg) across {b['count']} readings"
            })

    if not patterns:
        patterns.append({"type": "OK", "severity": "info", "message": "No unusual patterns detected"})

    return jsonify({"patterns_found": len(patterns), "patterns": patterns})


@app.route("/crowd", methods=["GET"])
def crowd():
    if not auth_required(request):
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    cursor = db.cursor()
    cutoff = datetime.utcnow() - timedelta(minutes=30)
    cursor.execute("SELECT SUM(weight_kg) as total_30min FROM readings WHERE timestamp >= ?", (cutoff.isoformat() + "Z",))
    total_30min = float(cursor.fetchone()["total_30min"] or 0)

    velocity = round(total_30min / 30, 2)
    threshold = 1.5

    status = "normal"
    alert = None
    if velocity >= threshold:
        status = "busy"
        alert = "Crowd is high. Recommend deploy extra bins."

    # per bin velocity
    cursor.execute("SELECT bin_id, SUM(weight_kg) as total FROM readings WHERE timestamp >= ? GROUP BY bin_id", (cutoff.isoformat() + "Z",))
    per_bin_velocity = {r["bin_id"]: round((r["total"] or 0) / 30, 2) for r in cursor.fetchall()}

    return jsonify({
        "velocity_kg_per_min": velocity,
        "threshold_kg_per_min": threshold,
        "crowd_status": status,
        "alert": alert,
        "per_bin_velocity": per_bin_velocity
    })


@app.route("/efficiency", methods=["GET"])
def efficiency():
    if not auth_required(request):
        return jsonify({"error": "Unauthorized"}), 401
    return analyzer()


@app.route("/predict", methods=["GET"])
def predict():
    if not auth_required(request):
        return jsonify({"error": "Unauthorized"}), 401

    # Simple prediction: if waste/dish is high, recommend reduce cooking
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT dish, SUM(weight_kg) as waste FROM readings GROUP BY dish")
    waste_by_dish = {r["dish"]: float(r["waste"] or 0) for r in cursor.fetchall()}

    cursor.execute("SELECT dish, total_cooked_kg FROM cooked")
    cooked = {r["dish"]: float(r["total_cooked_kg"] or 0) for r in cursor.fetchall()}

    recs = []
    for dish, cooked_amt in cooked.items():
        waste_amt = waste_by_dish.get(dish, 0.0)
        if cooked_amt <= 0:
            recs.append({"dish": dish, "message": "No cooked amount set; collect more data"})
            continue

        waste_pct = round((waste_amt / cooked_amt * 100), 1) if cooked_amt > 0 else 0
        recommendation = "Optimize cook amount" if waste_pct > 15 else "Cook levels good"

        recs.append({
            "dish": dish,
            "avg_waste_kg": round(waste_amt, 2),
            "waste_percent": waste_pct,
            "trend": "stable",
            "recommendation": f"Waste {waste_pct}% – {recommendation}"
        })

    if not recs:
        return jsonify({"message": "No predictions available; no cooked data yet", "recommendations": []})

    return jsonify({"recommendations": recs})


if __name__ == "__main__":
    # Ensure DB exists
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            init_db(conn)

    print("Starting Smart Bin AI backend on http://127.0.0.1:5500")
    app.run(host="127.0.0.1", port=5500)
