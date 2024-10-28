from pydantic import BaseModel
from datetime import datetime
class Server(BaseModel):
    ip: str
    name: str
    
class ServerInfo(Server):
    id: int
    create_at: datetime
    last_heartbeat: datetime | None
    
class ServerList(BaseModel):
    cnt: int    
    server: list[ServerInfo]