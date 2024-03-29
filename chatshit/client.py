import socket
from threading import Thread
from queue import Queue


MSG_SIZE = 4096


class Client:
    def __init__(self, host: str, port: int, nickname: str):
        self._host = host
        self._port = port
        self._nickname = nickname
        self.message_queue = Queue()

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        timeout = self._sock.gettimeout()
        self._sock.settimeout(5)
        self._sock.connect((self._host, self._port))
        self._sock.settimeout(timeout)

        self.send(self._nickname)
        self._start_reading()

    def _start_reading(self):
        recv = Thread(target=self._recv)
        recv.daemon = True
        recv.start()

    def send(self, msg: str):
        self._sock.sendall(self._pack_msg(msg))

    def _pack_msg(self, msg: str) -> bytes:
        encoded_msg = msg.encode()
        msg_len = len(encoded_msg)
        return socket.htonl(msg_len).to_bytes(4) + encoded_msg

    def __enter__(self):
        return self

    def __exit__(self):
        self._sock.close()

    def _recv(self):
        while True:
            try:
                msg = self._read_msg()
                if not msg:
                    self.close()
                    break
                self.message_queue.put(msg)
            except:
                self.close()
                break

    def _read_msg(self) -> str:
        raw_len = self._sock.recv(4)
        if not raw_len:
            return ""

        msg_len = socket.ntohl(int.from_bytes(raw_len))
        msg = self._sock.recv(msg_len)
        return msg.decode()

    def close(self):
        self._sock.close()
