from database import get_db_connection;
from flask import Blueprint, request, jsonify
import datetime

reports_bp = Blueprint('reports', __name__)


@reports_bp.route("/reports/user-history", methods=["GET"])
def get_user_attendance_history():
    data = request.get_json()
    badge_id = data.get("badge_id")

    if not badge_id:
        return jsonify({"error": "Missing badge_id"}), 400

    conn =  get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.event_name, l.check_in_time, l.check_out_time
        FROM attendance_logs l
        JOIN events e ON l.event_id = e.event_id
        WHERE l.badge_id = ?
        ORDER BY l.check_in_time
    """, (badge_id,))
    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "event_name": row[0],
            "check_in": row[1],
            "check_out": row[2]
        })

    return jsonify(history)


## No Show report
from flask import request, jsonify
import sqlite3

@reports_bp.route("/reports/no-shows", methods=["GET"])
def no_show_report():
    data = request.get_json() or {}
    event_id = data.get("event_id")
    if not event_id:
        return jsonify({"error": "Missing event_id"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1) Get all badge_ids
    cursor.execute("SELECT badge_id FROM badge_ids")
    all_badges = {row[0] for row in cursor.fetchall()}
    print('length of badges', len(all_badges))
    # 2) Get all badge_ids who checked in for this event
    cursor.execute("""
        SELECT DISTINCT badge_id
        FROM attendance_logs
        WHERE event_id = ?
          AND check_in_time IS NOT NULL
    """, (event_id,))
    present = {row[0] for row in cursor.fetchall()}
    print('present length', len(present))
    # 3) Compute no-shows
    no_shows = all_badges - present
    no_shows_count  =  len(all_badges)  -  len(present)
    print("No-shows",no_shows_count)
    results = []
    if no_shows:
        # Fetch details for each no-show badge
        placeholders = ",".join("?" for _ in no_shows)

        print("placeholders",placeholders)
        cursor.execute(f"""
            SELECT badge_id, fullname, department, grant, location
            FROM badge_ids
            WHERE badge_id IN ({placeholders})
            ORDER BY fullname
        """, tuple(no_shows))
        for badge_id, full_name, dept, grant, location in cursor.fetchall():
            results.append({
                "badge_id": badge_id,
                "full_name": full_name,
                "department": dept,
                "grant": grant,
                "location": location,
             
            })

    conn.close()
    return jsonify(
         {
              "count":no_shows_count,
              "no_shows": results
         }
    )

#Report attendes shows the people that showed to the report
# In your Flask app

@reports_bp.route("/reports/shows", methods=["GET"])
def event_attendees():
    from flask import request, jsonify

    data     = request.get_json() or {}
    event_id = data.get("event_id")
    if not event_id:
        return jsonify({"error": "Missing event_id"}), 400

    conn   = get_db_connection()
    cursor = conn.cursor()

    # 1) Total distinct attendees
    cursor.execute("""
        SELECT COUNT(DISTINCT badge_id)
        FROM attendance_logs
        WHERE event_id = ?
          AND check_in_time                                                      IS NOT NULL
    """, (event_id,))
    total = cursor.fetchone()[0] or 0

    # 2) Full list of attendees
    cursor.execute("""
        SELECT DISTINCT l.badge_id, b.fullname, b.department, b.grant, b.location
        FROM attendance_logs l
        JOIN badge_ids b ON l.badge_id = b.badge_id
        WHERE l.event_id = ?
          AND l.check_in_time IS NOT NULL
        ORDER BY b.fullname
    """, (event_id,))
    rows = cursor.fetchall()
    conn.close()

    attendees = [
        {
            "badge_id":    r[0],
            "full_name":   r[1],
            "department":  r[2],
            "grant":       r[3],
            "location":    r[4],
        }
        for r in rows
    ]

    return jsonify({
        "total_attended": total,
        "attendees":      attendees
    })



#report to get  the people that attendended

# In your Flask app

@reports_bp.route("/reports/event‐attendees", methods=["GET"])
def event_attendees_shows():
    data     = request.get_json() or {}
    event_id = data.get("event_id")
    if not event_id:
        return jsonify({"error": "Missing event_id"}), 400

    conn   = get_db_connection()
    cursor = conn.cursor()

    # 1) Total distinct attendees
    cursor.execute("""
        SELECT COUNT(DISTINCT badge_id)
        FROM attendance_logs
        WHERE event_id = ?
          AND check_in IS NOT NULL
    """, (event_id,))
    total = cursor.fetchone()[0] or 0

    # 2) Full list of attendees
    cursor.execute("""
        SELECT DISTINCT l.badge_id, b.full_name, b.department, b.grant, b.location
        FROM attendance_logs l
        JOIN badge_ids b ON l.badge_id = b.badge_id
        WHERE l.event_id = ?
          AND l.check_in IS NOT NULL
        ORDER BY b.full_name
    """, (event_id,))
    rows = cursor.fetchall()
    conn.close()

    attendees = [
        {
            "badge_id":    r[0],
            "full_name":   r[1],
            "department":  r[2],
            "grant":       r[3],
            "location":    r[4],
        }
        for r in rows
    ]

    return jsonify({
        "total_attended": total,
        "attendees":      attendees
    })
