from database import get_db_connection;
from flask import Blueprint, request, jsonify
import datetime

employees_bp = Blueprint('employees', __name__)


@employees_bp.route('/employeesttt', methods=['POST'])
def add_employee():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO badge_ids (badge_id, first_name, last_name, department, grant, location) VALUES (?, ?, ?, ?, ?, ?)",
                   (data['badge_id'], data['first_name'], data['last_name'], data['department'], data['grant'], data['location']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Employee added successfully'}), 201


@employees_bp.route('/employees/<badge_id>',methods=['GET'])
def get_employee_bybadge(badge_id):
    print('this is the badgeID ' , badge_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM badge_ids WHERE badge_id = ?",(badge_id,))
    employee =  cursor.fetchone()
    print(employee)
    conn.close()
    if employee:
         return  jsonify(dict(employee))
    else:
        return jsonify({'message':'Employee not found'}) , 404
    

@employees_bp.route('/employees',methods=['GET'])
def get_employee():
    ##data  =  request.json
   ## badge_id =  data['badge_id']
    print('this is the badgeID ')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM badge_ids ")
    rows  =  cursor.fetchall()
    conn.close()
    employees = []
    if rows :
         for row in rows:
             employees.append({
                   "badge_id":row[0],
                   "fullname": row[1],
                   "department": row[2],
                   "grant": row[3],
                   "location": row[4]
             })
    return jsonify(employees)
   

            
             
    

##this function will delete the employee
@employees_bp.route("/employees/<badge_id>", methods=["DELETE"])
def delete_employee(badge_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Optional: check if badge exists before deleting
    cursor.execute("SELECT * FROM badge_ids WHERE badge_id = ?", (badge_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    # Delete the badge record
    cursor.execute("DELETE FROM badge_ids WHERE badge_id = ?", (badge_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": f"User with badge ID {badge_id} deleted successfully."}), 200

# this routes edits the user
@employees_bp.route("/employees/<badge_id>", methods=["PUT"])
def update_employee(badge_id):
    data = request.get_json()

    full_name = data.get("fullname")
    department = data.get("department")
    grant = data.get("grant")
    location = data.get("location")

    if not all([full_name, department, grant, location]):
        return jsonify({"error": "Missing one or more fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the badge ID exists
    cursor.execute("SELECT * FROM badge_ids WHERE badge_id = ?", (badge_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    # Update the record
    cursor.execute("""
        UPDATE badge_ids
        SET fullname = ?, department = ?, grant = ?, location = ?
        WHERE badge_id = ?
    """, (full_name, department, grant, location, badge_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "User updated successfully."}), 200


# this route add a new user
@employees_bp.route("/employees",methods=["POST"])
def add_employess():
    data = request.get_json()
    badge_id   = data.get("badge_id")
    if not badge_id:
        return jsonify({"error": "badge_id is required"}), 400

    # Use empty string as default for any missing fields
    full_name  = data.get("full_name", "")
    department = data.get("department", "")
    grant      = data.get("grant", "")
    location   = data.get("location", "")

    conn = get_db_connection()
    cursor = conn.cursor()

    # (Optional) prevent exact duplicate badge_id entries
    cursor.execute("SELECT 1 FROM badge_ids WHERE badge_id = ?", (badge_id,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Employee with this badge ID already exists"}), 409

    cursor.execute("""
        INSERT INTO badge_ids (badge_id, fullname, department, grant, location)
        VALUES (?, ?, ?, ?, ?)
    """, (badge_id, full_name, department, grant, location))
    conn.commit()
    conn.close()

    return jsonify({"message": "Employee added successfully."}), 201

