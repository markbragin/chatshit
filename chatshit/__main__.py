import sys


def main():
    if len(sys.argv) == 1:
        run_client()
    elif len(sys.argv) == 4 and sys.argv[1] == '--server':
        try:
            run_server()
        except:
            print_usage()
            exit(1)
    else:
        print_usage()
        exit(1)

def print_usage():
    print("USAGE")
    print("chatshit")
    print("chatshit --server address port")


def run_client():
    from .app import ChatRoom
    app = ChatRoom()
    try:
        app.run()
    except KeyboardInterrupt:
        app.client.close()

def run_server():
    from .server import ChatServer
    server = ChatServer(sys.argv[2], int(sys.argv[3]))
    server.run_server()


if __name__ == "__main__":
    main()
