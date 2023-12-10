import tkinter as tk
from tkinter import ttk
import requests
from ..config import *
from .main import MainFrame

class LoginFrame(ttk.Frame):
    jwt_token = None  # Class variable to store JWT token

    def __init__(self, container):
        super().__init__(container)
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.error_var = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        # Login Frame
        login_frame = ttk.LabelFrame(self, text="Login")

        login_frame.grid_rowconfigure(0, weight=1)
        login_frame.grid_rowconfigure(5, weight=1)
        login_frame.grid_columnconfigure(0, weight=1)
        login_frame.grid_columnconfigure(4, weight=1)

        ttk.Label(login_frame, text="Email:").grid(row=1, column=1, padx=5, pady=5)
        ttk.Entry(login_frame, textvariable=self.email_var).grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(login_frame, text="Password:").grid(row=2, column=1, padx=5, pady=5)
        ttk.Entry(login_frame, textvariable=self.password_var, show="*").grid(row=2, column=2, padx=5, pady=5)

        ttk.Button(login_frame, text="Login", command=self.login).grid(row=3, column=1, columnspan=3, pady=10)
        ttk.Label(login_frame, textvariable=self.error_var).grid(row=4, column=1, columnspan=3, pady=10)
        login_frame.pack(fill="both", expand=1, anchor=tk.CENTER)

    def login(self):
        email = self.email_var.get()
        password = self.password_var.get()
        data = {"email": email, "password": password}

        response = requests.post(f"{BASE_URL}/user/login", json=data)

        if response.status_code == 200:
            LoginFrame.jwt_token = response.json().get("jwt_token")  # Store JWT token in class variable
            self.error_var.set("Login successful.")
            MainFrame.jwt_token = self.jwt_token
            frame = MainFrame(self.master)
            frame.update_balances()
            frame.update_messages()
            self.pack_forget()
            frame.pack(fill="both", expand=1)
        else:
            self.error_var.set("Invalid credentials.")
