import mysql.connector
from config.db_config import DB_CONFIG

def get_user_project_codes(email):
    db = mysql.connector.connect(**DB_CONFIG)
    c = db.cursor()
    c.execute("SELECT projectCode FROM ProjectDetails JOIN UserData ON ProjectDetails.userID = UserData.userID WHERE email = %s", (email,))
    results = [row[0] for row in c.fetchall()]
    db.close()
    return results

def get_project_id_from_code(project_code):
    db = mysql.connector.connect(**DB_CONFIG)
    c = db.cursor()
    c.execute("SELECT projectID FROM ProjectData WHERE projectCode = %s", (project_code,))
    result = c.fetchone()
    db.close()
    return result[0] if result else None

def get_overview_projects():
    db = mysql.connector.connect(**DB_CONFIG)
    c = db.cursor()
    c.execute("""SELECT projectCode, projectName, name 
                FROM ProjectDetails 
                JOIN UserData ON UserData.userID = ProjectDetails.userID 
                JOIN ProjectData On ProjectData.projectID = ProjectDetails.projectID 
                WHERE approver = True""")
    values = c.fetchall()
    db.close()
    return values

def get_approver_name(project_id):
    db = mysql.connector.connect(**DB_CONFIG)
    c = db.cursor()
    c.execute("""SELECT UserData.name
                 FROM ProjectDetails
                 JOIN ProjectData ON ProjectData.projectID = ProjectDetails.projectID
                 JOIN UserData ON UserData.userID = ProjectDetails.userID
                 WHERE ProjectDetails.projectID = %s""", (project_id,))
    result = c.fetchone()
    db.close()
    return result[0] if result else ""

def get_approver_list(project_id):
    db = mysql.connector.connect(**DB_CONFIG)
    c = db.cursor()
    c.execute("""SELECT approver_name
                 FROM CSVPermissions
                 JOIN ProjectData ON ProjectData.projectID = CSVPermissions.projectID
                 WHERE CSVPermissions.projectID = %s""", (project_id,))
    results = c.fetchall()
    db.close()
    return results

def update_missing_approver_names(approver, project_id):
    db = mysql.connector.connect(**DB_CONFIG)
    c = db.cursor()
    c.execute("""UPDATE CSVPermissions 
                 JOIN ProjectData ON ProjectData.projectID = CSVPermissions.projectID
                 SET approver_name = %s 
                 WHERE CSVPermissions.projectID = %s""", (approver, project_id))
    db.commit()
    db.close()

def get_status_list(project_id):
    db = mysql.connector.connect(**DB_CONFIG)
    c = db.cursor()
    c.execute("""SELECT approvalStatus, access, nameID
                 FROM CSVPermissions
                 JOIN ProjectData ON ProjectData.projectID = CSVPermissions.projectID
                 WHERE CSVPermissions.projectID = %s""", (project_id,))
    results = c.fetchall()
    db.close()
    return results

def update_missing_status_and_access(status_list, project_id):
    db = mysql.connector.connect(**DB_CONFIG)
    c = db.cursor()
    for approvalStatus, access, nameID in status_list:
        if approvalStatus is None:
            c.execute("""UPDATE CSVPermissions 
                         JOIN ProjectData ON ProjectData.projectID = CSVPermissions.projectID
                         SET approvalStatus = 'Please complete' 
                         WHERE CSVPermissions.projectID = %s AND nameID = %s""", (project_id, nameID))
        if access is None:
            c.execute("""UPDATE CSVPermissions 
                         JOIN ProjectData ON ProjectData.projectID = CSVPermissions.projectID
                         SET access = 'Y' 
                         WHERE CSVPermissions.projectID = %s AND nameID = %s""", (project_id, nameID))
    db.commit()
    db.close()

def get_permission_list(project_id):
    db = mysql.connector.connect(**DB_CONFIG)
    c = db.cursor()
    c.execute("""SELECT CSVUserData.CSVname, access, reason, approver_name, approvalStatus, expiry 
                 FROM CSVPermissions
                 JOIN ProjectData ON ProjectData.projectID = CSVPermissions.projectID
                 JOIN CSVUserData ON CSVUserData.nameID = CSVPermissions.nameID
                 WHERE CSVPermissions.projectID = %s""", (project_id,))
    result = c.fetchall()
    db.close()
    return result
