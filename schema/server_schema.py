from pydantic import BaseModel

class Server(BaseModel):
    ip: str
    name: str
    
class ServerInfo(Server):
    id: int
    status: str
    create_at: str
    last_heartbeat: str