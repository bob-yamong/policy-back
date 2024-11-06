from pydantic import BaseModel
from datetime import datetime

# ==================== Container Data ====================
class BaseContainer(BaseModel):
    id: int | None = None
    host_server: int
    runtime: str
    name: str
    
    
class ContainerInfo(BaseContainer):
    pid_id: int | None = None
    mnt_id: int | None = None
    cgroup_id: int | None = None
    tag: list[str] = []
    created_at: datetime
    removed_at: datetime | None = None
    req_time: datetime | None = None
    
# ==================== Container Schema ====================

class ContainerAddReq(BaseModel):
    host_server: str
    runtime: str
    name: str

class ContainerAddRes(BaseContainer):
    id: int
    created_at: datetime

class ServerContainerInfoRes(BaseModel):
    cnt: int
    containers: list[ContainerInfo] = []

class ContainerTagUpdate(BaseModel):
    tags: list[str]
    containers: list[int]
