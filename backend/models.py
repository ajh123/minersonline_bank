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
    

class OwnerType:
    def __init__(self, owner_type: str, owner_id: str):
        self.type = owner_type
        self.owner_id = owner_id

    @classmethod
    def from_json(cls, data):
        return cls(data.get("type", ""), data.get("owner_id", ""))

    def to_json(self):
        return {
            "type": self.type,
            "owner_id": self.owner_id
        }


class Message:
    def __init__(self, owner: OwnerType, data: str):
        self.owner = owner
        self.data = data

    @classmethod
    def from_json(cls, data):
        return cls(OwnerType.from_json(data.get("from", {})), data["data"])

    def to_json(self):
        return {
            "owner": self.owner.to_json(),
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
    def __init__(self, currency_id: str, name: str, code: str, symbol: str, bank_id: str, created_at: str):
        self.currency_id = currency_id
        self.name = name
        self.code = code
        self.symbol = symbol
        self.bank_id = bank_id
        self.created_at = created_at

    @classmethod
    def from_json(cls, data):
        return cls(data["currency_id"], data["name"], data["code"], data["symbol"], data["bank_id"], data["created_at"])

    def to_json(self):
        return {
            "currency_id": self.currency_id,
            "name": self.name,
            "code": self.code,
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
        currency_data = data.get("currency", {})
        currency_id = currency_data.get("currency_id", "")
        previous_balance = currency_data.get("previous_balance", 0)
        new_balance = currency_data.get("new_balance", 0)
        return cls(data.get("from", ""), data.get("to", ""), data.get("when", ""), currency_id, previous_balance, new_balance)

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


class User:
    def __init__(self, user_id: str, name: str, email: str, password: str, created_at: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.created_at = created_at

    @classmethod
    def from_json(cls, data):
        return cls(data["user_id"], data["name"], data["email"], data["password"], data["created_at"])

    def to_json(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at
        }


class BankAdminAuthentication:
    def __init__(self, user_id: str, permissions: List[str]):
        self.user_id = user_id
        self.permissions = permissions

    @classmethod
    def from_json(cls, data):
        return cls(data.get("user_id", ""), data.get("permissions", []))

    def to_json(self):
        return {
            "user_id": self.user_id,
            "permissions": self.permissions
        }


class Account:
    def __init__(self, account_id: str, bank_id: str, type_id: str, owner: OwnerType, created_at: str, balance: List[Balance], messages: List[Message], transactions: List[Transaction], authentication: List[Authentication]):
        self.account_id = account_id
        self.bank_id = bank_id
        self.type_id = type_id
        self.owner = owner
        self.created_at = created_at
        self.balance = balance
        self.messages = messages
        self.transactions = transactions
        self.authentication = authentication

    @classmethod
    def from_json(cls, data):
        balance_data = data.get("balance", [])
        messages_data = data.get("messages", [])
        transactions_data = data.get("transactions", [])
        authentication_data = data.get("authentication", [])

        if authentication_data == None:
            authentication_data = []

        return cls(
            data.get("account_id", ""),
            data.get("bank_id", ""),
            data.get("type_id", ""),
            OwnerType.from_json(data.get("owner", {})),
            data.get("created_at", ""),
            [Balance.from_json(b) for b in balance_data],
            [Message.from_json(m) for m in messages_data],
            [Transaction.from_json(t) for t in transactions_data],
            [Authentication.from_json(a) for a in authentication_data]
        )

    def to_json(self):
        return {
            "account_id": self.account_id,
            "bank_id": self.bank_id,
            "type_id": self.type_id,
            "owner": self.owner.to_json(),
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
        return cls(data.get("type_id", ""), data.get("name", ""), data.get("description", ""))

    def to_json(self):
        return {
            "type_id": self.type_id,
            "name": self.name,
            "description": self.description
        }


class Bank:
    def __init__(self, bank_id: str, name: str, bank_type: str, created_at: str, account_types: List[AccountType], admin_authentication: List[BankAdminAuthentication], accounts: List[Account]):
        self.bank_id = bank_id
        self.name = name
        self.bank_type = bank_type
        self.created_at = created_at
        self.account_types = account_types
        self.admin_authentication = admin_authentication
        self.accounts = accounts

    @classmethod
    def from_json(cls, data):
        account_types_data = data.get("account_types", [])
        admin_authentication_data = data.get("admin_authentication", [])
        accounts_data = data.get("accounts", [])

        return cls(
            data.get("bank_id", ""),
            data.get("name", ""),
            data.get("bank_type", ""),
            data.get("created_at", ""),
            [AccountType.from_json(a) for a in account_types_data],
            [BankAdminAuthentication.from_json(a) for a in admin_authentication_data],
            [Account.from_json(a) for a in accounts_data]
        )

    def to_json(self):
        return {
            "bank_id": self.bank_id,
            "name": self.name,
            "bank_type": self.bank_type,
            "created_at": self.created_at,
            "account_types": [a.to_json() for a in self.account_types],
            "admin_authentication": [a.to_json() for a in self.admin_authentication],
            "accounts": [a.to_json() for a in self.accounts]
        }


class DataModel:
    def __init__(self, currencies: List[Currency], users: List[User], banks: List[Bank]):
        self.currencies = currencies
        self.users = users
        self.banks = banks

    @classmethod
    def from_json(cls, data):
        currencies_data = data.get("currencies", [])
        users_data = data.get("users", [])
        banks_data = data.get("banks", [])

        return cls(
            [Currency.from_json(c) for c in currencies_data],
            [User.from_json(u) for u in users_data],
            [Bank.from_json(b) for b in banks_data]
        )

    def to_json(self):
        return {
            "currencies": [c.to_json() for c in self.currencies],
            "users": [u.to_json() for u in self.users],
            "banks": [b.to_json() for b in self.banks]
        }
