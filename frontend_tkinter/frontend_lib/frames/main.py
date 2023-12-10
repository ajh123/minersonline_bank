import tkinter as tk
from tkinter import ttk
import requests
from ..config import *

class MainFrame(ttk.Frame):
    jwt_token = None  # Class variable to store JWT token

    def __init__(self, container):
        super().__init__(container)
        self.amount_var = tk.StringVar()
        self.to_var = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        # Transaction Frame
        transaction_frame = ttk.LabelFrame(self, text="Transaction")
        transaction_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(transaction_frame, text="To Account:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(transaction_frame, textvariable=self.to_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(transaction_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(transaction_frame, textvariable=self.amount_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(transaction_frame, text="Make Transaction", command=self.make_transaction).grid(row=2, column=0, columnspan=2, pady=10)

        # Balances Frame
        balances_frame = ttk.LabelFrame(self, text="Balances")
        balances_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        self.balances_listbox = tk.Listbox(balances_frame, width=30, height=5)
        self.balances_listbox.grid(row=0, column=0, padx=5, pady=5)

        # Messages Frame
        messages_frame = ttk.LabelFrame(self, text="Messages")
        messages_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.messages_listbox = tk.Listbox(messages_frame, width=60, height=10)
        self.messages_listbox.grid(row=0, column=0, padx=5, pady=5)

    def make_transaction(self):
        if not MainFrame.jwt_token:
            self.update_messages("User not logged in.")
            return

        to_account = self.to_var.get()
        amount = float(self.amount_var.get())
        currency_id = tk.simpledialog.askstring("Currency", "Enter Currency ID:")
        data = {"to": to_account, "amount": amount, "currency_id": currency_id}

        headers = {"Authorization": f"Bearer {MainFrame.jwt_token}"}
        response = requests.post(f"{BASE_URL}/transaction", json=data, headers=headers)

        if response.status_code == 200:
            self.update_balances()
            self.update_messages("Transaction successful.")
        else:
            self.update_messages("Transaction failed.")

    def update_balances(self):
        if not MainFrame.jwt_token:
            self.update_messages("User not logged in.")
            return

        headers = {"Authorization": f"Bearer {MainFrame.jwt_token}"}
        response = requests.get(f"{BASE_URL}/balance", headers=headers)

        if response.status_code == 200:
            balances = response.json().get("balances", [])
            self.balances_listbox.delete(0, tk.END)

            for balance in balances:
                self.balances_listbox.insert(tk.END, f"{balance['currency_id']}: {balance['balance']}")

    def update_messages(self, message):
        self.messages_listbox.insert(tk.END, message)

    def update_messages(self):
        if not MainFrame.jwt_token:
            self.messages_listbox.insert(tk.END, "User not logged in.")
            return

        headers = {"Authorization": f"Bearer {MainFrame.jwt_token}"}
        response = requests.get(f"{BASE_URL}/messages", headers=headers)

        if response.status_code == 200:
            messages = response.json().get("messages", [])
            self.messages_listbox.delete(0, tk.END)

            for message in messages:
                self.messages_listbox.insert(tk.END, f"{message['from']}: {message['data']}")
        else:
            self.messages_listbox.insert(tk.END, "Failed to retrieve messages.")
