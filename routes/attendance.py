from database import get_db_connection;
from flask import Blueprint, request, jsonify
from datetime import datetime  , timezone
import pytz
attendance_bp = Blueprint('attendance', __name__)
LOCAL_TZ = pytz.timezone("America/New_york")  # Example: Central Time (CST/CDT)




@attendance_bp.route('/attendance/checkin', methods=['POST'])
def checkin():
    print("Inside")
    data = request.json
    date  =  datetime.today().strftime("%Y-%m-%d")
    check_in_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")  # Use UTC time
    print("@@@@@@@",data)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance_logs (badge_id, event_id, check_in_time,date) VALUES (?, ?, ?,?)",
                   (data['badge_id'], data['event_id'], check_in_time,date))
    conn.commit()
    badge_id =  data['badge_id']
    cursor.execute("SELECT fullname FROM badge_ids WHERE badge_id = ?", (badge_id,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
    
    print("Here is the User", user[0])

    name =   user[0]
    
    conn.close()
    return jsonify({'message': 'Successfully checked in', 'time': check_in_time,"name":name}), 201


@attendance_bp.route('/attendance/checkout', methods=['POST'])
def checkout():
    data = request.json
    badge_id =  data['badge_id']
    #date = date.today().strftime("%Y-%m-%d")
    check_out_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")  # Use UTC time # Use UTC time
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE attendance_logs SET check_out_time = ? WHERE badge_id = ? AND event_id = ? AND check_out_time IS NULL",
                   (check_out_time, data['badge_id'], data['event_id']))
    conn.commit()
    
    cursor.execute("SELECT fullname FROM badge_ids WHERE badge_id = ?", (badge_id,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
    
    name =  user[0]
    conn.close()
    return jsonify({'message': 'Check-out successful', 'time': check_out_time,"name":name}), 200


@attendance_bp.route('/attendance_logs', methods=['GET'])
def get_attendance_logs():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Join attendance_logs → events → badge_ids to get all fields
    cursor.execute("""
        SELECT
            e.event_name,
            l.badge_id,
            b.fullname,
            l.check_in_time,
            l.check_out_time
        FROM attendance_logs l
        JOIN events e       ON l.event_id = e.event_id
        JOIN badge_ids b    ON l.badge_id = b.badge_id
        ORDER BY l.check_in_time
    """)
    rows = cursor.fetchall()
    conn.close()

    logs = []
    for event_name, badge_id, full_name, check_in, check_out in rows:
        logs.append({
            "event_name":  event_name,
            "badge_id":    badge_id,
            "full_name":   full_name,
            "check_in":    check_in,
            "check_out":   check_out
        })

    return jsonify(logs)

@attendance_bp.route('/attendance_logs_all', methods=['GET'])
def get_logs():
    conn = get_db_connection()
    cursor = conn.cursor()   
    query = """
   SELECT 
    attendance_logs.log_id,
    attendance_logs.badge_id,
    badge_ids.fullname AS fullname,
    badge_ids.department AS department,
    badge_ids.location AS employee_location,
    attendance_logs.event_id,
    events.event_name event_name,
    events.location AS location,
    attendance_logs.check_in_time,
    attendance_logs.check_out_time
FROM attendance_logs
JOIN badge_ids ON attendance_logs.badge_id = badge_ids.badge_id
JOIN events ON attendance_logs.event_id = events.event_id
ORDER BY attendance_logs.check_in_time DESC
    """


    cursor.execute(query)
    logs = cursor.fetchall()
    conn.close()


    formatted_logs = [
           { 
               "full_name":row['fullname'],
               "event_name": row['event_name'],
              "location": row["location"],
             "check_in_time": (row['check_in_time']),
             "check_out_time": (row['check_out_time'])
        
           } for row in logs]


    return jsonify(formatted_logs)

##this function will get the attedance summary by event
@attendance_bp.route('/attendance/summary', methods=['GET'])
def get_attendance_summary():
    conn  = get_db_connection()
    cursor =  conn.cursor()
    data =  request.get_json()
    event_id =  data.get("event_id")
    cursor.execute(
        """
              SELECT
            SUM(CASE WHEN check_in_time IS NOT NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN check_out_time IS NOT NULL THEN 1 ELSE 0 END)
        FROM attendance_logs
        WHERE event_id = ?
        """ , (event_id,)
    )

    rows =   cursor.fetchone()
    cursor.execute("SELECT event_name FROM events WHERE event_id =?",(event_id,))
    event_name = cursor.fetchone()
    event_name = event_name[0]
    conn.close()
    print("@@@@@@" ,  event_id)
    checkins =  rows[0]
    checkouts =  rows[1]
    missing =   checkins -  checkouts


    return jsonify({
         "event_name":event_name,
         "event_id":event_id,
         "checkins": checkins , 
         "checkouts":checkouts, 
         "missing":missing
    })



##Attendance Home Page
@attendance_bp.route('/attendance/checkin', methods=['GET'])
def home():
   return "<h1> Atteandance Page </h1>"