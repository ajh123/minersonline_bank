import tkinter as tk
from tkinter import ttk
import requests

BASE_URL = "http://127.0.0.1:5000"

class SimpleBankApp:
    jwt_token = None  # Class variable to store JWT token

    def __init__(self, root):
        self.root = root
        self.root.title("Simple Bank App")

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.to_var = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Login Frame
        login_frame = ttk.LabelFrame(self.root, text="Login")
        login_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(login_frame, textvariable=self.username_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(login_frame, textvariable=self.password_var, show="*").grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(login_frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)

        # Transaction Frame
        transaction_frame = ttk.LabelFrame(self.root, text="Transaction")
        transaction_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(transaction_frame, text="To Account:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(transaction_frame, textvariable=self.to_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(transaction_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(transaction_frame, textvariable=self.amount_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(transaction_frame, text="Make Transaction", command=self.make_transaction).grid(row=2, column=0, columnspan=2, pady=10)

        # Balances Frame
        balances_frame = ttk.LabelFrame(self.root, text="Balances")
        balances_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        self.balances_listbox = tk.Listbox(balances_frame, width=30, height=5)
        self.balances_listbox.grid(row=0, column=0, padx=5, pady=5)

        # Messages Frame
        messages_frame = ttk.LabelFrame(self.root, text="Messages")
        messages_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.messages_listbox = tk.Listbox(messages_frame, width=60, height=10)
        self.messages_listbox.grid(row=0, column=0, padx=5, pady=5)

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        data = {"username": username, "password": password}

        response = requests.post(f"{BASE_URL}/login", json=data)

        if response.status_code == 200:
            SimpleBankApp.jwt_token = response.json().get("jwt_token")  # Store JWT token in class variable
            self.update_balances()
            self.update_messages("Login successful.")
        else:
            self.update_messages("Invalid credentials.")

    def make_transaction(self):
        if not SimpleBankApp.jwt_token:
            self.update_messages("User not logged in.")
            return

        to_account = self.to_var.get()
        amount = float(self.amount_var.get())
        data = {"to": to_account, "amount": amount, "currency_id": "c686341a-c073-4174-bbec-7df211ed07fc"}

        headers = {"Authorization": f"Bearer {SimpleBankApp.jwt_token}"}
        response = requests.post(f"{BASE_URL}/transaction", json=data, headers=headers)

        if response.status_code == 200:
            self.update_balances()
            self.update_messages("Transaction successful.")
        else:
            self.update_messages("Transaction failed.")

    def update_balances(self):
        if not SimpleBankApp.jwt_token:
            self.update_messages("User not logged in.")
            return

        headers = {"Authorization": f"Bearer {SimpleBankApp.jwt_token}"}
        response = requests.get(f"{BASE_URL}/balance", headers=headers)

        if response.status_code == 200:
            balances = response.json().get("balances", [])
            self.balances_listbox.delete(0, tk.END)

            for balance in balances:
                self.balances_listbox.insert(tk.END, f"{balance['currency_id']}: {balance['balance']}")

    def update_messages(self, message):
        self.messages_listbox.insert(tk.END, message)


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleBankApp(root)
    root.mainloop()
