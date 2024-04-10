# server.py

# importing socket and threading libraries
import socket
import threading

# defining global variables for server address and port and number of channels
SERVER = '127.0.0.1' # localhost
PORT = 8000 # server port
NUMBER_OF_CHANNELS = 3 # number of channels

# defining global variables for clients and channels
clients = []
channels = {i: [] for i in range(1, NUMBER_OF_CHANNELS + 1)}  # Initialize channels

def handleClient(client, address):
    """
    function to handle client connections
    """

    try:
        # Receiving the name of the client
        name = client.recv(1024).decode("utf-8")

        # Adding the client to the clients list
        clients.append((name, client, 1))  # Default channel is 1
        
        # Printing the connection message
        print(f"[SERVER] Connection from: {address}")

        # Sending a message to all clients indicating that the user has joined the chat
        sendServerMessage(f"{name} has joined the chat")

        # While loop to continuously receive messages from the client
        while True:
            message = client.recv(1024).decode("utf-8") # Assing message to variable
            
            # if message starts with / handle command
            if (message[0] == "/"):
                handleCommand(name, message)

            # else send message to all other clients
            else:
                sendMessage(name, message)
    
    # in case of error print the error
    except Exception as exception:
        print("Error:", exception)

    # Closing the connection after the user has left the chat
    finally:
        # Printing the disconnection message to the server for debugging purposes
        print(f"Connection closed for: {name}")

        # Closing the connection and removing the client from the clients list
        client.close()
        clients.remove((name, client, getChannel(name)))

        # Sending a message to all clients indicating that the user has left the chat
        sendServerMessage(f"{name} has left the chat")

def handleCommand(name, command):
    """
    function to handle commands
    """

    # if command starts with /msg handle sending a message to a specific client
    if (command.startswith("/msg")):

        # split command into parts then check if there are at least 3 parts and assing parts to recipient and message
        parts = command.split(" ", 2)
        if (len(parts) >= 3):
            recipient = parts[1]
            message = parts[2]

            # send the private message to the recipient
            sendPrivateMessage(name, recipient, message)
        else:
            # send an error message if the command is used incorrectly
            sendServerPrivateMessage(name, f"[SERVER] Invalid private message format, use /msg <recipient> <message>")

    # if command is /exit, close the connection
    elif (command.strip() == "/exit"):
        raise ConnectionResetError # close the connection
    
    # if command is /channel, set/change a client's channel
    elif (command.startswith("/channel")):

        # split command into parts
        parts = command.split()

        # check if there are at least 2 parts and assign number part to a channel
        if (len(parts) == 2 and parts[1].isdigit()):
            channel = int(parts[1])

            # check if the channel is between 1 and the number of channels
            if (1 <= channel <= NUMBER_OF_CHANNELS):
                setChannel(name, channel) # set the channel
                sendServerMessage(f"{name} switched to channel {channel}") # announce the channel change

            # send an error message if the channel number is invalid
            else:
                sendServerPrivateMessage(name, f"Invalid channel number {channel}. Must be between 1 and {NUMBER_OF_CHANNELS}")
        
        # send an error message if the command is used incorrectly
        else:
            sendServerPrivateMessage(name, f"Invalid command format for channel switch") # send an error message if the command is used incorrectly
    
    # if command is /help, send a list of available commands
    elif (command.startswith("/help")):
        sendServerPrivateMessage(name, f"Available commands: /msg <recipient> <message>, /channel <channel number>, /exit") # send a list of available commands
    
    # if command is invalid, send an error message
    else: 
        sendServerPrivateMessage(name, f"Invalid command please refer to /help for available commands") # send an error message if the command is used incorrectly

def setChannel(name, channel):
    """
    function to set/change a client's channel
    """

    # Setting the channel of the sender
    for i, (clientName, clientSocket, clientChannel) in enumerate(clients):
        if (clientName == name):
            clients[i] = (clientName, clientSocket, channel)
            break

def getChannel(name):
    """
    function to get a client's channel
    """

    # Getting the channel number of the sender
    for clientName, _, channel in clients:
        if clientName == name:
            return channel
    return None

def sendServerMessage(message):
    """
    function to send a message to all clients
    """

    # Server sending the message to all clients
    for clientName, clientSocket, clientChannel in clients:
        clientSocket.sendall(f"[SERVER] {message}".encode("utf-8"))

def sendServerPrivateMessage(recipient, message):
    """
    function to send a private message to a specific client
    """

    # Sending the message to the recipient
    for clientName, clientSocket, clientChannel in clients:
        if clientName == recipient:
            clientSocket.sendall(f"[SERVER] {message}".encode("utf-8"))
            break

def sendPrivateMessage(sender, recipient, message):
    """
    function to send a private message to a specific client
    """

    # Sending the private message to the recipient from the sender
    for clientName, clientSocket, clientChannel in clients:
        if clientName == recipient:
            clientSocket.sendall(f"[PM from {sender}]: {message}".encode("utf-8"))
            break

def sendMessage(sender, message):
    """
    function to send a message to all clients
    """

    # Getting the channel of the sender
    senderChannel = getChannel(sender)

    # Sending the message to all clients in the same channel
    for clientName, clientSocket, clientChannel in clients:
        if clientName != sender and clientChannel == senderChannel:
            clientSocket.sendall(f"{sender}: {message}".encode("utf-8"))

def main():
    """
    function to start the server
    """

    # Starting the server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER, PORT))
    server.listen()

    # Printing the server started message for debugging purposes
    print(f"[SERVER] Server started on {SERVER}:{PORT}")

    # Starting accepting connections
    while True:
        client, address = server.accept()
        thread = threading.Thread(target=handleClient, args=(client, address))
        thread.start()
        print(f"[SERVER] Current Connections: {threading.active_count() - 1}")

# Run the server
if __name__ == "__main__":
    main() # Calling the main server function
