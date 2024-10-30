from pydantic import BaseModel
from datetime import datetime

class BaseContainer(BaseModel):
    id: int
    host_server: int
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
    pid_id: int | None = None
    mnt_id: int | None = None
    cgroup_id: int | None = None
    create_at: datetime
    req_time: datetime | None = None
    
class ContainerTagUpdate(BaseModel):
    tag: list[str]
    containers: list[int]
