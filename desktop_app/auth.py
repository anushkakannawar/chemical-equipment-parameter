import tkinter as tk
from tkinter import messagebox
from api_client import client

class AuthScreen(tk.Frame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.master = master
        self.on_login_success = on_login_success
        self.pack(fill="both", expand=True)
        
        self.create_widgets()

    def create_widgets(self):
        # Center container
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container, text="Chemical Equipment Visualizer", font=("Helvetica", 16, "bold")).pack(pady=20)

        # Username
        tk.Label(container, text="Username").pack(anchor="w")
        self.username_entry = tk.Entry(container, width=30)
        self.username_entry.pack(pady=5)

        # Password
        tk.Label(container, text="Password").pack(anchor="w")
        self.password_entry = tk.Entry(container, show="*", width=30)
        self.password_entry.pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(container)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Login", command=self.login, width=12, bg="#1890ff", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Register", command=self.show_register_window, width=12).pack(side="left", padx=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        success, msg = client.login(username, password)
        if success:
            self.on_login_success()
        else:
            messagebox.showerror("Login Failed", msg)

    def show_register_window(self):
        RegisterWindow(self.master)

class RegisterWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Register")
        self.geometry("300x350")
        
        container = tk.Frame(self, padx=20, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Create Account", font=("Helvetica", 12, "bold")).pack(pady=10)

        tk.Label(container, text="Username").pack(anchor="w")
        self.username_entry = tk.Entry(container)
        self.username_entry.pack(fill="x", pady=5)

        tk.Label(container, text="Email").pack(anchor="w")
        self.email_entry = tk.Entry(container)
        self.email_entry.pack(fill="x", pady=5)

        tk.Label(container, text="Password").pack(anchor="w")
        self.password_entry = tk.Entry(container, show="*")
        self.password_entry.pack(fill="x", pady=5)

        tk.Button(container, text="Register", command=self.register, bg="#1890ff", fg="white").pack(pady=20, fill="x")

    def register(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not username or not password:
             messagebox.showerror("Error", "Username and Password required")
             return

        success, msg = client.register(username, email, password)
        if success:
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.destroy()
        else:
            messagebox.showerror("Registration Failed", msg)
