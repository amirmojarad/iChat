import socket
import threading

from protocol import protocol, parser
from server.viewmodels.users_manager import UsersManager

PORT = 5000


class Server:
    """
        Server Class, Configure all setups of server side application.
    """
    def __init__(self):
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.socket.bind((socket.gethostname(), PORT))
        self.socket.listen(10)
        # new usermanager instance create
        self.users_manager = UsersManager()
        # load data from json file
        self.users_manager.load_from_file()
        # all users that present in group
        self.group_users = []

    def check_type(self, fetched_info, client_socket):
        """
        check type of message (or request) that received from client side.
        check its type and select action to send data to client
        :param fetched_info: more readable data as dict that fetched from raw protocol message
        :param client_socket: socket of that user requested to server
        :return: None
        """
        fetched_type = fetched_info["type"]
        body = fetched_info["body"]
        if fetched_type == "Make":
            self.join_new_member(client_socket=client_socket, body=body)
        elif fetched_type == "Connect":
            self.login(client_socket=client_socket, body=body)
        elif fetched_type == "End":
            self.user_left(client_socket=client_socket, body=body)
            client_socket.detach()
        elif fetched_type == "Search":
            self.search_user(client_socket, body["user"])
        elif fetched_type == "PM":
            self.private_message(body)
        elif fetched_type == "GM":
            self.public_message(body)
        elif fetched_type == "Group":
            self.new_user_join(body)
        elif fetched_type == "Users":
            self.list_of_users(username=body["user"])

    def listen_for_client(self, client_socket, address):
        """
        this function always listen to data that received from client on separate thread
        :param client_socket: socket of client
        :return: None
        """
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message != '':
                    print(message)
                    fetched_info = parser.parse_client_messages(message)
                    if fetched_info is not None:
                        self.check_type(fetched_info, client_socket)
                else:
                    break
            except OSError:
                break
            except Exception as e:
                raise e

    def public_message(self, body):
        """
        for all users that present in group list, send message, except sender username
        :param body: contain information about message and its attributes like length, sender, etc
        :return: None
        """
        for user in self.group_users:
            if user.username != body["from"]:
                user.client_socket.send(
                    protocol.public_message(
                        message=body["message_body"],
                        message_len=body["message_len"],
                        sender_username=body["from"],
                        gname="ichat"
                    ).encode("utf-8")
                )

    def private_message(self, body):
        """
        send private message to receiver. all information fetched from body parameter
        :param body: contain information about message and its attributes like length, sender, etc
        :return: None
        """
        receiver = body["to"]
        message_body = body["message_body"]
        sender = body["from"]
        message_len = body["message_len"]
        # find user by receiver username, and use it client socket. user must be active!
        receiver_user = self.users_manager.search(receiver)
        if receiver_user.client_socket:
            receiver_user.client_socket.send(
                protocol.private_message(
                    message_len=message_len,
                    message=message_body,
                    receiver=receiver,
                    sender=sender).encode('utf-8')
            )

    def search_user(self, client_socket, username):
        """
        search users by username, response and send information to client
        :param client_socket:
        :param username:
        :return:
        """
        user = self.users_manager.search(username)
        if user:
            client_socket.send(protocol.user_found(username).encode('utf-8'))
        else:
            client_socket.send(protocol.user_not_found(username).encode('utf-8'))

    def user_left(self, client_socket, body: dict):
        """
        if user want to leave chat or any unexcepted event
        :param client_socket:
        :param body:
        :return:
        """
        username = body["id"]
        if self.users_manager.remove_user(username):
            client_socket.send(protocol.user_left(username).encode('utf-8'))
            print(f"{username} left the chat.")

    def login(self, client_socket, body: dict):
        """
        get information about user auth and log in user into system
        :param client_socket:
        :param body:
        :return:
        """
        if self.users_manager.login(username=body["user"], password=body["pass"], client_socket=client_socket):
            client_socket.send(protocol.successful_login(id=body["user"]).encode('utf-8'))
        else:
            protocol.login_error(reason="username or password does not match with any of users.")

    def join_new_member(self, client_socket, body: dict):
        """
        create new user with its user auth information
        :param client_socket:
        :param body:
        :return:
        """
        result = self.users_manager.create_user(username=body["user"],
                                                password=body["pass"],
                                                client_socket=client_socket
                                                )
        client_socket.send(result.encode('utf-8'))
        if "accepted" in result.lower():
            client_socket.send(protocol.welcome_message(body["user"]).encode('utf-8'))

    def connect(self):
        """
        always listening to new connection
        :return:
        """
        while True:
            try:
                client_socket, address = self.socket.accept()
                t = threading.Thread(target=self.listen_for_client, args=(client_socket,address))
                t.daemon = True
                t.start()
            except KeyboardInterrupt:
                self.users_manager.save_to_file()
                exit()

    def new_user_join(self, body):
        """
        new user joined to group and response to itself and another users that present in group
        :param body:
        :return:
        """
        fetched_user = self.users_manager.search(username=body["user"])
        for user in self.group_users:
            if fetched_user.username == user.username:
                return
        if fetched_user:
            for user in self.group_users:
                user.client_socket.send(protocol.user_joined(fetched_user.username).encode("utf-8"))
            self.group_users.append(fetched_user)
            fetched_user.client_socket.send(protocol.welcome_message(fetched_user.username).encode("utf-8"))

    def repr_users_in_group_users(self):
        """
        make representative users list
        :return:
        """
        users = ""
        for user in self.group_users:
            users += user.username + "|"
        return users

    def list_of_users(self, username: str):
        """
        send users list to client
        :param username:
        :return:
        """
        user = self.users_manager.search(username)
        if user:
            user.client_socket.send(protocol.users_list(users_repr=self.repr_users_in_group_users()).encode("utf-8"))
