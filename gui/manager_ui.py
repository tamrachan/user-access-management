import customtkinter
from tkinter import ttk, messagebox
from db import (
    get_user_project_codes,
    get_project_id_from_code,
    get_overview_projects,
    get_approver_name,
    get_approver_list,
    get_status_list,
    get_permission_list,
    update_missing_approver_names,
    update_missing_status_and_access,
)

class ManagerHomepage:
    def __init__(self, app, email):
        self.app = app
        self.email = email

        self.manager_home_frame = None
        self.overview_tree = None
        self.permission_tree = None
        self.edit_permissions_button = None
        self.scroll_down_label = None

        self.show_homepage()

    def show_homepage(self):
        self.manager_home_frame = customtkinter.CTkFrame(self.app, width=1000, height=800)
        self.manager_home_frame.pack(fill="both", expand=True)

        title_label = customtkinter.CTkLabel(self.manager_home_frame, text="Welcome, Manager", font=("Arial", 24))
        title_label.pack(pady=20)

        project_codes = get_user_project_codes(self.email)
        project_codes.insert(0, "Overview")

        project_var = customtkinter.StringVar()
        project_dropdown = customtkinter.CTkComboBox(
            self.manager_home_frame, values=project_codes, state="readonly", variable=project_var, width=200
        )
        project_dropdown.set("Select Project")
        project_dropdown.pack(pady=10)

        def show_project_data():
            selected = project_var.get()
            for widget in self.manager_home_frame.winfo_children():
                if isinstance(widget, ttk.Treeview) or isinstance(widget, customtkinter.CTkButton) or isinstance(widget, customtkinter.CTkLabel):
                    if widget not in [title_label, project_dropdown, go_button, logout_button]:
                        widget.destroy()

            if selected == "Overview":
                self.display_overview()
            elif selected != "Select Project":
                project_id = get_project_id_from_code(selected)
                if project_id:
                    self.display_permissions(project_id)
                else:
                    messagebox.showerror("Error", "Project ID not found.")
            else:
                messagebox.showinfo("Info", "Please select a project.")

        go_button = customtkinter.CTkButton(self.manager_home_frame, text="Go", command=show_project_data)
        go_button.pack(pady=10)

        logout_button = customtkinter.CTkButton(
            self.manager_home_frame, text="Log out", fg_color="transparent", border_width=2,
            border_color="#315184", command=lambda: [self.manager_home_frame.destroy()]
        )
        logout_button.pack(pady=30)

    def display_overview(self):
        self.overview_tree = ttk.Treeview(self.manager_home_frame, columns=("c1", "c2", "c3"), show='headings', height=14)
        self.overview_tree.column("#1", anchor=customtkinter.CENTER, width=500)
        self.overview_tree.heading("#1", text="Project code")
        self.overview_tree.column("#2", anchor=customtkinter.CENTER, width=300)
        self.overview_tree.heading("#2", text="Project name")
        self.overview_tree.column("#3", anchor=customtkinter.CENTER, width=400)
        self.overview_tree.heading("#3", text="Approver")
        self.overview_tree.place(relx=.5, rely=.4, anchor=customtkinter.CENTER)

        values = get_overview_projects()
        for num, row in enumerate(values):
            self.overview_tree.insert('', 'end', text=num, values=(row[0], row[1], row[2]))

    def display_permissions(self, db_project_id):
        if self.permission_tree:
            self.permission_tree.destroy()
        if self.edit_permissions_button:
            self.edit_permissions_button.destroy()
        if self.scroll_down_label:
            self.scroll_down_label.destroy()

        self.permission_tree = ttk.Treeview(self.manager_home_frame, columns=(
            "Employee", "Permission", "Reason", "Manager/Approver", "Approval Status", "Expiry date"),
            show='headings', height=15)

        col_cfg = [
            ("#1", 300, "Employee"),
            ("#2", 200, "Permission"),
            ("#3", 500, "Reason"),
            ("#4", 300, "Manager/Approver"),
            ("#5", 300, "Approval Status"),
            ("#6", 200, "Expiry date"),
        ]

        for col, width, heading in col_cfg:
            self.permission_tree.column(col, anchor=customtkinter.CENTER, width=width)
            self.permission_tree.heading(col, text=heading)

        approver = get_approver_name(db_project_id)
        approver_list = get_approver_list(db_project_id)

        if not approver_list or approver_list[0][0] is None:
            update_missing_approver_names(approver, db_project_id)

        status_list = get_status_list(db_project_id)
        update_missing_status_and_access(status_list, db_project_id)

        permission_list = get_permission_list(db_project_id)
        permission_list.sort()

        self.scroll_down_label = customtkinter.CTkLabel(self.manager_home_frame, text="")
        self.scroll_down_label.place(relx=.5, rely=.85, anchor=customtkinter.CENTER)

        if len(permission_list) > 15:
            self.scroll_down_label.configure(text="Please scroll down to view all records.")
        else:
            self.scroll_down_label.configure(text="")

        self.permission_tree.tag_configure('incomplete', background="red")

        for num, row in enumerate(permission_list, 1):
            if row[4] == "Please complete" or row[2] == "":
                self.permission_tree.insert('', 'end', iid=num, values=row, tags=('incomplete',))
            else:
                self.permission_tree.insert('', 'end', iid=num, values=row)

        self.permission_tree.place(relx=.5, rely=.2, anchor='n')

        self.edit_permissions_button = customtkinter.CTkButton(
            self.manager_home_frame, text="Edit permissions", font=("Arial", 16),
            command=lambda: self.edit_permissions(db_project_id)
        )
        self.edit_permissions_button.place(relx=.85, rely=.9, anchor=customtkinter.CENTER)

    def edit_permissions(self, project_id):
        messagebox.showinfo("Edit Permissions", f"Edit permissions for project ID: {project_id}")
