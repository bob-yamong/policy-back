from sqlalchemy.orm import Session

from schema import server_schema


def create_server(db: Session, server: server_schema.Server) -> server_schema.ServerInfo:
    db.add(**server)
    db.flush()
    db.refresh(server)
    db.commit()
    
    return server