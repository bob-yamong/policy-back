from pydantic import BaseModel
from datetime import datetime

# ========== Server Data ==========

class Server(BaseModel):
    uuid: str
    name: str
    
class ServerInfo(Server):
    id: int
    created_at: datetime
    last_heartbeat: datetime | None = None

# ========== Server Schema ==========

class ServerList(BaseModel):
    cnt: int    
    server: list[ServerInfo]
    
class ServerNameUpdateReq(BaseModel):
    name: str