import socket
import selectors
from threading import Thread


HOST = ""
PORT = 5432
MSG_SIZE = 4096


class ChatServer:
    def __init__(self, host:str, port:int):
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv_sock.bind((host, port))

        self.sel = selectors.DefaultSelector()
        self.sel.register(self.serv_sock, selectors.EVENT_READ,
                          self._get_connection)

        self.users: list[socket.socket] = []
        self.nicknames: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self):
        self.serv_sock.close()

    def _get_connection(self, sock: socket.socket):
        conn_t = Thread(target=self._get_conn, args=(sock,))
        conn_t.daemon = True
        conn_t.start()

    def _get_conn(self, sock: socket.socket):
        sock, addr = self._accept(sock)
        nickname = self._get_nickname(sock)
        if nickname:
            self.sel.register(sock, selectors.EVENT_READ, self._handle)
            self.users.append(sock)
            self.nicknames.append(nickname)
            self.broadcast(self.serv_sock, f"{nickname} joined the chat")
        else:
            self.remove(sock)

    def _accept(self, sock:socket.socket):
        sock, addr = sock.accept()
        print(f"{addr} connected")
        return (sock, addr)

    def _get_nickname(self, sock: socket.socket) -> str | None:
        try:
            msg = sock.recv(MSG_SIZE)
            if not msg:
                print(f"{sock.getpeername()} closed connection")
            else:
                return msg.decode().strip()
        except:
            print(f"Error getting nickname from {sock.getpeername()}")
        return None

    def _handle(self, sock: socket.socket):
        try:
            msg = sock.recv(MSG_SIZE)
            if not msg:
                print(f"{sock.getpeername()} closed connection")
                msg = f"{self._get_nickname_by_sock(sock)} left the chat"
                self.broadcast(self.serv_sock, msg)
                self.remove(sock)
            else:
                self.broadcast(sock, msg.decode())
        except:
            print(f"Error occured while reading {sock.getpeername()}")
            msg = f"{self._get_nickname_by_sock(sock)} left the server"
            self.broadcast(self.serv_sock, msg)
            self.remove(sock)

    def _get_nickname_by_sock(self, sock: socket.socket) -> str | None:
        try:
            nick = self.nicknames[self.users.index(sock)]
        except:
            nick = None
        return nick

    def remove(self, sock: socket.socket):
        try:
            self.sel.unregister(sock)
            self.nicknames.pop(self.users.index(sock))
            self.users.remove(sock)
        except (KeyError, ValueError):
            return
        sock.close()

    def send(self, src_sock: socket.socket, dest_sock: socket.socket, msg: str):
        if src_sock is self.serv_sock:
            nickname = "<Server>"
        else:
            nickname = self.nicknames[self.users.index(src_sock)]
        msg_encoded = f"{nickname}:⠀{msg}".encode()
        try:
            dest_sock.send(msg_encoded)
        except:
            print(f"Error occured while reading {dest_sock.getpeername()}")
            self.remove(dest_sock)

    def broadcast(self, sender_sock: socket.socket, msg: str):
        for user in self.users:
            self.send(sender_sock, user, msg)

    def run_server(self):
        self.serv_sock.listen()
        print("Waiting for connections...")
        while True:
            to_read = self.sel.select()
            for key, _ in to_read:
                callback = key.data
                callback(key.fileobj)

    def shutdown(self):
        self.broadcast(self.serv_sock, "Server shutdown")
        for sock in self.users:
            self.remove(sock)
        self.serv_sock.close()


if __name__ == "__main__":
    server = ChatServer(HOST, PORT)
    try:
        server.run_server()
    except KeyboardInterrupt:
        server.shutdown()
        print("Shutdown")
