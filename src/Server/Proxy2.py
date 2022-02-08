import socket



HOST = 'localhost'
PORT = int(input("Proxy Port: "))
SERVER_PORTS = {'choghondar': 6969,
                "shalgham": 8585,
                'proxy': [1111, 2222, 3333],
                "firewall": 6985}

BUFF_SIZE = 65536
proxy_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
proxy_server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
proxy_server.bind((HOST, PORT))
client_addr = None
server_addr = None

def send(message, addr):
    proxy_server.sendto(message, addr)

def read():
    m = proxy_server.recvfrom(BUFF_SIZE)
    return m

def handle():
    while True:
        try:
            message, addr = read()
            if addr == client_addr:
                print(m[0])
                send(message, server_addr)
            elif addr == server_addr:
                send(message, client_addr)
            else:
                print("noway")
        except ConnectionError as e:
            break

while True:
    server_addr = (HOST, SERVER_PORTS['shalgham'])
    m , client_addr = read()
    send(m, server_addr)
    m, server_addr = read()
    send(m, client_addr)
    connected = True
    while connected:
        message, addr = read()
        if addr == client_addr:
            send(message, server_addr)
            if message.decode('ascii') == 'q':
                connected = False
        elif addr == server_addr:
            send(message, client_addr)
        else:
            print("noway")


    
