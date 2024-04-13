import socket
from threading import Thread
from queue import Queue

import chatshit.network.proto as proto


class Client:
    def __init__(self, host: str, port: int, username: str):
        self.host = host
        self.port = port
        self.username = username
        self.message_queue = Queue()

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        timeout = self._sock.gettimeout()
        self._sock.settimeout(5)
        self._sock.connect((self.host, self.port))
        self._sock.settimeout(timeout)

        self.send_msg(proto.pack_join_chat_msg(self.username))
        self._start_reading()

    def _start_reading(self):
        recv = Thread(target=self._process_msg)
        recv.daemon = True
        recv.start()

    def _process_msg(self):
        while True:
            try:
                msg_len = socket.ntohl(int.from_bytes(self._sock.recv(4)))
                data = self._sock.recv(msg_len)
                msg = proto.decode_msg(data)
                self.message_queue.put(msg)
            except:
                self.close()

    def send_msg(self, msg: bytes):
        try:
            self._sock.sendall(msg)
        except (BrokenPipeError, OSError):
            self.close()

    def __enter__(self):
        return self

    def __exit__(self):
        self._sock.close()

    def close(self):
        self._sock.close()
