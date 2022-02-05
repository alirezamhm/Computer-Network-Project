from Server.User import User


class Message():
    def __init__(self, u_source:User, u_dest:User, content:str, seen=False) -> None:
        self.u_source = u_source
        self.u_dest = u_dest
        self.content = content
        self.seen = seen
        
    def __dict__(self):
        return {
            'sourcce': self.u_source.username,
            'dest': self.u_dest.username,
            'content': self.content,
            'seen': self.seen
        }