import socket
import threading
import json
from typing import Dict
import time

HOST = 'localhost'
SERVER_PORTS = {'choghondar': 6969,
                "shalgham": 8585, 'proxy': [1111, 2222, 3333]}
invalid_ports = []
mode = 0    # 0 indicates normal user, 1 indicates admin user
connected = False
message = ""
client = None
state = ''


# def read_choghondar(command: Dict):  # action based on message
#     global state
    # if 'Menu' in message or message=='Incorrect username or password.':
    #     state = 'menu'
    # elif message in ['Please enter your username.', 'This username is already existed or invalid. Please enter another one.']:
    #     state = 'username'
    # elif message == 'Please enter your password.':
    #     state = 'password'
    # elif 'Inbox' in message or message=='Username  not found':
    #     state = 'inbox'
    # elif "Chatbox" in message:
    #     state = 'chatbox'
    # state = command['state']
    
def print_chatbox(chatbox):
    username = chatbox['username']
    for message in chatbox['messages']:
        if message['source'] != username:
            print(f"({message['source']})", end='')
        print(message['content'])
    

def read_server(server):
    global message, connected, state
    try:
        while True:
            command = read(client)
            time.sleep(1)
            state = command['state']
            message = command['message']
            if state == 'chatbox':
                print_chatbox(message)
            if message:
                print(f"{message}")
            if message == 'exit':
                connected = False
            # if server == 'choghondar':
            #     read_choghondar(command)
            # time.sleep(1)

    except ConnectionError as e:
        print(e)
        client.close()

def read(client: socket.socket) -> Dict:
    try:
        return json.loads(client.recv(1024).decode('ascii'))
    except ConnectionError or ConnectionResetError:
        client.close()

def send(message: str, state: str=''):
    msg = json.dumps({'message': message, 'state': state}) # TODO: remove state?
    client.send(msg.encode('ascii'))


def handle_choghondar():
    global state
    try:
        while True:
            if state == 'menu':
                command = input("Enter command:\n")
                if command not in ['1', '2', '3']:
                    print('invalid command')
                    continue
                send(command)
                state = 'submit'
            elif any(x in state for x in['username', 'password', 'inbox']):
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
    threading.Thread(target=handle, args=(server_name,), daemon=True).start()
    threading.Thread(target=read_server, args=(server_name,), daemon=True).start()

    while connected: 
        pass


command = ''
while not command:
    command = input('1. Connect to external servers\n2. Login as admin\n3. Exit\n')
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
