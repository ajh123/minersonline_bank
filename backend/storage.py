import json
from models import *
from typing import List

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
                account.messages.append(Message(from_id=OwnerType("user", user_id), data=message_data))
            self.save_data()

    def get_messages(self, user_id: str) -> List[Message] | None:
        user_accounts = self.find_user_accounts(user_id)
        if user_accounts:
            messages = []
            for account in user_accounts:
                messages.extend([{"owner": message.owner.to_json(), "data": message.data} for message in account.messages])
            return messages
        return None


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
