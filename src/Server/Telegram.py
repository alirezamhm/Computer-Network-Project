import socket
import threading
import time
import random
import sys

HOST = 'localhost'
PORT = 6969

server = socket.socket()
server.bind((HOST, PORT))
server.listen()

