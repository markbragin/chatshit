from dataclasses import dataclass
import socket
import selectors
import time

import chatshit.network.proto as proto


SERVER_NAME = "[SERVER]"


@dataclass
class Member:
    username: str
    peername: None


class ChatRoomServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serversock.bind((host, port))

        self._selector = selectors.DefaultSelector()
        self._selector.register(
            self.serversock,
            selectors.EVENT_READ,
            self._get_new_connection,
        )

        self.on = True
        self._next_message_id = 1

        self._members: dict[socket.socket, Member] = {}

    def __enter__(self):
        return self

    def __exit__(self):
        self.serversock.close()

    def _get_new_connection(self, sock: socket.socket):
        sock, _ = sock.accept()
        self._selector.register(sock, selectors.EVENT_READ, self._login)

    def _login(self, sock: socket.socket):
        msg_len = self._read_msg_len(sock)
        if msg_len == 0:
            self._close_sock(sock)
            return

        data = sock.recv(msg_len)
        try:
            msg = proto.decode_msg(data)
            if msg["Type"] == "join_chat":
                self._add_member(sock, msg["Username"])
                self._selector.modify(
                    sock,
                    selectors.EVENT_READ,
                    self._handle_new_message,
                )
            else:
                self._close_sock(sock)
        except (proto.WrongFormat, OSError) as e:
            print(e)
            self._close_sock(sock)

    def _read_msg_len(self, sock: socket.socket) -> int:
        try:
            return socket.ntohl(int.from_bytes(sock.recv(4)))
        except ConnectionResetError:
            return 0

    def _handle_new_message(self, sock: socket.socket):
        msg_len = self._read_msg_len(sock)
        if msg_len == 0:
            self._remove(sock)
            return

        data = sock.recv(msg_len)
        try:
            msg = proto.decode_msg(data)
        except proto.WrongFormat as e:
            print(e)
            return

        if msg["Type"] == "text":
            username = self._members[sock].username
            text = f"{username}: {msg['Text']}"
            self._broadcast_text(text)
        elif msg["Type"] == "join_chat":
            self._add_member(sock, msg["Username"])
        elif msg["Type"] == "delete_message":
            self._broadcast(proto.pack_delete_message(msg["Id"]))

    def _broadcast_text(self, text: str):
        to_send = proto.pack_text_msg(text, self._next_message_id)
        self._next_message_id += 1
        self._broadcast(to_send)

    def _add_member(self, sock: socket.socket, username: str):
        username = self._generate_unique_username(username)
        sock.sendall(proto.pack_unique_username(username))

        for member in self._members.values():
            sock.sendall(proto.pack_join_chat_msg(member.username))

        self._members[sock] = Member(username, sock.getpeername())

        self._broadcast_text(f"{SERVER_NAME}: {username} joined the chat")
        self._broadcast(proto.pack_join_chat_msg(self._members[sock].username))
        print(f"{username}: {self._members[sock].peername} connected")

    def _generate_unique_username(self, username: str) -> str:
        usernames = [member.username for member in self._members.values()]
        if username in usernames:
            i = 1
            while username + str(i) in usernames:
                i += 1
            username = f"{username}({str(i)})"
        return username if username != SERVER_NAME else "NOT a " + username

    def _broadcast(self, msg: bytes):
        for sock in self._members.copy():
            try:
                sock.sendall(msg)
            except:
                self._remove(sock)

    def _close_sock(self, sock: socket.socket):
        username = "Somebody"
        peername = "??"
        if sock in self._members:
            username = self._members[sock].username
            peername = self._members[sock].peername
        else:
            try:
                peername = sock.getpeername()
            except:
                pass

        print(f"{username} {peername} closed connection")
        self._selector.unregister(sock)
        sock.close()

    def _remove(self, sock: socket.socket, send_close: bool = True):
        self._close_sock(sock)
        member = self._members[sock]
        self._members.pop(sock)

        if send_close:
            text = f"{SERVER_NAME}: {member.username} left the chat"
            self._broadcast_text(text)
            self._broadcast(proto.pack_left_chat_msg(member.username))

    def run_server(self):
        self.serversock.listen()
        print("Waiting for connections...")
        while True and self.on:
            to_read = self._selector.select()
            for key, _ in to_read:
                callback = key.data
                callback(key.fileobj)
        self.shutdown()

    def stop(self):
        self.on = False

    def shutdown(self):
        self._broadcast_text(f"{SERVER_NAME}: shutdown")
        time.sleep(1)
        for sock in self._members:
            self._close_sock(sock)
        self.serversock.close()


if __name__ == "__main__":
    host = ""
    port = 9876
    server = ChatRoomServer(host, port)
    try:
        server.run_server()
    except KeyboardInterrupt:
        server.shutdown()
        print("Shutdown")
