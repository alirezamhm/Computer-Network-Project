from Message import Message
from datetime import datetime

from Server.User import User

class Chatbox():
    def __init__(self, user1:User, user2:User) -> None:
        self.user1 = user1
        self.user2 = user2
        self.online1 = False
        self.online2 = False
        self.messages = []
        self.last_update = datetime.now()
        

    def chat_has_updated(self):
        self.last_update = datetime.now()
        
    def __eq__(self, other):  
        return self.last_update == other.last_update
    
    def __ge__(self, other):
        return self.last_update >= other.last_update
    
    def get_messages_dict(self, n, username) -> dict:
        return {
            'username': username,
            'messages': [x.__dict__() for x in self.messages[-n:]],
        }
    
    def update_online(self, username, in_out):
        if username == self.user1.username:
            self.online1 = in_out
        elif username == self.user2.username:
            self.online1 = in_out
