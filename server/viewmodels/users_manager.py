from typing import List

from client.clinet import pwd_context
from protocol import protocol
from server.models.user import User
from server.viewmodels import json_management


def username_is_valid(username: str):
    return len(username) >= 6


def password_is_valid(password: str):
    return len(password) >= 6


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


class UsersManager:
    def __init__(self) -> None:
        self.active_users: List[User] = []
        self.users: List[User] = []

    def create_user(self, username: str, password: str, client_socket):
        """
        if username and password is valid, check user exists or not
        else
        create new user and append it to active users and users list
        :param username:
        :param password:
        :param client_socket:
        :return:
        """
        if not username_is_valid(username):
            return protocol.user_not_accepted(f"username is invalid: {username}")
        if not password_is_valid(password):
            return protocol.user_not_accepted(f"password is invalid")
        if self.user_already_exist(username):
            return protocol.user_not_accepted(f"user with this username: {username} is already exist.")
        new_user = User(username=username, _id=username, password=password, client_socket=client_socket)
        self.active_users.append(new_user)
        self.users.append(User(username=new_user.username, client_socket=None, password=new_user.password,
                               _id=new_user.id))
        return protocol.user_accepted(id=username)

    def search(self, username: str):
        """
        search for user with {username} as a parameter
        :param username:
        :return:
        """
        active_user = self.find_active_user(username)
        if active_user:
            return active_user
        de_active_user = self.find_de_active_user(username)
        if de_active_user:
            return de_active_user
        return None

    def find_de_active_user(self, username: str):
        """

        :param username:
        :return:
        """
        for user in self.users:
            if user.username == username:
                return user
        return None

    def find_active_user(self, username: str):
        """
        really you need more information? :_)
        :param username:
        :return:
        """
        for user in self.active_users:
            if user.username == username:
                return user
        return None

    def login(self, username: str, password: str, client_socket):
        """
        get a client_socket and assign it to offline user
        then user with client socket will add to active users
        :param username:
        :param password:
        :param client_socket:
        :return:
        """
        for user in self.users:
            if user.username == username and verify_password(hashed_password=user.password, plain_password=password):
                user.client_socket = client_socket
                self.active_users.append(user)
                return True
        return False

    def remove_user(self, username: str):
        """
        get a username and return True if user exists and removed,
        return False if not deleted
        :param username:
        :return:
        """
        user = self.find_active_user(username)
        if user is not None:
            self.active_users.remove(user)
            return True
        return False

    def load_from_file(self):
        """
        load and fetch users' information from json file
        :return:
        """
        information = json_management.load()
        for data in information:
            user = User(username=data["username"], password=data["password"], client_socket=None, _id=data["username"])
            self.users.append(user)

    def save_to_file(self):
        """
        save all users' data in json file
        :return:
        """
        information = []
        json_management.save(information)
        for user in self.users:
            information.append({"username": user.username, "password": user.password})
        json_management.save(information)

    def user_already_exist(self, username: str):
        """
        check user with passed username exists or not
        :param username:
        :return: True if exists, False if not
        """
        for user in self.users:
            if user.username == username:
                return True
        return False
