from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from models import *
from storage import JsonDataEngine
import jwt

app = Flask(__name__)

# Secret key for JWT, change this to a strong secret in production
JWT_SECRET_KEY = "your_jwt_secret_key"

# Instantiate JsonDataEngine with the file path
data_engine = JsonDataEngine(file_path="data.json")

# Load data from the file
data_engine.load_data()

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

@app.route("/info/banks", methods=["POST"])
def banks():
    banksL = data_engine.find_banks()
    return jsonify({"banks": banksL}), 401

@app.route("/info/currencies", methods=["POST"])
def currencies():
    currenciesL = data_engine.find_currencies()
    return jsonify({"currencies": currenciesL}), 401

@app.route("/user/login", methods=["POST"])
def login():
    data = request.get_json()

    user = data_engine.find_user(email=data["email"])
    if user and data["password"] == user.password:
        user_id = user.user_id
        jwt_token = generate_jwt_token(user_id)
        return jsonify({"message": "Login successful", "jwt_token": jwt_token}), 200

    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/user/balance")
def view_balance():
    user_id = authenticate_user()
    if user_id:
        user_accounts = data_engine.find_user_accounts(user_id)
        if user_accounts:
            balances = []
            for account in user_accounts:
                balances.extend([{"account_id": account.account_id, "currency_id": balance.currency_id, "balance": balance.balance} for balance in account.balance])
            return jsonify({"balances": balances})
    return jsonify({"error": "User not authenticated"}), 401

@app.route("/user/transaction", methods=["POST"])
def make_transaction():
    user_id = authenticate_user()
    if user_id:
        data = request.get_json()

        # Validate sender and recipient accounts
        sender_account: Account = data_engine.find_account_by_id(user_id, data["from"])
        recipient_account: Account = data_engine.find_account_by_id(user_id, data["to"])

        if not sender_account or not recipient_account:
            return jsonify({"error": "Invalid sender or recipient account"}), 400

        # Validate ownership of the sender account
        if sender_account.owner.owner_id != user_id:
            return jsonify({"error": "User does not own the specified sender account"}), 401

        # Validate specified currency in sender and recipient accounts
        currency = data.get("currency")

        if not data_engine.find_currency_by_id(currency):
            return jsonify({"error": "Invalid or missing currency"}), 400

        # Validate if both accounts can have the chosen currency
        if not any(balance.currency_id == currency for balance in sender_account.balance) or \
           not any(balance.currency_id == currency for balance in recipient_account.balance):
            return jsonify({"error": "Invalid currency for sender or recipient account"}), 400

        # Validate if the user has enough balance in the sender account
        sender_balance = next((balance.balance for balance in sender_account.balance if balance.currency_id == currency), None)
        if not sender_balance or sender_balance < data["amount"]:
            return jsonify({"error": "Insufficient balance in the sender account"}), 400

        # Calculate new balances
        new_sender_balance = sender_balance - data["amount"]
        recipient_balance = next((balance.balance for balance in recipient_account.balance if balance.currency_id == currency), None)
        if not recipient_balance:
            return jsonify({"error": "Invalid recipient balance data"}), 500

        new_recipient_balance = recipient_balance + data["amount"]

        # Update balances
        sender_account.balance = [Balance(currency_id=currency, balance=new_sender_balance)]
        recipient_account.balance = [Balance(currency_id=currency, balance=new_recipient_balance)]

        # Create a new Transaction object for the sender
        sender_transaction = Transaction(
            from_id=sender_account.account_id,
            to_id=recipient_account.account_id,
            when=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            currency_id=currency,
            previous_balance=sender_balance + data["amount"],
            new_balance=new_sender_balance
        )

        # Create a new Transaction object for the recipient
        recipient_transaction = Transaction(
            from_id=sender_account.account_id,
            to_id=recipient_account.account_id,
            when=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            currency_id=currency,
            previous_balance=recipient_balance - data["amount"],
            new_balance=new_recipient_balance
        )

        sender_account.transactions.append(sender_transaction)
        recipient_account.transactions.append(recipient_transaction)
        data_engine.save_data()

        return jsonify({"message": "Transaction successful"}), 200

    return jsonify({"error": "User not authenticated"}), 401

@app.route("/user/messages")
def view_messages():
    user_id = authenticate_user()
    if user_id:
        messages = data_engine.get_messages(user_id)
        return jsonify({"messages": messages})

    return jsonify({"error": "User not authenticated"}), 401

if __name__ == "__main__":
    app.run(debug=True)
