import socket
import selectors
import time
from threading import Thread


MSG_SIZE = 4096
SERVER_NAME = "[SERVER]"


class ChatServer:
    def __init__(self, host: str, port: int):
        self._serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._serversock.bind((host, port))

        self._selector = selectors.DefaultSelector()
        self._selector.register(
            self._serversock,
            selectors.EVENT_READ,
            self._get_new_connection,
            # self._listen_to_new_connections,
        )

        self._users: list[socket.socket] = []
        self._nicknames: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self):
        self._serversock.close()

    # def _listen_to_new_connections(self, sock: socket.socket):
    #     conn_t = Thread(target=self._get_new_connection, args=(sock,))
    #     conn_t.daemon = True
    #     conn_t.start()

    def _get_new_connection(self, sock: socket.socket):
        sock, addr = sock.accept()
        nickname = self._get_nickname(sock)
        if nickname:
            nickname = self._generate_unique_nickname(nickname)
            self._selector.register(
                sock, selectors.EVENT_READ, self._handle_new_message
            )
            self._users.append(sock)
            self._nicknames.append(nickname)

            self.broadcast(self._serversock, f"{nickname} joined the chat")
            print(f"{nickname}: {sock.getpeername()} connected")
        else:
            self.remove(sock)

    def _get_nickname(self, sock: socket.socket) -> str | None:
        try:
            msg = self._read_msg(sock)
            if not msg:
                print(f"{sock.getpeername()} closed connection")
            else:
                return msg.strip()
        except:
            print(f"Error getting nickname from {sock.getpeername()}")
        return None

    def _generate_unique_nickname(self, nickname: str) -> str:
        if nickname in self._nicknames:
            i = 1
            while nickname + str(i) in self._nicknames:
                i += 1
            nickname = nickname + str(i)
        return nickname if nickname != SERVER_NAME else "NOT a " + nickname

    def _read_msg(self, sock: socket.socket) -> str:
        raw_len = sock.recv(4)
        if not raw_len:
            return ""

        msg_len = socket.ntohl(int.from_bytes(raw_len))
        msg = sock.recv(msg_len)
        return msg.decode()

    def _handle_new_message(self, sock: socket.socket):
        try:
            msg = self._read_msg(sock)
            if not msg:
                print(f"{sock.getpeername()} closed connection")
                msg = f"{self._get_nickname_by_sock(sock)} left the chat"
                self.broadcast(self._serversock, msg)
                self.remove(sock)
            else:
                self.broadcast(sock, msg)
        except:
            print(f"Error occured while reading {sock.getpeername()}")
            msg = f"{self._get_nickname_by_sock(sock)} left the server"
            self.broadcast(self._serversock, msg)
            self.remove(sock)

    def _get_nickname_by_sock(self, sock: socket.socket) -> str | None:
        try:
            nick = self._nicknames[self._users.index(sock)]
        except:
            nick = None
        return nick

    def remove(self, sock: socket.socket):
        try:
            self._selector.unregister(sock)
            self._nicknames.pop(self._users.index(sock))
            self._users.remove(sock)
            sock.close()
        except (KeyError, ValueError):
            return

    def send(
        self, src_sock: socket.socket, dest_sock: socket.socket, msg: str
    ):
        if src_sock is self._serversock:
            nickname = SERVER_NAME
        else:
            nickname = self._nicknames[self._users.index(src_sock)]

        msg_encoded = self._pack_msg(f"{nickname}:⠀{msg}")
        try:
            dest_sock.sendall(msg_encoded)
        except:
            print(f"Error occured while sending to {dest_sock.getpeername()}")
            self.remove(dest_sock)

    def _pack_msg(self, msg: str) -> bytes:
        encoded_msg = msg.encode()
        msg_len = len(encoded_msg)
        return socket.htonl(msg_len).to_bytes(4) + encoded_msg

    def broadcast(self, sender_sock: socket.socket, msg: str):
        for user in self._users:
            self.send(sender_sock, user, msg)

    def run_server(self):
        self._serversock.listen()
        print("Waiting for connections...")
        while True:
            to_read = self._selector.select()
            for key, _ in to_read:
                callback = key.data
                callback(key.fileobj)

    def shutdown(self):
        self.broadcast(self._serversock, "Server shutdown")
        time.sleep(1)
        for sock in self._users:
            self.remove(sock)
        self._serversock.close()


if __name__ == "__main__":
    host = ""
    port = 9876
    server = ChatServer(host, port)
    try:
        server.run_server()
    except KeyboardInterrupt:
        server.shutdown()
        print("Shutdown")
