from matplotlib.style import use
from Message import Message
from datetime import datetime

class Chatbox():
    def __init__(self, user1, user2) -> None:
        self.user1 = user1
        self.user2 = user2
        self.onlines = {user1: False, user2: False}
        self.messages = []
        self.not_seens = {user1: 0, user2: 0}
        self.last_update = datetime.now()
        

    def has_updated(self):
        self.last_update = datetime.now()
        
    def __eq__(self, other):  
        return self.last_update == other.last_update
    
    def __gt__(self, other):
        return self.last_update > other.last_update
    
    def __lt__(self, other):
        return self.last_update < other.last_update
    
    
    def get_messages_dict(self, n, username) -> dict:
        n = min(n, len(self.messages))
        return {
            'username': username,
            'messages': [x.to_dict() for x in self.messages[-n:]],
        }
    
    def update_online(self, username, in_out):
        self.onlines[username] = in_out
        
    def send_message(self, dest, msg):
        self.messages.append(msg)
        self.has_updated()
        self.not_seens[dest] += 1
        
    def reset_seens(self, user):
        self.not_seens[user] = 0
        
    def get_string(self, username):
        not_seen = self.not_seens[username]
        return f'{self.user2 if self.user1==username else self.user1} {f"({not_seen})" if not_seen > 0 else ""}'