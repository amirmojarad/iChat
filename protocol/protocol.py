def make(username: str, password: str):
    return f"Make -Option <user:{username}> -Option <pass:{password}> -Option <id:{username}>"


def join_request(username: str):
    return f"Group -Option <user:{username}> -Option <gname:ichat>"


def list_of_users(username: str):
    return f"Users -Option <user:{username}>"


def users_list(users_repr: str):
    return f"USERS_LIST:\r\n{users_repr}"


def user_joined(username: str):
    return f"{username} join the chat room."


def user_accepted(id: str):
    return f"User Accepted -Option <id:{id}>"


def user_not_accepted(reason: str):
    return f"User Not Accepted -Option <reason:{reason}>"


def welcome_message(username: str):
    return f"Hi {username} , welcome to iChat!"


def successful_login(id: str):
    return f"Connected -Option <id:{id}>"


def login_error(reason: str):
    return f"ERROR -Option <reason:{reason}>"


def login(username: str, password: str):
    return f"Connect -Option <user:{username}> -Option <pass:{password}>"


def user_not_found(username: str):
    return f"User not found -Option <user:{username}>"


def user_found(username: str):
    return f"User found -Option <user:{username}>"


def search_user(username: str):
    return f"Search -Option <user:{username}>"


def private_message(message_len: int, receiver: str, sender: str, message: str):
    return f"PM -Option <message_len:{message_len}> -Option <from:{sender}> -Option <to:{receiver}>\r\n-Option <message_body:{message}>"


def public_message(gname: str, message_len: int, message: str, sender_username: str):
    return f"GM -Option <to:{gname}> -Option <from:{sender_username}> -Option <message_len:{message_len}>\r\n-Option <message_body:{message}>"


def end(username: str, group_name: str):
    return f"End -Option <id:{username} OR {group_name}>"


def user_left(username: str):
    return f"{username} left the chat room"


def left(_id: str):
    return f"End -Option <id:{_id}>"
