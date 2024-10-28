from sqlalchemy.orm import Session

from schema import server_schema
from database import models


def create_server(db: Session, server: server_schema.Server) -> server_schema.ServerInfo:
    insert_data = models.Server(
        **server
    )
    
    db.add(insert_data)
    db.flush()
    db.refresh(insert_data)
    db.commit()
    
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
        last_heartbeat=last_heartbeat
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