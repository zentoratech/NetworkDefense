from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from functools import wraps
from datetime import datetime
import sqlite3
import os


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

# Vercel / WSGI compatibility
application = app

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "network-defense-secure-key"
)


# =========================================================
# DATABASE
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "network_defense.db")


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


# =========================================================
# DEMO LOGIN
# =========================================================

DEMO_USER = {
    "username": "admin",
    "password": "admin123"
}


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_database():

    db = get_db()

    # =====================================================
    # THREATS
    # =====================================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS threats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            threat_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            vector TEXT NOT NULL,
            risk TEXT NOT NULL,
            status TEXT NOT NULL,
            detected_at TEXT NOT NULL
        )
    """)

    # =====================================================
    # INCIDENTS
    # =====================================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            priority TEXT NOT NULL,
            owner TEXT NOT NULL,
            state TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # =====================================================
    # SECURITY EVENTS
    # =====================================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            message TEXT NOT NULL,
            endpoint TEXT,
            severity TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # =====================================================
    # SETTINGS
    # =====================================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_name TEXT UNIQUE NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1
        )
    """)

    # =====================================================
    # SAMPLE THREATS
    # =====================================================

    threat_count = db.execute(
        "SELECT COUNT(*) FROM threats"
    ).fetchone()[0]

    if threat_count == 0:

        sample_threats = [

            (
                "THR-20481",
                "Suspicious Connection",
                "ND-042",
                "Outbound",
                "CRITICAL",
                "INVESTIGATING",
                "2026-09-09 00:41:18"
            ),

            (
                "THR-20477",
                "Brute Force Pattern",
                "GW-001",
                "Authentication",
                "HIGH",
                "BLOCKED",
                "2026-09-09 00:38:04"
            ),

            (
                "THR-20472",
                "DNS Anomaly",
                "ND-087",
                "DNS",
                "MEDIUM",
                "MONITORING",
                "2026-09-09 00:31:51"
            ),

            (
                "THR-20468",
                "Port Scan Activity",
                "ND-019",
                "Network",
                "HIGH",
                "BLOCKED",
                "2026-09-09 00:27:33"
            ),

            (
                "THR-20461",
                "Unusual Data Transfer",
                "ND-103",
                "Outbound",
                "MEDIUM",
                "MONITORING",
                "2026-09-09 00:21:12"
            )

        ]

        db.executemany("""
            INSERT INTO threats
            (
                threat_id,
                name,
                endpoint,
                vector,
                risk,
                status,
                detected_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, sample_threats)

    # =====================================================
    # SAMPLE INCIDENTS
    # =====================================================

    incident_count = db.execute(
        "SELECT COUNT(*) FROM incidents"
    ).fetchone()[0]

    if incident_count == 0:

        sample_incidents = [

            (
                "INC-1042",
                "Suspicious outbound traffic detected",
                "Endpoint ND-042",
                "CRITICAL",
                "SOC TEAM",
                "INVESTIGATING",
                "2026-09-09 00:41:18"
            ),

            (
                "INC-1039",
                "Authentication attack pattern",
                "Gateway GW-001",
                "HIGH",
                "SOC TEAM",
                "CONTAINED",
                "2026-09-09 00:38:04"
            ),

            (
                "INC-1036",
                "Unexpected DNS activity",
                "Endpoint ND-087",
                "MEDIUM",
                "ANALYST 04",
                "MONITORING",
                "2026-09-09 00:31:51"
            ),

            (
                "INC-1032",
                "Port scanning activity",
                "Network segment C",
                "HIGH",
                "SOC TEAM",
                "RESOLVED",
                "2026-09-09 00:27:33"
            )

        ]

        db.executemany("""
            INSERT INTO incidents
            (
                incident_id,
                title,
                endpoint,
                priority,
                owner,
                state,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, sample_incidents)

    # =====================================================
    # DEFAULT SETTINGS
    # =====================================================

    default_settings = [

        ("real_time_detection", 1),
        ("automatic_blocking", 1),
        ("threat_intelligence", 1),
        ("security_notifications", 1)

    ]

    for setting_name, enabled in default_settings:

        db.execute("""
            INSERT OR IGNORE INTO settings
            (
                setting_name,
                enabled
            )
            VALUES (?, ?)
        """, (
            setting_name,
            enabled
        ))

    db.commit()
    db.close()


# =========================================================
# INITIALIZE DATABASE
# =========================================================

init_database()


# =========================================================
# LOGIN PROTECTION
# =========================================================

def login_required(view):

    @wraps(view)
    def wrapped_view(*args, **kwargs):

        if "user" not in session:

            return redirect(
                url_for("login")
            )

        return view(*args, **kwargs)

    return wrapped_view


# =========================================================
# GLOBAL TEMPLATE VARIABLES
# =========================================================

@app.context_processor
def inject_globals():

    return {
        "current_year": datetime.now().year,
        "username": session.get("user")
    }


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if (
            username == DEMO_USER["username"]
            and
            password == DEMO_USER["password"]
        ):

            session["user"] = username

            return redirect(
                url_for("dashboard")
            )

        error = (
            "Invalid credentials. "
            "Please verify your username and password."
        )

    return render_template(
        "login.html",
        error=error
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("index")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    db = get_db()

    active_threats = db.execute("""
        SELECT COUNT(*)
        FROM threats
        WHERE status != 'RESOLVED'
    """).fetchone()[0]

    critical = db.execute("""
        SELECT COUNT(*)
        FROM threats
        WHERE risk = 'CRITICAL'
        AND status != 'RESOLVED'
    """).fetchone()[0]

    blocked = db.execute("""
        SELECT COUNT(*)
        FROM threats
        WHERE status = 'BLOCKED'
    """).fetchone()[0]

    incidents = db.execute("""
        SELECT COUNT(*)
        FROM incidents
        WHERE state != 'RESOLVED'
    """).fetchone()[0]

    recent_events = db.execute("""
        SELECT *
        FROM security_events
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()

    db.close()

    return render_template(
        "dashboard.html",
        active_threats=active_threats,
        critical=critical,
        blocked=blocked,
        incidents=incidents,
        devices=128,
        network_health=97,
        recent_events=recent_events
    )


# =========================================================
# THREAT INTELLIGENCE
# =========================================================

@app.route("/threats")
@login_required
def threats():

    db = get_db()

    threats_data = db.execute("""
        SELECT *
        FROM threats
        ORDER BY id DESC
    """).fetchall()

    critical = db.execute("""
        SELECT COUNT(*)
        FROM threats
        WHERE risk = 'CRITICAL'
    """).fetchone()[0]

    high = db.execute("""
        SELECT COUNT(*)
        FROM threats
        WHERE risk = 'HIGH'
    """).fetchone()[0]

    medium = db.execute("""
        SELECT COUNT(*)
        FROM threats
        WHERE risk = 'MEDIUM'
    """).fetchone()[0]

    blocked_today = db.execute("""
        SELECT COUNT(*)
        FROM threats
        WHERE status = 'BLOCKED'
    """).fetchone()[0]

    db.close()

    return render_template(
        "threats.html",
        threats=threats_data,
        critical=critical,
        high=high,
        medium=medium,
        blocked_today=blocked_today
    )


# =========================================================
# NETWORK MONITOR
# =========================================================

@app.route("/network")
@login_required
def network():

    return render_template(
        "network.html"
    )


# =========================================================
# INCIDENTS
# =========================================================

@app.route("/incidents")
@login_required
def incidents():

    db = get_db()

    incidents_data = db.execute("""
        SELECT *
        FROM incidents
        ORDER BY id DESC
    """).fetchall()

    db.close()

    return render_template(
        "incidents.html",
        incidents=incidents_data
    )


# =========================================================
# SETTINGS
# =========================================================

@app.route("/settings")
@login_required
def settings():

    db = get_db()

    settings_data = db.execute("""
        SELECT *
        FROM settings
        ORDER BY id
    """).fetchall()

    db.close()

    return render_template(
        "settings.html",
        settings=settings_data
    )


# =========================================================
# API - DASHBOARD STATS
# =========================================================

@app.route("/api/stats")
@login_required
def stats():

    db = get_db()

    active_threats = db.execute("""
        SELECT COUNT(*)
        FROM threats
        WHERE status != 'RESOLVED'
    """).fetchone()[0]

    critical = db.execute("""
        SELECT COUNT(*)
        FROM threats
        WHERE risk = 'CRITICAL'
        AND status != 'RESOLVED'
    """).fetchone()[0]

    blocked = db.execute("""
        SELECT COUNT(*)
        FROM threats
        WHERE status = 'BLOCKED'
    """).fetchone()[0]

    incidents = db.execute("""
        SELECT COUNT(*)
        FROM incidents
        WHERE state != 'RESOLVED'
    """).fetchone()[0]

    db.close()

    return jsonify({

        "threats": active_threats,
        "critical": critical,
        "blocked": blocked,
        "devices": 128,
        "network": 97,
        "incidents": incidents

    })


# =========================================================
# API - CREATE SECURITY EVENT
# =========================================================

@app.route("/api/events", methods=["POST"])
@login_required
def create_event():

    data = request.get_json(
        silent=True
    ) or {}

    event_type = data.get(
        "event_type",
        ""
    ).strip()

    message = data.get(
        "message",
        ""
    ).strip()

    endpoint = data.get(
        "endpoint",
        ""
    ).strip()

    severity = data.get(
        "severity",
        "LOW"
    ).upper()

    allowed_severity = [
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL"
    ]

    if not event_type or not message:

        return jsonify({

            "success": False,

            "error": (
                "event_type and message are required"
            )

        }), 400

    if severity not in allowed_severity:

        severity = "LOW"

    db = get_db()

    db.execute("""
        INSERT INTO security_events
        (
            event_type,
            message,
            endpoint,
            severity,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (

        event_type,
        message,
        endpoint,
        severity,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    ))

    db.commit()
    db.close()

    return jsonify({

        "success": True,

        "message": "Security event recorded"

    }), 201


# =========================================================
# API - UPDATE THREAT STATUS
# =========================================================

@app.route(
    "/api/threats/<int:threat_id>",
    methods=["PATCH"]
)
@login_required
def update_threat(threat_id):

    data = request.get_json(
        silent=True
    ) or {}

    status = data.get(
        "status",
        ""
    ).upper()

    allowed_statuses = [

        "INVESTIGATING",
        "MONITORING",
        "BLOCKED",
        "RESOLVED"

    ]

    if status not in allowed_statuses:

        return jsonify({

            "success": False,

            "error": "Invalid threat status"

        }), 400

    db = get_db()

    cursor = db.execute("""
        UPDATE threats
        SET status = ?
        WHERE id = ?
    """, (
        status,
        threat_id
    ))

    db.commit()

    updated = cursor.rowcount

    db.close()

    if updated == 0:

        return jsonify({

            "success": False,

            "error": "Threat not found"

        }), 404

    return jsonify({

        "success": True,

        "message": "Threat status updated"

    })


# =========================================================
# API - CREATE INCIDENT
# =========================================================

@app.route(
    "/api/incidents",
    methods=["POST"]
)
@login_required
def create_incident():

    data = request.get_json(
        silent=True
    ) or {}

    title = data.get(
        "title",
        ""
    ).strip()

    endpoint = data.get(
        "endpoint",
        ""
    ).strip()

    priority = data.get(
        "priority",
        "MEDIUM"
    ).upper()

    owner = data.get(
        "owner",
        "SOC TEAM"
    ).strip()

    if not title:

        return jsonify({

            "success": False,

            "error": "Incident title is required"

        }), 400

    allowed_priority = [

        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL"

    ]

    if priority not in allowed_priority:

        priority = "MEDIUM"

    db = get_db()

    last_incident = db.execute("""
        SELECT id
        FROM incidents
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    if last_incident:

        next_number = (
            1001 + last_incident["id"]
        )

    else:

        next_number = 1001

    incident_id = f"INC-{next_number}"

    db.execute("""
        INSERT INTO incidents
        (
            incident_id,
            title,
            endpoint,
            priority,
            owner,
            state,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (

        incident_id,
        title,
        endpoint or "Unknown endpoint",
        priority,
        owner or "SOC TEAM",
        "INVESTIGATING",
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    ))

    db.commit()
    db.close()

    return jsonify({

        "success": True,

        "incident_id": incident_id

    }), 201


# =========================================================
# LOCAL DEVELOPMENT
# =========================================================

if __name__ == "__main__":

    print("")
    print("==============================================")
    print("       NETWORK DEFENSE SECURITY CORE")
    print("==============================================")
    print("Database:", DATABASE)
    print("Console:  http://127.0.0.1:5000")
    print("==============================================")
    print("")

    app.run(
        debug=True
    )