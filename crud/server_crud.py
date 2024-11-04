from sqlalchemy.orm import Session
from fastapi import Request
from schema import server_schema
from schema import heartbeat_schema
from database import models

def get_server_info_from_ip(db: Session, ip: str) -> models.Server | None:
    return db.query(models.Server).filter(models.Server.ip == ip).first()

def create_server(db: Session, server: server_schema.Server) -> server_schema.ServerInfo:
    insert_data = models.Server(
        ip=server.ip,
        name=server.name
    )
    
    db.add(insert_data)
    db.commit()
    
    insert_data = db.query(models.Server).filter(models.Server.ip == server.ip).first()
    
    return server_schema.ServerInfo(
        id=insert_data.id,
        ip=insert_data.ip,
        name=insert_data.name,
        create_at=insert_data.create_at,
        last_heartbeat=insert_data.create_at
    )

def get_server_info(db: Session, server_id: int) -> server_schema.ServerInfo:
    server_info = db.query(models.Server).filter(models.Server.id == server_id).first()
    last_heartbeat = db.query(models.Heartbeat).filter(models.Heartbeat.ip == server_info.ip).order_by(models.Heartbeat.timestamp.desc()).first() 
    
    info_data = server_schema.ServerInfo(
        id=server_info.id,
        ip=server_info.ip,
        name=server_info.name,
        create_at=server_info.create_at,
        last_heartbeat=last_heartbeat.timestamp if last_heartbeat else None
    )
    
    return info_data

def get_server_list(db: Session) -> server_schema.ServerList:
    server_list = db.query(models.Server).all()
    
    server_list_info = server_schema.ServerList(
        cnt=len(server_list),
        server=list(map(lambda x: get_server_info(db, x.id), server_list))
    )
    
    return server_list_info

def delete_server(db: Session, server_id: int) -> None:
    db.query(models.Server).filter(models.Server.id == server_id).delete()
    db.commit()
    
    return

def add_heartbeat(db: Session, req: Request, heartbeat: heartbeat_schema.InfoReq):
    server = get_server_info_from_ip(db, heartbeat.host_ip) 
    if not server:
       server = create_server(db, server_schema.Server(
           ip = heartbeat.host_ip,
           name = str(heartbeat.host_ip)
       ))
    
    for container in heartbeat.containers:
        container_info = db.query(models.Container).filter(models.Container.name == container.container_name).first()
        
        if not container_info:
            db.add(models.Container(
                host_server = server.id,
                runtime = container.runtime,
                name = container.container_name
            ))
            db.commit()
            
        container_info = db.query(models.Container).filter(models.Container.name == container.container_name).first()
        internal_container_id = db.query(models.InternalContainerId).filter(
            models.InternalContainerId.container_id == container_info.id,
            models.InternalContainerId.pid_id == container.namespace.pid,
            models.InternalContainerId.mnt_id == container.namespace.mnt,
            models.InternalContainerId.cgroup_id == container.cgroup_id
        ).first()
        
        if not internal_container_id:
            db.add(models.InternalContainerId(
            container_id = container_info.id,
            pid_id = container.namespace.pid,
            mnt_id = container.namespace.mnt,
            cgroup_id = container.cgroup_id
            ))
            db.commit()
    
    insert_data = models.Heartbeat(
        ip = heartbeat.host_ip,
        survival_container_cnt = len(heartbeat.containers),
        req_ip = req.client.host
    )
    
    db.add(insert_data)
    db.commit()
    
    return