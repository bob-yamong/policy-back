from pydantic import BaseModel
from datetime import datetime

# ==================== Policy Data ====================

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
    containers: list[Policy]

class ContainerPolicy(BaseModel):
    api_version: str
    name: str
    policy: Policy

class ContainerPolicyInfo(BaseModel):
    tracepoint: list[str]
    lsm_file: list[LSMFilePolicy]
    lsm_network: list[LSMNetworkPolicy]
    lsm_process: list[LSMProcessPolicy]
    
# ==================== Policy Schema ====================

class PolicyRes(BaseModel):
    policies: list[ContainerPolicy]
    
class ContainerPolicyCreateRes(BaseModel):
    containers: dict[str, ContainerPolicyInfo]

    @classmethod
    def from_dict(cls, data: dict):
        containers = {}
        for container_name, policy_info in data.items():
            containers[container_name] = ContainerPolicyInfo(
                tracepoint=policy_info["tracepoint"],
                lsm_file=[LSMFilePolicy(**policy) for policy in policy_info["lsm_file"]],
                lsm_network=[LSMNetworkPolicy(**policy) for policy in policy_info["lsm_network"]],
                lsm_process=[LSMProcessPolicy(**policy) for policy in policy_info["lsm_process"]]
            )
        return cls(containers=containers)

    
