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
        return self.user_collection.find_one({"_id": user_id})

    def get_user_by_username(self, username):
        """
        Get user by username
        :param username: username
        :return: user
        """
        return User.from_db_item(self.user_collection.find_one({"username": username}))

    def get_user_by_email(self, username):
        """
        Get user by email
        :param username: email
        :return: user
        """
        return User.from_db_item(self.user_collection.find_one({"email": username}))

    def add_user(self, user):
        """
        Add user
        :param user: user
        :return: user
        """
        return self.user_collection.insert_one(user.dict())
