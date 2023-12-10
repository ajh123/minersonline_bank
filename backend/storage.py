import json
from datetime import datetime
from models import *
from typing import List, Tuple


class DataEngine:
    def __init__(self):
        self.data_model: DataModel = None

    def load_data(self):
        raise NotImplementedError("load_data method must be implemented in the subclass")

    def save_data(self):
        raise NotImplementedError("save_data method must be implemented in the subclass")

    def find_user(self, email: str) -> User | None:
        for user in self.data_model.users:
            if user.email == email:
                return user
        return None

    def find_user_accounts(self, user_id: str) -> List[Account]:
        user_accounts = []
        for bank in self.data_model.banks:
            for account in bank.accounts:
                if account.owner.owner_id == user_id:
                    user_accounts.append(account)
        return user_accounts

    def find_account_by_id(self, account_id: str) -> Account | None:
        for bank in self.data_model.banks:
            for account in bank.accounts:
                if account.account_id == account_id:
                    return account
        return None

    def find_accounts_by_currency(self, user_id: str, currency_id: str) -> List[Account]:
        user_accounts = self.find_user_accounts(user_id)
        return [account for account in user_accounts if any(balance.currency_id == currency_id for balance in account.balance)]

    def find_currency_by_id(self, currency_id: str) -> Currency | None:
        for currency in self.data_model.currencies:
            if currency.currency_id == currency_id:
                return currency
        return None

    def add_message(self, user_id: str, message_data: str):
        user_accounts = self.find_user_accounts(user_id)
        if user_accounts:
            for account in user_accounts:
                account.messages.append(Message(from_id=user_id, data=message_data))
            self.save_data()

    def get_messages(self, user_id: str) -> List[Message] | None:
        user_accounts = self.find_user_accounts(user_id)
        if user_accounts:
            messages = []
            for account in user_accounts:
                messages.extend([{"from": message.from_id, "data": message.data} for message in account.messages])
            return messages
        return None

    def make_transaction(self, from_account_id: str, to_account_id: str, currency_id: str, amount: float) -> Tuple[bool, str]:
        from_account = self.find_account_by_id(from_account_id)
        to_account = self.find_account_by_id(to_account_id)

        if from_account and to_account:
            from_balance = next((balance for balance in from_account.balance if balance.currency_id == currency_id), None)
            to_balance = next((balance for balance in to_account.balance if balance.currency_id == currency_id), None)

            if from_balance and to_balance:
                if from_balance.balance >= amount:
                    from_balance.balance -= amount
                    to_balance.balance += amount

                    # Create transactions
                    from_transaction = Transaction(
                        from_id=from_account_id,
                        to_id=to_account_id,
                        when=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                        currency_id=currency_id,
                        previous_balance=from_balance.balance + amount,
                        new_balance=from_balance.balance
                    )

                    to_transaction = Transaction(
                        from_id=from_account_id,
                        to_id=to_account_id,
                        when=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                        currency_id=currency_id,
                        previous_balance=to_balance.balance - amount,
                        new_balance=to_balance.balance
                    )

                    from_account.transactions.append(from_transaction)
                    to_account.transactions.append(to_transaction)

                    self.save_data()
                    return True, "Transaction successful."
                else:
                    return False, "Insufficient balance."
            else:
                return False, "Invalid balance data."
        else:
            return False, "Invalid account data."


class JsonDataEngine(DataEngine):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def load_data(self):
        with open(self.file_path, "r") as file:
            data = json.load(file)
            self.data_model = DataModel.from_json(data)

    def save_data(self):
        with open(self.file_path, "w") as file:
            json.dump(self.data_model.to_json(), file, indent=4)
            print("Data saved")
