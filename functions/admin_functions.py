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