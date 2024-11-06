from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class TimeUnit(Enum):
    MINUTE = 'minute'
    HOUR = 'hour'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    
class funcList(Enum):
    MEAN = 'mean'
    MEDIAN = 'median'
    MAX = "max"

class ContainerCpu(BaseModel):
    kernel_usage: float
    online_cpus: int
    usage_percent: float
    user_usage: float

class ContainerIo(BaseModel):
    read_mb: float
    write_mb: float
    
class ContainerMemory(BaseModel):
    active: float
    cache: float
    limit_mb: float
    usage_mb: float
    usage_percent: float
    
class ContainerNetwork(BaseModel):
    errors: int
    rx_mb: float
    rx_packets: int
    tx_mb: float
    tx_packets: int
    
class ContainerStats(BaseModel):
    cpu: ContainerCpu
    io: ContainerIo
    memory: ContainerMemory
    network: ContainerNetwork
    proc_cnt: int

class Namespace(BaseModel):
    mnt: int
    pid: int

class ContainerInfo(BaseModel):
    cgroup_id: int
    container_name: str
    namespace: Namespace
    runtime: str
    stats: ContainerStats

class HostCpu(BaseModel):
    CPU_freq_MHz: float
    CPU_logical_core: int
    CPU_percent: float
    CPU_physical_core: int
    core_usage: list[float]

class HostDiskUsage(BaseModel):
    free_GB: float
    percent: float
    total_GB: float
    used_GB: float

class HostDisk(BaseModel):
    read_MB: float
    write_MB: float
    usage: HostDiskUsage
    
class HostMemory(BaseModel):
    mem_percent: float
    total_mem_GB: float
    used_mem_GB: float

class HostNetwork(BaseModel):
    recv_data_MB: float
    recv_err: int
    recv_packets: int
    sent_data_MB: float
    sent_err: int
    sent_packets: int
    
class HostInfo(BaseModel):
    cpu: HostCpu
    disk: HostDisk
    memory: HostMemory
    network: HostNetwork
    
class InfoReq(BaseModel):
    containers: list[ContainerInfo]
    host: HostInfo
    host_uuid: str
    timestamp: datetime
