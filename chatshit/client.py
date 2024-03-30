import json
import socket
from threading import Thread
from queue import Queue


MSG_SIZE = 4096


class Client:
    def __init__(self, host: str, port: int, nickname: str):
        self._host = host
        self._port = port
        self._nickname = nickname
        self.text_message_queue = Queue()

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        timeout = self._sock.gettimeout()
        self._sock.settimeout(5)
        self._sock.connect((self._host, self._port))
        self._sock.settimeout(timeout)

        self.send_msg(self.pack_new_member_msg(self._nickname))
        self._start_reading()

    def _start_reading(self):
        recv = Thread(target=self._process_msg)
        recv.daemon = True
        recv.start()

    def _process_msg(self) -> None:
        while True:
            msg_len = socket.ntohl(int.from_bytes(self._sock.recv(4)))
            msg = json.loads(self._sock.recv(msg_len).decode())
            if msg["Type"] == "text":
                self._read_text_msg(msg)
            elif msg["Type"] == "new_member":
                self._read_new_member_msg(msg)
            elif msg["Type"] == "left_chat":
                self._read_left_chat_msg(msg)

    def _read_text_msg(self, msg: dict) -> None:
        self.text_message_queue.put(msg["Text"])

    def _read_new_member_msg(self, msg: dict):
        pass

    def _read_left_chat_msg(self, msg: dict):
        pass

    def send_msg(self, msg: bytes):
        try:
            self._sock.sendall(msg)
        except BrokenPipeError:
            self.close()

    def pack_text_msg(self, text: str) -> bytes:
        msg = {
            "Type": "text",
            "Text": text,
        }
        encoded_msg = json.dumps(msg).encode()
        msg_len = socket.htonl(len(encoded_msg)).to_bytes(4)
        return msg_len + encoded_msg

    def pack_new_member_msg(self, nickname: str) -> bytes:
        msg = {
            "Type": "new_member",
            "Nickname": nickname,
        }
        encoded_msg = json.dumps(msg).encode()
        msg_len = socket.htonl(len(encoded_msg)).to_bytes(4)
        return msg_len + encoded_msg

    def __enter__(self):
        return self

    def __exit__(self):
        self._sock.close()

    def close(self):
        self._sock.close()
