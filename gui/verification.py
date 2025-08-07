import string
import random
import customtkinter
from tkinter import messagebox
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

class Verification:
    def __init__(self, app, email):
        self.app = app
        self.email = email
        self.attempts = 0

        self.vc_frame = None
        self.vc_code = None
        self.vc_enter_button = None
        self.back_button = None

    def send_email(self, receiver_address: str, body: str) -> None:
        #SMTP information
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_address = "testeremailforcode@gmail.com"
        
        #Message information passed in the parameters
        message = MIMEText(body)
        message["Subject"] = "Verification code for login"
        message["From"] = sender_address
        message["To"] = receiver_address

        try: #Attempts to send the message to the user
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_address, os.getenv("EMAIL_PASSWORD"))
            server.send_message(message)
            server.quit()
        except: #If no email is sent, an error message is displayed
            messagebox.showerror('Email not sent', 'Time out error')

    def generate_code_and_send_email(self, length: int = 6) -> str:
        # Generate code
        chars = string.ascii_letters + string.digits
        code = ''.join(random.choice(chars) for _ in range(length))
        print("Generated verification code:", code)
        
        body = f"Your verification code is: {code}\n\n[Do not reply to this email]"

        # Send email with code
        send_email(self.email, body)

        return code

    def display(self) -> None:
        self.vc_frame = customtkinter.CTkFrame(self.app, width=2000, height=1000)

        self.vc_code = self.generate_code_and_send_email()

        vc_label = customtkinter.CTkLabel(self.vc_frame, text="Verification code", font=("Arial", 30))
        vc_label.place(relx=.5, rely=.15, anchor=customtkinter.CENTER)
        vc1_label = customtkinter.CTkLabel(self.vc_frame, text="A verification code was sent to your email. Enter below.", font=("Arial", 16))
        vc1_label.place(relx=.5, rely=.3, anchor=customtkinter.CENTER)

        vc_input = customtkinter.CTkEntry(self.vc_frame, placeholder_text="Enter verification code...", width=250, font=("Arial", 16))
        vc_input.place(relx=.5, rely=.4, anchor=customtkinter.CENTER)

        def on_enter():
            correct_code = self.check_code(vc_input.get())
            if correct_code:
                self.vc_frame.destroy()

                if login_type == "admin" and admin_homepage_callback:
                    admin_homepage_callback()
                elif login_type == "manager" and manager_homepage_callback:
                    manager_homepage_callback()
                else:
                    # fallback if no callbacks provided
                    print("No valid homepage callback provided")

        self.vc_enter_button = customtkinter.CTkButton(
            self.vc_frame, text="Enter", height=35, width=30, corner_radius=20, font=("Arial", 16), command=on_enter
        )
        self.vc_enter_button.place(relx=.5, rely=.7, anchor=customtkinter.CENTER)

        self.back_button = customtkinter.CTkButton(
            self.vc_frame, text="Back to Login", height=35, width=30, corner_radius=20, font=("Arial", 16),
            command=lambda: [self.vc_frame.destroy(), self.login_callback()]
        )
        self.back_button.place(relx=.5, rely=.9, anchor=customtkinter.CENTER)

        self.vc_frame.pack(fill="both", expand=1)

    def check_code(self, vc_code_inputted):
        if vc_code_inputted == "":
            messagebox.showerror('Invalid entry', 'Please enter in the verification code.')
            return

        if vc_code_inputted == self.vc_code:
            print("Successful verification code")
            return True
        else:
            print("Wrong verification code")
            self.attempts += 1
            if self.attempts < 3:
                self.vc_frame.destroy()
                messagebox.showerror('Wrong verification code', f'Please log in again. You have {3 - self.attempts} attempt(s) left.')
                self.login_callback()
            else:
                self.vc_enter_button.configure(text='Limit reached. Try again in 24hrs.')
                self.back_button.configure(text='Close application', command=self.app.destroy)
                if wait_callback:
                    wait_callback()
        return False