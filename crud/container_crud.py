from sqlalchemy.orm import Session
from fastapi import HTTPException

from schema import container_schema
from database import models

def get_tag_id_set(db: Session, tag_list: list[str]) -> set:
    tag_id_set = set()
    
    # get tag id list from data
    for tag in tag_list:
        tag_id = db.query(models.Tag).filter(models.Tag.name == tag).first()
        
        if tag_id is None:
            db.add(models.Tag(name=tag))
            db.flush()
            db.refresh(tag_id)
            db.commit()
            
        tag_id_set.add(tag_id.id)
                
    return tag_id_set
    

def add_container(db:Session, container: container_schema.BaseContainer) -> container_schema.ContainerAddRes:
    db.add(models.Container(**container))
    db.flush()
    db.refresh(container)
    db.commit()
    
    return container
    
def update_container_tag(db: Session, data:container_schema.ContainerTagUpdate):
    tag_id_set = get_tag_id_set(db, data.tags)

    for container in data.containers:
        container_id = db.query(models.Container).filter(models.Container.id == container).first().id
        
        if container_id is None:
            raise HTTPException(status_code=404, detail="Container not found")
        
        db.query(models.t_Container_tag).filter(models.t_Container_tag.container_id == container_id).delete()
        
        for tag_id in tag_id_set:
            db.add(models.t_Container_tag(
                container_id=container_id,
                tag_id=tag_id
            ))
        
        db.commit()
    

def add_container_tag(db: Session, data: container_schema.ContainerTagUpdate):
    tag_id_set = get_tag_id_set(db, data.tags)
        
    # get container id list from data
    for container in data.containers:
        container_id = db.query(models.Container).filter(models.Container.id == container).first().id
        
        if container_id is None:
            raise HTTPException(status_code=404, detail="Container not found")

        for tag_id in tag_id_set:
            db.add(models.t_Container_tag(
                container_id=container_id,
                tag_id=tag_id
            ))
        
        db.commit()