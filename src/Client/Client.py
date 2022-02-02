import socket
import threading

HOST = 'localhost'
SERVER_PORTS = {'choghondar': 6969,
                "shalgham": 8585, 'proxy': [1111, 2222, 3333]}
invalid_ports = []
mode = 0    # 0 indicates normal user, 1 indicates admin user
connected = False
message = ""
client = None
state = ''


def read_choghondar(client, message):  # action based on message
    global state
    if 'Menu' in message or message=='Incorrect username or password.':
        state = 'menu'
    elif message in ['Please enter your username.', 'This username is already existed or invalid. Please enter another one.']:
        state = 'username'
    elif message == 'Please enter your password.':
        state = 'password'
    elif 'Inbox' in message or message=='Username  not found':
        state = 'inbox'
    elif "Chatbox" in message:
        state = 'chatbox'
    


def read(server):
    global message, connected
    try:
        while True:
            message = client.recv(1024).decode('ascii').strip()
            print(f'{message}')
            if message == 'exit':
                connected = False
            if server == 'choghondar':
                read_choghondar(client, message)

    except ConnectionError as e:
        print(e)
        client.close()


def send(message: str):
    client.send(message.encode('ascii'))


def handle_choghondar():
    global state
    try:
        while True:
            if state == 'menu':
                command = input("Enter command:\n")
                if command not in ['1', '2', '3']:
                    print('invalid command')
                send(command)
                state = 'submit'
            elif state in ['username', 'password', 'inbox']:
                send(input())
                state = 'submit'
            elif state == 'chatbox':
                command = input()
                send(command)
                if command == '/exit':
                    state = 'submit'
    except ConnectionError as e:
        print(e)
        client.close()


def handle(server_name):
    if server_name == 'choghondar':
        handle_choghondar()


def connect_to_server(server_name):
    if server_name not in SERVER_PORTS:
        print('invalid server')
        return
    global client
    client = socket.socket()
    client.connect((HOST, SERVER_PORTS[server_name]))
    connected = True
    threading.Thread(target=handle, args=(server_name), daemon=True).start()
    threading.Thread(target=read, args=(server_name), daemon=True).start()

    while connected: 
        pass


command = ''
while not command:
    command = input('''1. Connect to external servers
                2. Login as admin
                3. Exit\n''')
    if command == '1':
        command = input("Enter server name\n")
        connect_to_server(command)
    elif command == '2':
        command = input("Enter password\n")  # first time for setting password
    elif command == '3':
        break
    else:
        print('invalid command')
        command = ''
