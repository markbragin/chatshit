from dataclasses import dataclass
import json
import socket
import selectors
import time

# from threading import Thread


MSG_SIZE = 4096
SERVER_NAME = "[SERVER]"


@dataclass
class Member:
    username: str
    peername: None


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

        self._members: dict[socket.socket, Member] = {}

    def __enter__(self):
        return self

    def __exit__(self):
        self._serversock.close()

    # def _listen_to_new_connections(self, sock: socket.socket):
    #     conn_t = Thread(target=self._get_new_connection, args=(sock,))
    #     conn_t.daemon = True
    #     conn_t.start()

    def _get_new_connection(self, sock: socket.socket):
        sock, _ = sock.accept()
        self._selector.register(
            sock, selectors.EVENT_READ, self._handle_new_message
        )

    def _handle_new_message(self, sock: socket.socket):
        try:
            msg_len = socket.ntohl(int.from_bytes(sock.recv(4)))
            if msg_len == 0:
                self.remove(sock)
                return
            msg = json.loads(sock.recv(msg_len))
        except json.decoder.JSONDecodeError:
            print("Json corrupted")
            self.remove(sock)
            return
        except ConnectionResetError:
            self.remove(sock)
            return

        if msg["Type"] == "text":
            self._read_text_msg(sock, msg)
        elif msg["Type"] == "new_member":
            self._read_new_member_msg(sock, msg)

    def _read_text_msg(self, sock: socket.socket, msg: dict):
        username = self._members[sock].username
        self.broadcast(self.pack_text_msg(f"{username}: {msg['Text']}"))

    def _read_new_member_msg(self, sock: socket.socket, msg: dict):
        self._add_member(sock, msg["Username"])

    def _add_member(self, sock: socket.socket, username: str):
        for member in self._members.values():
            self.send_msg(sock, self.pack_new_member_msg(member))

        username = self._generate_unique_username(username)
        self._members[sock] = Member(
            username,
            sock.getpeername(),
        )

        self.send_msg(sock, self.pack_unique_username(username))
        self.broadcast(
            self.pack_text_msg(f"{SERVER_NAME}: {username} joined the chat")
        )
        self.broadcast(self.pack_new_member_msg(self._members[sock]))
        print(f"{username}: {self._members[sock].peername} connected")

    def _generate_unique_username(self, username: str) -> str:
        usernames = [member.username for member in self._members.values()]
        if username in usernames:
            i = 1
            while username + str(i) in usernames:
                i += 1
            username = username + str(i)
        return username if username != SERVER_NAME else "NOT a " + username

    def pack_text_msg(self, text: str) -> bytes:
        msg = {
            "Type": "text",
            "Text": text,
        }
        encoded_msg = json.dumps(msg).encode()
        msg_len = socket.htonl(len(encoded_msg)).to_bytes(4)
        return msg_len + encoded_msg

    def pack_new_member_msg(self, member: Member) -> bytes:
        msg = {
            "Type": "new_member",
            "Username": member.username,
        }
        encoded_msg = json.dumps(msg).encode()
        msg_len = socket.htonl(len(encoded_msg)).to_bytes(4)
        return msg_len + encoded_msg

    def pack_left_chat_msg(self, member: Member) -> bytes:
        header = {
            "Type": "left_chat",
            "Username": member.username,
        }
        encoded_msg = json.dumps(header).encode()
        msg_len = socket.htonl(len(encoded_msg)).to_bytes(4)
        return msg_len + encoded_msg

    def pack_unique_username(self, username: str) -> bytes:
        msg = {
            "Type": "unique_username",
            "Username": username,
        }
        encoded_msg = json.dumps(msg).encode()
        msg_len = socket.htonl(len(encoded_msg)).to_bytes(4)
        return msg_len + encoded_msg

    def broadcast(self, msg: bytes):
        for sock in self._members:
            self.send_msg(sock, msg)

    def send_msg(self, sock: socket.socket, msg: bytes):
        try:
            sock.sendall(msg)
        except:
            self.remove(sock)

    def remove(self, sock: socket.socket, send_close: bool = True):
        member = self._members[sock]
        print(f"{member.username}: {member.peername} closed connection")

        self._selector.unregister(sock)
        self._members.pop(sock)
        sock.close()

        if send_close:
            text = f"{SERVER_NAME}: {member.username} left the chat"
            self.broadcast(self.pack_text_msg(text))
            self.broadcast(self.pack_left_chat_msg(member))

    def run_server(self):
        self._serversock.listen()
        print("Waiting for connections...")
        while True:
            to_read = self._selector.select()
            for key, _ in to_read:
                callback = key.data
                callback(key.fileobj)

    def shutdown(self):
        self.broadcast(self.pack_text_msg(f"{SERVER_NAME}: shutdown"))
        time.sleep(1)
        for sock in self._members:
            self.remove(sock, send_close=False)
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
