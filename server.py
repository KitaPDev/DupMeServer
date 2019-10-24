import socket
import threading
import random
import time
from datetime import datetime
from tkinter import *

TCP_IP = '0.0.0.0'
TCP_PORT = 54321

lsClientThreads = []
lsPlayers = []
lsPlayers_ready = []
dictPlayer_key = {}
dictPlayer_startBit = {}
root = Tk()
text = StringVar()


class ClientThread(threading.Thread):
    strUsername = ''
    strUsernameOpponent = ''
    reset = False

    def __init__(self, clientSocket: socket.socket, clientAddress):
        super().__init__()
        self.clientSocket = clientSocket
        self.clientAddress = clientAddress

    def run(self):

        while True:
            recvData = self.clientSocket.recv(1024).decode()
            recvData = recvData.split()

            print(self.getName(), "Received Data:", recvData)

            recvData = [data.replace('b\'', '\'') for data in recvData]

            if len(recvData) == 0:
                self.clientSocket.close()
                lsPlayers.remove(self.strUsername)
                lsPlayers_ready.remove(self.strUsername)
                print(str(datetime.now()), 'Client closed:', self.clientAddress[0], ':', self.clientAddress[1])
                break

            elif recvData[0] == 'set_username':

                if len(recvData) == 1:
                    self.clientSocket.send('BAD\n'.encode())

                elif recvData[1] not in lsPlayers:
                    lsPlayers.append(recvData[1])
                    self.strUsername = recvData[1]
                    self.clientSocket.send('OK\n'.encode())

                else:
                    self.clientSocket.send('BAD\n'.encode())

            else:

                if len(self.strUsername) > 0:
                    if self.strUsername not in lsPlayers:
                        self.clientSocket.send('opponent_left\n'.encode())
                        self.clientSocket.close()
                        break

                if self.reset:
                    self.clientSocket.send('RST\n'.encode())
                    self.reset = False

                if recvData[0] == 'close':
                    if self.strUsername in lsPlayers:
                        lsPlayers.remove(self.strUsername)

                    if len(self.strUsernameOpponent) > 0:
                        lsPlayers.remove(self.strUsernameOpponent)

                        if self.strUsername in dictPlayer_key.keys():
                            del dictPlayer_key[self.strUsername]
                            del dictPlayer_key[self.strUsernameOpponent]
                            del dictPlayer_startBit[self.strUsername]
                            del dictPlayer_startBit[self.strUsernameOpponent]

                elif recvData[0] == 'find_match':
                    while len(lsPlayers) < 2:
                        pass

                    lsPlayers_temp = []
                    for player in lsPlayers:
                        lsPlayers_temp.append(player)
                    lsPlayers_temp.remove(self.strUsername)
                    random.shuffle(lsPlayers_temp)

                    self.strUsernameOpponent = lsPlayers_temp[0]
                    strData = self.strUsernameOpponent

                    strData = strData + '\n'
                    self.clientSocket.send(strData.encode())

                elif recvData[0] == 'get_start_bit':
                    if self.strUsernameOpponent in dictPlayer_startBit.keys():
                        if dictPlayer_startBit[self.strUsernameOpponent] == 1:
                            dictPlayer_startBit[self.strUsername] = 0

                        else:
                            dictPlayer_startBit[self.strUsername] = 1

                    else:
                        if random.randint(0, 1) == 1:
                            dictPlayer_startBit[self.strUsername] = 1

                        else:
                            dictPlayer_startBit[self.strUsername] = 0

                    strData = str(dictPlayer_startBit[self.strUsername]) + '\n'
                    self.clientSocket.send(strData.encode())

                elif recvData[0] == 'ready':
                    lsPlayers_ready.append(self.strUsername)

                    while True:
                        if self.strUsernameOpponent in lsPlayers_ready:
                            self.clientSocket.send('1\n'.encode())
                            break

                elif recvData[0] == 'C':
                    dictPlayer_key[self.strUsername] = 'C'

                elif recvData[0] == 'D':
                    dictPlayer_key[self.strUsername] = 'D'

                elif recvData[0] == 'E':
                    dictPlayer_key[self.strUsername] = 'E'

                elif recvData[0] == 'F':
                    dictPlayer_key[self.strUsername] = 'F'

                elif recvData[0] == 'G':
                    dictPlayer_key[self.strUsername] = 'G'

                elif recvData[0] == 'A':
                    dictPlayer_key[self.strUsername] = 'A'

                elif recvData[0] == 'B':
                    dictPlayer_key[self.strUsername] = 'B'

                elif recvData[0] == 'get_key':

                    while True:
                        if self.strUsernameOpponent in dictPlayer_key.keys():

                            if len(dictPlayer_key[self.strUsernameOpponent]) > 0:
                                strData = dictPlayer_key[self.strUsernameOpponent]

                                strData = strData + '\n'

                                self.clientSocket.send(strData.encode())

                            else:
                                pass

                else:
                    self.clientSocket.send("Invalid message syntax!\n".encode())

                    print(self.getName(), "Invalid message syntax!")

    def resetMatch(self):
        self.reset = True


class Server(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverSocket.bind((TCP_IP, TCP_PORT))

            print(str(datetime.now()), 'Server started... waiting on port ' + str(TCP_PORT))

            serverSocket.listen(10)
            (clientSocket, clientAddress) = serverSocket.accept()
            clientThread = ClientThread(clientSocket, clientAddress)
            clientThread.setName('Client' + clientThread.getName())

            lsClientThreads.append(clientThread)

            print(str(datetime.now()), 'Client accepted:', clientAddress[0], ':', clientAddress[1])

            clientThread.start()


def resetMatch():
    for t in threading.enumerate():
        if 'ClientThread' in t.getName():
            t: ClientThread
            t.resetMatch()

    print('Scores Reset')


def updateLabel():
    while True:
        for t in lsClientThreads:
            lsClientThreads.remove(t)

        for t in threading.enumerate():
            if 'ClientThread' in t.getName():
                if t not in lsClientThreads:
                    lsClientThreads.append(t)

        text.set('Concurrent Clients: ' + str(len(lsClientThreads)))
        time.sleep(0.1)


server = Server()
server.start()

root.title('DupMe Server')
root.geometry('300x300')

labelThread = threading.Thread(target=updateLabel, args=[])
labelThread.start()

labelClients = Label(root, textvariable=text)
labelClients.pack()

btnReset = Button(root, text="Reset", command=resetMatch)
btnReset.pack()

root.mainloop()
