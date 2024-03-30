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
            raw_len = self._sock.recv(4)
            header_len = socket.ntohl(int.from_bytes(raw_len))
            header = json.loads(self._sock.recv(header_len).decode())
            if header["Type"] == "text":
                self._read_text_msg(header["Length"])
            elif header["Type"] == "new_member":
                self._read_new_member_msg(header["Length"])
            elif header["Type"] == "left_chat":
                self._read_left_chat_msg(header["Length"])

    def _read_text_msg(self, length: int) -> None:
        text = self._sock.recv(length).decode()
        self.text_message_queue.put(text)

    def _read_new_member_msg(self, length: int):
        nickname = self._sock.recv(length).decode().strip()

    def _read_left_chat_msg(self, length: int):
        nickname = self._sock.recv(length).decode().strip()

    def send_msg(self, msg: bytes):
        try:
            self._sock.sendall(msg)
        except BrokenPipeError:
            self.close()

    def pack_text_msg(self, text: str) -> bytes:
        encoded_text = text.encode()
        text_len = len(encoded_text)
        header = {
            "Type": "text",
            "Length": text_len,
        }
        encoded_header = json.dumps(header).encode()
        header_len = socket.htonl(len(encoded_header)).to_bytes(4)
        return header_len + encoded_header + encoded_text

    def pack_new_member_msg(self, nickname: str) -> bytes:
        encoded_text = nickname.encode()
        text_len = len(encoded_text)
        header = {
            "Type": "new_member",
            "Length": text_len,
        }
        encoded_header = json.dumps(header).encode()
        header_len = socket.htonl(len(encoded_header)).to_bytes(4)
        return header_len + encoded_header + encoded_text

    def __enter__(self):
        return self

    def __exit__(self):
        self._sock.close()

    def close(self):
        self._sock.close()
