from Utill.Chatbox import Chatbox

class User():
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password
        self.online = False
        self.chats = []
    
    def __hash__(self) -> int:
        return hash(self.username)

    def add_chat(self, other):
        self.chats.append(Chatbox(self, other))