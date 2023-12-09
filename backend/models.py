from typing import List, Union

class Balance:
    def __init__(self, currency_id: str, balance: float):
        self.currency_id = currency_id
        self.balance = balance

    @classmethod
    def from_json(cls, data):
        return cls(data["currency_id"], data["balance"])

    def to_json(self):
        return {
            "currency_id": self.currency_id,
            "balance": self.balance
        }

class Message:
    def __init__(self, from_id: str, data: str):
        self.from_id = from_id
        self.data = data

    @classmethod
    def from_json(cls, data):
        return cls(data["from"], data["data"])

    def to_json(self):
        return {
            "from": self.from_id,
            "data": self.data
        }

class Authentication:
    def __init__(self, auth_type: str, data: Union[int, dict, None] = None):
        self.type = auth_type
        self.data = data

    @classmethod
    def from_json(cls, data):
        return cls(data["type"], data.get("data"))

    def to_json(self):
        return {
            "type": self.type,
            "data": self.data
        }

class Currency:
    def __init__(self, currency_id: str, name: str, symbol: str, bank_id: str, created_at: str):
        self.currency_id = currency_id
        self.name = name
        self.symbol = symbol
        self.bank_id = bank_id
        self.created_at = created_at

    @classmethod
    def from_json(cls, data):
        return cls(data["currency_id"], data["name"], data["symbol"], data["bank_id"], data["created_at"])

    def to_json(self):
        return {
            "currency_id": self.currency_id,
            "name": self.name,
            "symbol": self.symbol,
            "bank_id": self.bank_id,
            "created_at": self.created_at
        }

class Transaction:
    def __init__(self, from_id: str, to_id: str, when: str, currency_id: str, previous_balance: float, new_balance: float):
        self.from_id = from_id
        self.to_id = to_id
        self.when = when
        self.currency_id = currency_id
        self.previous_balance = previous_balance
        self.new_balance = new_balance

    @classmethod
    def from_json(cls, data):
        currency_data = data["currency"]
        currency_id = currency_data["currency_id"]
        previous_balance = currency_data["previous_balance"]
        new_balance = currency_data["new_balance"]
        return cls(data["from"], data["to"], data["when"], currency_id, previous_balance, new_balance)

    def to_json(self):
        return {
            "from": self.from_id,
            "to": self.to_id,
            "when": self.when,
            "currency": {
                "currency_id": self.currency_id,
                "previous_balance": self.previous_balance,
                "new_balance": self.new_balance
            }
        }

class Account:
    def __init__(self, account_id: str, bank_id: str, type: str, name: str, created_at: str, balance: List[Balance], messages: List[Message], transactions: List[Transaction], authentication: List[Authentication]):
        self.account_id = account_id
        self.bank_id = bank_id
        self.type = type
        self.name = name
        self.created_at = created_at
        self.balance = balance
        self.messages = messages
        self.transactions = transactions
        self.authentication = authentication

    @classmethod
    def from_json(cls, data):
        balance_data = data["balance"]
        messages_data = data["messages"]
        transactions_data = data["transactions"]
        authentication_data = data["authentication"]

        return cls(
            data["account_id"],
            data["bank_id"],
            data["type_id"],
            data["name"],
            data["created_at"],
            [Balance.from_json(b) for b in balance_data],
            [Message.from_json(m) for m in messages_data],
            [Transaction.from_json(t) for t in transactions_data],
            [Authentication.from_json(a) for a in authentication_data]
        )

    def to_json(self):
        return {
            "account_id": self.account_id,
            "bank_id": self.bank_id,
            "type_id": self.type,
            "name": self.name,
            "created_at": self.created_at,
            "balance": [b.to_json() for b in self.balance],
            "messages": [m.to_json() for m in self.messages],
            "transactions": [t.to_json() for t in self.transactions],
            "authentication": [a.to_json() for a in self.authentication]
        }

class AccountType:
    def __init__(self, type_id: str, name: str, description: str):
        self.type_id = type_id
        self.name = name
        self.description = description

    @classmethod
    def from_json(cls, data):
        return cls(data["type_id"], data["name"], data["description"])

    def to_json(self):
        return {
            "type_id": self.type_id,
            "name": self.name,
            "description": self.description
        }

class BankAdminAuthentication:
    def __init__(self, name: str, created_at: str, username: str, password: str):
        self.name = name
        self.created_at = created_at
        self.username = username
        self.password = password

    @classmethod
    def from_json(cls, data):
        return cls(data["name"], data["created_at"], data["username"], data["password"])

    def to_json(self):
        return {
            "name": self.name,
            "created_at": self.created_at,
            "username": self.username,
            "password": self.password
        }

class Bank:
    def __init__(self, bank_id: str, name: str, bank_type: str, created_at: str, account_types: List[AccountType], admin_authentication: List[BankAdminAuthentication]):
        self.bank_id = bank_id
        self.name = name
        self.bank_type = bank_type
        self.created_at = created_at
        self.account_types = account_types
        self.admin_authentication = admin_authentication

    @classmethod
    def from_json(cls, data):
        account_types_data = data["account_types"]
        admin_authentication_data = data["admin_authentication"]

        return cls(
            data["bank_id"],
            data["name"],
            data["bank_type"],
            data["created_at"],
            [AccountType.from_json(a) for a in account_types_data],
            [BankAdminAuthentication.from_json(a) for a in admin_authentication_data]
        )

    def to_json(self):
        return {
            "bank_id": self.bank_id,
            "name": self.name,
            "bank_type": self.bank_type,
            "created_at": self.created_at,
            "account_types": [a.to_json() for a in self.account_types],
            "admin_authentication": [a.to_json() for a in self.admin_authentication]
        }

class DataModel:
    def __init__(self, accounts: List[Account], currencies: List[Currency], banks: List[Bank]):
        self.accounts = accounts
        self.currencies = currencies
        self.banks = banks

    @classmethod
    def from_json(cls, data):
        accounts_data = data["accounts"]
        currencies_data = data["currencies"]
        banks_data = data["banks"]

        return cls(
            [Account.from_json(a) for a in accounts_data],
            [Currency.from_json(c) for c in currencies_data],
            [Bank.from_json(b) for b in banks_data]
        )

    def to_json(self):
        return {
            "accounts": [a.to_json() for a in self.accounts],
            "currencies": [c.to_json() for c in self.currencies],
            "banks": [b.to_json() for b in self.banks]
        }
