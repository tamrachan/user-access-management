import customtkinter
from tkinter import ttk

from gui import *

def main():
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("blue")

    app = customtkinter.CTk()
    app.title("User Access Management System")
    app.geometry("600x600")
    # app.iconbitmap('icon/Cartesian.ico')
    app._state_before_windows_set_titlebar_color = 'zoomed'

    #Style the system
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Arial",25))
    style.configure("Treeview", font=("Arial", 25), rowheight=50)

    login_app = LoginPage(app)

    app.mainloop()

if __name__ == "__main__":
    main()