import sys
import socket


def main():
    if len(sys.argv) == 1:
        run_client()
    elif len(sys.argv) == 4 and sys.argv[1] == '--server':
        run_server()
    else:
        print_usage()
        exit(1)


def print_usage():
    print("\nUSAGE:")
    print("chatshit")
    print("chatshit --server HOST PORT")


def run_client():
    from chatshit.app import ChatApp
    app = ChatApp()
    try:
        app.run()
    except KeyboardInterrupt:
        app.close_all_clients()

def run_server():
    from chatshit.network.server import ChatServer

    try:
        server = ChatServer(sys.argv[2], int(sys.argv[3]))
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
