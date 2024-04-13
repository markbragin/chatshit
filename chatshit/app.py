from threading import Thread
from textual.app import App, events

from chatshit.screens.chatroom_screen import ChatRoomScreen
from chatshit.screens.home_screen import HomeScreen
from chatshit.network.chatroom_server import ChatRoomServer
from chatshit.widgets.chat_list import ChatList
from chatshit.screens.client_screen import ClientScreen
from chatshit.widgets.server_list import ServerList



class ServerInfo:
    def __init__(self, id: int, server: ChatRoomServer):
        self.id = id
        self.server = server


class ClientInfo:
    def __init__(self, id: int, screen: ClientScreen, screen_name: str):
        self.id = id
        self.screen = screen
        self.screen_name = screen_name


class ChatApp(App):

    CSS_PATH = "styles.css"

    def __init__(self):
        super().__init__()

        self._clients: dict[int, ClientInfo] = {}
        self._servers: dict[int, ServerInfo] = {}

        self._next_server_id: int = 1
        self._next_client_id: int = 1
        self._server_threads: list[Thread] = []

    def on_mount(self):
        self.home_screen = HomeScreen()
        self.push_screen(self.home_screen)
        self.set_interval(30, self.join_dead_server_threads)

    def join_dead_server_threads(self):
        for thread in self._server_threads.copy():
            if not thread.is_alive():
                thread.join()
                self._server_threads.remove(thread)

    def add_client(self, screen: ClientScreen):
        cid = self._next_client_id
        self._next_client_id += 1

        screen_name = f"chatroom_screen_{cid}"
        self._clients[cid] = ClientInfo(cid, screen, screen_name)
        self.install_screen(screen, screen_name)

        client = screen.client
        assert client is not None
        name = screen.chat_name if screen.chat_name else ""
        self.home_screen.chat_list.add_chat(
            cid, client.host, client.port, name
        )

    def create_server(self, host: str, port: int):
        server = ChatRoomServer(host, port)

        sid = self._next_server_id
        self._next_server_id += 1

        serv_th = Thread(target=server.run_server)
        serv_th.daemon = True
        serv_th.start()
        self._server_threads.append(serv_th)

        self._servers[sid] = ServerInfo(sid, server)

        self.home_screen.server_list.add_server(sid, host, port)

    def on_chat_room_screen_add_client(
        self, message: ChatRoomScreen.AddClient
    ):
        self.add_client(message.screen)

    def on_chat_list_open_chat(self, message: ChatList.OpenChat):
        self.push_screen(self._clients[message.chat_id].screen)

    def on_chat_list_leave_chat(self, message: ChatList.OpenChat):
        chat_id = message.chat_id

        try:
            client_info = self._clients.pop(chat_id)
        except:
            return

        self.uninstall_screen(client_info.screen_name)
        if client_info.screen.client is not None:
            client_info.screen.client.close()
        self.home_screen.chat_list.remove_chat(chat_id)

    def on_server_list_stop_server(self, message: ServerList.StopServer):
        server_id = message.server_id
        try:
            server_info = self._servers.pop(server_id)
        except:
            return
        server_info.server.stop()
        self.home_screen.server_list.remove_server(server_id)

    def on_key(self, event: events.Key):
        if event.key == "escape" and self.screen_stack[-1] != self.home_screen:
            self.pop_screen()

    def close_all_clients(self):
        for client_info in self._clients.values():
            if client_info.screen.client:
                client_info.screen.client.close()

    def close_all_servers(self):
        for server_info in self._servers.values():
            server_info.server.shutdown()

    def get_server_address(self, server_id: int) -> tuple[str, int]:
        server = self._servers[server_id].server
        return (server.host, server.port)


if __name__ == "__main__":
    app = ChatApp()
    try:
        app.run()
        app.close_all_clients()
        app.close_all_servers()
    except KeyboardInterrupt:
        app.close_all_clients()
        app.close_all_servers()
