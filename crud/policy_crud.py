from sqlalchemy.orm import Session
from fastapi import Request
from fastapi import HTTPException
from starlette import status

from schema import server_schema, policy_schema
from database import models

from crud.server_crud import get_server_info_from_ip, create_server

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