# client.py

# importing socket and threading libraries
import socket
import threading
import sys

# defining global variables for server address and port
SERVER = '127.0.0.1' # localhost
PORT = 8000 # server port

def getMessage(socket):
    """
    function to get messages from the server
    """

    # While loop to continuously receive messages from the server
    while True:
        try:
            message = socket.recv(1024).decode("utf-8")
            print(message)
        except Exception as exception: # In case of error print the error, break the loop
            print("Error:", exception)
            break

def sendMessage(socket):
    """
    function to send messages to the server
    """

    # While loop to continuously send messages to the server
    while True:
        try:
            message = input("")
            if (message == "/exit"):
                break
            socket.sendall(message.encode("utf-8"))
        except Exception as exception: # In case of error print the error, break the loop
            print("Error:", exception)
            break

def main():
    """
    function to start the client
    """

    # Starting the client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4, TCP
    client.connect((SERVER, PORT)) # Connecting to the server

    # Printing the NAME header and asking the user for their name
    print("\n############## NAME ##############\n")
    name = input("Give your name: ") # Get the user's nickname

    # Printing the CHAT header and sending the user's name to the server
    print("\n############## CHAT ##############\n")
    client.sendall(name.encode("utf-8")) # Send the user's nickname

    # Starting a thread to continuously receive messages from the server
    thread = threading.Thread(target=getMessage, args=(client,))
    thread.start()

    # Starting sending messages to the server
    sendMessage(client)

    # Closing the connection after the user has left the chat
    client.close()

# Run the client
if __name__ == "__main__":
    main() # Calling the main client function
    sys.exit()  # Exit the program after main() finishes
