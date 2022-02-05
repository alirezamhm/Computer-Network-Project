from os import stat
import socket
import threading
import time
import random
import sys
import json
from typing import Dict
from User import User
from Utill.Chatbox import Chatbox

HOST = 'localhost'
PORT = 6969
MENU_STRING = 'Menu\n1. Sign Up\n2. Login\n3. Exit'

server = socket.socket()
server.bind((HOST, PORT))
server.listen()

users: Dict[str, User] = {} # username: user
clients = {} # port: client socket

# def handle_client(port):
#     client = clients[port]
#     send_menu(client)
    
def read_client(port):
    client = clients[port]
    state = 'menu'
    send(client, MENU_STRING, state)
    username = ''
    while True:
        command = read(client)
        if not command:
            continue
        message = command['message'].strip()
        if state == 'menu':
            if message == '1':
                state = 'sign up - username'
                send(client, 'Please enter your username.', state)
            elif message == '2':
                state = 'login - username'
                send(client, "Please enter your username.", state)
            elif message == '3':
                clients.pop(port)
                break
        elif state == 'sign up - username':
            if message in users:
                send(client, "This username is already existed or invalid. Please enter another one.", state)
                continue
            username = message
            state = 'sign up - password'
            send(client, 'Please enter your password.', state)
        elif state == 'sign up - password':
            password = message
            users[username] = User(username, password)
            state = 'menu'
            send(client, "Successful\n"+MENU_STRING, state)
            username = ''
        elif state == 'login - username':
            username = message
            state = 'login - password'
            send(client, "Please enter your password.", state)
        elif state == 'login - password':
            if username not in users or users[username].password != message:
                state = 'menu'
                send(client, "Incorrect username or password.\n"+MENU_STRING, state)
                continue
            users[username].online = True
            state = 'inbox'
            send(client, get_inbox(), state)
        elif state == 'inbox':
            if message not in users:
                send(client, "User not found", state)
                continue
            chatbox = get_chatbox()
            state == 'chatbox'
            send(client, chatbox.__dict__(), state)
            
            
def get_chatbox() -> Chatbox: 
    pass

def get_inbox(user: User) -> str:
    pass

def read(client: socket.socket) -> dict:
    try:
        return json.loads(client.recv(1024).decode('ascii'))
    except ConnectionError or ConnectionResetError or OSError:
        print('Connection Error')
        client.close()


def send(client: socket.socket, message, state: str =''):
    msg = json.dumps({'message': message, 'state': state})
    client.send(msg.encode('ascii'))
    
while True:
    client, address = server.accept()
    port = address[1]
    clients[port] = client
    # threading.Thread(target=handle_client, args=(port,), daemon=True).start()
    threading.Thread(target=read_client, args=(port,), daemon=True).start()

    