import threading
from lib.player import Player
from services.match_thread import MatchThread


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
        import server
        server.stop_clientThread(self)

    def get_player(self) -> Player:
        """Returns Player object"""
        return self.player

    def get_player_username(self) -> str:
        """Returns Player username"""
        return self.player.get_username()

    def get_clientAddress(self) -> str:
        """Returns Client Address in form of '(IP Address),(Port)'"""
        return self.clientAddress[0] + "," + str(self.clientAddress[1])

    def set_matchThread(self, matchThread: MatchThread):
        self.matchThread = matchThread
