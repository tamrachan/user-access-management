#MANAGER FUNCTIONS
def GetUserProjectCodes(email):
	#Connect to MySQL
	db = mysql.connector.connect(
		host = "localhost",
		user = "root",
		passwd = pd, #Assigned the password to this variable
		database = "CartesianAccessDB"
		)
	#Create the database cursor
	c = db.cursor()
	#Get user ID of employee
	c.execute("""
			SELECT userID
			FROM UserData
			WHERE email = (%s)
			""", (email,))
	userID = c.fetchall()
	userID = str(userID).replace('(','').replace(')','').replace('[','').replace(']','').replace(',','')
	#Get projects of the employee as a list
	c.execute("""
			SELECT projectCode
			FROM ProjectData
			JOIN ProjectDetails
			ON ProjectData.projectID = ProjectDetails.projectID
			WHERE userID = %s 
			""", (userID,));
	projects = c.fetchall()
	project_list = []
	#Remove the formatting of the fetched data and add it to a new list
	for name in projects:
		project_name=str(name).replace('(','').replace(')','').replace('[','').replace(']','').replace(',','').strip(" ' ")
		project_list.append(project_name)
	#CLoses the database
	db.close()

	return(project_list)
def Project_page(event):
	#This function is used to display specific project pages
	#Assign project_code to the combobox option selected
	project_code = project_option_box.get()
	global edit_permissions_button

	#If this page is called after the homepage, remove the homepage Treeview
	try:
		overview_tree.destroy()
	except:
		pass
	#If this page is called after viewing/editing permissions, remove the tree/labels/comboboxes
	try:
		permission_tree.destroy()
		employee_label.destroy()
		yn_option_box.destroy()
		reason_input.destroy()
		approver_input.destroy()
		approval_status_option_box.destroy()
		expiry_option_box.destroy()
		submit_button.destroy()
	except:
		pass
	#Remove the edit permissions button if it is shown on the screen 
	try:
		edit_permissions_button.destroy()
	except:
		pass

	#Connect to MySQL
	db = mysql.connector.connect(
		host = "localhost",
		user = "root",
		passwd = pd, #Assigned the password to this variable
		database = "CartesianAccessDB"
		)
	c = db.cursor() #Create the database cursor

	#Fetch the project ID given the project code
	c.execute("SELECT projectID FROM ProjectData WHERE projectCode = %s",(project_code,))
	db_project_id = c.fetchall()
	db_project_id = str(db_project_id).replace('(','').replace(')','').replace('[','').replace(']','').replace(',','')

	#Display the project options combobox
	ProjectOptionComboBox()


	if project_code != "Overview":
		#If the project option is not Overview, change labels based on the project selected and remove the overview tree
		project_option_box.set(project_code)
		overview_tree.destroy()
		manager_welcome_label.configure(text=project_code)
		#Display the Treeview of the employee data
		DisplayPermissions(db_project_id)
	else:
		#If "Overview" is selected, adjust the title label and display the overview tree
		project_option_box.set("Overview")
		manager_welcome_label.configure(text="Manager homepage")
		OverviewTreeview(manager_home_frame)
def ProjectOptionComboBox():
	global edit_permissions_button
	#If this page is called after the homepage, remove the homepage Treeview
	try:
		overview_tree.destroy()
	except:
		pass
	#If this page is called after viewing/editing permissions, remove the tree/labels/comboboxes
	try:
		permission_tree.destroy()
		employee_label.destroy()
		yn_option_box.destroy()
		reason_input.destroy()
		approver_input.destroy()
		approval_status_option_box.destroy()
		expiry_option_box.destroy()
		submit_button.destroy()
	except:
		pass
	#Remove the edit permissions button if it is shown on the screen 
	try:
		edit_permissions_button.destroy()
	except:
		pass

	global project_option_box
	project_option_box=customtkinter.CTkComboBox(manager_home_frame, state="readonly", values=m_project_list, 
		width=200, command =Project_page)

	#project_option_box.bind("<<ComboboxSelected>>", Project_page)
	project_option_box.place(relx=.1, rely=.9,anchor= 'w')
	#Allow the user to input the project they would like to go to
	go_to_project_label = customtkinter.CTkLabel(manager_home_frame, text="Go to project: ", font=("Arial",16))
	go_to_project_label.place(relx=.1, rely=.85, anchor= 'w')
def OverviewTreeview(frame):
	#Connect to MySQL
	db = mysql.connector.connect(
		host = "localhost",
		user = "root",
		passwd = pd, #Assigned the password to this variable
		database = "CartesianAccessDB"
		)
	c = db.cursor() #Create the database cursor

	c.execute("""SELECT projectCode, projectName, name 
				FROM ProjectDetails 
				JOIN UserData 
				ON UserData.userID = ProjectDetails.userID 
				JOIN ProjectData On ProjectData.projectID = ProjectDetails.projectID 
				WHERE approver = True""")
	values = c.fetchall() 
	#Add a Treeview widget to display the access rights
	global overview_tree
	overview_tree = ttk.Treeview(frame, column=("c1", "c2", "c3"), show='headings', height=14)
	overview_tree.column("# 1", anchor=customtkinter.CENTER, width=500)
	overview_tree.heading("# 1", text="Project code")
	overview_tree.column("# 2", anchor=customtkinter.CENTER, width=300)
	overview_tree.heading("# 2", text="Project name")
	overview_tree.column("# 3", anchor=customtkinter.CENTER, width=400)
	overview_tree.heading("# 3", text="Approver")
	overview_tree.place(relx=.5, rely=.4,anchor= customtkinter.CENTER)

	#Insert values into the treeview
	num = 0
	for row in values:
		overview_tree.insert('', 'end', text=num, values=(row[0], row[1], row[2]))
		num += 1

	db.close()
#MANAGER - view permissions
def WritePermissionstoDB(employee_name, access, reason, approval_status, expiry, db_project_id, approver_name):
	if employee_name == "" or access == "" or reason == "" or approval_status == "" or expiry == "":
		messagebox.showerror('Invalid entry', 'Please ensure all fields are completed.')
	else:
		#print(employee_name, access, reason, approval_status, expiry)
		#Connect to MySQL
		db = mysql.connector.connect(
			host = "localhost",
			user = "root",
			passwd = pd, #Assigned the password to this variable
			database = "CartesianAccessDB"
			)
		c = db.cursor() #Create the database cursor

		#Fetch nameID for employee name
		c.execute("SELECT nameID FROM CSVUserData WHERE CSVname = %s",(employee_name,))
		name_id = c.fetchall()
		name_id = str(name_id).replace('(','').replace(')','').replace('[','').replace(']','').replace(',','')

		#Update database
		c.execute("""UPDATE CSVPermissions
			SET access = %s, reason = %s, approvalStatus = %s, expiry = %s, approver_name = %s
			WHERE nameID = %s and projectID = %s
			""", (access, reason, approval_status, expiry, approver_name, name_id, db_project_id));
		db.commit()

		#Update treeview function
		permission_tree.destroy()
		employee_label.destroy()
		yn_option_box.destroy()
		reason_input.destroy()
		approver_input.destroy()
		approval_status_option_box.destroy()
		expiry_option_box.destroy()
		submit_button.destroy()
		DisplayPermissions(db_project_id)

		#Close the database
		db.close()
def ShowPermissionComboboxes(employee_name, access, reason, approval_status, expiry, db_project_id, approver):
	#Remove label if already on screen so the updated values does not overlap
	global employee_label
	try:
		employee_label.destroy()
	except:
		pass
	
	#Create label to display the name of the employee selected
	employee_label = customtkinter.CTkLabel(manager_home_frame, text=employee_name, font=("Arial",16))
	employee_label.place(relx=.15, rely=.75, anchor=customtkinter.CENTER)

	#Create an Y/N access combobox
	yn_options = [
		"Y",
		"N"
		]
	global yn_option_box
	yn_option_box = customtkinter.CTkComboBox(manager_home_frame, state="readonly", values=yn_options)
	yn_option_box.place(relx=.3, rely=.75,anchor= customtkinter.CENTER)
	#Set the default option
	if access == "Y":
		yn_option_box.set("Y")
	elif access == "N":
		yn_option_box.set("N")
	
	#Create an entry box for reason
	global reason_input
	reason_input = customtkinter.CTkEntry(manager_home_frame, font=("Arial",15))
	reason_input.place(relx=.44, rely=.75, relwidth=0.12, anchor= customtkinter.CENTER)
	#Add the text into the input box
	if reason != "None":
		reason_input.insert(0,reason)

	#Create an entry box for approver
	global approver_input
	approver_input = customtkinter.CTkEntry(manager_home_frame, font=("Arial",15))
	approver_input.place(relx=.58, rely=.75, relwidth=0.12, anchor= customtkinter.CENTER)
	#Add the text into reason
	if approver != "None":
		approver_input.insert(0,approver)

	#Create an approval status combobox
	approval_status_options = [
		"Please complete",
		"Approved",
		"Remove"
		]
	global approval_status_option_box 
	approval_status_option_box = customtkinter.CTkComboBox(manager_home_frame, state="readonly", values=approval_status_options)
	approval_status_option_box.place(relx=.72, rely=.75,anchor= customtkinter.CENTER)
	#Set the default option
	if approval_status == "Approved":
		approval_status_option_box.set("Approved")
	elif approval_status == "Remove":
		approval_status_option_box.set("Remove")
	else:
		approval_status_option_box.set("Please complete")

	#Create an expiry combobox
	expiry_options = [
		"Ongoing",
		"Expired"
		]
	global expiry_option_box
	expiry_option_box = customtkinter.CTkComboBox(manager_home_frame, state="readonly", values=expiry_options)
	expiry_option_box.place(relx=.85, rely=.75,anchor= customtkinter.CENTER)
	#Set the default option
	if expiry == "Ongoing":
		expiry_option_box.set("Ongoing")
	elif expiry == "Expired":
		expiry_option_box.set("Expired")
	else:
		expiry_option_box.set("Please complete")

	global submit_button
	submit_button = customtkinter.CTkButton(manager_home_frame, text="Submit",height=35, width=30, corner_radius=20, font=("Arial",20), command=lambda: [WritePermissionstoDB(employee_name, yn_option_box.get(), reason_input.get(), approval_status_option_box.get(), expiry_option_box.get(), db_project_id, approver_input.get())])
	submit_button.place(relx=.5, rely=.8,anchor= 'n')
def EditPermissions(db_project_id):
	#Assign selected value to 'selected'
	selected = permission_tree.focus()
	selected_value = permission_tree.item(selected, 'values')
	if selected_value == "":
		#If no value is selected, show an error message
		messagebox.showerror('Invalid selection', 'Please select a record.')
	else:
		#Assign variables to the selected values
		employee_name = selected_value[0]
		access = selected_value[1]
		reason = selected_value[2]
		approver = selected_value[3]
		approval_status = selected_value[4]
		expiry = selected_value[5]
		ShowPermissionComboboxes(employee_name, access, reason, approval_status, expiry, db_project_id, approver)

#This function is used to create a treeview of all the permissions
def DisplayPermissions(db_project_id):
	global permission_tree
	permission_tree = ttk.Treeview(manager_home_frame, column=("Employee", "Permission", "Reason", "Manager/Approver", "Approval Status", "Expiry date"), show='headings', height=15)
	permission_tree.column("# 1", anchor=customtkinter.CENTER, width=300)
	permission_tree.heading("# 1", text="Employee")
	permission_tree.column("# 2", anchor=customtkinter.CENTER, width=200)
	permission_tree.heading("# 2", text="Permission")
	permission_tree.column("# 3", anchor=customtkinter.CENTER, width=500)
	permission_tree.heading("# 3", text="Reason")
	permission_tree.column("# 4", anchor=customtkinter.CENTER, width=300)
	permission_tree.heading("# 4", text="Manager/Approver")
	permission_tree.column("# 5", anchor=customtkinter.CENTER, width=300)
	permission_tree.heading("# 5", text="Approval Status")
	permission_tree.column("# 6", anchor=customtkinter.CENTER, width=200)
	permission_tree.heading("# 6", text="Expiry date")

	#Insert the data in Treeview widget#

	#Connect to MySQL
	db = mysql.connector.connect(
		host = "localhost",
		user = "root",
		passwd = pd, #Assigned the password to this variable
		database = "CartesianAccessDB"
		)
	c = db.cursor() #Create the database cursor

	#Select approver name from the database
	c.execute("""SELECT UserData.name
		FROM ProjectDetails
		JOIN ProjectData
		ON ProjectData.projectID = ProjectDetails.projectID
		JOIN UserData
		ON UserData.userID = ProjectDetails.userID
		WHERE ProjectDetails.projectID = %s
	""", (db_project_id,))
	approver = c.fetchall()
	approver = str(approver).replace('(','').replace(')','').replace('[','').replace(']','').replace(',','').strip(" ' ")

	#Select approver from database
	c.execute("""SELECT approver_name
		FROM CSVPermissions
		JOIN ProjectData
		ON ProjectData.projectID = CSVPermissions.projectID
		WHERE CSVPermissions.projectID = %s""",(db_project_id,))
	approver_list = c.fetchall()

	#Set default approver as the approver name
	first_approver = approver_list[0]
	if str(first_approver) == "(None,)":
		print("Updating database")
		c.execute("""
			UPDATE CSVPermissions 
			JOIN ProjectData
			ON ProjectData.projectID = CSVPermissions.projectID
			SET approver_name = %s 
			WHERE CSVPermissions.projectID = %s""",(approver, db_project_id))
		db.commit()

	#Select approvalStatus and access from database
	c.execute("""SELECT approvalStatus, access, nameID
		FROM CSVPermissions
		JOIN ProjectData
		ON ProjectData.projectID = CSVPermissions.projectID
		WHERE CSVPermissions.projectID = %s""",(db_project_id,))
	status_list = c.fetchall()

	#Set default approval status and permission status as please complete and Y respectively
	for item in status_list:
		name_id = item[2]
		if str(item[0]) == "None":
			c.execute("""
				UPDATE CSVPermissions 
				JOIN ProjectData
				ON ProjectData.projectID = CSVPermissions.projectID
				SET approvalStatus = "Please complete" 
				WHERE CSVPermissions.projectID = %s and nameID = %s""",(db_project_id, name_id))
			db.commit()
		if str(item[1]) == "None":
			permission = item[1]
			c.execute("""
				UPDATE CSVPermissions 
				JOIN ProjectData
				ON ProjectData.projectID = CSVPermissions.projectID
				SET access = "Y"
				WHERE CSVPermissions.projectID = %s and nameID = %s""",(db_project_id, name_id))
			db.commit()

	#Select the rows required for the treeview
	c.execute("""SELECT CSVUserData.CSVname, access, reason, approver_name, approvalStatus, expiry 
		FROM CSVPermissions
		JOIN ProjectData
		ON ProjectData.projectID = CSVPermissions.projectID
		JOIN CSVUserData
		ON CSVUserData.nameID = CSVPermissions.nameID
		WHERE CSVPermissions.projectID = %s""",(db_project_id,))
	permission_list = c.fetchall()
	#Sort the values alphabetically
	permission_list.sort()
	#Assigns the length of the list to this variable
	length_of_list = len(permission_list)

	#If the list length is greater than 15, the user will need to scroll down on the treeview to see all records
	if length_of_list > 15:
		#Displays 
		scroll_down_label.configure(text="Please scroll down to view all records.")
	else:
		scroll_down_label.configure(text="")

	#Colours the incomplete Treeview rows red
	permission_tree.tag_configure('incomplete', background="red")

	num = 0
	for row in permission_list:
		num = num + 1
		if row[4] == "Please complete" or row[2]=="":
			#Changes the colour of the incomplete Treeview row
			permission_tree.insert(parent='', index='end', iid=num, values=(row), tags=('incomplete',))
		else:
			#No colour is set to the Treeview row
			permission_tree.insert(parent='', index='end', iid=num, values=(row))

	#Places the permission tree on the screen
	permission_tree.place(relx=.5, rely=.2, anchor= 'n')

	#Create and display the edit permissions button
	global edit_permissions_button
	edit_permissions_button = customtkinter.CTkButton(manager_home_frame, text="Edit permissions", font=("Arial",16), command=lambda: [EditPermissions(db_project_id)])
	edit_permissions_button.place(relx=.85, rely=.9,anchor= customtkinter.CENTER)

#This function displays the manager homepage
def ManagerHomepage():
	#If the edit permissions button is displayed, remove it
	try:
		edit_permissions_button.destroy()
	except:
		pass

	#Display the titles of the page
	manager_welcome_label.place(relx=.5, rely=.1, anchor=customtkinter.CENTER)
	access_rights_label.place(relx=.7, rely=.25, anchor=customtkinter.CENTER)

	#Get the project codes for the user logged in
	global m_project_list
	m_project_list = GetUserProjectCodes(email)
	m_project_list.insert(0, 'Overview')

	#Display the drop-down menu to select the project page
	ProjectOptionComboBox()
	#Set the manager home page as "Overview"
	project_option_box.set("Overview")
	#Display the overview treeview with the projects and approvers
	OverviewTreeview(manager_home_frame)

	#Pack the manager home frame on the screen
	manager_home_frame.pack(fill="both", expand=1)