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
        container_info = container_crud.get_container_by_name(db, container.container_name)
        
        if not container_info:
            container_info = container_crud.add_container(
                db, container_schema.ContainerAddReq(
                    # Todo 이후 서버 설정이 가능해 질 때 수정이 필요함.
                    host_server="192.168.0.1", 
                    runtime="docker", 
                    name=container.container_name
                ))
        
        try:
            if db.query(models.RawTracePointPolicy).filter(
                models.RawTracePointPolicy.container_id == container_info.id
            ).first():
                raise Exception("Already exists")
            
            db.add(models.RawTracePointPolicy(
                policy_id = policy_data.id,
                container_id = container_info.id,
                state = container.raw_tp
            ))
            db.commit()
        except Exception as e:
            db.query(models.RawTracePointPolicy) \
                .filter(models.RawTracePointPolicy.container_id == container_info.id) \
                .update({"state": container.raw_tp})
        
        for tracepoint in container.tracepoint_policy.tracepoints:
            try:
                if db.query(models.TracepointPolicy).filter(
                    models.TracepointPolicy.container_id == container_info.id,
                    models.TracepointPolicy.tracepoint == tracepoint
                ).first():
                    raise Exception("Already exists")
                
                db.add(models.TracepointPolicy(
                    policy_id = policy_data.id,
                    container_id = container_info.id,
                    tracepoint = tracepoint
                ))
                db.commit()
            except Exception as e:
                insert_failed_policy.setdefault(container.container_name, {}).setdefault("tracepoint", []).append(tracepoint)
        
        for file_policy in container.lsm_policies.file:
            try:
                if db.query(models.LsmFilePolicy).filter(
                    models.LsmFilePolicy.container_id == container_info.id,
                    models.LsmFilePolicy.path == file_policy.path
                ).first():
                    raise Exception("Already exists")
                
                db.add(models.LsmFilePolicy(
                    policy_id = policy_data.id,
                    container_id = container_info.id,
                    path = file_policy.path,
                    flags = file_policy.flags,
                    uid = file_policy.uid
                ))
                db.commit()
            except Exception as e:
                insert_failed_policy.setdefault(container.container_name, {}).setdefault("lsm_file", []).append(file_policy)
        
        for net_policy in container.lsm_policies.network:
            try:
                if db.query(models.LsmNetPolicy).filter(
                    models.LsmNetPolicy.container_id == container_info.id,
                    models.LsmNetPolicy.ip == net_policy.ip,
                    models.LsmNetPolicy.port == net_policy.port,
                    models.LsmNetPolicy.protocol == net_policy.protocol
                ).first():
                    raise Exception("Already exists")
                
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
                insert_failed_policy.setdefault(container.container_name, {}).setdefault("lsm_network", []).append(net_policy)
                
        for process_policy in container.lsm_policies.process:
            try:
                if db.query(models.LsmProcPolicy).filter(
                    models.LsmProcPolicy.container_id == container_info.id,
                    models.LsmProcPolicy.comm == process_policy.comm
                ).first():
                    raise Exception("Already exists")
                
                db.add(models.LsmProcPolicy(
                    policy_id = policy_data.id,
                    container_id = container_info.id,
                    comm = process_policy.comm,
                    flags = process_policy.flags,
                    uid = process_policy.uid
                ))
                db.commit()
            except Exception as e:
                insert_failed_policy.setdefault(container.container_name, {}).setdefault("lsm_process", []).append(process_policy)
                                                                                                                   
    return insert_failed_policy

def get_server_policy(db: Session, server_id: int) -> policy_schema.ServerPolicy:
    server = db.query(models.Server).filter(models.Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    
    container_list_in_server = db.query(models.Container).filter(models.Container.host_server == server_id).all()
    
    ret = {
        "policies": []
    }
    
    for container in container_list_in_server:
        policy = get_container_policy(db, container.id)
        if len(policy["policies"]) == 0:
            continue
        ret["policies"].extend(policy["policies"])
    
    return ret

def get_container_policy(db: Session, container_id: int) -> policy_schema.ContainerPolicy:
    # 컨테이너와 연관된 정책들을 함께 조회
    container = db.query(models.Container).filter(
        models.Container.id == container_id
    ).first()
    
    if not container:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")
    
    # 컨테이너와 연관된 모든 정책들을 그룹화하여 조회
    policies_data = []
    
    # 컨테이너에 연결된 고유한 정책 ID들을 수집
    policy_ids = set()
    policy_ids.update([p.policy_id for p in container.RawTracePointPolicy])
    policy_ids.update([p.policy_id for p in container.TracepointPolicy])
    policy_ids.update([p.policy_id for p in container.LsmFilePolicy])
    policy_ids.update([p.policy_id for p in container.LsmNetPolicy])
    policy_ids.update([p.policy_id for p in container.LsmProcPolicy])
    
    # 각 정책 ID에 대해 모든 관련 정책 정보를 수집
    for policy_id in policy_ids:
        policy = db.query(models.Policy).filter(models.Policy.id == policy_id).first()
        
        # Raw Tracepoint Policy
        raw_tp = db.query(models.RawTracePointPolicy).filter(
            models.RawTracePointPolicy.policy_id == policy_id,
            models.RawTracePointPolicy.container_id == container_id
        ).first()
        
        # Tracepoint Policies
        tracepoints = db.query(models.TracepointPolicy).filter(
            models.TracepointPolicy.policy_id == policy_id,
            models.TracepointPolicy.container_id == container_id
        ).all()
        
        # LSM File Policies
        file_policies = db.query(models.LsmFilePolicy).filter(
            models.LsmFilePolicy.policy_id == policy_id,
            models.LsmFilePolicy.container_id == container_id
        ).all()
        
        # LSM Network Policies
        net_policies = db.query(models.LsmNetPolicy).filter(
            models.LsmNetPolicy.policy_id == policy_id,
            models.LsmNetPolicy.container_id == container_id
        ).all()
        
        # LSM Process Policies
        proc_policies = db.query(models.LsmProcPolicy).filter(
            models.LsmProcPolicy.policy_id == policy_id,
            models.LsmProcPolicy.container_id == container_id
        ).all()
        
        # 정책 데이터 구성
        policy_data = {
            "api_version": policy.api_version,
            "name": policy.name,
            "policy": {
                "container_name": container.name,
                "raw_tp": raw_tp.state if raw_tp else "off",
                "tracepoint_policy": {
                    "tracepoints": [tp.tracepoint for tp in tracepoints]
                },
                "lsm_policies": {
                    "file": [
                        {
                            "path": fp.path,
                            "flags": fp.flags,
                            "uid": fp.uid
                        } for fp in file_policies
                    ],
                    "network": [
                        {
                            "ip": np.ip,
                            "port": np.port,
                            "protocol": np.protocol,
                            "flags": np.flags,
                            "uid": np.uid
                        } for np in net_policies
                    ],
                    "process": [
                        {
                            "comm": pp.comm,
                            "flags": pp.flags,
                            "uid": pp.uid
                        } for pp in proc_policies
                    ]
                }
            }
        }
        
        policies_data.append(policy_data)
    
    return {
        "policies": policies_data
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