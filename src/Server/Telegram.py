import socket
import threading
import time
import random
import sys
import json
from typing import Dict

from matplotlib.style import use
from urllib3 import Retry
from User import User
from Chatbox import Chatbox
from Message import Message

HOST = 'localhost'
PORT = 6969
MENU_STRING = 10*'*' + '\nMenu\n1. Sign Up\n2. Login\n3. Exit\n' + 10*'*'

server = socket.socket()
server.bind((HOST, PORT))
server.listen()

users: Dict[str, User] = {} # username: user
clients = {} # port: client socket


# def handle_client(port):
#     client = clients[port]
#     send_menu(client)
    
def handle_client(port):
    client = clients[port]
    state = 'menu'
    send(client, MENU_STRING, state)
    username = ''
    chat_othername = ''
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
            users[username].client = client
            state = 'inbox'
            send(client, get_inbox(username), state)
            
        elif state == 'inbox':
            if message == '0':
                send(client, "exit", "")
                return
            if message not in users:
                send(client, "User not found", state)
                continue
            
            chat_othername = message
            chatbox = get_chatbox(username, message)
            state = 'chatbox'
            send(client, chatbox.get_messages_dict(5, username), state)
            
        elif state == 'chatbox':
            if '/load' in message:
                send(client, chatbox.get_messages_dict(int(message.split()[-1]), username), state)
            elif '/exit' in message:
                state = 'inbox'
                chatbox = users[username].chats[chat_othername]
                chatbox.update_online(username, False)
                chatbox.reset_seens(username)
                send(client, get_inbox(username), state)
            else:
                send_chat(username, chat_othername, message)

def send_chat(username, othername, message):
    user = users[username]
    other = users[othername]
    chatbox = user.chats[othername]
    chatbox.send_message(username, othername, message)
    if chatbox.onlines[othername]:
        send(other.client, {'username': othername, 'messages': [msg.to_dict()]}, "chatbox")
  
            
def get_chatbox(username, othername) -> Chatbox: 
    user = users[username]
    other = users[othername]
    if user.get_chat(othername):
        chat = user.get_chat(othername)
    else:
        chat = Chatbox(username, othername)
        user.add_chat(othername, chat)
        other.add_chat(username, chat)
    chat.update_online(username, True)
    return chat

def get_inbox(username) -> str:
    user = users[username]
    chats = sorted(list(user.chats.values()), reverse=True)
    chat_list = "\n".join([chat.get_string(username) for chat in chats])
    return f'{10*"*"}\nInbox\n{chat_list}\n{10*"*"}'


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
    threading.Thread(target=handle_client, args=(port,), daemon=True).start()

    