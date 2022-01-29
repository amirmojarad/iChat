import json

__PATH = "res/users.json"


def save(data: list):
    """
    save data as list to json file
    :param data:
    :return:
    """
    with open(__PATH, 'w') as f:
        json.dump(data, f, indent=4)


def clear():
    """ save empty list to json file """
    save([])


def load() -> dict:
    """
    open json file and loads it then returns it
    :return:
    """
    f = open(__PATH)
    data = json.load(f)
    print(data)
    f.close()
    return data
