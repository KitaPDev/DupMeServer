import socket

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect(('127.0.0.1', 54321))
clientSocket.send('a'.encode())
print(clientSocket.recv(1024).decode())

clientSocket.close()
