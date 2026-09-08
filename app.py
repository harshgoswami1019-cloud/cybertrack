from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    Response
)

import sqlite3
import secrets
import csv
import io
import math
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

DATABASE = "locations.db"

# Session lifetime
SESSION_MINUTES = 120


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            share_token TEXT UNIQUE NOT NULL,
            monitor_token TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            active INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            accuracy REAL DEFAULT 0,
            distance_from_previous REAL DEFAULT 0,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# HELPERS
# =========================================================

def utc_now():
    return datetime.now(timezone.utc)


def iso_now():
    return utc_now().isoformat()


def parse_time(value):
    return datetime.fromisoformat(value)


def session_expired(session):
    return utc_now() > parse_time(session["expires_at"])


def generate_token():
    return secrets.token_urlsafe(32)


def get_session_by_share_token(token):
    conn = get_db()

    session = conn.execute(
        """
        SELECT *
        FROM sessions
        WHERE share_token = ?
        """,
        (token,)
    ).fetchone()

    conn.close()
    return session


def get_session_by_monitor_token(token):
    conn = get_db()

    session = conn.execute(
        """
        SELECT *
        FROM sessions
        WHERE monitor_token = ?
        """,
        (token,)
    ).fetchone()

    conn.close()
    return session


def haversine_km(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two GPS points.
    """

    earth_radius_km = 6371.0

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius_km * c


def get_last_location(session_id):
    conn = get_db()

    location = conn.execute(
        """
        SELECT *
        FROM locations
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (session_id,)
    ).fetchone()

    conn.close()

    return location


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():
    return render_template("index.html")


# =========================================================
# CREATE SESSION
# =========================================================

@app.route("/api/session/create", methods=["POST"])
def create_session():

    share_token = generate_token()
    monitor_token = generate_token()

    created = utc_now()
    expires = created + timedelta(minutes=SESSION_MINUTES)

    conn = get_db()

    conn.execute(
        """
        INSERT INTO sessions
        (
            share_token,
            monitor_token,
            created_at,
            expires_at,
            active
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            share_token,
            monitor_token,
            created.isoformat(),
            expires.isoformat(),
            0
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "share_token": share_token,
        "monitor_token": monitor_token,
        "expires_at": expires.isoformat()
    })


# =========================================================
# SHARE PAGE
# =========================================================

@app.route("/share/<share_token>")
def share_page(share_token):

    session = get_session_by_share_token(share_token)

    if not session:
        return "Invalid sharing session.", 404

    if session_expired(session):
        return "This sharing session has expired.", 410

    return render_template(
        "share.html",
        share_token=share_token,
        expires_at=session["expires_at"]
    )


# =========================================================
# MONITOR PAGE
# =========================================================

@app.route("/monitor/<monitor_token>")
def monitor_page(monitor_token):

    session = get_session_by_monitor_token(monitor_token)

    if not session:
        return "Invalid monitoring session.", 404

    if session_expired(session):
        return "This monitoring session has expired.", 410

    return render_template(
        "monitor.html",
        monitor_token=monitor_token,
        expires_at=session["expires_at"]
    )


# =========================================================
# START SESSION
# =========================================================

@app.route("/api/session/<share_token>/start", methods=["POST"])
def start_session(share_token):

    session = get_session_by_share_token(share_token)

    if not session:
        return jsonify({
            "success": False,
            "message": "Invalid session."
        }), 404

    if session_expired(session):
        return jsonify({
            "success": False,
            "message": "Session expired."
        }), 410

    conn = get_db()

    conn.execute(
        """
        UPDATE sessions
        SET active = 1
        WHERE id = ?
        """,
        (session["id"],)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Tracking started."
    })


# =========================================================
# STOP SESSION
# =========================================================

@app.route("/api/session/<share_token>/stop", methods=["POST"])
def stop_session(share_token):

    session = get_session_by_share_token(share_token)

    if not session:
        return jsonify({
            "success": False,
            "message": "Invalid session."
        }), 404

    conn = get_db()

    conn.execute(
        """
        UPDATE sessions
        SET active = 0
        WHERE id = ?
        """,
        (session["id"],)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Tracking stopped."
    })


# =========================================================
# SAVE LOCATION
# =========================================================

@app.route("/api/location", methods=["POST"])
def save_location():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400

    share_token = data.get("share_token")

    try:
        latitude = float(data.get("latitude"))
        longitude = float(data.get("longitude"))
        accuracy = float(data.get("accuracy", 0))
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid coordinates."
        }), 400

    session = get_session_by_share_token(share_token)

    if not session:
        return jsonify({
            "success": False,
            "message": "Invalid session."
        }), 404

    if session_expired(session):
        return jsonify({
            "success": False,
            "message": "Session expired."
        }), 410

    if not (-90 <= latitude <= 90):
        return jsonify({
            "success": False,
            "message": "Invalid latitude."
        }), 400

    if not (-180 <= longitude <= 180):
        return jsonify({
            "success": False,
            "message": "Invalid longitude."
        }), 400

    last_location = get_last_location(session["id"])

    distance = 0

    if last_location:
        distance = haversine_km(
            last_location["latitude"],
            last_location["longitude"],
            latitude,
            longitude
        )

    conn = get_db()

    conn.execute(
        """
        INSERT INTO locations
        (
            session_id,
            latitude,
            longitude,
            accuracy,
            distance_from_previous,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session["id"],
            latitude,
            longitude,
            accuracy,
            distance,
            iso_now()
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "distance_km": distance
    })


# =========================================================
# CURRENT LOCATION
# =========================================================

@app.route("/api/monitor/<monitor_token>/location")
def current_location(monitor_token):

    session = get_session_by_monitor_token(monitor_token)

    if not session:
        return jsonify({
            "success": False,
            "message": "Invalid monitoring token."
        }), 404

    if session_expired(session):
        return jsonify({
            "success": False,
            "message": "Session expired."
        }), 410

    location = get_last_location(session["id"])

    if not location:
        return jsonify({
            "success": True,
            "available": False,
            "active": bool(session["active"])
        })

    return jsonify({
        "success": True,
        "available": True,
        "active": bool(session["active"]),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "accuracy": location["accuracy"],
        "timestamp": location["timestamp"]
    })


# =========================================================
# HISTORY
# =========================================================

@app.route("/api/monitor/<monitor_token>/history")
def history(monitor_token):

    session = get_session_by_monitor_token(monitor_token)

    if not session:
        return jsonify({
            "success": False,
            "message": "Invalid monitoring token."
        }), 404

    conn = get_db()

    locations = conn.execute(
        """
        SELECT
            latitude,
            longitude,
            accuracy,
            distance_from_previous,
            timestamp
        FROM locations
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT 200
        """,
        (session["id"],)
    ).fetchall()

    conn.close()

    total_distance = sum(
        row["distance_from_previous"]
        for row in locations
    )

    data = []

    for row in locations:

        data.append({
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "accuracy": row["accuracy"],
            "distance_km": row["distance_from_previous"],
            "timestamp": row["timestamp"]
        })

    return jsonify({
        "success": True,
        "active": bool(session["active"]),
        "total_distance_km": total_distance,
        "history": data
    })


# =========================================================
# SESSION INFO
# =========================================================

@app.route("/api/monitor/<monitor_token>/info")
def session_info(monitor_token):

    session = get_session_by_monitor_token(monitor_token)

    if not session:
        return jsonify({
            "success": False,
            "message": "Invalid token."
        }), 404

    if session_expired(session):
        return jsonify({
            "success": False,
            "message": "Session expired."
        }), 410

    return jsonify({
        "success": True,
        "active": bool(session["active"]),
        "created_at": session["created_at"],
        "expires_at": session["expires_at"]
    })


# =========================================================
# CSV EXPORT
# =========================================================

@app.route("/api/monitor/<monitor_token>/export.csv")
def export_csv(monitor_token):

    session = get_session_by_monitor_token(monitor_token)

    if not session:
        return "Invalid monitoring token.", 404

    conn = get_db()

    locations = conn.execute(
        """
        SELECT
            latitude,
            longitude,
            accuracy,
            distance_from_previous,
            timestamp
        FROM locations
        WHERE session_id = ?
        ORDER BY id ASC
        """,
        (session["id"],)
    ).fetchall()

    conn.close()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Timestamp",
        "Latitude",
        "Longitude",
        "Accuracy (m)",
        "Distance From Previous (km)"
    ])

    for row in locations:

        writer.writerow([
            row["timestamp"],
            row["latitude"],
            row["longitude"],
            row["accuracy"],
            row["distance_from_previous"]
        ])

    filename = "cybertrack-location-history.csv"

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


# =========================================================
# DELETE HISTORY
# =========================================================

@app.route("/api/monitor/<monitor_token>/history", methods=["DELETE"])
def delete_history(monitor_token):

    session = get_session_by_monitor_token(monitor_token)

    if not session:
        return jsonify({
            "success": False,
            "message": "Invalid monitoring token."
        }), 404

    conn = get_db()

    conn.execute(
        """
        DELETE FROM locations
        WHERE session_id = ?
        """,
        (session["id"],)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "History deleted."
    })


# =========================================================
# HEALTH
# =========================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "online",
        "service": "CyberTrack",
        "time": iso_now()
    })


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    init_db()

    print("")
    print("==========================================")
    print("           CYBERTRACK V2")
    print("==========================================")
    print("Local URL:")
    print("http://127.0.0.1:5000")
    print("")
    print("Location is shared only after")
    print("explicit browser permission.")
    print("==========================================")
    print("")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )