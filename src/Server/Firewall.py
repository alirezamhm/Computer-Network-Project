import socket
import threading


HOST = 'localhost'
PORT = 6985
SERVER_PORTS = set([6969, 8585, 1111, 2222, 3333])


server = socket.socket()
server.bind((HOST, PORT))
server.listen()
admin_password = ''
clients = []
invalid_ports = set()


def send(client: socket.socket, message: str):
    client.send(message.encode('ascii'))

def send_to_all(message: str):
    for client in clients:
        send(client, message)

def read(client: socket.socket):
    return client.recv(1024).decode('ascii').strip()

def handle_client(client: socket.socket): 
    global invalid_ports
    update_clients()
    while True:
        try:
            message = read(client)
            if message == 'login':
                send(client, 'Enter admin passowrd')
                password = read(client)
                if password == admin_password:
                    send(client, 'logged in')
                else:
                    send(client, 'wrong password')
            elif message == 'activate whitelist firewall':
                invalid_ports = set()
                update_clients()
            elif message == 'activate blacklist firewall':
                invalid_all_ports()
                update_clients()
            elif 'open port' in message:
                open_port(int(message.split()[-1]))
                update_clients()
            elif 'close port' in message:
                close_port(int(message.split()[-1]))
                update_clients()
        except (ConnectionError, ConnectionResetError) as e:
            break
        

def update_clients():
    send_to_all('invalids '+' '.join(map(str, invalid_ports)))

def invalid_all_ports():
    global invalid_ports
    for port in SERVER_PORTS:
        invalid_ports.add(port)

def open_port(port: int):
    global invalid_ports
    if port in invalid_ports:
        invalid_ports.remove(port)

def close_port(port: int):
    global invalid_ports
    invalid_ports.add(port)

while True:
    client, address = server.accept()
    clients.append(client)
    if not admin_password:
        send(client, "Enter admin passowrd")
        admin_password = read(client)
    threading.Thread(target=handle_client, args=(client, ), daemon=True).start()
    
        
