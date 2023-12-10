from datetime import datetime, timedelta
from typing import List
from flask import Flask, request, jsonify
from models import DataModel, Transaction, Account, Balance
import json
import jwt

app = Flask(__name__)

# Secret key for JWT, change this to a strong secret in production
JWT_SECRET_KEY = "your_jwt_secret_key"

data_model: DataModel = None
with open("data.json") as file:
    data = json.load(file)
    data_model = DataModel.from_json(data)

def generate_jwt_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=1)  # Token expiration time
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    return token

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

def authenticate_user():
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split("Bearer ")[1]
        user_id = verify_jwt_token(token)
        return user_id
    return None

def find_user_accounts(user_id) -> List[Account]:
    user_accounts = []
    for bank in data_model.banks:
        for account in bank.accounts:
            if account.owner.owner_id == user_id:
                user_accounts.append(account)
    return user_accounts

def find_user_account(user_id, account_id):
    for bank in data_model.banks:
        for account in bank.accounts:
            if account.owner.owner_id == user_id and account.account_id == account_id:
                return account
    return None

def save_data():
    # Save DataModel back to JSON
    with open("data.json", "w") as file:
        json.dump(data_model.to_json(), file, indent=4)
        print("Data saved")

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    for user in data_model.users:
        if user.email == data["email"] and user.password == data["password"]:
            user_id = user.user_id
            jwt_token = generate_jwt_token(user_id)
            return jsonify({"message": "Login successful", "jwt_token": jwt_token}), 200

    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/balance")
def view_balance():
    user_id = authenticate_user()
    if user_id:
        user_accounts = find_user_accounts(user_id)
        if user_accounts:
            balances = []
            for account in user_accounts:
                balances.extend([{"account_id": account.account_id, "currency_id": balance.currency_id, "balance": balance.balance} for balance in account.balance])
            return jsonify({"balances": balances})
    return jsonify({"error": "User not authenticated"}), 401


# ...

@app.route("/transaction", methods=["POST"])
def make_transaction():
    user_id = authenticate_user()
    if user_id:
        data = request.get_json()

        # Validate sender and recipient accounts
        sender_account = find_user_account(user_id, data["from"])
        recipient_account = find_user_account(user_id, data["to"])

        if not sender_account or not recipient_account:
            return jsonify({"error": "Invalid sender or recipient account"}), 400

        # Validate ownership of the sender account
        if sender_account.owner.owner_id != user_id:
            return jsonify({"error": "User does not own the specified sender account"}), 401

        # Validate specified currency in sender and recipient accounts
        sender_currency = data.get("currency")
        recipient_currency = sender_currency  # Assuming the same currency for simplicity

        if not sender_currency or not recipient_currency:
            return jsonify({"error": "Invalid or missing currency"}), 400

        # Validate if both accounts can have the chosen currency
        if not any(balance.currency_id == sender_currency for balance in sender_account.balance) or \
           not any(balance.currency_id == recipient_currency for balance in recipient_account.balance):
            return jsonify({"error": "Invalid currency for sender or recipient account"}), 400

        # Validate if the user has enough balance in the sender account
        sender_balance = next((balance.balance for balance in sender_account.balance if balance.currency_id == sender_currency), None)
        if not sender_balance or sender_balance < data["amount"]:
            return jsonify({"error": "Insufficient balance in the sender account"}), 400

        # Calculate new balances
        new_sender_balance = sender_balance - data["amount"]
        recipient_balance = next((balance.balance for balance in recipient_account.balance if balance.currency_id == recipient_currency), None)
        if not recipient_balance:
            return jsonify({"error": "Invalid recipient balance data"}), 500

        new_recipient_balance = recipient_balance + data["amount"]

        # Update balances
        sender_account.balance = [Balance(currency_id=sender_currency, balance=new_sender_balance)]
        recipient_account.balance = [Balance(currency_id=recipient_currency, balance=new_recipient_balance)]

        # Create a new Transaction object for the sender
        sender_transaction = Transaction(
            from_id=sender_account.account_id,
            to_id=recipient_account.account_id,
            when=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            currency_id=sender_currency,
            previous_balance=sender_balance + data["amount"],
            new_balance=new_sender_balance
        )

        # Create a new Transaction object for the recipient
        recipient_transaction = Transaction(
            from_id=sender_account.account_id,
            to_id=recipient_account.account_id,
            when=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            currency_id=recipient_currency,
            previous_balance=recipient_balance - data["amount"],
            new_balance=new_recipient_balance
        )

        sender_account.transactions.append(sender_transaction)
        recipient_account.transactions.append(recipient_transaction)
        save_data()

        return jsonify({"message": "Transaction successful"}), 200

    return jsonify({"error": "User not authenticated"}), 401


@app.route("/messages")
def view_messages():
    user_id = authenticate_user()
    if user_id:
        user_accounts = find_user_accounts(user_id)
        messages = []

        for account in user_accounts:
            messages.extend([{"from": message.from_id, "data": message.data} for message in account.messages])

        return jsonify({"messages": messages})

    return jsonify({"error": "User not authenticated"}), 401

if __name__ == "__main__":
    app.run(debug=True)
