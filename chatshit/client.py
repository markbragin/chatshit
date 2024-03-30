import json
import socket
from threading import Thread
from queue import Queue


MSG_SIZE = 4096


class Client:
    def __init__(self, host: str, port: int, username: str):
        self._host = host
        self._port = port
        self.username = username
        self.message_queue = Queue()

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        timeout = self._sock.gettimeout()
        self._sock.settimeout(5)
        self._sock.connect((self._host, self._port))
        self._sock.settimeout(timeout)

        self.send_msg(self.pack_new_member_msg(self.username))
        self._start_reading()

    def _start_reading(self):
        recv = Thread(target=self._process_msg)
        recv.daemon = True
        recv.start()

    def _process_msg(self) -> None:
        while True:
            msg_len = socket.ntohl(int.from_bytes(self._sock.recv(4)))
            msg = json.loads(self._sock.recv(msg_len).decode())
            self.message_queue.put(msg)

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

    def pack_new_member_msg(self, username: str) -> bytes:
        msg = {
            "Type": "new_member",
            "Username": username,
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
