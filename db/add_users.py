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
