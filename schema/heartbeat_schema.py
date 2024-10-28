from pydantic import BaseModel

class Heartbeat(BaseModel):
    ip: str
    living_container_cnt: int