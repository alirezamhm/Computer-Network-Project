class Message():
    def __init__(self, u_source, u_dest, content:str, seen=False) -> None:
        self.u_source = u_source
        self.u_dest = u_dest
        self.content = content
        # self.seen = seen
        
    def to_dict(self):
        return {
            'source': self.u_source,
            'dest': self.u_dest,
            'content': self.content,
            # 'seen': self.seen
        }