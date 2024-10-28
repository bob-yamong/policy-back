from pydantic import BaseModel

    
class HealthCheckContainer(BaseModel):
    runtime:str
    name: str
    pid: int
    mnt: int
    
class Heartbeat(BaseModel):
    ip: str
    survival_container: list[HealthCheckContainer]
    