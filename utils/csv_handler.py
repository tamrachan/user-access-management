from config.db_config import DB_CONFIG

#These five functions work together to generate the CSV list in Python
def OrganiseCSVFile(csv):
	#Creates a new list
	organised_csv = []
	#Sorts the list by project alphabetically
	sorted_csv = sorted(csv, key=lambda d: d['project'])

	#Removes the specific projects that my client requested to remove
	for row in sorted_csv:
		if (row.get('project') == "Administrators" or row.get('project') == "all-unix-users" 
			or row.get('project') == "analytics-unix-access" or row.get('project') == "analytics-01-win-admins" 
			or row.get('project') == "analytics-01-win-users" or row.get('project') == "ash-unix-access" 
			or row.get('project') == "common-unix-access" or row.get('project') == "cvs-users" 
			or row.get('project') == "demo-unix-access" or row.get('project') == "Denied RODC Password Replication Group" 
			or row.get('project') == "Domain Admins" or row.get('project') == "dub-unix-access" 
			or row.get('project') == "Enterprise Admins" or row.get('project') == "Group Policy Creator Owners" 
			or row.get('project') == "Guests" or row.get('project') == "mashup-admins" 
			or row.get('project') == "monitoring-users" or row.get('project') == "project-unix-access" 
			or row.get('project') == "Schema Admins" or row.get('project') == "securezone15-unix-access" 
			or row.get('project') == "shared-win-admins" or row.get('project') == "shared-win-users" 
			or row.get('project') == "team-unix-access" or row.get('project') == "unix-admins" 
			or row.get('project') == "upgrd-win-admins" or row.get('project') == "upgrd-win-users" 
			or row.get('project') == "vpn-users" or row.get('project') == "win-upgrade-win-admins" 
			or row.get('project') == "win-upgrade-win-users"):
			row.clear()

	#Removes any empty dictionaries
	sorted_csv = [ele for ele in sorted_csv if ele !={}]

	#Removes duplicate entries in the list of dictionary
	seen = set()
	seen2 = set()
	for row in sorted_csv:
		prefix = row['project']
		if prefix[:3]=="att":
			if prefix == "att-unix-access":
				organised_csv.append(row)
			else:
				t = tuple(row.items())
				if t not in seen:
					seen.add(t)
					organised_csv.append(row)
		elif prefix[:9]=="gnrl-win-":
			t2 = tuple(row.items())
			if t2 not in seen2:
				seen2.add(t2)
				organised_csv.append(row)
		else:
			organised_csv.append(row)

	return(organised_csv)

def DelCSVFile(csv):
	#This function deletes the requested columns/rows in the CSV File 
	for row in csv:
		if row.get('type') == "linux":
			row.clear()
		if row.get('name') == "Alteryx att":
			row.clear()

	#Removes the blank entries
	csv = [ele for ele in csv if ele !={}]

	#Tries to remove the key "type" if it exists 
	for row in csv:
		try:
			row.pop('type')
		except:
			pass
	return csv

def GetCSVFile():
	#This function fetches the latest file name in the database and assigns to the global variable csv_list
	csvDict = []

	#Connects to the database
	db = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )
	#Create a cursor
	c = db.cursor()

	c.execute("SELECT fileName FROM CSVFileUploaded ORDER BY dateChanged DESC;")
	global csvFileName
	csvFileName = c.fetchone()
	
	#Removes additional punctuation to the file name
	csvFileName = str(csvFileName)
	csvFileName = csvFileName[2:]
	csvFileName = csvFileName[:-3]

	#Reads the CSV file and imports it into a list of dictionaries
	with open(csvFileName, 'r') as f:
		for line in csv.reader(f):
			file = (line[1], line[2], line[3])
			headings = ['name','project','type']
			data = zip(headings,file)
			dataDict =dict(data)
			csvDict.append(dataDict)
	
	#Calls these functions to filter the imported data
	deleted_file = DelCSVFile(csvDict)
	csv_list = OrganiseCSVFile(deleted_file)

	return csv_list
    
def GetProjectCSV(csv_list):
	#This function returns only the project names in the CSV file (de-duplicated)
	seen = set()
	project_list = []
	for row in csv_list:
		project_name = row.get('project')
		if project_name not in seen:
			seen.add(project_name)
			project_list.append(project_name)

	#Connects to the database
	db = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )
	#Select the project codes from the database
	c = db.cursor()
	c.execute("SELECT projectcode FROM ProjectData")
	code_list_1 = c.fetchall()
	code_list = []
	for item in code_list_1:
		code_list.append(item[0])

	#Add new project codes to the database
	project_codes_added = [i for i in project_list if i not in code_list]
	if len(project_codes_added) != 0:
		for name in project_codes_added:
			#Adds project to the database
			c.execute("""
				INSERT INTO ProjectData(projectCode) 
				VALUES(%s)
				""",(name,))
			db.commit()
	
	return project_list

def GetUserList():
	#This function returns only the user names in the CSV file (de-duplicated)
	seen = set()
	username_list = []
	for row in csv_file:
		user_name = row.get('name')
		if user_name not in seen:
			seen.add(user_name)
			username_list.append(user_name)

	#Sorts the CSV file alphabetically
	username_list.sort()
	return username_list
