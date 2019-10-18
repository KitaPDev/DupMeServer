import threading
from services.client_thread import ClientThread


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
