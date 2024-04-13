import sys
import socket


def main():
    if len(sys.argv) == 1:
        run_app()
    elif len(sys.argv) == 4 and sys.argv[1] == '--server':
        run_server()
    else:
        print_usage()
        exit(1)


def print_usage():
    print("\nUSAGE:")
    print("chatshit")
    print("chatshit --server HOST PORT")


def run_app():
    from chatshit.app import ChatApp
    app = ChatApp()
    try:
        app.run()
        app.close_all_clients()
        app.close_all_servers()
    except KeyboardInterrupt:
        app.close_all_clients()
        app.close_all_servers()

def run_server():
    from chatshit.network.chatroom_server import ChatRoomServer

    try:
        server = ChatRoomServer(sys.argv[2], int(sys.argv[3]))
    except socket.gaierror:
        print("Wrong host or port")
        exit(1)

    try:
        server.run_server()
    except KeyboardInterrupt:
        server.shutdown()
        print("\nServer shutdown")


if __name__ == "__main__":
    main()
