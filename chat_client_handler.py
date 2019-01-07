from chat_server import *

# CLIENT REQUEST IDENTIFIERS:
ENTRANCE_REQUEST_IDENTIFIER = 'ENTRANCE:'
BROADCAST_MESSAGE = 'BROADCAST:'
PRIVATE_MESSAGE = 'PRIVATE:'

# RESPONSES TO CLIENT
SUCCESSFUL_ENTRY = 'ENTERED SUCCESSFULLY'
WRONG_DETAILS = 'WRONG DETAILS'
USER_NOT_FOUND = '** Requested user does not exist, or is not connected **'


class ClientHandler(threading.Thread):
    """ responsible for the server-client communication """

    def __init__(self, address, socket):
        super(ClientHandler, self).__init__()
        self.sock = socket
        self.address = address

    def handle_user_entrance(self, entrance_details):
        """ responsible for verifying and authenticating the user's information,
            and informing the client on whether or not the entrance succeeded."""
        entrance_details = entrance_details.split(':')  # details are separated by ':'.
        entrance_type = entrance_details[1]  # entrance type: login/register.
        client_username = entrance_details[2]  # client's username entered.
        client_password = entrance_details[3]  # client's password entered.

        if entrance_type == 'register':  # if the client chose to register (connecting as a new user)
            EXISTING_USERS.update({client_username: client_password})  # adding the details to the server's database.
            CONNECTED_USERS.update(
                {client_username: self.sock})  # updating the connected users dictionary with client's details.

            # sending an approval string and the chat history to the client.
            self.sock.send((SUCCESSFUL_ENTRY + '-' + MESSAGES).ljust(1024, '0'))

        elif entrance_type == 'login':  # if the client chose to login (connecting as an existing user)
            if client_username in EXISTING_USERS.keys() and EXISTING_USERS[client_username] == client_password:
                # if username and password exist in the server's database

                CONNECTED_USERS.update(
                    {client_username: self.sock})  # updating the connected users dictionary with client's details.

                # sending an approval string and the chat history to the client.
                self.sock.send((SUCCESSFUL_ENTRY + '-' + MESSAGES).ljust(1024, '0'))

            else:
                # if the details the client entered don't match the database, informing the client on that.
                self.sock.send(WRONG_DETAILS.ljust(1024, '0'))

    def send_messages(self, message, message_type):
        """ responsible for sending the messages.
            receiving the message itself and whether it's a private or a broadcast message, sending it to the intended
            clients using their sockets which are saved in the server's 'connected users' dictionary."""

        global MESSAGES  # the chat history string, which is in the server.

        if message_type == BROADCAST_MESSAGE:
            for user_socket in CONNECTED_USERS.values():  # sending message to all the connected users.
                user_socket.send(message.ljust(1024, '0'))

            message = message.split('0')[0].split(':')
            sender = message[1]  # message sender
            the_message = message[2]  # message itself
            new_message = sender + ': ' + the_message  # arranging info in a presentable string
            MESSAGES += new_message + '\n'  # appending the chat history string, which will be sent to every new client.

        elif message_type == PRIVATE_MESSAGE:
            message = message.split('0')[0].split(':')
            sender = message[1]  # message sender
            message_part = message[2].split('@')  # '@' separates the message from the requested addressee username.
            send_to = message_part[0]  # intended addressee
            the_message = message_part[1]  # message itself

            # Checking if the intended addressee is an actual user in the system, and if they are connected:
            found_user = False
            for user in CONNECTED_USERS.keys():
                if user == send_to:
                    found_user = True

            if found_user:
                # if addressee found, sending message to both the sender and the addressee
                CONNECTED_USERS[send_to].send((message_type + sender + ':' + the_message).ljust(1024, '0'))
                CONNECTED_USERS[sender].send((message_type + sender + ':' + the_message).ljust(1024, '0'))

            if found_user is False:
                # if addressee is not connected, inform the sender
                CONNECTED_USERS[sender].send(USER_NOT_FOUND.ljust(1024, '0'))

    def run(self):
        while True:
            message_from_client = self.sock.recv(1024).split('0')[0]

            if message_from_client.startswith(ENTRANCE_REQUEST_IDENTIFIER):
                self.handle_user_entrance(message_from_client)

            elif message_from_client.startswith(BROADCAST_MESSAGE):
                self.send_messages(message_from_client, BROADCAST_MESSAGE)

            elif message_from_client.startswith(PRIVATE_MESSAGE):
                self.send_messages(message_from_client, PRIVATE_MESSAGE)
