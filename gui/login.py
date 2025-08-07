import customtkinter
from tkinter import messagebox
import mysql.connector
from config.db_config import DB_CONFIG
import hashlib
from .verification import Verification

class LoginPage:
    def __init__(self, app):
        self.app = app
        self.attempts = 0
        self.login_frame = None
        self.login_button = None
        self.email_input = None
        self.password_input = None
        
        # Connect to MySQL
        db = mysql.connector.connect(**DB_CONFIG)
        self.c = db.cursor()

        self.c.execute("SELECT * FROM UserData")
        self.login_list = self.c.fetchall()

        # self.login_list = [
        #     {"email": "test", "password": "123", "type": "admin"},
        #     {"email": "user", "password": "abc", "type": "user"},
        # ]

        self.setup_login_ui()

    def setup_login_ui(self):
        self.login_frame = customtkinter.CTkFrame(self.app, width=2000, height=1000)

        login_label = customtkinter.CTkLabel(self.login_frame, text="User Access Management Login", font=("Arial",30))
        login_label.place(relx=.5, rely=.15, anchor=customtkinter.CENTER)

        self.email_input = customtkinter.CTkEntry(self.login_frame, placeholder_text="Email", font=("Arial",18), width=280)
        self.email_input.place(relx=.5, rely=.3, anchor=customtkinter.CENTER)

        self.password_input = customtkinter.CTkEntry(self.login_frame, placeholder_text="Password", font=("Arial",18), width=280, show="*")
        self.password_input.place(relx=.5, rely=.4, anchor=customtkinter.CENTER)

        self.login_button = customtkinter.CTkButton(
            self.login_frame, 
            text="Login", 
            height=35, 
            width=30, 
            corner_radius=20, 
            font=("Arial",18), 
            command=self.login_check
        )
        self.login_button.place(relx=.5, rely=.5, anchor=customtkinter.CENTER)

        self.login_frame.pack()

    def decrypt_password(email, password) -> bool:
        self.c.execute("SELECT password, salt FROM UserData WHERE email = %s",(email,))
        password_list = c.fetchone()
        password, salt = password_list[0], password_list[1]

        #Get hash equivalent of the password entered
        hash_object = hashlib.sha256((password_entered + salt).encode())
        hashed_password_entered = hash_object.hexdigest()

        if password == hashed_password_entered:
            return True
        else:
            return False

    def login_check(self):
        username = self.email_input.get()
        password = self.password_input.get()

        if not username or not password:
            messagebox.showerror('Invalid login', 'Ensure there are no blank entries.')
            return

        if self.attempts >= 5:
            self.login_button.configure(text="Limit reached. Try again in 24hrs.")
            messagebox.showerror('Locked Out', 'Too many failed attempts. Please try again later.')
            return

        user_found = False
        password_correct = False
        user_email = None
        for user in self.login_list:
            if user["email"] == username:
                user_found = True
                user_email = user["email"]
                password_correct = decrypt_password(user["email"], user["password"])
                break

        if user_found and user_email and password_correct:
            messagebox.showinfo('Success', 'Login successful!')
            self.attempts = 0  # reset on success
            # Proceed to verification code, next page, etc.
            verification = Verification(self.app, user_email)
            verification.display()
        else:
            self.attempts += 1
            attempts_left = 5 - self.attempts
            self.login_button.configure(text=f"Try again ({attempts_left} attempts left)")
            messagebox.showerror('Failed', 'Email or password is incorrect.')
