import json
import socket


"""
Text message {
    "Type": "text",
    "Id": int,
    "Text": str
}

Join chat {
    "Type": "join_chat",
    "Username": str
}

Left chat {
    "Type": "left_chat",
    "Username": str
}

Unique username {
    "Type": "unique_username":
    "Username": str
}

Delete message {
    "Type": "delete_message",
    "Id": int
}
"""


class WrongFormat(Exception):
    def __init__(self, msg=""):
        super().__init__(msg)


def decode_msg(data: bytes) -> dict:
    try:
        msg: dict = json.loads(data.decode())
    except json.JSONDecodeError:
        raise WrongFormat("Message format doesn't comply with protocol std")

    if not "Type" in msg:
        raise WrongFormat("Missing 'Type' field")

    msg_type = msg["Type"]
    if msg_type == "text":
        if not "Id" in msg:
            raise WrongFormat(f"Missing 'Id' field with type: {msg_type}")
        if not "Text" in msg:
            raise WrongFormat(f"Missing 'Text' field with type: {msg_type}")
    elif msg_type in ("join_chat", "left_chat", "unique_username"):
        if not "Username" in msg:
            raise WrongFormat(f"Missing 'Username' field with type: {msg_type}")
    elif msg_type == 'delete_message':
        if not "Id" in msg:
            raise WrongFormat(f"Missing 'Id' field with type: {msg_type}")

    return msg


def pack(msg: dict) -> bytes:
    encoded_msg = json.dumps(msg).encode()
    msg_len = socket.htonl(len(encoded_msg)).to_bytes(4)
    return msg_len + encoded_msg


def pack_text_msg(text: str, msg_id: int = -1) -> bytes:
    msg = {
        "Type": "text",
        "Id": msg_id,
        "Text": text,
    }
    return pack(msg)


def pack_join_chat_msg(username: str) -> bytes:
    msg = {
        "Type": "join_chat",
        "Username": username,
    }
    return pack(msg)


def pack_left_chat_msg(username: str) -> bytes:
    msg = {
        "Type": "left_chat",
        "Username": username,
    }
    return pack(msg)


def pack_unique_username(username: str) -> bytes:
    msg = {
        "Type": "unique_username",
        "Username": username,
    }
    return pack(msg)


def pack_delete_message(msg_id: int) -> bytes:
    msg = {
        "Type": "delete_message",
        "Id": msg_id,
    }
    return pack(msg)
