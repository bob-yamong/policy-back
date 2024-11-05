from pydantic import BaseModel
from datetime import datetime

class TracepointPolicy(BaseModel):
    tracepoints: list[str] = []

class LSMPolicy(BaseModel):
    flags: list[str] = []
    uid: list[int] = []

class LSMFilePolicy(LSMPolicy):
    path: str
    
class LSMNetworkPolicy(LSMPolicy):
    ip: str
    port: int
    protocol: int
    
class LSMProcessPolicy(LSMPolicy):
    comm: str

class LSMPolicies(BaseModel):
    file: list[LSMFilePolicy]
    network: list[LSMNetworkPolicy]
    process: list[LSMProcessPolicy]

class Policy(BaseModel):
    container_name: str
    raw_tp: str
    tracepoint_policy: TracepointPolicy
    lsm_policies: LSMPolicies

class ServerPolicy(BaseModel):
    api_version: str
    name: str
    containers: Policy

class ContainerPolicy(BaseModel):
    api_version: str
    name: str
    policy: Policy