def make_pure(parameter: str):
    return parameter.replace("<", "").replace(">", "").replace("{", "").replace("}", "")


def make_response(message: str, status: int, information_list):
    result = {
        "status": status,
        "message": message
    }
    for info in information_list:
        result[info[0]] = info[1]
    return result


def make_dict_for_messages(message: str):
    parts = message.split("\r\n")
    message_body = parts[1]
    headers = parts[0]
    message_body = message_body.split("<message_body:")[1].split(">")[0]
    info_dict = make_info_dict(headers)
    info_dict["body"]["message_body"] = message_body
    return info_dict


def parse_server_messages(message: str):
    """
        200 : Ok.
        201 : Created
        202 : Accepted
        401 : Unauthorized
        404 : Not Found
    :param message:
    :return:
    """
    raw_message = message
    message = message.lower()
    tokens = message.split()
    information_list = make_dict(tokens)
    if message.startswith("user accepted"):
        return make_response(message="User accepted.", status=201, information_list=information_list)
    elif message.startswith("user not accepted"):
        return make_response(message="User not Accepted.", status=401, information_list=information_list)
    elif message.startswith("connected"):
        return make_response(message="User Signed In Successfully", status=202, information_list=information_list)
    elif message.startswith("error"):
        return make_response("Error", 401, information_list)
    elif message.startswith("user found"):
        return make_response("User found.", 200, information_list)
    elif message.startswith("user not found"):
        return make_response("User not found", 404, information_list)
    elif "join the chat room." in message:
        tokens = message.split()
        return {
            "username": tokens[0],
            "status": 200,
            "message": "New User Joined"
        }
    elif message.startswith("users_list"):
        parts = raw_message.split("\r\n")
        users_list = parts[1].split("|")
        return {
            "status": 200,
            "message": "Users List",
            "users": users_list

        }
    elif message.startswith("pm"):
        info_dic = make_dict_for_messages(raw_message)
        return {
            "status": 200,
            "message": "You have new message!",
            "message_body": info_dic["body"]["message_body"],
            "to": info_dic["body"]["to"],
            "from": info_dic["body"]["from"],
            "message_len": info_dic["body"]["message_len"],
            "type": info_dic["type"]

        }
    elif message.startswith("gm"):
        info_dic = make_dict_for_messages(raw_message)
        return {
            "status": 200,
            "message": "You have a new Group Message!",
            "from": info_dic["body"]["from"],
            "gname": info_dic["body"]["to"],
            "message_len": info_dic["body"]["message_len"],
            "type": info_dic["type"],
            "message_body": info_dic["body"]["message_body"]
        }
    elif message.startswith("hi"):
        return {
            "status": 200,
            "message": "Welcome",
            "username": tokens[1]
        }


def make_info_dict(headers: str):
    tokens = headers.split()
    message_type = tokens[0]
    tokens = [token for token in tokens if token.startswith("<")]
    information_list = []
    for parameter in tokens:
        information_list.append(make_pure(parameter).split(":"))
    information_dict = {"type": message_type, "body": {}}
    for information in information_list:
        information_dict["body"][information[0]] = information[1]
    return information_dict


def make_dict(tokens):
    tokens = [token for token in tokens if token.startswith("<")]
    information_list = []
    for parameter in tokens:
        information_list.append(make_pure(parameter).split(":"))
    return information_list


def parse_client_messages(message: str):
    if "Make" in message or "Connect" in message or "Users" in message or "End" in message or "Group" in message or "Search" in message:
        return make_info_dict(message)
    elif "PM" in message or "GM" in message:
        return make_dict_for_messages(message)
