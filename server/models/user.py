class User:
    def __init__(self, username: str, password: str, _id: str, client_socket):
        self.username = username
        self.password = password
        self.id = _id
        self.client_socket = client_socket

    def __repr__(self):
        return f"username: {self.username} with id: {self.id}"

