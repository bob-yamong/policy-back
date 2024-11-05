from sqlalchemy.orm import Session
from fastapi import Request
from schema import server_schema
from schema import heartbeat_schema
from database import models

from crud.server_crud import get_server_info_from_ip, create_server

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