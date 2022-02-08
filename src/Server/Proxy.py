import socket
import threading


HOST = 'localhost'
PORT = int(input("Proxy Port: "))
SERVER_PORTS = {'choghondar': 6969,
                "shalgham": 8585,
                'proxy': [1111, 2222, 3333],
                "firewall": 6985}

proxy_server = socket.socket()
proxy_server.bind((HOST, PORT))
proxy_server.listen()

def send(client: socket.socket, message: str):
    client.send(message.encode('ascii'))

def read(client: socket.socket):
    return client.recv(1024).decode('ascii').strip()


def client_to_server(client:socket.socket, server:socket.socket):
    while True:
        try:
            message = read(client)
            send(server, message)
        except ConnectionError as e:
            break
        

def server_to_client(client:socket.socket, server:socket.socket):
    while True:
        try:
            message = read(server)
            send(client, message)
        except ConnectionError as e:
            break

while True:
    client, address = proxy_server.accept()
    server_name = read(client)
    server = socket.socket()
    server.connect((HOST, SERVER_PORTS[server_name]))
    threading.Thread(target=client_to_server, args=(client, server,), daemon=True).start()
    threading.Thread(target=server_to_client, args=(client, server,), daemon=True).start()

    
