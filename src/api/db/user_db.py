#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
from src.api.db.database import Database
from src.api.models import User


class UserDB(Database):
    def __init__(self, config):
        super().__init__(config)
        self.user_collection = self.database.get_collection("users")

    def get_user_by_id(self, user_id):
        """
        Get user by id
        :param user_id: user id
        :return: user
        """
        db_item = self.user_collection.find_one({"_id": user_id})
        if db_item is None:
            return None
        return User.from_db_item(db_item)

    def get_user_by_username(self, username):
        """
        Get user by username
        :param username: username
        :return: user
        """
        db_item = self.user_collection.find_one({"username": username})
        if db_item is None:
            return None
        return User.from_db_item(db_item)

    def get_user_by_email(self, username):
        """
        Get user by email
        :param username: email
        :return: user
        """
        db_item = self.user_collection.find_one({"email": username})
        if db_item is None:
            return None
        return User.from_db_item(db_item)

    def add_user(self, user):
        """
        Add user
        :param user: user
        :return: user
        """
        return self.user_collection.insert_one(user.dict())

    def update_user(self, user):
        """
        Update user
        :param user: user
        :return: user
        """
        return self.user_collection.update_one({"_id": user.id}, {"$set": user.dict()})

    def get_all_users(self):
        """
        Get all users
        :return: users
        """
        return self.user_collection.find()

    def delete_user(self, user):
        """
        Delete user
        :param user: username
        :return: user
        """
        return self.user_collection.delete_one({"username": user.username})
