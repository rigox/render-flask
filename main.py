from flask import Flask
from routes.employees import employees_bp
from routes.events import events_bp
from routes.attendance import attendance_bp
from routes.reports  import reports_bp
from flask_cors import CORS
import sqlite3



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins
# Register blueprints
app.register_blueprint(employees_bp)
app.register_blueprint(events_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(attendance_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)