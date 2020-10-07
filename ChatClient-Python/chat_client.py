#################################################################################
# A Chat Client application. Used in the course IELEx2001 Computer networks, NTNU
#################################################################################

from socket import *


# --------------------
# Constants
# --------------------
# The states that the application can be in
states = [
    "disconnected",  # Connection to a chat server is not established
    "connected",  # Connected to a chat server, but not authorized (not logged in)
    "authorized"  # Connected and authorized (logged in)
]
TCP_PORT = 1300  # TCP port used for communication
SERVER_HOST = "datakomm.work"  # Set this to either hostname (domain) or IP address of the chat server

# --------------------
# State variables
# --------------------
current_state = "disconnected"  # The current state of the system
# When this variable will be set to false, the application will stop
must_run = True
# Use this variable to create socket connection to the chat server
# Note: the "type: socket" is a hint to PyCharm about the type of values we will assign to the variable
client_socket = None  # type: socket


def quit_application():
    """ Update the application state so that the main-loop will exit """
    global must_run
    must_run = False


def send_command(command, arguments=None):
    """
    Send one command to the chat server.
    :param command: The command to send (login, sync, msg, ...(
    :param arguments: The arguments for the command as a string, or None if no arguments are needed
        (username, message text, etc)
    :return:
    """
    global client_socket
    if arguments is not None:
        command += ' ' + arguments + '\n'
    else:
        command += '\n'
    try:
        client_socket.send(command.encode())
    except IOError as e:
        print(e)


def read_one_line(sock):
    """
    Read one line of text from a socket
    :param sock: The socket to read from.
    :return:
    """
    newline_received = False
    message = ""
    while not newline_received:
        character = sock.recv(1).decode()
        if character == '\n':
            newline_received = True
        elif character == '\r':
            pass
        else:
            message += character
    return message


def get_servers_response():
    """
    Wait until a response command is received from the server
    :return: The response of the server, the whole line as a single string
    """
    global client_socket
    valid_responses = ["loginok", "loginerr", "modeok", "msgok", "msgerr", "inbox", "supported", "cmderr", "users", "joke"]
    response = read_one_line(client_socket)
    while response.split()[0] not in valid_responses:
        response = read_one_line(client_socket)

    return response


def connect_to_server():
    """
    Opens socket, connects to server, changes state to connected and enters synchronized mode
    """
    global client_socket
    global current_state
    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
        client_socket.connect((SERVER_HOST, TCP_PORT))
    except IOError as e:
        print(e)
        return
    current_state = "connected"
    send_command("sync")
    if "modeok" not in get_servers_response():
        print("ERROR: NOT IN SYNC MODE")


def disconnect_from_server():
    """
    Closes socket and changes state to disconnected
    """
    global client_socket
    global current_state
    try:  
        client_socket.close()
    except IOError as e:
        print(e)
        return
    current_state = "disconnected"


def login():
    """
    Logs in user and changes state to authorized
    """
    global current_state
    username = input("Enter username: ")
    send_command("login", username)
    response = get_servers_response()
    if "loginerr" in response:
        print(response)
    else:
        current_state = "authorized"


def send_public_message():
    """
    Sends a public message
    """
    message = input("Enter public message: ")
    send_command("msg", message)
    response = get_servers_response()
    if "msgerr" in response:
        print(response)


def send_private_message():
    """
    Sends a private message
    """
    recipient = input("Enter recipient: ")
    message = input("Enter message: ")
    send_command("msg", recipient + ' ' + message)
    response = get_servers_response()
    if "msgerr" in response:
        print(response)


def get_user_list():
    """
    Fetches available users from server
    """
    send_command("users")
    response = get_servers_response()
    if "users" in response:
        print(response.replace("users", "Users:"))
    else:
        print("ERROR: COULD NOT FETCH USERS")


def read_inbox():
    """
    Fetches unread messages from server
    """
    global client_socket
    send_command("inbox")
    number_of_messages = int(read_one_line(client_socket).strip("inbox\n"))
    public_messages = []
    print("Unread messages:", number_of_messages)
    print("----------------\nPrivate messages\n----------------")
    for i in range(number_of_messages):
        message = read_one_line(client_socket)
        if "privmsg" in message:
            print(message.replace("privmsg ", ""))
        else:
            public_messages.append(message.replace("msg ", ""))
    print("---------------\nPublic messages\n---------------")
    for message in public_messages: print(message)


def get_joke():
    """
    Fetches random joke from server
    """
    send_command("joke")
    response = get_servers_response()
    print(response)



"""
The list of available actions that the user can perform
Each action is a dictionary with the following fields:
description: a textual description of the action
valid_states: a list specifying in which states this action is available
function: a function to call when the user chooses this particular action. The functions must be defined before
            the definition of this variable
"""
available_actions = [
    {
        "description": "Connect to a chat server",
        "valid_states": ["disconnected"],
        "function": connect_to_server
    },
    {
        "description": "Disconnect from the server",
        "valid_states": ["connected", "authorized"],
        "function": disconnect_from_server
    },
    {
        "description": "Authorize (log in)",
        "valid_states": ["connected", "authorized"],
        "function": login
    },
    {
        "description": "Send a public message",
        "valid_states": ["connected", "authorized"],
        "function": send_public_message
    },
    {
        "description": "Send a private message",
        "valid_states": ["authorized"],
        "function": send_private_message
    },
    {
        "description": "Read messages in the inbox",
        "valid_states": ["connected", "authorized"],
        "function": read_inbox
    },
    {
        "description": "See list of users",
        "valid_states": ["connected", "authorized"],
        "function": get_user_list
    },
    {
        "description": "Get a joke",
        "valid_states": ["connected", "authorized"],
        "function": get_joke
    },
    {
        "description": "Quit the application",
        "valid_states": ["disconnected", "connected", "authorized"],
        "function": quit_application
    },
]


def run_chat_client():
    """ Run the chat client application loop. When this function exists, the application will stop """

    while must_run:
        print_menu()
        action = select_user_action()
        perform_user_action(action)
    print("Thanks for watching. Like and subscribe! 👍")


def print_menu():
    """ Print the menu showing the available options """
    print("==============================================")
    print("What do you want to do now? ")
    print("==============================================")
    print("Available options:")
    i = 1
    for a in available_actions:
        if current_state in a["valid_states"]:
            # Only hint about the action if the current state allows it
            print("  %i) %s" % (i, a["description"]))
        i += 1
    print()


def select_user_action():
    """
    Ask the user to choose and action by entering the index of the action
    :return: The action as an index in available_actions array or None if the input was invalid
    """
    number_of_actions = len(available_actions)
    hint = "Enter the number of your choice (1..%i):" % number_of_actions
    choice = input(hint)
    # Try to convert the input to an integer
    try:
        choice_int = int(choice)
    except ValueError:
        choice_int = -1

    if 1 <= choice_int <= number_of_actions:
        action = choice_int - 1
    else:
        action = None

    return action


def perform_user_action(action_index):
    """
    Perform the desired user action
    :param action_index: The index in available_actions array - the action to take
    :return: Desired state change as a string, None if no state change is needed
    """
    if action_index is not None:
        print()
        action = available_actions[action_index]
        if current_state in action["valid_states"]:
            function_to_run = available_actions[action_index]["function"]
            if function_to_run is not None:
                function_to_run()
            else:
                print("Internal error: NOT IMPLEMENTED (no function assigned for the action)!")
        else:
            print("This function is not allowed in the current system state (%s)" % current_state)
    else:
        print("Invalid input, please choose a valid action")
    print()
    return None

# Entrypoint for the application. In PyCharm you should see a green arrow on the left side.
# By clicking it you run the application.
if __name__ == '__main__':
    run_chat_client()
