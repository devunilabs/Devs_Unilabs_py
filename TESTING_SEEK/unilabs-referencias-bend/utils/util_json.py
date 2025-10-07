import json


def is_json(data):
    try:
        json_object = json.loads(data.text)
    except ValueError as e:
        return False
    return True

