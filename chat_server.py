import threading
import socket
import chat_client_handler

EXISTING_USERS = {'one': '1', 'two': '2', 'three': '3'}
CONNECTED_USERS = {}  # will contain the connected users information ({username: socket})
MESSAGES = ''  # will contain the chatting history, for the new users to receive.


class Server(object):
    def __init__(self):
        self.server_socket = socket.socket()
        self.server_socket.bind(('0.0.0.0', 4522))
        self.server_socket.listen(10)

    def accept(self):
        return self.server_socket.accept()

def main():
    server = Server()
    while True:
        socket, address = server.accept()
        client_hand = chat_client_handler.ClientHandler(address, socket)
        client_hand.start()


if __name__ == '__main__':
    main()

