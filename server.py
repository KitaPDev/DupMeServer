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
dictPlayer_Opponent = {}
dictPlayer_lsKeys = {}
dictPlayer_StartFlag = {}

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

                if len(self.strUsername) > 0:
                    if self.strUsername in lsPlayers:
                        lsPlayers.remove(self.strUsername)

                    if len(self.strUsernameOpponent) > 0:
                        lsPlayers.remove(self.strUsernameOpponent)

                        if self.strUsername in dictPlayer_Opponent.keys():
                            self.strUsernameOpponent = dictPlayer_Opponent[self.strUsername]
                            del dictPlayer_Opponent[self.strUsername]
                            del dictPlayer_Opponent[self.strUsernameOpponent]

                        if self.strUsername in dictPlayer_lsKeys.keys():
                            del dictPlayer_lsKeys[self.strUsername]
                            del dictPlayer_lsKeys[self.strUsernameOpponent]

                        if self.strUsername in dictPlayer_StartFlag.keys():
                            del dictPlayer_StartFlag[self.strUsername]

                print(str(datetime.now()), 'Client closed:', self.clientAddress[0], ':', self.clientAddress[1])
                break

            elif recvData[0] == 'set_username':

                if len(recvData) == 1:
                    self.clientSocket.send('BAD\n'.encode())

                if recvData[1] not in lsPlayers:
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

                        if self.strUsername in dictPlayer_Opponent.keys():
                            self.strUsernameOpponent = dictPlayer_Opponent[self.strUsername]
                            del dictPlayer_Opponent[self.strUsername]
                            del dictPlayer_Opponent[self.strUsernameOpponent]

                        if self.strUsername in dictPlayer_lsKeys.keys():
                            del dictPlayer_lsKeys[self.strUsername]
                            del dictPlayer_lsKeys[self.strUsernameOpponent]

                        if self.strUsername in dictPlayer_StartFlag.keys():
                            del dictPlayer_StartFlag[self.strUsername]

                if recvData[0] == 'find_match':
                    startIndex = random.randint(0, 1)

                    if len(lsPlayers) < 2:
                        self.clientSocket.send('REQ_AGAIN\n'.encode())

                    else:
                        if self.strUsername in dictPlayer_Opponent.keys():

                            strData: str = dictPlayer_Opponent[self.strUsername]

                            if startIndex == 0:
                                strData = strData + ' start'
                                dictPlayer_StartFlag[self.strUsername] = True

                            strData = strData + "\n"
                            self.clientSocket.send(strData.encode())

                        else:
                            lsPlayers_inMatch = [dictPlayer_Opponent[player] for player in lsPlayers]
                            lsPlayers_unmatched = lsPlayers
                            lsPlayers_unmatched.remove(self.strUsername)

                            for player in lsPlayers_inMatch:
                                lsPlayers_unmatched.remove(player)

                            self.strUsernameOpponent: str = lsPlayers_unmatched[
                                random.randrange(0, len(lsPlayers_unmatched) - 1)]
                            dictPlayer_Opponent[self.strUsername] = self.strUsernameOpponent
                            dictPlayer_Opponent[self.strUsernameOpponent] = self.strUsername

                            strData = self.strUsernameOpponent

                            if startIndex == 1:
                                strData = strData + ' start'
                                dictPlayer_StartFlag[self.strUsername] = True

                            strData = strData + "\n"
                            self.clientSocket.send(strData.encode())

                elif recvData[0] == 'C':
                    dictPlayer_lsKeys[self.strUsername] = list(dictPlayer_lsKeys[self.strUsername]).append('C')
                    self.clientSocket.send('OK\n'.encode())

                elif recvData[0] == 'D':
                    dictPlayer_lsKeys[self.strUsername] = list(dictPlayer_lsKeys[self.strUsername]).append('D')
                    self.clientSocket.send('OK\n'.encode())

                elif recvData[0] == 'E':
                    dictPlayer_lsKeys[self.strUsername] = list(dictPlayer_lsKeys[self.strUsername]).append('E')
                    self.clientSocket.send('OK\n'.encode())

                elif recvData[0] == 'F':
                    dictPlayer_lsKeys[self.strUsername] = list(dictPlayer_lsKeys[self.strUsername]).append('F')
                    self.clientSocket.send('OK\n'.encode())

                elif recvData[0] == 'G':
                    dictPlayer_lsKeys[self.strUsername] = list(dictPlayer_lsKeys[self.strUsername]).append('G')
                    self.clientSocket.send('OK\n'.encode())

                elif recvData[0] == 'A':
                    dictPlayer_lsKeys[self.strUsername] = list(dictPlayer_lsKeys[self.strUsername]).append('A')
                    self.clientSocket.send('OK\n'.encode())

                elif recvData[0] == 'B':
                    dictPlayer_lsKeys[self.strUsername] = list(dictPlayer_lsKeys[self.strUsername]).append('B')
                    self.clientSocket.send('OK'.encode())

                elif recvData[0] == 'get_keys':
                    self.strUsernameOpponent = dictPlayer_Opponent[self.strUsername]

                    while True:
                        if len(dictPlayer_lsKeys[self.strUsernameOpponent]) > 0:
                            strData = ''

                            for key in dictPlayer_lsKeys[self.strUsernameOpponent]:
                                strData = key + ' '

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
