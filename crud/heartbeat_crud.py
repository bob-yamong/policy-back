from sqlalchemy.orm import Session

from schema.heartbeat_schema import Heartbeat


def create_heartbeat(db: Session, heartbeat: Heartbeat):
    db.add(**heartbeat)
    db.commit()
    
    return