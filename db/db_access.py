# db/db_access.py
import mysql.connector
from config.db_config import DB_CONFIG

def get_user_project_codes(email):
    db = mysql.connector.connect(**DB_CONFIG)
    c = db.cursor()
    c.execute("SELECT userID FROM UserData WHERE email = %s", (email,))
    user_id = c.fetchone()
    user_id = user_id[0] if user_id else None

    if not user_id:
        return []

    c.execute("""
        SELECT projectCode
        FROM ProjectData
        JOIN ProjectDetails ON ProjectData.projectID = ProjectDetails.projectID
        WHERE userID = %s
    """, (user_id,))
    results = c.fetchall()
    db.close()
    return [row[0] for row in results]
