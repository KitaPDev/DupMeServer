class Player:

    username = ''

    def __init__(self, username):
        self.username = username

    def get_username(self):
        return self.username

    def set_username(self, username):
        self.username = username
