from sqlalchemy.orm import Session
from fastapi import Request
from fastapi import HTTPException
from starlette import status

from schema import server_schema, policy_schema, container_schema
from database import models

from crud import container_crud
from crud.server_crud import get_server_info_from_uuid, create_server


def create_custom_policy(db: Session, policy: policy_schema.ServerPolicy):
    # TODO: 다중 서버 환경을 지원될 때 yaml 구조와 정책 적용 방식이 변경되어야 함
    # ! 현재는 일단 13번 서버에 등록되어있는 컨테이너에 적용 예정
    
    # 기존 정책 확인
    policy_data = db.query(models.Policy).filter(models.Policy.name == policy.name).first()
    if policy_data:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Policy "{policy.name}" already exists')
    else:
        db.add(models.Policy(
            name=policy.name,
            api_version=policy.api_version
        ))
        db.commit()
        
        policy_data = db.query(models.Policy).filter(models.Policy.name == policy.name).first()
    
    # 정책 생성
    insert_failed_policy = {}
    for container in policy.containers:
        container_info = container_crud.is_exist_container(db, container.container_name)
        
        if not container_info:
            container_info = container_crud.add_container(
                db, container_schema.ContainerAddReq(
                    # Todo 이후 서버 설정이 가능해 질 때 수정이 필요함.
                    host_server="192.168.0.1", 
                    runtime="docker", 
                    name=container.container_name
                ))
        
        try:
            db.add(models.RawTracePointPolicy(
                policy_id = policy_data.id,
                container_id = container_info.id,
                state = container.raw_tp
            ))
            db.commit()
        except Exception as e:
            print(e)
            
            db.query(models.RawTracePointPolicy) \
                .filter(models.RawTracePointPolicy.container_id == container_info.id) \
                .update({"state": container.raw_tp})
        
        for tracepoint in container.tracepoint_policy.tracepoints:
            try:
                db.add(models.TracepointPolicy(
                    policy_id = policy_data.id,
                    container_id = container_info.id,
                    tracepoint = tracepoint
                ))
                db.commit()
            except Exception as e:
                print(e)
                
                insert_failed_policy.setdefault(container.container_name, {}).setdefault("tracepoint", []).append(tracepoint)
        for file_policy in container.lsm_policies.file:
            try:
                db.add(models.LsmFilePolicy(
                    policy_id = policy_data.id,
                    container_id = container_info.id,
                    path = file_policy.path,
                    flags = file_policy.flags,
                    uid = file_policy.uid
                ))
                db.commit()
            except Exception as e:
                print(e)
                
                insert_failed_policy.setdefault(container.container_name, {}).setdefault("lsm_file", []).append(file_policy)
        for net_policy in container.lsm_policies.network:
            try:
                db.add(models.LsmNetPolicy(
                    policy_id = policy_data.id,
                    container_id = container_info.id,
                    ip = net_policy.ip,
                    port = net_policy.port,
                    protocol = net_policy.protocol,
                    flags = net_policy.flags,
                    uid = net_policy.uid
                ))
                db.commit()
            except Exception as e:
                print(e)
                
                insert_failed_policy.setdefault(container.container_name, {}).setdefault("lsm_network", []).append(net_policy)
                
        for process_policy in container.lsm_policies.process:
            try:
                db.add(models.LsmProcPolicy(
                    policy_id = policy_data.id,
                    container_id = container_info.id,
                    comm = process_policy.comm,
                    flags = process_policy.flags,
                    uid = process_policy.uid
                ))
                db.commit()
            except Exception as e:
                print(e)
                
                insert_failed_policy.setdefault(container.container_name, {}).setdefault("lsm_process", []).append(process_policy)
                                                                                                                   
    return insert_failed_policy

def get_server_policy(db: Session, server_id: int) -> policy_schema.ServerPolicy:
    server = db.query(models.Server).filter(models.Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    
    return {
    "api_version": "policy.yamong.com/v1",
    "name": "multi-container-example-policy",
    "containers": [
        {
        "container_name": "sharp_yalow",
        "raw_tp": "on",
        "tracepoint_policy": {
            "tracepoints": [
                "__NR_umount2"
            ]
        },
        "lsm_policies": {
            "file": [
            {
                "path": "/etc/passwd",
                "flags": [
                "POLICY_ALLOW",
                "POLICY_AUDIT",
                "POLICY_FILE_READ"
                ],
                "uid": [
                1000,
                1001
                ]
            },
            {
                "path": "/var/log",
                "flags": [
                "POLICY_ALLOW",
                "POLICY_AUDIT",
                "POLICY_FILE_WRITE",
                "POLICY_FILE_APPEND",
                "POLICY_RECURSIVE"
                ],
                "uid": [
                1000,
                1001
                ]
            },
            {
                "path": "/sys",
                "flags": [
                "POLICY_ALLOW",
                "POLICY_AUDIT",
                "POLICY_FILE_WRITE",
                "POLICY_FILE_APPEND",
                "POLICY_RECURSIVE"
                ],
                "uid": [
                1000,
                1001
                ]
            }
            ],
            "network": [
            {
                "ip": "192.168.1.100",
                "port": 80,
                "protocol": 6,
                "flags": [
                "POLICY_ALLOW",
                "POLICY_AUDIT",
                "POLICY_NET_CONNECT"
                ],
                "uid": [
                1000,
                1001
                ]
            },
            {
                "ip": "10.0.0.0/8",
                "port": 443,
                "protocol": 6,
                "flags": [
                "POLICY_NET_CONNECT",
                "POLICY_DENY"
                ],
                "uid": [
                1000,
                1001
                ]
            }
            ],
            "process": [
            {
                "comm": "nginx",
                "flags": [
                "POLICY_ALLOW",
                "POLICY_AUDIT",
                "POLICY_PROC_EXEC"
                ],
                "uid": [
                1000,
                1001
                ]
            },
            {
                "comm": "bash",
                "flags": [
                "POLICY_ALLOW",
                "POLICY_AUDIT",
                "POLICY_PROC_EXEC"
                ],
                "uid": [
                1000,
                1001
                ]
            }
            ]
        }
        },
        {
        "container_name": "test-container-2",
        "raw_tp": "on",
        "tracepoint_policy": {
            "tracepoints": [
                "__NR_umount2"
            ]
        },
        "lsm_policies": {
            "file": [
            {
                "path": "/app/data",
                "flags": [
                "POLICY_ALLOW",
                "POLICY_AUDIT",
                "POLICY_FILE_READ",
                "POLICY_FILE_WRITE"
                ],
                "uid": [
                1000,
                1001
                ]
            }
            ],
            "network": [
            {
                "ip": "0.0.0.0/0",
                "port": 8080,
                "protocol": 6,
                "flags": [
                "POLICY_ALLOW",
                "POLICY_AUDIT",
                "POLICY_NET_BIND",
                "POLICY_NET_ACCEPT"
                ],
                "uid": [
                1000,
                1001
                ]
            }
            ],
            "process": [
            {
                "comm": "python",
                "flags": [
                "POLICY_ALLOW",
                "POLICY_AUDIT",
                "POLICY_PROC_EXEC"
                ],
                "uid": [
                1000,
                1001
                ]
            }
            ]
        }
        }
    ]
    }

def get_container_policy(db:Session, server_id: int, container_id: int) -> policy_schema.ContainerPolicy:
    container = db.query(models.Container).filter(
        models.Container.id == container_id,
        models.Container.host_server == server_id
    ).first()
    
    if not container:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")
    
    return {
        "policies" : [
            {
                "api_version": "policy.yamong.com/v1",
                "name": "multi-container-example-policy",
                "policy":{
                    "container_name": "sharp_yalow",
                    "raw_tp": "on",
                    "tracepoint_policy": {
                        "tracepoints": [
                            "__NR_umount2"
                        ]
                    },
                    "lsm_policies": {
                        "file": [
                            {
                            "path": "/etc/passwd",
                            "flags": [
                                "POLICY_ALLOW",
                                "POLICY_AUDIT",
                                "POLICY_FILE_READ"
                            ],
                            "uid": [
                                1000,
                                1001
                            ]
                            },
                            {
                            "path": "/var/log",
                            "flags": [
                                "POLICY_ALLOW",
                                "POLICY_AUDIT",
                                "POLICY_FILE_WRITE",
                                "POLICY_FILE_APPEND",
                                "POLICY_RECURSIVE"
                            ],
                            "uid": [
                                1000,
                                1001
                            ]
                            },
                            {
                            "path": "/sys",
                            "flags": [
                                "POLICY_ALLOW",
                                "POLICY_AUDIT",
                                "POLICY_FILE_WRITE",
                                "POLICY_FILE_APPEND",
                                "POLICY_RECURSIVE"
                            ],
                            "uid": [
                                1000,
                                1001
                            ]
                            }
                        ],
                        "network": [
                            {
                            "ip": "192.168.1.100",
                            "port": 80,
                            "protocol": 6,
                            "flags": [
                                "POLICY_ALLOW",
                                "POLICY_AUDIT",
                                "POLICY_NET_CONNECT"
                            ],
                            "uid": [
                                1000,
                                1001
                            ]
                            },
                            {
                            "ip": "10.0.0.0/8",
                            "port": 443,
                            "protocol": 6,
                            "flags": [
                                "POLICY_NET_CONNECT",
                                "POLICY_DENY"
                            ],
                            "uid": [
                                1000,
                                1001
                            ]
                            }
                        ],
                        "process": [
                            {
                            "comm": "nginx",
                            "flags": [
                                "POLICY_ALLOW",
                                "POLICY_AUDIT",
                                "POLICY_PROC_EXEC"
                            ],
                            "uid": [
                                1000,
                                1001
                            ]
                            },
                            {
                            "comm": "bash",
                            "flags": [
                                "POLICY_ALLOW",
                                "POLICY_AUDIT",
                                "POLICY_PROC_EXEC"
                            ],
                            "uid": [
                                1000,
                                1001
                            ]
                            }
                        ]
                    }
                }
            }
        ]
    }
    
def check_conflict(db: Session, server_id: int, container_id: int | None = None):
    server = db.query(models.Server).filter(models.Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    
    container = db.query(models.Container).filter(models.Container.id == container_id).first()
    if not container:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")
    
    return {
        "conflict": False
    }