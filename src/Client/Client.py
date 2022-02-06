from concurrent.futures import thread
import re
import socket
import threading
import json
from typing import Dict
import time
import base64
import cv2
import imutils
import numpy as np
import socket


HOST = 'localhost'
SERVER_PORTS = {'choghondar': 6969,
                "shalgham": 8585,
                'proxy': [1111, 2222, 3333],
                "firewall": 6985}

BUFF_SIZE = 65536
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
    elif server_name == 'shalgham':
        read_shalgham()


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
        client.close()
        
        
def read_shalgham():
    global message, connected, state
    state = 'memu'
    try:
        menu = client.recvfrom(BUFF_SIZE)[0].decode('ascii')
        print(menu)
        client.sendto(input().encode('ascii'), (HOST, port))
        while True:
            packet, _ = client.recvfrom(BUFF_SIZE)
            data = base64.b64decode(packet, ' /')
            np_data = np.fromstring(data, dtype=np.uint8)
            frame = cv2.imdecode(np_data, 1)
            # frame = cv2.putText(frame, 'FPS: ' + str(fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow("RECEIVING VIDEO", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                connected = False
                client.close()
                break
            # if cnt == frames_to_count:
                # try:
                    # fps = round(frames_to_count / (time.time() - st))
                    # st = time.time()
                    # cnt = 0
                # except:
                    # pass
            # cnt += 1
        
        # while connected:
        #     if state != "stream": # TODO: ?
        #         command = read_json(client)
        #     message = read_string(client)
        #     time.sleep(1)
        #     if message:
        #         print(f"{message}")
        #     # if message == 'exit':
        #     #     connected = False
    except (ConnectionError, TypeError) as e:
        client.close()
        

# def handle_shalgham():
#     global state
#     try:
#         while connected:
#             if state == 'menu':
#                 print('kiri')
#                 client.sendto(input().encode('ascii'), (HOST, port))
#                 state = 'submit'
#             # elif state == 'stream':
#             #     command = input()
#             #     if command == 'q':
                    
#     except ConnectionError as e:
#         client.close()

def handle(server_name):
    if server_name == 'choghondar':
        handle_choghondar()
    # elif server_name == 'shalgham':
    #     handle_shalgham()


def connect_to_server(server_name):
    global connected, client, port
    if 'via' in server_name:
        server_name, port = server_name.split(' via ')
        port = int(port)
    else:  
        port = SERVER_PORTS[server_name]
    if server_name not in SERVER_PORTS:
        print('invalid server')
        port = 0
        return
    if port in invalid_ports:
        print('packet dropped due to firewall rules')
        port = 0
        return
    if server_name == 'shalgham':
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
        client.sendto("hi".encode('ascii'), (HOST, port)) 
        if port in SERVER_PORTS['proxy']:
            # send_string(client, server_name)
            pass
    else: 
        client = socket.socket()
        client.connect((HOST, port))
        if port in SERVER_PORTS['proxy']:
            send_string(client, server_name)
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
