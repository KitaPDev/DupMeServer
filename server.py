import socket
import random
import threading
from lib.player import Player

TCP_IP = '0.0.0.0'
TCP_PORT = 54321

# for Heroku
# import os
# TCP_PORT = os.environ['PORT']


class ClientThread(threading.Thread):

    stop_flag = False

    player = Player('')
    matchThread = None
    isPlaying = False

    def __init__(self, clientSocket, clientAddress):
        threading.Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket

        print("Log: Client added:", clientAddress[0], ":", clientAddress[1], "\n")

    def run(self):
        print("Log: Running thread " + self.getName() + "\n")

        while True:

            if self.stop_flag:
                break

            receivedData = self.clientSocket.recv(1024).decode()
            print(self.getName() + ": Received data:" + receivedData + "\n")
            receivedData = receivedData.split()

            if len(receivedData) == 0:
                self.clientSocket.send("Invalid Process Request Syntax!".encode())
                self.clientSocket.close()
                self.stop()
                break

            elif len(receivedData) == '':
                print((self.getName() + ": Client closed connection... closing server connection").encode())
                self.matchThread.stop()
                self.clientSocket.close()
                self.stop()
                break

            else:
                strClassName = receivedData[0]
                strMethodName = receivedData[1]
                lsParameters = [data for data in receivedData[2:]]

                if strClassName == 'Player':

                    if strMethodName == 'set_username':
                        if len(lsParameters) == 0:
                            self.player.set_username(lsParameters[0])

                        else:
                            print(self.getName() + ": Invalid Parameters: " + (str(i + " " for i in receivedData)))
                            self.clientSocket.send("Invalid Parameters".encode())
                            continue

                elif strClassName == 'MatchThread':

                    if strMethodName == 'add_score':

                        if len(lsParameters) == 1:
                            self.matchThread.add_score_player(int(lsParameters[0]))

                    if strMethodName == 'key_click':

                        key_id = lsParameters[0]

                        if key_id == 'C':
                            self.matchThread.key_clicked('C')

                        elif key_id == 'D':
                            self.matchThread.key_clicked('D')

                        elif key_id == 'E':
                            self.matchThread.key_clicked('E')

                        elif key_id == 'F':
                            self.matchThread.key_clicked('F')

                        elif key_id == 'G':
                            self.matchThread.key_clicked('G')

                        elif key_id == 'A':
                            self.matchThread.key_clicked('A')

                        elif key_id == 'B':
                            self.matchThread.key_clicked('B')

                    elif strMethodName == 'end_turn':
                        self.isPlaying = False

                    elif strMethodName == 'end_match':

                        if len(lsParameters) > 0:
                            self.matchThread.update_scores_opponent(self, lsParameters)

                    elif strMethodName == 'play_again':
                        self.matchThread.play_again()

                else:
                    self.clientSocket.send("Invalid Process Request Syntax!".encode())
                    self.clientSocket.close()
                    self.stop()
                    break

        print("Log: " + self.getName() + " closed\n")

    def tx_start_turn(self):
        """Sends start signal"""
        self.clientSocket.send("start_turn".encode())

    def tx_stop_match(self):
        """Sends stop signal"""
        self.clientSocket.send("stop_match".encode())

    def tx_add_score(self, score: int):
        """Adds to Player's current score"""
        self.clientSocket.send(("add_score " + str(score)).encode())

    def tx_profile_opponent(self, username: str):
        """Sends Opponent's Profile (e.g. Username) to Client via TCP socket"""
        self.clientSocket.send(("profile_opponent " + username).encode())

    def tx_start_turn_opponent(self):
        self.clientSocket.send("start_turn_opponent".encode())

    def tx_key_click_opponent(self, key_id: str):
        """Sends Opponent's Key Click ID"""
        self.clientSocket.send(("key_click_opponent " + key_id).encode())

    def tx_add_score_opponent(self, score: int):
        """Sends Opponent's Score to Client via TCP socket"""
        self.clientSocket.send(("add_score_opponent " + str(score)).encode())

    def tx_scores_opponent(self, scores: list):
        """Sends Opponent's Scores in each round via TCP socket"""
        strData = "scores_opponent "

        for i in scores:
            if i == scores[len(scores)-1]:
                strData = strData + str(i)
            strData = strData + str(i) + " "

        self.clientSocket.send(strData.encode())

    def stop(self):
        """Informs MainServer Thread and main thread that this ClientThread has stopped."""
        stop_clientThread(self)

    def get_player(self) -> Player:
        """Returns Player object"""
        return self.player

    def get_player_username(self) -> str:
        """Returns Player username"""
        return self.player.get_username()

    def get_clientAddress(self) -> str:
        """Returns Client Address in form of '(IP Address),(Port)'"""
        return self.clientAddress[0] + "," + str(self.clientAddress[1])


class MatchThread(threading.Thread):

    stop_flag = False
    play_again_flag = False

    rounds = 1
    clientThread_waiting: ClientThread
    clientThread_playing: ClientThread
    score_clientThread1: list
    score_clientThread2: list

    def __init__(self, clientThread1: ClientThread, clientThread2: ClientThread):
        super().__init__()
        self.clientThread1 = clientThread1
        self.clientThread2 = clientThread2

        strUsername_client1 = clientThread1.get_player_username()
        strUsername_client2 = clientThread2.get_player_username()

        clientThread1.tx_profile_opponent(strUsername_client2)
        clientThread2.tx_profile_opponent(strUsername_client1)

        self.clientThread_playing = clientThread1
        self.clientThread_waiting = clientThread2
        self.clientThread_playing.tx_start_turn()
        self.clientThread_playing.isPlaying = True

    def run(self):
        while self.clientThread1.isAlive() and self.clientThread2.isAlive():

            if self.stop_flag:
                break

            if not self.clientThread_playing.isPlaying:

                if self.clientThread_playing == self.clientThread1:
                    self.clientThread1.isPlaying = False

                    self.clientThread_playing = self.clientThread2
                    self.clientThread_waiting = self.clientThread1
                    self.clientThread_playing.tx_start_turn()
                    self.clientThread_playing.isPlaying = True

                elif self.clientThread_playing == self.clientThread2:
                    self.clientThread2.isPlaying = False

                    self.clientThread_playing = self.clientThread1
                    self.clientThread_waiting = self.clientThread2
                    self.clientThread_playing.tx_start_turn()
                    self.clientThread_playing.isPlaying = True

    def add_score_player(self, score: int):
        """Add playing player's score to waiting player's playing player's score"""
        self.clientThread_waiting.tx_add_score_opponent(score)

        if self.clientThread_playing == self.clientThread1:

            currentScore = self.score_clientThread1[self.rounds - 1]
            self.score_clientThread1[self.rounds - 1] = currentScore + score

        elif self.clientThread_playing == self.clientThread2:

            currentScore = self.score_clientThread2[self.rounds - 1]
            self.score_clientThread2[self.rounds - 1] = currentScore + score

    def update_scores_opponent(self, clientThread: ClientThread, scores: list):
        if clientThread == self.clientThread1:
            self.clientThread2.tx_scores_opponent(scores)

        elif clientThread == self.clientThread2:
            self.clientThread1.tx_scores_opponent(scores)

    def key_clicked(self, key_id: str):
        self.clientThread_waiting.tx_key_click_opponent(key_id)

    def play_again(self):
        self.rounds = self.rounds + 1

        if self.score_clientThread1[self.rounds - 1] > self.score_clientThread2[self.rounds - 1]:
            self.clientThread2.isPlaying = False

            self.clientThread_playing = self.clientThread1
            self.clientThread_waiting = self.clientThread2
            self.clientThread_playing.tx_start_turn()
            self.clientThread_playing.isPlaying = True

        else:
            self.clientThread1.isPlaying = False

            self.clientThread_playing = self.clientThread2
            self.clientThread_waiting = self.clientThread1
            self.clientThread_playing.tx_start_turn()
            self.clientThread_playing.isPlaying = True

    def stop(self):
        if self.clientThread1.isAlive():
            self.clientThread1.tx_stop_match()

        elif self.clientThread2.isAlive():
            self.clientThread2.tx_stop_match()

        self.stop_flag = True


class MainServer(threading.Thread):
    stop_flag = False

    lsClientThreads = []
    lsClientThreads_unmatched = []

    def __init__(self, ip_address, port):
        super().__init__()
        self.setName('Thread-MainServer')
        self.ipAddress = ip_address
        self.port = port

    def run(self):
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((TCP_IP, TCP_PORT))

        print(self.getName() + ": Server started")
        print(self.getName() + ": Waiting on port", TCP_PORT)

        while True:
            if self.stop_flag:
                break

            serverSocket.listen(10)
            (clientSocket, clientAddress) = serverSocket.accept()
            clientThread = ClientThread(clientSocket, clientAddress)

            self.lsClientThreads.append(clientThread)

            clientThread.run()

    def get_clientThreads(self) -> []:
        """Returns a list of running ClientThreads."""
        return self.lsClientThreads

    def remove_clientThread(self, clientThread: ClientThread):
        """Removes stopped ClientThread from MainServer thread list."""
        self.lsClientThreads.remove(clientThread)

    def stop(self):
        self.stop_flag = True


lsClientThreads_unmatched = []
lsMatchThreads_inProgress = []


def stop_clientThread(clientThread):
    """Removes stopped ClientThread from MainServer thread and main thread list."""
    mainServerThread.remove_clientThread(clientThread)


mainServerThread = MainServer(TCP_IP, TCP_PORT)
mainServerThread.start()

while True:
    if mainServerThread.isAlive():
        lsClientThreads_unmatched = mainServerThread.get_clientThreads()

    if len(lsClientThreads_unmatched) >= 2:
        iFirstClientThread = int(random.randrange(0, len(lsClientThreads_unmatched)))
        iSecondClientThread = int(random.choice(range(0, iFirstClientThread) + range(iFirstClientThread,
                                                                                     len(lsClientThreads_unmatched))))
        firstClientThread = ClientThread
        secondClientThread = ClientThread
        # noinspection PyRedeclaration
        firstClientThread = lsClientThreads_unmatched[iFirstClientThread]
        # noinspection PyRedeclaration
        secondClientThread = lsClientThreads_unmatched[iSecondClientThread]

        matchThread = MatchThread(firstClientThread, secondClientThread)
        firstClientThread.matchThread(matchThread)
        secondClientThread.matchThread(matchThread)
        matchThread.start()

        mainServerThread.remove_clientThread(firstClientThread)
        mainServerThread.remove_clientThread(secondClientThread)

        lsClientThreads_unmatched.remove(firstClientThread)
        lsClientThreads_unmatched.remove(secondClientThread)

        lsMatchThreads_inProgress.append(matchThread)
