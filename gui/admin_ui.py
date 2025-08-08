import customtkinter
from tkinter import messagebox, simpledialog
# from utils import GetCSVFile, GetProjectCSV, GetUserList
# from utils.auth import reset_password_to_default

class AdminHomepage:
    def __init__(self, app, email):
        self.app = app
        self.email = email
        self.admin_frame = None

        self.show_homepage()

    def show_homepage(self):
        self.admin_frame = customtkinter.CTkFrame(self.app, width=1000, height=800)
        self.admin_frame.pack(fill="both", expand=True)

        #Create the title label
        admin_welcome_label = customtkinter.CTkLabel(self.admin_frame, text="Admin homepage", font=("Arial",30))
        admin_welcome_label.place(relx=.5, rely=.15,anchor= customtkinter.CENTER)

        #Create menu buttons for the CSV functions
        csv_label = customtkinter.CTkLabel(self.admin_frame, text="CSV:", font=("Arial",16))
        csv_label.place(relx=.55, rely=.25,anchor='w')
        upload_csv_button = customtkinter.CTkButton(self.admin_frame, text="Upload CSV", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184",font=("Arial",16), command=UploadCSVFile)
        upload_csv_button.place(relx=.55, rely=.3,anchor= 'w')
        edit_csv_button = customtkinter.CTkButton(self.admin_frame, text="Edit CSV", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184", font=("Arial",16), command=lambda: [EditCSVFile(), admin_home_frame.destroy()])
        edit_csv_button.place(relx=.55, rely=.4,anchor= 'w')
        del_csv_button = customtkinter.CTkButton(self.admin_frame, text="Delete users from CSV file", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184", font=("Arial",16), command=lambda: [DeleteUser(), admin_home_frame.destroy()])
        del_csv_button.place(relx=.55, rely=.5,anchor= 'w')
        #Create menu buttons for the linking CSV to database functions
        csv_to_db_label = customtkinter.CTkLabel(self.admin_frame, text="CSV to database:", font=("Arial",16))
        csv_to_db_label.place(relx=.55, rely=.6,anchor='w')
        add_project_name_button = customtkinter.CTkButton(self.admin_frame, text="Add project name", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184", font=("Arial",16), command=lambda: [AddProjectName(), admin_home_frame.destroy()])
        add_project_name_button.place(relx=.55, rely=.65,anchor= 'w')
        assign_project_manager_button = customtkinter.CTkButton(self.admin_frame, text="Assign project approver", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184", font=("Arial",16), command=lambda: [AssignProjectManager(), admin_home_frame.destroy()])
        assign_project_manager_button.place(relx=.55, rely=.75,anchor= 'w')
        change_project_manager_button = customtkinter.CTkButton(self.admin_frame, text="Change project approver", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184", font=("Arial",16), command=lambda: [ChangeProjectManager(), admin_home_frame.destroy()])
        change_project_manager_button.place(relx=.55, rely=.85,anchor= 'w')
        #Create menu buttons for the database functions
        db_label = customtkinter.CTkLabel(self.admin_frame, text="DB:", font=("Arial",16))
        db_label.place(relx=.35, rely=.25,anchor='w')
        reset_password_button = customtkinter.CTkButton(self.admin_frame, text="Reset password", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184", font=("Arial",16), command=lambda: [ResetPassword(""), admin_home_frame.destroy()])
        reset_password_button.place(relx=.35, rely=.3,anchor= 'w')
        add_users_button = customtkinter.CTkButton(self.admin_frame, text="Add users", font=("Arial",16), height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184", command=lambda: [AddUser(), admin_home_frame.destroy()])
        add_users_button.place(relx=.35, rely=.4,anchor= 'w')
        del_users_button = customtkinter.CTkButton(self.admin_frame, text="Delete users", height=45, width=30, corner_radius=20, fg_color="transparent", border_width=2, border_color="#315184", font=("Arial",16), command=lambda: [DeleteAccount(), admin_home_frame.destroy()])
        del_users_button.place(relx=.35, rely=.5,anchor= 'w')

        self.admin_frame.pack()

    def open_upload_csv(self):
        try:
            csv_list = GetCSVFile()
            messagebox.showinfo("Upload CSV", f"Loaded {len(csv_list)} entries from latest CSV.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {e}")

    def open_edit_csv(self):
        try:
            projects = GetProjectCSV(GetCSVFile())
            project_str = "\n".join(projects)
            messagebox.showinfo("Edit CSV - Projects", f"Projects:\n{project_str}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get projects: {e}")

    def open_delete_user(self):
        try:
            users = GetUserList()
            user_str = "\n".join(users)
            messagebox.showinfo("Delete User - User List", f"Users:\n{user_str}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get user list: {e}")

    def open_add_project_name(self):
        project_name = simpledialog.askstring("Add Project Name", "Enter new project name:")
        if project_name:
            messagebox.showinfo("Add Project Name", f"Project '{project_name}' would be added (TODO).")

    def open_assign_manager(self):
        messagebox.showinfo("Assign Manager", "Assign Manager screen coming soon.")

    def open_change_manager(self):
        messagebox.showinfo("Change Manager", "Change Manager screen coming soon.")

    # def open_reset_passwords(self):
    #     if reset_password_to_default(self.email):
    #         messagebox.showinfo("Success", "Your password has been reset to default.")
    #     else:
    #         messagebox.showerror("Failure", "Failed to reset password.")

if __name__ == "__init__":
    email = "test@gmail.com"
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

    homepage = AdminHomepage(app, email)

    app.mainloop()