from database import get_db_connection;
from flask import Blueprint, request, jsonify

events_bp = Blueprint('events', __name__)

@events_bp.route('/events', methods=['POST'])
def add_event():
    data =  request.get_json()
    print('HERE',data)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (event_name, location ,date ) VALUES (?, ?,?)",
                   (data['event_name'], data['location'], data['date']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Event added successfully'}), 201



##route to  get all event names
@events_bp.route('/events',methods=['GET'])
def get_events():
    conn  =  get_db_connection()
    cursor =  conn.cursor()
    cursor.execute("SELECT event_id , event_name ,  location FROM events")
    
    rows =   cursor.fetchall()

    conn.close()
    events=[]
    for row in rows:
      events.append({
         "event_id": row[0],
         "event_name": row[1],
            "location": row[2]
        })

    return jsonify(events)
    
    




## this route will allows us to get logs by the event ID
@events_bp.route("/events/logs" , methods=['GET'])
def get_logs():
    event_id =  request.json
    event_id =  event_id['event_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    if event_id:
        cursor.execute("""
            SELECT e.event_name, b.badge_id, b.fullname, l.check_in_time, l.check_out_time
            FROM attendance_logs l
            JOIN badge_ids b ON l.badge_id = b.badge_id
            JOIN events e ON l.event_id = e.event_id
            WHERE e.event_id = ?
        """, (event_id,))
    else:
        cursor.execute("""
            SELECT e.event_name, b.badge_id, b.fullname,  l.check_in_time, l.check_out_time
            FROM attendance_logs l
            JOIN badge_ids b ON l.badge_id = b.badge_id
            JOIN events e ON l.event_id = e.event_id
        """)

    logs = cursor.fetchall()
    conn.close()

    return jsonify([
        {
            "event_name": row[0],
            "badge_id": row[1],
            "fullname": row[2],
            "check_in": row[3],
            "check_out": row[4]
        } for row in logs
    ])



## this route will allows us to get logs by the event ID and filter by date 
@events_bp.route("/events/logs" , methods=['GET'])
def get_logs_bydate():
    data =  request.get_json()
    event_id =  data.get('event_id')
    conn = get_db_connection()
    data_filter = data.get("date")
    cursor = conn.cursor()

    if event_id & data_filter:
        cursor.execute("""
            SELECT e.event_name, b.badge_id, b.fullname, l.check_in_time, l.check_out_time
            FROM attendance_logs l
            JOIN badge_ids b ON l.badge_id = b.badge_id
            JOIN events e ON l.event_id = e.event_id
            WHERE e.event_id  AND l.date= ?
        """, (event_id,data_filter)) 
    else:
        cursor.execute("""
            SELECT e.event_name, b.badge_id, b.fullname,  l.check_in_time, l.check_out_time
            FROM attendance_logs l
            JOIN badge_ids b ON l.badge_id = b.badge_id
            JOIN events e ON l.event_id = e.event_id
        """)

    logs = cursor.fetchall()
    conn.close()

    return jsonify([
        {
            "event_name": row[0],
            "badge_id": row[1],
            "fullname": row[2],
            "check_in": row[3],
            "check_out": row[4]
        } for row in logs
    ])
