import sqlite3
import csv

def seed_badge_data(csv_file_path, db_file_path='LJAttendance.db'):
    """
    Seeds the badge_ids table with data for the badge_id and fullname columns only.
    
    The CSV file is expected to have at least the following headers:
      - badge_id
      - fullname
      
    Other columns in the table (department, grant, location) will remain NULL.
    
    :param csv_file_path: Path to the CSV file containing badge data.
    :param db_file_path: Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                badge_id = row['badge_id'].strip()
                print(badge_id)
                fullname = row['fullname'].strip()
                print(badge_id, fullname)
                cursor.execute("""
                INSERT INTO badge_ids (badge_id, fullname)
                VALUES (?, ?)
                ON CONFLICT(badge_id) DO NOTHING
            """, (row['badge_id'], row['fullname']))
    conn.commit()
    conn.close()
            
  

if __name__ == '__main__':
    # Update the CSV file path as needed.
    seed_badge_data('theone.csv')
