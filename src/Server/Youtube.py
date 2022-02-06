import base64

import cv2
import imutils
import socket

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
# server_socket.listen()

# client, address = server_socket.accept()
m , client_addr = server_socket.recvfrom(BUFF_SIZE)
# print(m)
server_socket.sendto(f"Welcome to Choghondar.\n{video_list}".encode('ascii'), client_addr)
movie_index = int(server_socket.recvfrom(BUFF_SIZE)[0].decode('ascii')) - 1

video = cv2.VideoCapture(videos[list(videos.keys())[movie_index]])

try:
    while video.isOpened():
        _, frame = video.read()
        frame = imutils.resize(frame, width=WIDTH)
        encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        message = base64.b64encode(buffer)
        server_socket.sendto(message, client_addr)
except (ConnectionError, ConnectionResetError) as e:
    pass
    # frame = cv2.putText(frame, 'FPS: ' + str(fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    # cv2.imshow('TRANSMITTING VIDEO', frame)
    # key = cv2.waitKey(1) & 0xFF
    # if key == ord('q'):
    #     server_socket.close()
    #     break
    # if cnt == frames_to_count:
    #     try:
    #         fps = round(frames_to_count / (time.time() - st))
    #         st = time.time()
    #         cnt = 0
    #     except:
    #         pass
    # cnt += 1