from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from models import *
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

def save_data():
    # Save DataModel back to JSON
    with open("data.json", "w") as file:
        json.dump(data_model.to_json(), file, indent=4)
        print("Data saved")

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    for account in data_model.accounts:
        if account.authentication:
            for auth in account.authentication:
                if (
                    auth.type == "online_account"
                    and auth.data["username"] == data["username"]
                    and auth.data["password"] == data["password"]
                ):
                    user_id = account.account_id
                    jwt_token = generate_jwt_token(user_id)
                    return jsonify({"message": "Login successful", "jwt_token": jwt_token}), 200

    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/balance")
def view_balance():
    user_id = authenticate_user()
    if user_id:
        current_user = next((account for account in data_model.accounts if account.account_id == user_id), None)
        if current_user:
            balances = [{"currency_id": balance.currency_id, "balance": balance.balance} for balance in current_user.balance]
            return jsonify({"balances": balances})
    return jsonify({"error": "User not authenticated"}), 401

@app.route("/transaction", methods=["POST"])
def make_transaction():
    user_id = authenticate_user()
    if user_id:
        current_user = next((account for account in data_model.accounts if account.account_id == user_id), None)
        if current_user:
            data = request.get_json()

            # Validate currency_id
            currency_id_valid = any(balance.currency_id == data["currency_id"] for balance in current_user.balance)
            if not currency_id_valid:
                return jsonify({"error": "Invalid currency_id"}), 400

            # Validate recipient (to)
            recipient = next((account for account in data_model.accounts if account.account_id == data["to"]), None)
            if not recipient:
                return jsonify({"error": "Invalid recipient (to)"}), 400

            # Check if the user has enough balance
            sender_balance = next((balance for balance in current_user.balance if balance.currency_id == data["currency_id"]), None)
            if not sender_balance or sender_balance.balance < data["amount"]:
                return jsonify({"error": "Insufficient balance"}), 400

            # Calculate new balances
            sender_balance = next((balance for balance in current_user.balance if balance.currency_id == data["currency_id"]), None)
            recipient_balance = next((balance for balance in recipient.balance if balance.currency_id == data["currency_id"]), None)

            if not sender_balance or not recipient_balance:
                return jsonify({"error": "Invalid balance data"}), 500

            new_sender_balance = sender_balance.balance - data["amount"]
            new_recipient_balance = recipient_balance.balance + data["amount"]

            # Update balances
            sender_balance.balance = new_sender_balance
            recipient_balance.balance = new_recipient_balance

            # Create a new Transaction object for the sender
            sender_transaction = Transaction(
                from_id=current_user.account_id,
                to_id=data["to"],
                when=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                currency_id=data["currency_id"],
                previous_balance=sender_balance.balance + data["amount"],
                new_balance=new_sender_balance
            )

            # Create a new Transaction object for the recipient
            recipient_transaction = Transaction(
                from_id=current_user.account_id,
                to_id=data["to"],
                when=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                currency_id=data["currency_id"],
                previous_balance=recipient_balance.balance - data["amount"],
                new_balance=new_recipient_balance
            )

            current_user.transactions.append(sender_transaction)
            recipient.transactions.append(recipient_transaction)
            save_data()

            return jsonify({"message": "Transaction successful"}), 200

    return jsonify({"error": "User not authenticated"}), 401

@app.route("/messages")
def view_messages():
    user_id = authenticate_user()
    if user_id:
        current_user = next((account for account in data_model.accounts if account.account_id == user_id), None)
        if current_user:
            messages = [{"from": message.from_id, "data": message.data} for message in current_user.messages]
            return jsonify({"messages": messages})

    return jsonify({"error": "User not authenticated"}), 401

if __name__ == "__main__":
    app.run(debug=True)
