from concurrent.futures import thread
import re
import socket
import threading
import json
from typing import Dict
import time

HOST = 'localhost'
SERVER_PORTS = {'choghondar': 6969,
                "shalgham": 8585,
                'proxy': [1111, 2222, 3333],
                "firewall": 6985}

invalid_ports = set()
mode = 0    # 0 indicates normal user, 1 indicates admin user
connected = False
message = ""
client = None
port = 0
client_firewall = None
state = ''
is_admin = 0

def print_chatbox(chatbox):
    username = chatbox['username']
    for message in chatbox['messages']:
        if message['source'] != username:
            print(f"({message['source']}) ", end='')
        print(message['content'])

def read_choghondar():
    global message, connected, state
    try:
        while connected:
            command = read_json(client)
            time.sleep(1)
            state = command['state']
            message = command['message']
            if state == 'chatbox':
                print_chatbox(message)
            elif message:
                print(f"{message}")
            if message == 'exit':
                connected = False
    except (ConnectionError, TypeError) as e:
        client.close()

def read_server(server_name):
    if server_name == 'choghondar':
        read_choghondar()


def read_json(client: socket.socket) -> Dict:
    try:
        return json.loads(read_string(client))
    except TypeError:
        return

def send_json(message: str, **kwargs):
    send_string(client, json.dumps({'message': message, **kwargs}))

def send_string(client: socket.socket, message: str):
    global port, connected
    if port in invalid_ports:
        # print(port, "fadfa", invalid_ports)
        print('packet dropped due to firewall rules')
        port = 0
        connected = False
        client.close()
        return
    client.send(message.encode('ascii'))

def read_string(client: socket.socket):
    try:
        return client.recv(1024).decode('ascii').strip()
    except (ConnectionError, ConnectionResetError):
        client.close()


def handle_choghondar():
    global state
    try:
        while connected:
            if state == 'menu':
                command = input()
                if command not in ['1', '2', '3']:
                    print('invalid command')
                    continue
                send_json(command)
                state = 'submit'
            elif any(x in state for x in ['username', 'password', 'inbox']):
                send_json(input())
                state = 'submit'
            elif state == 'chatbox':
                command = input()
                send_json(command)
                if command == '/exit':
                    state = 'submit'

    except ConnectionError as e:
        print(e)
        client.close()


def handle(server_name):
    if server_name == 'choghondar':
        handle_choghondar()


def connect_to_server(server_name):
    global connected, client, port
    if server_name not in SERVER_PORTS:
        print('invalid server')
        return
    port = SERVER_PORTS[server_name]
    if port in invalid_ports:
        print('packet dropped due to firewall rules')
        port = 0
        return
    client = socket.socket()
    client.connect((HOST, port))
    connected = True
    threading.Thread(target=handle, args=(server_name,), daemon=True).start()
    threading.Thread(target=read_server, args=(server_name,), daemon=True).start()

    while connected:
        pass
    
    port = 0
    client.close()

def admin():
    global is_admin
    send_string(client_firewall, "login")
    is_admin = 1
    while is_admin > 0:
        if is_admin == 2:
            command = input()
            if command == 'exit':
                is_admin = 0
                return
            send_string(client_firewall, command)
    

def handle_firewall():
    global is_admin, invalid_ports
    while True:
        message = read_string(client_firewall)
        if message == 'Enter admin passowrd':
            send_string(client_firewall, input('Enter admin password: '))
        elif message == 'logged in':
            print('Logged in as admin')
            is_admin = 2
        elif message == 'wrong password':
            print('Wrong password\n')
            is_admin = 0
        elif 'invalids' in message:
            port_list = message.split()
            if len(port_list) == 1:
                invalid_ports = set()
            else:
                invalid_ports = set(map(int, port_list[1:]))
        # elif re.fullmatch(r"(\d+?\s?)*", message.strip()):
        #     print("debug", message)
        #     invalid_ports = set(map(int, message.split()))
        #     print(invalid_ports)
        
        

client_firewall = socket.socket()
client_firewall.connect((HOST, SERVER_PORTS['firewall']))
threading.Thread(target=handle_firewall, daemon=True).start()
time.sleep(0.5)

command = ''
while True:
    command = input('1. Connect to external servers\n2. Login as admin\n3. Exit\n')
    if command == '1':
        command = input("Enter server name\n")
        connect_to_server(command)
    elif command == '2':
        admin()
    elif command == '3':
        break
    else:
        print('invalid command')
