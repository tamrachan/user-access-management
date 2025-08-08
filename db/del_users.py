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