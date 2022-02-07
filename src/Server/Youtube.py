import base64
import threading

import cv2
import imutils
import socket

from sympy import arg

BUFF_SIZE = 65536
WIDTH = 400
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
host_ip = 'localhost'
port = 8585
videos = {
    "House of Gucci" : r'C:\Users\Asus\Videos\Temp\House of Gucci.mkv',
    "Boba fett": r'C:\Users\Asus\Videos\Temp\Boba fett.mkv',
    "Peacemaker": r'C:\Users\Asus\Videos\Temp\Peacemaker.mkv'
}

video_list = ''
for i, k in enumerate(videos.keys()):
    video_list += f"{i+1}. {k}\n"

server_socket.bind((host_ip, port))
connected = False
# server_socket.listen()

def read_client():
    global connected
    while True:
        message = server_socket.recvfrom(BUFF_SIZE)[0].decode('ascii')
        if message == 'q':
            connected = False
            return
        

while True:
    # client, address = server_socket.accept()
    m , client_addr = server_socket.recvfrom(BUFF_SIZE)
    connected = True
    server_socket.sendto(f"Welcome to Choghondar.\n{video_list}".encode('ascii'), client_addr)
    movie_index = int(server_socket.recvfrom(BUFF_SIZE)[0].decode('ascii')) - 1
    video = cv2.VideoCapture(videos[list(videos.keys())[movie_index]])
    # try:
    threading.Thread(target=read_client, args=(), daemon=True).start()
    while video.isOpened() and connected:
        _, frame = video.read()
        frame = imutils.resize(frame, width=WIDTH)
        encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        message = base64.b64encode(buffer)
        server_socket.sendto(message, client_addr)
    # except (ConnectionError, ConnectionResetError) as e:
    #     pass
    print("Client exited")
