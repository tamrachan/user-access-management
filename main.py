import customtkinter
from tkinter import ttk

from gui import LoginPage

def main():
    app = customtkinter.CTk()
    app.title("User Access Management System")
    app.geometry("600x600")
    app._state_before_windows_set_titlebar_color = 'zoomed'

    #Set the login count and attempts to 0
    count = 0
    attempts = 0

    #Style the system
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Arial",25))
    style.configure("Treeview", font=("Arial", 25), rowheight=50)

    login_app = LoginPage(app)

    app.mainloop()

if __name__ == "__main__":
    main()