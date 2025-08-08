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