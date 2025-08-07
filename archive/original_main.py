#Import the modules used in the system
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from time import strftime
from datetime import date
import customtkinter
import mysql.connector
import csv
import string
import random
import os
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import secrets

#Imports the text file containing the MySQL password
file = open("password.txt", "r")
pd = file.read()
file.close()

#Set the style of the user interface
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

#Create the TKinter GUI
app = customtkinter.CTk()
app.title("User Access Management System")
app.geometry("600x600")
app.iconbitmap('C:/Users/tamra/OneDrive/Documents/Python projects/Cartesian.ico')
app._state_before_windows_set_titlebar_color = 'zoomed'

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
	host = "localhost",
	user = "root",
	passwd = pd,
	database = "CartesianAccessDB"
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
	host = "localhost",
	user = "root",
	passwd = pd,
	database = "CartesianAccessDB"
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

#ADMIN FUNCTIONS
#Upload files - These functions work together to compare the csv imported to the csv previously in use
def SaveChangestoCSV(added_list,deleted_list):
	#For the values added, the dictionary key is adjusted to "Added"
	for row in added_list:
		row['added/deleted'] = str("Added")
		#Set the date to today's date
		row['date'] = str(date.today())
	#For the values deleted, the dictionary key is adjusted to "Deleted"
	for row in deleted_list:
		row['added/deleted'] = "Deleted"
		#Set the date to today's date
		row['date'] = str(date.today())
	
	#Open the Log csv and append the additional data
	with open('ChangesToAccess.csv', 'a') as csvfile:
	    csvwriter = csv.DictWriter(csvfile, fieldnames = ["added/deleted", "date", "name", "project"], lineterminator = '\n')
	    csvwriter.writerows(added_list)
	    csvwriter.writerows(deleted_list)
def CompareCSV(old_csv, new_csv):
	#This compares the new csv with the old csv
	csv_new_values_added = [i for i in new_csv if i not in old_csv]
	csv_values_deleted = [j for j in old_csv if j not in new_csv]
	#Saves these additional values to the CSV file log
	SaveChangestoCSV(csv_new_values_added, csv_values_deleted)
def UploadCSVFile(event=None):
	#Makes sure these variables are updated in the main code too
	global csv_file
	global project_csv
	global no_of_projects

	#This function allows the user to select a CSV file from their computer to upload
	filename = filedialog.askopenfilename(title="Select CSV File:", filetypes=(("CSV Files","*.csv"),))
	filename = os.path.basename(filename) #Removes the path from the filename
	print('Selected:', filename)

	#Connects to this database and gets the name of the last file added
	db = mysql.connector.connect(
	host = "localhost",
	user = "root",
	passwd = pd,
	database = "CartesianAccessDB"
	)
	mycursor = db.cursor()

	#Adds the file name selected into the CSVFileNAmes table
	mycursor.execute("INSERT INTO CSVFileUploaded (fileName) VALUES (%s)", (filename,))
	#Deletes blank entries
	mycursor.execute("DELETE FROM CSVFileUploaded WHERE fileName = '';")
	#Commits the changes to the database
	db.commit()

	if filename == '':
		#When no filename is selected and the 'cancel' button is pressed, print this message in the terminal
		print("No file selected")
	else:
		#Keep the old csv file temporarily to use in comparison
		temp_csv = csv_file
		#Update the filtered csv file variables so the treeviews update
		csv_file = GetCSVFile()
		project_csv = GetProjectCSV(csv_file)
		no_of_projects = len(project_csv)

		#Calls the function to compare the old and new csv files
		CompareCSV(temp_csv, csv_file)

#These functions work together to fulfil the "Edit CSV" button features
#This function removes the selected record from the treeview
def Remove_Selected_Treeview(csv):
	global csv_file
	global csvFileName

	#This displays a messagebox to confirm to remove the record
	response = messagebox.askyesnocancel("Confirm", "Are you sure you want to remove this item?")
	if response is None:
		#User clicked "Cancel" or "No"
		return
	elif response:
		if (csv_tree.focus() == ""):
			#If nothing is selected, this messagebox pops up
			messagebox.showerror('Invalid input', 'No record selected')
		else:
			try:
				#If a name is selected, this removes the name from the CSV file
				selected = csv_tree.focus()
				values = csv_tree.item(selected, 'values')
				project_name = csv_tree.parent(selected)
				name_to_delete = values[1]
				print("Name selected is: ", name_to_delete)
				print("Project selected is: ", project_name)
				for row in csv:
					if row.get('name') == name_to_delete:
						row.clear()
			except:
				#If a project is selected, this removes the whole project and the associated names from the CSV file
				selected = csv_tree.focus()
				project_name = selected
				print("NO NAME SELECTED:", selected)
				for row in csv:
					if row.get("project") == project_name:
						row.clear()
			#This clears blank entries from the csv file
			csv = [ele for ele in csv if ele !={}]
			#Updates the global variable
			csv_file = csv

			#Delete from treeviewer
			x = csv_tree.selection()
			csv_tree.delete(x)

			#Attempts to write the list of dictionaries to the csv file to make it permanent
			try:
				fileHandle = open(csvFileName, 'w')
				for row in csv_file:
					fileHandle.write('None,{name},{project},None'.format(**row))
					fileHandle.write('\n')
				fileHandle.close()
			except OSError:
				#If an error is found, display this error message
				print("Cannot write to file!")
				messagebox.showerror('File error', 'Data could not be written to file')
#This function generates a treeview of the CSV list
def GenerateTreeview(csv, frame):
	#Create Treeview scrollbar
	tree_scroll = Scrollbar(frame)
	tree_scroll.pack(side=RIGHT, fill=Y)
	#Create the Treeview to display the csv file data
	global csv_tree
	csv_tree = ttk.Treeview(frame, height=15, yscrollcommand=tree_scroll.set)
	#Configure the scrollbar
	tree_scroll.config(command=csv_tree.yview)
	
	#Define the columns
	csv_tree['columns'] = ("ID", "Name")
	#Format the columns
	csv_tree.column("#0", width=500, minwidth=25)
	csv_tree.column("ID", anchor='w', width=100)
	csv_tree.column("Name", anchor='w', width=500)
	#Create the headings
	csv_tree.heading("#0", text="Project", anchor='w')
	csv_tree.heading("ID", text="ID", anchor='w')
	csv_tree.heading("Name", text="Name", anchor='w')

	#De-duplicates the names in the CSV file to display them
	num = 0
	project_count=0
	seen = set()
	project_list = []

	#Display each name and project in the Treeview
	for row in csv:
		name = row['name']
		project_name = row.get('project')
		if not csv_tree.exists(project_name):
			seen.add(project_name)
			project_list.append(project_name)

			#Inserts project names as parent nodes
			csv_tree.insert(parent='', index='end', iid=project_name, text=project_name)
			project_count+=1
		#Inserts user names as child nodes
		csv_tree.insert(parent=project_name, index='end', iid=num, values=(num,name))
		num += 1

	#Place the CSV Treeview on the screen
	csv_tree.place(relx=.5, rely=.4, anchor=CENTER)
#This function is the menu for users to edit the CSV file
def EditCSVFile():
	#Create a frame for this page
	edit_csv_frame = customtkinter.CTkFrame(app, width=2000, height=1000)

	#Create and display the title label
	project_label = customtkinter.CTkLabel(edit_csv_frame, text="Edit CSV File", font=("Arial",30))
	project_label.place(relx=.5, rely=.1,anchor= customtkinter.CENTER)
	#Fetch the csv file and generate the Treeview
	csv = GetCSVFile()
	GenerateTreeview(csv, edit_csv_frame)

	#Create and display a button to remove the record
	remove_button = customtkinter.CTkButton(edit_csv_frame, text="Remove record", height=35, width=30, corner_radius=20, font=("Arial",16), command=lambda: [Remove_Selected_Treeview(csv)])
	remove_button.place(relx=.5, rely=.7,anchor= customtkinter.CENTER)

	#Create and display a button to go back to the homepage
	back_button = customtkinter.CTkButton(edit_csv_frame, text="Back to Homepage", fg_color="transparent", border_width=2, border_color="#315184", height=35, width=30, corner_radius=20, font=("Arial",16), command=lambda: [edit_csv_frame.destroy(), AdminHomepage()])
	back_button.place(relx=.5, rely=.9,anchor= customtkinter.CENTER)

	#Display the frame on the screen
	edit_csv_frame.pack(fill="both", expand=1)

#These three functions work together to delete users from the CSV file
#Listbox functions
def update(data):
	#This function imports the csv data into the listbox

	#Clear the listbox
	list_box.delete(0, END)

	#Add data to the listbox
	for item in data:
		list_box.insert(END, item)
def fillout(e):
	#This function updates entry box with listbox clicked

	#Delete whatever is in the entry box
	del_username_input.delete(0, END)
	text = list_box.get(ANCHOR)

	#Add clicked list item to entry box
	del_username_input.insert(0, text)
def check(e):
	#This function allows for usernames to be searched in the entry box

	#Fetch what was typed
	typed = del_username_input.get()
	if typed == '':
		#If nothing is typed, display all the data in the csv file
		data = username_list
	else:
		data = []
		for item in username_list:
			if typed.lower() in item.lower():
				#Only displays items relevant to the user's searched string
				data.append(item)

	#Update our listbox with selected items
	update(data)
#This function creates a listbox of all the names in the csv file
def CreateUserListbox(frame):
	global list_box
	#Create the scollbar
	global my_scrollbar
	my_scrollbar = Scrollbar(frame, orient=VERTICAL)
	#Create a listbox
	list_box = Listbox(frame, width=50, height=15, font=("Arial",25), yscrollcommand=my_scrollbar)
	list_box.place(relx=.5, rely=.35,anchor= CENTER)
	
	#Configure the scrollbar
	my_scrollbar.config(command=list_box.yview)
	my_scrollbar.pack(side=RIGHT,fill=Y)

	#Create a binding on the listbox onclick
	list_box.bind("<<ListboxSelect>>", fillout)

	#Get csv file and the list of names in the csv file
	csv = GetCSVFile()
	global username_list
	username_list = GetUserList()

	#Update the listbox contents
	update(username_list)

	#Automatically call the functions when a name in the listbox is clicked
	del_username_input.bind("<KeyRelease>", check)
#This function deletes individual names from the csv file
def DeleteUserFromCSV(name_to_delete):
	global csv_file
	#Removes the name selected from the list of dictionaries
	for row in csv_file:
		if row.get('name') == name_to_delete:
			row.clear()

	#This clears the cleared blank entry from the csv file
	csv_file = [ele for ele in csv_file if ele !={}]

	#Attempts to write list of dictionaries to the csv file to make it permanent
	try:
		fileHandle = open(csvFileName, 'w')
		for row in csv_file:
			fileHandle.write('None,{name},{project},None'.format(**row))
			fileHandle.write('\n')
		fileHandle.close()
	except OSError:
		#If an error is found, display this error message
		print("Cannot write to file!")
		messagebox.showerror('File error', 'Data could not be written to file')

	#Remove the old listbox and scrollbar to display the updated listbox and its contents
	list_box.destroy()
	my_scrollbar.destroy()
	CreateUserListbox(del_user_frame)

	#Removes the input from the input box
	del_username_input.delete(0, END)
#This function displays a messagebox to confirm to remove the record
def ConfirmDelete(username_to_delete):
	#Display the confirmation message
	response = messagebox.askyesnocancel("Confirm", "Are you sure you want to remove this user?")
	if response is None:
		#If the user clicked "Cancel" or "No", nothing happens
		return
	elif response:
		#If the user clicked "Yes", delete the record from the database
		DeleteUserFromCSV(username_to_delete)
#This function acts as a menu to delete users
def DeleteUser():
	#Create the frame for the delete user page
	global del_user_frame
	del_user_frame = customtkinter.CTkFrame(app, width=500, height=500)
	
	#Create the title label
	del_user_label = customtkinter.CTkLabel(del_user_frame, text="Delete users from CSV File", font=("Arial",30))
	del_user_label.place(relx=.5, rely=.1,anchor= customtkinter.CENTER)

	#Create input boxes
	global del_username_input
	del_username_input = customtkinter.CTkEntry(del_user_frame, placeholder_text="Enter name to delete...", width=300, font=("Arial",18))
	del_username_input.place(relx=.5, rely=.6,anchor= customtkinter.CENTER)
	
	#Display the listbox on the screen
	CreateUserListbox(del_user_frame)

	#Create and display the enter button which removes the user selected
	enter_button = customtkinter.CTkButton(del_user_frame, text="Delete",  height=45, width=30, corner_radius=20, font=("Arial",16), command=lambda: [ConfirmDelete(del_username_input.get())])
	enter_button.place(relx=.5, rely=.7,anchor= customtkinter.CENTER)

	#Create and display the back button
	back_button = customtkinter.CTkButton(del_user_frame, text="Back to Homepage", fg_color="transparent", border_width=2, border_color="#315184", height=45, width=30, corner_radius=20, font=("Arial",16), command=lambda: [del_user_frame.destroy(), AdminHomepage()])
	back_button.place(relx=.5, rely=.9,anchor= customtkinter.CENTER)

	#Display the frame on the page
	del_user_frame.pack(fill="both", expand=1)
#This function removes the project code from the database
def RemoveProjectNameFromDB(project_code):
	#Connect to MySQL
	db = mysql.connector.connect(
		host = "localhost",
		user = "root",
		passwd = pd, #Assigned the password to this variable
		database = "CartesianAccessDB"
		)
	c = db.cursor() #Create the database cursor

	#Delete the project selected from the database
	c.execute("DELETE FROM ProjectData WHERE projectcode=%s",(project_code,))
	#Commit the change to the database
	db.commit()
	#Close the database connection
	db.close()

	#Delete the frame 
	add_project_name_frame.destroy()
	#Recall the frame so the page displays the updated data
	AddProjectName()
#This function adds the project name to the database
def AddProjectNameToDB(project_code, project_name):
	#Assign the project code and project name to these variables
	project_code_to_add = str(project_code)
	project_name_to_add = str(project_name.get())

	if project_code_to_add == "" or project_name_to_add == "":
		#If no project code or no project name is inputted, show this error message
		messagebox.showerror('Invalid entry', 'Please enter a project name.')	
	else:
		#If a project code and project name is selected, add/update the project name to database
		#Connect to MySQL
		db = mysql.connector.connect(
			host = "localhost",
			user = "root",
			passwd = pd, #Assigned the password to this variable
			database = "CartesianAccessDB"
			)
		#Create the database cursor
		c = db.cursor()
		#Updates the database with the new project name
		sql_command = """UPDATE ProjectData SET projectName = %s WHERE projectCode = %s"""
		inputs = (project_name_to_add, project_code_to_add)
		c.execute(sql_command, inputs)
		#Commit the change to the database
		db.commit()
		
		#Empty the project name input box
		project_name.delete(0, END)
		#Delete and recall the frame so updated information is displayed
		add_project_name_frame.destroy()
		AddProjectName()
#This function displays the selected project and the buttons to add or delete project names
def SelectedProject(event):
	#Get the record selected on the Treeview
	selected = project_name_treeview.focus()
	selected_values = project_name_treeview.item(selected, 'values')
	projectCode_selected = selected_values[0]
	#Adjust the label to display the selected Treeview project code
	projectCode_selected_label.configure(text=projectCode_selected)

	#Create and display the entry box for the user to enter the name of the project
	projectName_input = customtkinter.CTkEntry(add_project_name_frame, width=200,placeholder_text="Enter project name..." ,font=("Arial",16))
	projectName_input.place(relx=.45, rely=.75,anchor= 'w')
	#Create and display the button to remove the project code
	delete_button = customtkinter.CTkButton(add_project_name_frame, height=35, width=30, corner_radius=20, text="Delete project code", fg_color="#E34234", font=("Arial",16), command=lambda: [RemoveProjectNameFromDB(projectCode_selected)])
	delete_button.place(relx=.5, rely=.83,anchor= customtkinter.CENTER)
	#Create and display the button to add the project name
	enter_button = customtkinter.CTkButton(add_project_name_frame, height=35, width=30, corner_radius=20, text="Enter", font=("Arial",16), command=lambda: [AddProjectNameToDB(projectCode_selected, projectName_input)])
	enter_button.place(relx=.6, rely=.75,anchor= 'w')
#This function creates the Treeview to display the project code and project name
def GenerateProjectNameTreeview(db_values):
	#Create Treeview scrollbar
	tree_scroll = Scrollbar(add_project_name_frame)
	tree_scroll.pack(side=RIGHT, fill=Y)
	global project_name_treeview
	#Create the Treeview to display the project names
	project_name_treeview = ttk.Treeview(add_project_name_frame, height=15,yscrollcommand=tree_scroll.set)
	#Configure the scrollbar
	tree_scroll.configure(command=project_name_treeview.yview)

	#Define the columns
	project_name_treeview['columns'] = ("Project Code", "Project Name")
	#Format the columns
	project_name_treeview.column("#0", width=0, minwidth=0)
	project_name_treeview.column("Project Code", anchor='w', width=500)
	project_name_treeview.column("Project Name", anchor='w', width=400)

	#Create the headings
	project_name_treeview.heading("#0", text="", anchor='w')
	project_name_treeview.heading("Project Code", text="Project Code", anchor='w')
	project_name_treeview.heading("Project Name", text="Project Name", anchor='w')

	#Sort the values alphabetically
	db_values = sorted(db_values)

	#Insert the data into the treeview
	num = 0
	for row in db_values:
		project_name_treeview.insert(parent='', index='end', iid=num, values=(row[0], row[1]))
		num += 1
	#Place the treeview on the GUI
	project_name_treeview.place(relx=.5, rely=.4, anchor=CENTER)
#This function is the menu for users to edit the CSV file
def AddProjectName():
	#Create the frame for this page
	global add_project_name_frame
	add_project_name_frame = customtkinter.CTkFrame(app, width=2000, height=1000)
	
	#Connect to MySQL
	db = mysql.connector.connect(
		host = "localhost",
		user = "root",
		passwd = pd, #Assigned the password to this variable
		database = "CartesianAccessDB"
		)
	#Create the database cursor
	c = db.cursor()

	#Display the title label for this page
	project_label = customtkinter.CTkLabel(add_project_name_frame, text="Add project name", font=("Arial",30))
	project_label.place(relx=.5, rely=.1, anchor=customtkinter.CENTER)

	#Fetch the project code and project names from the database
	c.execute("""
		SELECT projectCode, projectName
		FROM ProjectData""")
	values = c.fetchall()

	#Display the project name Treeview
	GenerateProjectNameTreeview(values)

	#Create the labels for the project code selected
	projectCode_label = customtkinter.CTkLabel(add_project_name_frame, text="Project Code:", font=("Arial",16))
	projectCode_label.place(relx=.35, rely=.7, anchor='w')
	global projectCode_selected_label
	projectCode_selected_label = customtkinter.CTkLabel(add_project_name_frame, text="", font=("Arial",16))
	projectCode_selected_label.place(relx=.45, rely=.7, anchor='w')

	#Call the function SelectedProject when a record on the Treeview is clicked
	project_name_treeview.bind("<ButtonRelease-1>", SelectedProject)

	#Create and display the back button to go back to the homepage
	back_button = customtkinter.CTkButton(add_project_name_frame, height=35, width=30, corner_radius=20, text="Back to Homepage", fg_color="transparent", border_width=2, border_color="#315184", font=("Arial",16), command=lambda: [add_project_name_frame.destroy(), AdminHomepage()])
	back_button.place(relx=.5, rely=.9,anchor= customtkinter.CENTER)

	#Display the frame on the screen
	add_project_name_frame.pack(fill="both", expand=1)

#These functions allow the user to assign the project manager to projects
def AssignManagerToDB(approver_to_change, manager_name, project_code, frame, edit):
	#This function updates the database with the project manager
	if manager_name == "Select approver":
		#If no manager is selected, an error message is shown
		messagebox.showerror("No approver selected", "Select an approver to change permissions.")
	else:
		if manager_name == "":
			#If no manager name is inputted, an error message is shown
			messagebox.showerror('No user inputted', 'Please choose a user.')
		elif project_code == "Select project code":
			#If no project code is inputted, an error message is shown
			messagebox.showerror('No project code selected', 'Please select a project code.')
		else:
			#Connect to MySQL
			db = mysql.connector.connect(
				host = "localhost",
				user = "root",
				passwd = pd, #Assigned the password to this variable
				database = "CartesianAccessDB"
				)
			c = db.cursor() #Create the database cursor

			#Select corresponding projectID to the project_code from the database
			c.execute("""
					SELECT projectID
					FROM ProjectData
					WHERE projectCode = %s 
					""", (project_code,));
			project_id = c.fetchall()
			project_id = str(project_id).replace('(','').replace(')','').replace('[','').replace(']','').replace(',','')

			#Select corresponding userID to the manager from the database
			c.execute("""
					SELECT userID
					FROM UserData
					WHERE name = %s 
					""", (manager_name,));
			user_id = c.fetchall()
			user_id = str(user_id).replace('(','').replace(')','').replace('[','').replace(']','').replace(',','')

			if user_id == "":
				#If no user_id is found, display this error message
				messagebox.showerror('No user found', 'Please create a manager account.')
				#Refresh the AddUser page by deleting and recalling it
				frame.destroy()
				AddUser()
			elif edit == False:
				try:
					#Attempts to insert the project approver information to the database
					c.execute("""
						INSERT INTO ProjectDetails(userID, projectID, accessRights, approver)
						Values(%s, %s, "Write", True)
						""",(int(user_id),int(project_id)))
					db.commit()
				except:
					#If value cannot be added to the database, show this duplication error
					messagebox.showerror("Database error", "Duplicate entry")
			else:
				#Select corresponding userID to the approver to change
				c.execute("""
						SELECT userID
						FROM UserData
						WHERE name = %s 
						""", (approver_to_change,));
				approver_id = c.fetchall()
				approver_id = str(approver_id).replace('(','').replace(')','').replace('[','').replace(']','').replace(',','')
				try:
					#Attempts to update the project approver information to the database
					c.execute("""
						UPDATE ProjectDetails SET userID = %s WHERE userID = %s and projectID = %s
						""",(int(user_id), int(approver_id),int(project_id)))
					db.commit()
					#Refresh the CHangeProjectManager page by deleting and recalling it
					frame.destroy()
					ChangeProjectManager()
				except:
					#If value cannot be updated to the database, show this duplication error
					messagebox.showerror("Database error", "Duplicate entry")
				
			try:
				#Empty the input box if it was used
				del_username_input.delete(0, END)
			except:
				pass

			#Close the database connection
			db.close()
#This function assigns the manager to the project		
def AssignProjectManager():
	#Create the frame for the page
	assign_manager_frame = customtkinter.CTkFrame(app, width=2000, height=1000)
	
	#Create and display the title label
	title_label = customtkinter.CTkLabel(assign_manager_frame, text="Assign project manager", font=("Arial",30))
	title_label.place(relx=.5, rely=.1,anchor= customtkinter.CENTER)

	#Create input boxes for the manager selected
	global del_username_input
	del_username_input = customtkinter.CTkEntry(assign_manager_frame, width=250, font=("Arial",16))
	del_username_input.place(relx=.55, rely=.57,anchor= 'n')
	#Create labels for input boxes
	del_username_label = customtkinter.CTkLabel(assign_manager_frame, text="Manager selected:", font=("Arial",16))
	del_username_label.place(relx=.4, rely=.57,anchor= 'n')

	#Create a combobox with all the project codes
	options = GetProjectCSV(csv_file)
	clicked = StringVar()
	clicked.set(options[0])
	global project_option_box
	project_option_box = customtkinter.CTkComboBox(assign_manager_frame, state="readonly", values=options, width=250)
	project_option_box.set("Select project code")
	#Place the combobox on the screeb
	project_option_box.place(relx=.45, rely=.65,anchor='n')

	#Display listbox on this page
	CreateUserListbox(assign_manager_frame)

	#Create and display the button to assign the added values to the database
	enter_button = customtkinter.CTkButton(assign_manager_frame, text="Assign", height=45, width=30, corner_radius=20, font=("Arial",16), command=lambda: [AssignManagerToDB(None, del_username_input.get(), project_option_box.get(), assign_manager_frame, False)])
	enter_button.place(relx=.59, rely=.64,anchor= 'n')

	#Create and display the back button which returns the user to the homepage
	back_button = customtkinter.CTkButton(assign_manager_frame, height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184",text="Back to Homepage", font=("Arial",16), command=lambda: [assign_manager_frame.destroy(), AdminHomepage()])
	back_button.place(relx=.5, rely=.9,anchor= customtkinter.CENTER)

	#Display this page on the screen
	assign_manager_frame.pack(fill="both", expand=1)
#This function changes the project manager
def DeleteApprover(frame):
	global overview_tree
	#Gets the record selected on the Treeview and assigns the values to these variables
	selected = overview_tree.focus()
	selected_value = overview_tree.item(selected, 'values')
	project_code = selected_value[0]
	approver_to_change = selected_value[2]

	#Connect to MySQL
	db = mysql.connector.connect(
		host = "localhost",
		user = "root",
		passwd = pd, #Assigned the password to this variable
		database = "CartesianAccessDB"
		)
	c = db.cursor() #Create the database cursor

	#Select corresponding projectID to the project_code
	c.execute("""
			SELECT projectID
			FROM ProjectData
			WHERE projectCode = %s 
			""", (project_code,));
	project_id = c.fetchall()
	project_id = str(project_id).replace('(','').replace(')','').replace('[','').replace(']','').replace(',','')

	#Select corresponding userID to the project_code
	c.execute("""
			SELECT userID
			FROM UserData
			WHERE name = %s 
			""", (approver_to_change,));
	user_id = c.fetchall()
	user_id = str(user_id).replace('(','').replace(')','').replace('[','').replace(']','').replace(',','')

	#Deletes the data from the database permanently
	c.execute("""DELETE FROM ProjectDetails WHERE userID = %s and projectID = %s""",(int(user_id),int(project_id)))
	db.commit()

	#Refreshes the OverviewTree with the updated data
	overview_tree.destroy()
	OverviewTreeview(frame)
	
#This function displays the selected values chosen
def ChangeApproverOptions(delete_approver_button, frame, selected_project_code_label, selected_approval):
	global overview_tree
	#Fetch the values selected from the Treeview
	selected = overview_tree.focus()
	selected_value = overview_tree.item(selected, 'values')
	if selected_value=="":
		#If no row is selected, this error message is displayed
		messagebox.showerror("No record selected", "Select a record to change.")
	else:
		project_code = selected_value[0]
		approver_to_change = selected_value[2]

		#Get names from the CSV file
		username_list = GetUserList()

		#Create and configure these labels to display the selected values
		selected_project_label = customtkinter.CTkLabel(frame, text="Selected project:", font=("Arial",16))
		selected_project_label.place(relx=.29, rely=.65,anchor='w')
		selected_project_code_label.configure(text=project_code)
		selected_project_code_label.place(relx=.39, rely=.65,anchor='w')
		selected_approval_label = customtkinter.CTkLabel(frame, text="Selected approver:", font=("Arial",16))
		selected_approval_label.place(relx=.29, rely=.68,anchor='w')
		selected_approval.configure(text=approver_to_change)
		selected_approval.place(relx=.39, rely=.68,anchor='w')
		change_label = customtkinter.CTkLabel(frame, text="Change approver:", font=("Arial",16))
		change_label.place(relx=.29, rely=.75,anchor='w')

		#Create a combobox to select the approver
		approver_combobox = customtkinter.CTkComboBox(frame, state="readonly", values=username_list, width=200)
		approver_combobox.place(relx=.39, rely=.75,anchor='w')
		#Set the default option
		approver_combobox.set("Select approver")

		#Create and display the submit button
		submit_button = customtkinter.CTkButton(frame, text="Submit", height=35, width=30, corner_radius=20, font=("Arial",16), command=lambda: [AssignManagerToDB(approver_to_change, approver_combobox.get(),selected_value[0], frame, True)])
		submit_button.place(relx=.5, rely=.8,anchor= customtkinter.CENTER)
#This function displays the change project manager page
def ChangeProjectManager():
	#Create the frame to display this page
	change_manager_frame = customtkinter.CTkFrame(app, width=2000, height=1000)

	#Create and display the title label
	title_label = customtkinter.CTkLabel(change_manager_frame, text="Change project manager", font=("Arial",30))
	title_label.place(relx=.5, rely=.1,anchor= customtkinter.CENTER)

	#Create and display the back button
	back_button = customtkinter.CTkButton(change_manager_frame, height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184",text="Back to Homepage", font=("Arial",16), command=lambda: [change_manager_frame.destroy(), AdminHomepage()])
	back_button.place(relx=.5, rely=.9,anchor= customtkinter.CENTER)

	#Show the Treeview on this page
	OverviewTreeview(change_manager_frame)
	selected_project_code_label = customtkinter.CTkLabel(change_manager_frame, text="", font=("Arial",16))
	selected_approval = customtkinter.CTkLabel(change_manager_frame, text="", font=("Arial",16))

	#Create and display the approver buttons
	change_approver_button = customtkinter.CTkButton(change_manager_frame, text="Change approver", height=35, width=30, corner_radius=20, font=("Arial",16), command=lambda: [ChangeApproverOptions(delete_approver_button, change_manager_frame, selected_project_code_label, selected_approval)])
	change_approver_button.place(relx=.65, rely=.66,anchor= customtkinter.CENTER)
	delete_approver_button = customtkinter.CTkButton(change_manager_frame, text="Delete approver", height=35, width=30, fg_color="transparent", border_width=2, border_color="#E34234" ,corner_radius=20, font=("Arial",16), command=lambda: [DeleteApprover(change_manager_frame)])
	delete_approver_button.place(relx=.65, rely=.76,anchor= customtkinter.CENTER)

	#Show the page on the screen
	change_manager_frame.pack(fill="both", expand=1)
	
#These five functions work together to reset passwords
def ChangePassword(change_password, confirm_password, button, user):
	#This function checks if the passwords match
	if change_password == "" or confirm_password == "":
		#If passwords do not match, an error message is shown
		messagebox.showerror('Invalid password', 'Please type in a password')
	else:
		if change_password == confirm_password:
			#Change the password#

			#Connect to MySQL
			db = mysql.connector.connect(
				host = "localhost",
				user = "root",
				passwd = pd, #Assigned the password to this variable
				database = "CartesianAccessDB"
				)
			#Create the database cursor
			c = db.cursor()

			#Get the salt and hashed password
			change_password, salt = HashPassword(change_password)

			#Updates the database with the new password
			sql_command = """UPDATE UserData SET password = %s, salt = %s WHERE email = %s"""
			inputs = (change_password, salt, user)
			c.execute(sql_command, inputs)
			db.commit()

			#Button changes when the password has been changed
			button.configure(text="Password changed",state=DISABLED)

			#This back button takes you back to the user's homepage
			back_button = customtkinter.CTkButton(reset_password_frame, text="Back to Homepage", font=("Arial",16), height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184",command=lambda: [BackToHome(), reset_password_frame.destroy()])
			back_button.place(relx=.5, rely=.9,anchor= customtkinter.CENTER)
		else:
			#If passwords do not match, an error message is shown
			messagebox.showerror('Invalid password', 'Passwords do not match')
#This function makes sure that an email is chosen from the combobox
def CheckUser(email):
	#This function updates the user's password
	if email=="Choose email":
		#If nothing is entered, error messagebox is shown
		messagebox.showerror('Invalid input', 'Select an email')
	else:
		#Display the labels and entry boxes to change passwords
		change_password_label = customtkinter.CTkLabel(reset_password_frame, text="New password: ", font=("Arial",16))
		change_password_label.place(relx=.45, rely=.45,anchor= 'w')
		change_password_input = customtkinter.CTkEntry(reset_password_frame, font=("Arial",16), show="*")
		change_password_input.place(relx=.6, rely=.45,anchor= 'w')
		confirm_password_label = customtkinter.CTkLabel(reset_password_frame, text="Confirm password: ", font=("Arial",16))
		confirm_password_label.place(relx=.45, rely=.5,anchor= 'w')
		confirm_password_input = customtkinter.CTkEntry(reset_password_frame, font=("Arial",16), show="*")
		confirm_password_input.place(relx=.6, rely=.5,anchor= 'w')
		change_password_button = customtkinter.CTkButton(reset_password_frame, text="Change", font=("Arial",16), command=lambda: [ChangePassword(change_password_input.get(),confirm_password_input.get(),change_password_button,email)])
		change_password_button.place(relx=.6, rely=.55 ,anchor= 'w')
#This function resets the password in the database
def ResetPasswordToDB(email):
	#Connect to MySQL
	db = mysql.connector.connect(
		host = "localhost",
		user = "root",
		passwd = pd, #Assigned the password to this variable
		database = "CartesianAccessDB"
		)
	#Create the database cursor
	c = db.cursor()

	#Set the password to the default password "BLANK"
	set_password = "BLANK"
	password_to_add, salt_to_add = HashPassword(set_password)

	#Updates the database with the new password
	sql_command = """UPDATE UserData SET password = %s, salt = %s WHERE email = %s"""
	inputs = (password_to_add, salt_to_add, email)
	c.execute(sql_command, inputs)
	db.commit()

	#Success message is shown
	messagebox.showinfo('Database updated', 'Password reset')
#This function sends the user back to the correct homepage based on their login type
def BackToHome():
	if login_type == "manager":
		#If login type is "manager", send the user back to the manager homepage
		ManagerHomepage()
	elif login_type == "admin":
		#If login type is "admin", send the user back to the admin homepage
		AdminHomepage()
#This function acts as a menu to allow admins to reset the password of users
def ResetPassword(email):
	#Create the frame for this page
	global reset_password_frame
	reset_password_frame = customtkinter.CTkFrame(app, width=2000, height=1000)

	#Display title of the page
	reset_password_label = customtkinter.CTkLabel(reset_password_frame, text="Reset password", font=("Arial",30))
	reset_password_label.place(relx=.5, rely=.15,anchor= customtkinter.CENTER)

	if email == "":
		#If this function is called from the Admin homepage, allow admin to choose the user

		#Connect to MySQL
		db = mysql.connector.connect(
			host = "localhost",
			user = "root",
			passwd = pd, #Assigned the password to this variable
			database = "CartesianAccessDB"
				)

		c = db.cursor() #Create the database cursor

		c.execute("SELECT email FROM UserData")
		email_list = c.fetchall()
		email_option = []

		for email in email_list:
			email_option.append(email[0])
		
		#Create an email combobox
		email_option_box = customtkinter.CTkComboBox(reset_password_frame, state="readonly", values=email_option, width=250)
		email_option_box.place(relx=.5, rely=.3,anchor= customtkinter.CENTER)
		#Set the default option
		email_option_box.set("Choose email")

		#This button sends the username selected to the ResetPasswordToDB page
		select_username_button = customtkinter.CTkButton(reset_password_frame, text="Enter",height=35, width=30, corner_radius=20, font=("Arial",16), command=lambda: [ResetPasswordToDB(email_option_box.get())])
		select_username_button.place(relx=.5, rely=.35,anchor=customtkinter.CENTER)

		#This back button takes you back to the admin homepage
		back_button = customtkinter.CTkButton(reset_password_frame, text="Back to Homepage", font=("Arial",16), height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184",command=lambda: [AdminHomepage(), reset_password_frame.destroy()])
		back_button.place(relx=.5, rely=.9,anchor= customtkinter.CENTER)
	else:
		#Allow new user to change their password
		CheckUser(email)

	#This displays the page on the screen
	reset_password_frame.pack(fill="both", expand=1)

#These two functions work together to add users
def HashPassword(password):
	#Generate a random salt using the secrets module
	salt = secrets.token_hex(16)
	#Hash the password using the salt and hashlib's SHA-256 algorithm
	hash_object = hashlib.sha256((password + salt).encode())
	#Get the hexadecimal representation of the hash to put into the database
	hash_hex = hash_object.hexdigest()
	return(hash_hex, salt)
def AddUserToDB(name_input, email_input, account_type_input):
	#Fetch the inputs and assign them to these variables
	name_to_add = name_input.get()
	email_to_add = email_input.get()
	set_password = "BLANK"
	password_to_add, salt_to_add = HashPassword(set_password)
	account_type_to_add = (account_type_input.get()).lower()

	#Validate email input to contain @ symbol
	email_status = False
	if "@cartesian.com" in email_to_add:
		email_status = True

	#Makes sure all fields are filled out
	if name_to_add == "Select name" or email_to_add == "" or account_type_to_add=="select account type":
		#If no input is entered, an error message is shown
		messagebox.showerror('No input', 'Please ensure all fields are filled out.')
	elif email_status == False:
		#If an invalid email is entered, an error message is shown
		messagebox.showerror('Invalid email', 'Please ensure a valid email is entered.')
	else:
		#If there are no errors with the inputted data, the new user is added to the database

		#Connect to database
		db = mysql.connector.connect(
		host = "localhost",
		user = "root",
		passwd = pd,
		database = "CartesianAccessDB"
		)
		c = db.cursor()

		#Adds user details to the database
		c.execute("""
			INSERT INTO UserData(name, email, password, accountType, salt) 
			VALUES(%s, %s, %s, %s, %s)
			""",(name_to_add, email_to_add, password_to_add, account_type_to_add, salt_to_add))
		
		#Commits the change to the database
		db.commit()
		#Closes the database connection
		db.close()
		
		#Removes the input from the input boxes, ready for the next account to be added
		name_input.set("Select name")
		email_input.delete(0, END)
		account_type_input.set("Select account type")
#This function acts a menu to add users to the database
def AddUser():
	#Create a frame for this page
	global add_user_frame
	add_user_frame = customtkinter.CTkFrame(app, width=2000, height=1000)

	#Create title label
	add_user_label = customtkinter.CTkLabel(add_user_frame, text="Add users to the database", font=("Arial",30))
	add_user_label.place(relx=.5, rely=.15,anchor= customtkinter.CENTER)

	#Fetch the name list from the csv file
	name_options = GetUserList()

	#Connect to MySQL
	db = mysql.connector.connect(
		host = "localhost",
		user = "root",
		passwd = pd, #Assigned the password to this variable
		database = "CartesianAccessDB"
			)

	c = db.cursor() #Create the database cursor
	#Fetch the names from the database
	c.execute("SELECT name FROM UserData")
	name_list = c.fetchall()

	#Removes name from accounts that have been already created
	for name in name_options:
		for csv_name in name_list:
			csv_name = csv_name[0]
			if csv_name == name:
				name_options.remove(name)
	
	#Create a combobox with the list of names with people who do not have accounts
	name_combo_box = customtkinter.CTkComboBox(add_user_frame, state="readonly", values=name_options, width=170)
	name_combo_box.set("Select name")
	name_combo_box.place(relx=.5, rely=.3,anchor= 'n')
	#Create an input box for the email of the user to be input
	email_input = customtkinter.CTkEntry(add_user_frame, width=300, font=("Arial",16))
	email_input.place(relx=.55, rely=.35,anchor= 'n')

	#Create a combo box for the account type options
	options = [
		"Manager",
		"Admin"
		]

	#Create a combobox to so the user can select an account type
	account_type_combo_box = customtkinter.CTkComboBox(add_user_frame, state="readonly", values=options, width=170)
	account_type_combo_box.set("Select account type")
	account_type_combo_box.place(relx=.5, rely=.4,anchor= 'n')

	#Create labels for input boxes
	name_label = customtkinter.CTkLabel(add_user_frame, text="Name:", font=("Arial",16))
	name_label.place(relx=.4, rely=.3,anchor= 'n')
	email_label = customtkinter.CTkLabel(add_user_frame, text="Email:", font=("Arial",16))
	email_label.place(relx=.4, rely=.35,anchor= 'n')

	#Create enter and back buttons
	enter_button = customtkinter.CTkButton(add_user_frame, text="Enter",height=35, width=30, corner_radius=20, font=("Arial",16), command=lambda: [AddUserToDB(name_combo_box, email_input, account_type_combo_box)])
	enter_button.place(relx=.48, rely=.5,anchor= 'w')
	back_button = customtkinter.CTkButton(add_user_frame, text="Back to Homepage", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184",font=("Arial",16), command=lambda: [add_user_frame.destroy(), AdminHomepage()])
	back_button.place(relx=.5, rely=.9,anchor= 'n')

	#Displays the frame on the screen
	add_user_frame.pack(fill="both", expand=1)

#These three functions work together to delete users from the database
def DeleteAccountTreeview(frame):
	#Connect to MySQL
	db = mysql.connector.connect(
		host = "localhost",
		user = "root",
		passwd = pd, #Assigned the password to this variable
		database = "CartesianAccessDB"
		)
	c = db.cursor() #Create the database cursor

	#Fetch the name, email and account type from the database
	c.execute("SELECT name, email, accountType FROM UserData")
	values = c.fetchall()
	#Sort the values alphabetically
	values.sort()

	#Add a Treeview widget to display the account data
	global account_overview_tree
	account_overview_tree = ttk.Treeview(frame, column=("c1", "c2", "c3"), show='headings', height=14)
	account_overview_tree.column("# 1", anchor=customtkinter.CENTER, width=300)
	account_overview_tree.heading("# 1", text="Name")
	account_overview_tree.column("# 2", anchor=customtkinter.CENTER, width=600)
	account_overview_tree.heading("# 2", text="Email")
	account_overview_tree.column("# 3", anchor=customtkinter.CENTER, width=250)
	account_overview_tree.heading("# 3", text="Account type")
	account_overview_tree.place(relx=.5, rely=.4,anchor= customtkinter.CENTER)

	#Insert values into the treeview
	num = 0
	for row in values:
		account_overview_tree.insert('', 'end', text=num, values=(row[0], row[1], row[2]))
		num += 1

	#Close the connection to the database
	db.close()
#This function removes the user selected from the database
def DeleteAccountFromDB(frame):
	#Get the record selected on the Treeview
	selected = account_overview_tree.focus()
	selected_value = account_overview_tree.item(selected, 'values')

	if selected_value == "":
		#If no user is selected, an error message is displayed
		messagebox.showerror('No input', 'Please choose a user to delete.')
	else:
		#Assigns variables to the selected values
		name = selected_value[0]
		email = selected_value[1]

		#Confirm that the admin user wants to delete the user
		response = messagebox.askyesnocancel("Confirm", "Are you sure you want to remove this user?")
		if response is None:
			#If the user clicks "Cancel" or "No", nothing happens
			return
		elif response: #If the user clicks "Yes", delete the record from the database
			
			#Connect to database
			db = mysql.connector.connect(
			host = "localhost",
			user = "root",
			passwd = pd,
			database = "CartesianAccessDB"
			)
			c = db.cursor() #Create the database cursor

			#Delete selected user from database
			c.execute("""DELETE FROM UserData WHERE email = %s and name = %s""",(email,name))
			#Commit the change to the database
			db.commit()
			#Close the database connection
			db.close()

			#Update the Treeview
			DeleteAccountTreeview(frame)
#This function displays the page for deleting an account
def DeleteAccount():
	#Create a frame for this page
	delete_account_frame = customtkinter.CTkFrame(app, width=2000, height=1000)

	#Display the title label
	delete_account_label = customtkinter.CTkLabel(delete_account_frame, text="Delete user from database", font=("Arial",30))
	delete_account_label.place(relx=.5, rely=.1,anchor= customtkinter.CENTER)

	#Display the Treeview of all the accounts
	DeleteAccountTreeview(delete_account_frame)

	#Create a button to delete a selected user
	delete_approver_button = customtkinter.CTkButton(delete_account_frame, text="Delete approver", height=35, width=30, fg_color="transparent", border_width=2, border_color="#E34234" ,corner_radius=20, font=("Arial",16), command=lambda: [DeleteAccountFromDB(delete_account_frame)])
	delete_approver_button.place(relx=.5, rely=.7,anchor= customtkinter.CENTER)

	#Add back button
	back_button = customtkinter.CTkButton(delete_account_frame, text="Back to Homepage", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184",font=("Arial",16), command=lambda: [delete_account_frame.destroy(), AdminHomepage()])
	back_button.place(relx=.5, rely=.9,anchor= 'n')

	#Display the page on the screen
	delete_account_frame.pack()

#This function displays the admin homepage
def AdminHomepage(): 	
	#Create a frame for this page
	admin_home_frame = customtkinter.CTkFrame(app, width=2000, height=1000)
	
	#Create the title label
	admin_welcome_label = customtkinter.CTkLabel(admin_home_frame, text="Admin homepage", font=("Arial",30))
	admin_welcome_label.place(relx=.5, rely=.15,anchor= customtkinter.CENTER)

	#Create menu buttons for the CSV functions
	csv_label = customtkinter.CTkLabel(admin_home_frame, text="CSV:", font=("Arial",16))
	csv_label.place(relx=.55, rely=.25,anchor='w')
	upload_csv_button = customtkinter.CTkButton(admin_home_frame, text="Upload CSV", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184",font=("Arial",16), command=UploadCSVFile)
	upload_csv_button.place(relx=.55, rely=.3,anchor= 'w')
	edit_csv_button = customtkinter.CTkButton(admin_home_frame, text="Edit CSV", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184", font=("Arial",16), command=lambda: [EditCSVFile(), admin_home_frame.destroy()])
	edit_csv_button.place(relx=.55, rely=.4,anchor= 'w')
	del_csv_button = customtkinter.CTkButton(admin_home_frame, text="Delete users from CSV file", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184", font=("Arial",16), command=lambda: [DeleteUser(), admin_home_frame.destroy()])
	del_csv_button.place(relx=.55, rely=.5,anchor= 'w')
	#Create menu buttons for the linking CSV to database functions
	csv_to_db_label = customtkinter.CTkLabel(admin_home_frame, text="CSV to database:", font=("Arial",16))
	csv_to_db_label.place(relx=.55, rely=.6,anchor='w')
	add_project_name_button = customtkinter.CTkButton(admin_home_frame, text="Add project name", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184", font=("Arial",16), command=lambda: [AddProjectName(), admin_home_frame.destroy()])
	add_project_name_button.place(relx=.55, rely=.65,anchor= 'w')
	assign_project_manager_button = customtkinter.CTkButton(admin_home_frame, text="Assign project approver", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184", font=("Arial",16), command=lambda: [AssignProjectManager(), admin_home_frame.destroy()])
	assign_project_manager_button.place(relx=.55, rely=.75,anchor= 'w')
	change_project_manager_button = customtkinter.CTkButton(admin_home_frame, text="Change project approver", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184", font=("Arial",16), command=lambda: [ChangeProjectManager(), admin_home_frame.destroy()])
	change_project_manager_button.place(relx=.55, rely=.85,anchor= 'w')
	#Create menu buttons for the database functions
	db_label = customtkinter.CTkLabel(admin_home_frame, text="DB:", font=("Arial",16))
	db_label.place(relx=.35, rely=.25,anchor='w')
	reset_password_button = customtkinter.CTkButton(admin_home_frame, text="Reset password", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184", font=("Arial",16), command=lambda: [ResetPassword(""), admin_home_frame.destroy()])
	reset_password_button.place(relx=.35, rely=.3,anchor= 'w')
	add_users_button = customtkinter.CTkButton(admin_home_frame, text="Add users", font=("Arial",16), height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184", command=lambda: [AddUser(), admin_home_frame.destroy()])
	add_users_button.place(relx=.35, rely=.4,anchor= 'w')
	del_users_button = customtkinter.CTkButton(admin_home_frame, text="Delete users", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184", font=("Arial",16), command=lambda: [DeleteAccount(), admin_home_frame.destroy()])
	del_users_button.place(relx=.35, rely=.5,anchor= 'w')

	#Display the page on the screen
	admin_home_frame.pack()

#This function allows the user to login again after waiting for the set time
def Wait():
	global count
	count=0
	print("Finished wait")

#This function sends an email to the user
def SendEmail(receiver_address, subject, body):
	#SMTP information
	smtp_server = 'smtp.gmail.com'
	smtp_port = 587
	sender_address = "testeremailforcode@gmail.com"
	
	#Message information passed in the parameters
	message = MIMEText(body)
	message["Subject"] = subject
	message["From"] = sender_address
	message["To"] = receiver_address

	try: #Attempts to send the message to the user
		server = smtplib.SMTP(smtp_server, smtp_port)
		server.starttls()
		server.login(sender_address, 'rako uapo panx joth')
		server.send_message(message)
		server.quit()
	except: #If no email is sent, an error message is displayed
		messagebox.showerror('Email not sent', 'Time out error')

#This function checks the verification code inputted against verification code generated
def VerificationCodeCheck(vc_frame, vc_code_inputted, vc_code, blank_check):
	#Checks if the verification code inputted is the same as the one sent in the email to the user
	if vc_code == vc_code_inputted:
		#If the verification code check is successful, either send the user to the homepage or let them set their password
		print("Successful verification code")
		vc_frame.destroy()
		if blank_check == True:
			ResetPassword(email)
		if login_type == "admin":
			AdminHomepage()
		else:
			ManagerHomepage()
	elif vc_code_inputted == "":
		#If no verification code is entered, an error message is displayed
		messagebox.showerror('Invalid entry', 'Please enter in the verification code.')
	else:
		print("Wrong verification code")
		if attempts !=2: #If the verification code check failed, an error message is shown if the user still has a login attempt left
			vc_frame.destroy()
			messagebox.showerror('Wrong verification code', 'Please log in again. You have one more attempt.')
			Login()
		else: #If the verification code check failed and the user has used up all their login attempts, user is locked out of the system for 10 minutes
			vc_enter_button.configure(text=f'Limit reached. Try again in 24hrs.')
			back_button.configure(text=f'Close application', command=app.destroy)
			#Makes the user wait for 10 mins
			app.after(600000, Wait)
#This function generates a random 6-digit long code consisting of letters and numbers
def VerificationCode():
	#Generates a 6-character long code
	length = 6
	chars = string.ascii_letters
	chars += string.digits
	code = ""
	for i in range(length):
		code += random.choice(chars)
	print(code)

	#Send the code to the associated email
	receiver_address = email
	subject = "Verification code for login"
	#Body of the email
	body = 'Your verification code is: ' + code + '\n\n[Do not reply to this email]'
	SendEmail(receiver_address, subject, body)
	return(code)
#This function creates the verification code page
def VerificationCodeDisplay(blank_check):
	#Create the frame for this page
	vc_frame = customtkinter.CTkFrame(app, width=2000, height=1000)

	#Generate the verification code and send it to the user's email
	vc_code = VerificationCode()

	#Create the title label and instructions
	vc_label = customtkinter.CTkLabel(vc_frame, text="Verification code", font=("Arial",30))
	vc_label.place(relx=.5, rely=.15,anchor=customtkinter.CENTER)
	vc1_label = customtkinter.CTkLabel(vc_frame, text="A verification code was sent to your email. Enter below.", font=("Arial",16))
	vc1_label.place(relx=.5, rely=.3,anchor=customtkinter.CENTER)
	vc_input = customtkinter.CTkEntry(vc_frame, placeholder_text="Enter verification code...", width=250, font=("Arial",16))
	vc_input.place(relx=.5, rely=.4,anchor=customtkinter.CENTER)

	#Create the enter button to allow the user to submit the verification code
	global vc_enter_button
	vc_enter_button = customtkinter.CTkButton(vc_frame, text="Enter", height=35, width=30, corner_radius=20, font=("Arial",16), command=lambda: VerificationCodeCheck(vc_frame, vc_input.get(), vc_code, blank_check))
	vc_enter_button.place(relx=.5, rely=.7,anchor=customtkinter.CENTER)
	#Create the back button to allow the user to go back to the login page
	global back_button
	back_button = customtkinter.CTkButton(vc_frame, text="Back to Login", height=35, width=30, corner_radius=20, font=("Arial",16), command=lambda: [vc_frame.destroy(), Login()])
	back_button.place(relx=.5, rely=.9,anchor=customtkinter.CENTER)

	#Displays the page on the screen
	vc_frame.pack(fill="both", expand=1)

#This function records the login attempt to the database
def LoginLog(username_record, account_type_record):
	#Get today's date
	dateattempt_record = date.today()
	timeattempt_record = strftime('%H:%M:%S')

	#Connect to database
	db = mysql.connector.connect(
	host = "localhost",
	user = "root",
	passwd = pd,
	database = "CartesianAccessDB"
	)
	mycursor = db.cursor()

	#Insert data into the database
	insert_sql = "INSERT INTO loginattempts (email, accountType, dateattempt, timeattempt) VALUES (%s, %s, %s, %s)"
	val = (username_record, account_type_record, dateattempt_record, timeattempt_record)
	mycursor.execute(insert_sql, val)
	#Commit the changes to the database
	db.commit()
	#Close the database
	db.close()

#This function can be used to check if the password is the default password of "BLANK"
def DecryptPassword(user, password_entered):
	#Connect to MySQL
	db = mysql.connector.connect(
		host = "localhost",
		user = "root",
		passwd = pd, #Assigned the password to this variable
		database = "CartesianAccessDB"
		)
	c = db.cursor() #Create the database cursor
	#Fetch the password and salt from the database
	c.execute("SELECT password, salt FROM UserData WHERE email = %s",(user,))
	password_list = c.fetchone()
	password, salt = password_list[0], password_list[1]

	#Get hash equivalent of the password entered
	hash_object = hashlib.sha256((password_entered + salt).encode())
	hashed_password_entered = hash_object.hexdigest()

	#Get hash equivalent of hashed "BLANK"
	blank = "BLANK"
	hash_object1 = hashlib.sha256((blank + salt).encode())
	hashed_blank = hash_object1.hexdigest()

	#Compares hashed password entered against hashed password in the database
	if password == hashed_password_entered:
		if hashed_password_entered == hashed_blank: #The password is "BLANK"
			return(True, True)
		else: #The password is not "BLANK" but still correct
			return (True, False)
	else: #The password is incorrect
		return(False, False)
#This function checks the username and password entered against the database
def LoginCheck(frame, username, password, login_button):
	global count
	global attempts
	global login_type
	global email

	#Create the error labels
	login_wrong_label = customtkinter.CTkLabel(frame, text=("Email or password is incorrect. \nYou have" , (4-count), "attempts left"), font=("Arial",30))
	error_label = customtkinter.CTkLabel(frame, text="Ensure there are no blank entries", text_color="#E34234", font=("Arial",16))
	#Makes sure only 5 attempts are allowed
	if count < 4 and len(username) != 0 and len(password) != 0:
		#Connect to MySQL
		db = mysql.connector.connect(
			host = "localhost",
			user = "root",
			passwd = pd, #Assigned the password to this variable
			database = "CartesianAccessDB"
			)
		#Create the database cursor
		c = db.cursor()
		
		#Fetch the user data from the database
		c.execute("SELECT * FROM UserData")
		login_list = c.fetchall()

		#Set the password check boolean to be false
		login_check = False
		
		if len(username) != 0 and len(password) != 0 and count < 4 and login_check==False:
			#The email, password is blank, the count is less than four and the login attempt is false
			count = count + 1
			for row in login_list:
				#Hash the password entered with the correct salt
				password_check, blank_check = DecryptPassword(row[2], password)
				if username == row[2] and password_check == True:
					print("Login correct")
					login_check = True
					login_type = row[4]
					email = row[2]
					#If login is correct, store the login attempt
					LoginLog(username, row[4])
					if attempts < 2:
						#If the verification attempts is less than two, send the user to the verification code display page
						attempts = attempts + 1
						print("attempts is:",attempts)
						VerificationCodeDisplay(blank_check)
						#Destroy the login page
						frame.destroy()
			if login_check != True:
				#If login is incorrect, store the login attempt and show the error labels
				print("Login NOT correct")
				LoginLog(username, None)
				login_button.configure(text=("You have" , (4-count), "attempts left"))
				error_label.configure(text="  Incorrect email or password  ")
				error_label.place(relx=.5, rely=.6,anchor=customtkinter.CENTER)
		#Close the database connection
		db.close()
	elif count < 4:
		#If any input is blank, show this error message
		messagebox.showerror('Invalid login', 'Ensure there are no blank entries.')
	else:
		#If all login attempts have been used and the login was unsuccessful, lock user out of the system
		login_wrong_label.destroy()
		login_button.configure(text=f'Limit reached. Try again in 24hrs.')
		#Stores the login attempt and does not allow user to input details until wait is up
		LoginLog(username, None)
		#Makes the user wait for 24 hours
		app.after(86400000, Wait)
#This function displays the login page
def Login():
	#Create a frame for this page
	login_choice_frame = customtkinter.CTkFrame(app, width=2000, height=1000)

	#Create username and password labels
	login_label = customtkinter.CTkLabel(login_choice_frame, text="User Access Management Login", font=("Arial",30))
	login_label.place(relx=.5, rely=.15,anchor=customtkinter.CENTER)
	email_input = customtkinter.CTkEntry(login_choice_frame, placeholder_text="Email", font=("Arial",18), width=280)
	email_input.place(relx=.5, rely=.3,anchor=customtkinter.CENTER)
	password_input = customtkinter.CTkEntry(login_choice_frame, placeholder_text="Password", font=("Arial",18), width=280, show="*")
	password_input.place(relx=.5, rely=.4,anchor=customtkinter.CENTER)
	
	#Get the email and password entered from the entry boxes
	email = email_input.get()
	password = password_input.get()

	#Create login button
	login_button = customtkinter.CTkButton(login_choice_frame, text="Login", height=35, width=30, corner_radius=20, font=("Arial",18), command=lambda: [LoginCheck(login_choice_frame, email_input.get(), password_input.get(), login_button)])
	login_button.place(relx=.5, rely=.5,anchor=customtkinter.CENTER)

	#Display the page on the screen
	login_choice_frame.pack()

#Set these global variables to be used in functions
csv_file = GetCSVFile()
project_csv = GetProjectCSV(csv_file)
no_of_projects = len(project_csv)
login_type = ''
email = ''

#Get the date of today
today = date.today()
today_date = today.strftime("%d")
today_date = str(today_date)

#If today is th 1st or 15th day of the month, send a reminder email
if int(today_date) == 1 or int(today_date) == 15:
	print("Sending reminder email")
	#Connect to MySQL
	db = mysql.connector.connect(
		host = "localhost",
		user = "root",
		passwd = pd, #Assigned the password to this variable
		database = "CartesianAccessDB"
		)
	c = db.cursor() #Create the database cursor

	#Select all the permission data from the database
	c.execute("SELECT * FROM CSVPermissions")
	values = c.fetchall()

	reminder_managers = []
	for row in values:
		#If rows have not been completed, add the associated manager to the reminder_managers list
		if str(row[5]) == "None" or row[5] == "Please complete":
			manager = row[7]
			if str(manager) != "None":
				reminder_managers.append(manager)
	send_managers = []
	#De-duplicate the manager list
	for i in reminder_managers:
	  if i not in send_managers:
	    send_managers.append(i)

	for manager in send_managers       :
		#Fetch the corresponding email for each manager
		c.execute("SELECT email FROM UserData WHERE name = %s",(manager,))
		recipient = c.fetchone()
		print(recipient[0])

		#Subject of the email
		subject = "Reminder: Check User access rights"
		#Body of the email
		body = "Please log into the user access management system to complete this month's user access rights review"
		
		#Send the email to the recipients
		SendEmail(recipient[0], subject, body)

#Set the login count and attempts to 0
count = 0
attempts = 0

#Style the system
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Arial",25))
style.configure("Treeview", font=("Arial", 25), rowheight=50)

#Create the managerhome frame
manager_home_frame = customtkinter.CTkFrame(app, width=2000, height=1000)
#Create the title label
manager_welcome_label = customtkinter.CTkLabel(manager_home_frame, text="Manager homepage", font=("Arial",30))
#Create access rights label
access_rights_label = customtkinter.CTkLabel(manager_home_frame, text="",font=("Arial",16))

#Create the scroll down label
scroll_down_label = customtkinter.CTkLabel(manager_home_frame, text="", font=("Arial",16))
scroll_down_label.place(relx=.3, rely=.15 ,anchor= 'n')

#Call the login function to initiate the system
Login()

#Run customtkinter
app.mainloop()