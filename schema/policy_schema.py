from pydantic import BaseModel
from datetime import datetime

# ==================== Policy Data ====================

class TracepointPolicy(BaseModel):
    """
    트레이스포인트 정책을 저장합니다

    tracepoints: list[str] - 트레이스포인트 목록
    """
    tracepoints: list[str] = []

class LSMPolicy(BaseModel):
    """
    LSM 정책을 저장합니다

    flags: list[str] - LSM 정책에 적용될 플래그 목록
    uid: list[int] - LSM 정책에 적용될 uid 목록
    """
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
    """
    제약 사항

    raw_tp의 길이는 10글자를 넘기지 않습니다.
    """
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

    
