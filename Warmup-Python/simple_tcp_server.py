# A Simple TCP server, used as a warm-up exercise for assignment A3

from socket import *
import threading


def run_server():
    # TODO - implement the logic of the server, according to the protocol.
    # Take a look at the tutorial to understand the basic blocks: creating a listening socket,
    # accepting the next client connection, sending and receiving messages and closing the connection
    print("Starting TCP server...")

    welcome_socket = socket(AF_INET, SOCK_STREAM)
    welcome_socket.bind(('', 13001))
    welcome_socket.listen(1)
    client_id = 1

    while True:
        connection_socket, client_address = welcome_socket.accept()
        client_thread = threading.Thread(target=handle_next_client, 
                                         args=(connection_socket, client_id))
        client_thread.start()
        client_id += 1

    welcome_socket.close()



def handle_next_client(connection_socket, client_id):
    try:
        equation = connection_socket.recv(10).decode().rstrip()
        first_num, second_num = equation.split('+')
        answer = str(int(first_num) + int(second_num)) + '\n'
        connection_socket.send(answer.encode())
    except IOError as e:
        print("Error happened: ", e)
        connection_socket.send("error".encode())



# Main entrypoint of the script
if __name__ == '__main__':
    run_server()
