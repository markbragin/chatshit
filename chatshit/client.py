import socket 
from threading import Thread
from queue import Queue


HOST = "localhost"
PORT = 1234
MSG_SIZE = 4096


class Client:
    def __init__(
            self,
            host: str = "localhost",
            port: int = 1234,
            nickname="Unknown"
    ):
        self.set_address(host, port)
        self.nickname = nickname
        self.message_queue = Queue()
        self.connection_closed = True

    def set_address(self, host: str, port: int):
        self.host = host
        self.port = port

    def set_nickname(self, nickname: str):
        self.nickname = nickname

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.connection_closed = False
        # try:
        #     self.sock.connect((self.host, self.port))
        # except socket.gaierror:
        #     print("Wrong address")
        # except ConnectionRefusedError:
        #     print("Connection refused")
        self.send(self.nickname)
        self._start_reading()

    def _start_reading(self):
        recv = Thread(target=self._recv)
        recv.daemon = True
        recv.start()

    def send(self, msg: str):
        if not self.connection_closed:
            self.sock.send(msg.encode())

    def __enter__(self):
        return self

    def __exit__(self):
        self.sock.close()

    def _recv(self):
        while True:
            try:
                msg = self.sock.recv(MSG_SIZE)
                if not msg:
                    self.close()
                    break
                self.message_queue.put(msg.decode())
            except:
                self.close()
                break

    def close(self):
        self.sock.close()
        self.connection_closed = True


if __name__ == "__main__":
    client = Client(HOST, PORT)
    try:
        client.connect()
        while True:
            msg = input()
            if msg:
                client.send(msg)
    except KeyboardInterrupt:
        client.send("")
    except OSError:
        pass

