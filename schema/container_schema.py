from pydantic import BaseModel
from datetime import datetime

class BaseContainer(BaseModel):
    id: int
    runtime: str
    name: str

class ContainerAddReq(BaseModel):
    host_server: str
    runtime: str
    name: str
    

class ContainerAddRes(BaseContainer):
    id: int
    create_at: datetime
    
class ContainerInfo(BaseContainer):
    id: int
    pid_id: int
    mnt_id: int
    cgroup_id: int
    create_at: datetime
    
class ContainerTagUpdate(BaseModel):
    tag: list[str]
    containers: list[int]
