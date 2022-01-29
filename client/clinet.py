import socket
import threading
import time
from os import system, name
from protocol import protocol, parser

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password, hashed_password):
    """
    get plain password and hashed password and with pwd_context verify it
    :param plain_password:
    :param hashed_password:
    :return:
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_hash_password(plain_password):
    """
    get plain password and hash it with pwd context lib
    :param plain_password:
    :return:
    """
    return pwd_context.hash(plain_password)


def wait_and_clear():
    """
    clear terminal
    :return:
    """
    if name == 'nt':
        _ = system('cls')

    else:
        _ = system('clear')
    time.sleep(1)


def auth_menu():
    print("* * * * * * * * * * * * * * Authentication * * * * * * * * * * * * * *")
    print("1. Sign Up")
    print("2. Sign In")
    print("3. Exit")
    return int(input("Enter Your Request:\n"))


def group_menu():
    print("* * * * * * * * * * * * * * Menu * * * * * * * * * * * * * *")
    print("1. Send Message to Group")
    print("2. Users List")
    print("3. back")
    option = int(input("Enter Your Request:\n"))
    return option


def menu():
    print("* * * * * * * * * * * * * * Menu * * * * * * * * * * * * * *")
    print("1. Public Message")
    print("2. Private Message")
    print("3. Search User")
    print("4. Leave")
    option = int(input("Enter Your Request:\n"))
    return option


class Clinet:
    def __init__(self):
        self.username = ""
        self.password = ""
        self.sckt: socket = None
        self._id = ""
        self.auth_key = False

    def leave(self):
        """
        left chat room and send to server leave request
        :return:
        """
        self.sckt.send(protocol.left(self.username).encode('utf-8'))
        self.sckt.close()
        exit(1)

    def listen_for_message(self):
        """
        listen to messages and responses from server
        :return:
        """
        while True:
            try:
                msg = self.sckt.recv(1024).decode('utf-8')
                # parse received message and generate more flexible data as dict structure
                """
                this structure is common between all of them
                {
                    "status": int,
                    "message": str,    
                }
                status codes:
                    its like http response codes.
                    200, 201, 202, 401, 404, ...
                """
                result = parser.parse_server_messages(msg)
                status = result["status"]
                message = result["message"].lower()
                if status == 201 or status == 202:
                    # user signed up or logged in successfully
                    # print message and turn auth key to True!
                    print(message)
                    self.auth_key = True
                elif status == 401:
                    # auth problem! turn auth key to False
                    print(message)
                    self.auth_key = False
                elif status == 200 and "user found" in message:
                    searched_username = result["user"]
                    print(f"user with {searched_username} found.")
                elif status == 404 and "user not found" in message:
                    searched_username = result["user"]
                    print(f"user with {searched_username} not found.")
                elif status == 200 and "you have new message!" in message:
                    message_body = result["message_body"]
                    sender = result["from"]
                    print(f"a new message from {sender}:\r\n{message_body}")
                elif status == 200 and "you have a new group message!" in message:
                    message_body = result["message_body"]
                    sender = result["from"]
                    gname = result["gname"]
                    print(f"a new message from {gname} Group!\r\n{sender}: {message_body}")
                elif status == 200 and "users list" in message:
                    users = result["users"]
                    print(f"Users in Group: {users}")
                elif status == 200 and "new user joined" in message:
                    username = result["username"]
                    print(f"{username} joined the ChatRoom.")
                elif status == 200 and "welcome" in message:
                    username = result["username"]
                    print(f"Hi {username}, Welcome to iChat Group!")
            except Exception as ex:
                self.leave()
                print(ex)
                break

    def search_user(self):
        receiver = input("Enter Receiver Username:\n")
        self.sckt.send(protocol.search_user(receiver).encode('utf-8'))

    def public_message(self):
        # first send a join request to server
        self.sckt.send(protocol.join_request(username=self.username).encode("utf-8"))
        while True:
            option = group_menu()
            if option == 1:
                message = input("Enter your message:\n")
                self.sckt.send(
                    protocol.public_message(
                        message=message,
                        message_len=len(message.encode('utf-8')),
                        sender_username=self.username, gname="ichat"
                    ).encode("utf-8")
                )
            elif option == 2:
                self.sckt.send(protocol.list_of_users(self.username).encode("utf-8"))
            elif option == 3:
                break

    def send_private_message(self):
        receiver = input("Enter Receiver Username:\n")
        message = input("Enter your message:\n")
        self.sckt.send(protocol.private_message(
            message=message,
            receiver=receiver,
            sender=self.username,
            message_len=len(message.encode('utf-8'))).encode('utf-8')
                       )

    def auth_operation(self, option):
        if option == 1:
            self.username = input("username: \n")
            self.password = input("password: \n")
            self.password = generate_hash_password(self.password)
            self.sckt.send(protocol.make(self.username, self.password).encode('utf-8'))
        elif option == 2:
            self.username = input("username: \n")
            self.password = input("password: \n")
            self.sckt.send(protocol.login(self.username, self.password).encode('utf-8'))
        elif option == 3:
            self.leave()

    def connect(self):
        try:
            self.sckt = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self.sckt.connect((socket.gethostname(), 5000))
            t = threading.Thread(target=self.listen_for_message, args=())
            t.daemon = True
            option = auth_menu()
            self.auth_operation(option)
            t.start()
            wait_and_clear()
            while True:
                print(self.auth_key)
                if self.auth_key:
                    option = menu()
                    if option == 1:
                        self.public_message()
                    elif option == 2:
                        self.send_private_message()
                    elif option == 3:
                        self.search_user()
                    elif option == 4:
                        self.leave()
                        exit(1)
                else:
                    option = auth_menu()
                    self.auth_operation(option)
        except KeyboardInterrupt:
            self.leave()
            exit(1)
