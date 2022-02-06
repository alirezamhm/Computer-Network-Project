import Chatbox

class User():
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password
        self.online = False # TODO: remove
        self.chats = {}   # ohter_username: Chatbox
        self.client = None
        
    
    def __hash__(self) -> int:
        return hash(self.username)

    def add_chat(self, other, chatbox: Chatbox):  # Mutual chatbox object
        self.chats[other] = chatbox
        
    def get_chat(self, other):
        if other not in self.chats:
            return None
        return self.chats[other]