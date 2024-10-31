from sqlalchemy.orm import Session
from fastapi import HTTPException
from starlette import status

from schema import container_schema, server_schema
from crud import server_crud
from database import models

def get_tag_id_set(db: Session, tag_list: list[str]) -> set:
    tag_id_set = set()
    
    # get tag id list from data
    for tag in tag_list:
        tag_id = db.query(models.Tag).filter(models.Tag.name == tag).first()
        
        if tag_id is None:
            db.add(models.Tag(name=tag))
            db.commit()
            
        db.query(models.Tag).filter(models.Tag.name == tag).first() 
            
        tag_id_set.add(tag_id.id)
                
    return tag_id_set
    

def add_container(db:Session, container: container_schema.ContainerAddReq) -> container_schema.ContainerAddRes:
    host_server = db.query(models.Server).filter(models.Server.ip == container.host_server).first()
    
    if host_server is None:
        host_server = server_crud.create_server(db, server_schema.Server(ip=container.host_server, name=container.host_server))
    
    host_server = host_server.id
    
    db.add(models.Container(
        host_server=host_server,
        runtime=container.runtime,
        name=container.name
    ))
    
    try:
        db.commit()
    except: 
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Container add failed")
    
    return db.query(models.Container).filter(models.Container.host_server == host_server).first()


def get_server_container_info(db: Session, server_id: int) -> container_schema.ServerContainerInfoRes:
    server_check = db.query(models.Server).filter(models.Server.id == server_id).first()
    
    if not server_check:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # get left join result container list from server_id and InternalContainerId
    container_list = db.query(models.Container).filter(models.Container.host_server == server_id).all()
    
    print(container_list)
    
    if not container_list:
        return container_schema.ServerContainerInfoRes(cnt=0, containers=[])
    
    res = container_schema.ServerContainerInfoRes(cnt=len(container_list), containers=[])
    
    for container in container_list:
        container_tag_list = db.query(models.t_Container_tag).join(models.Container).filter(models.t_Container_tag.container_id == container.id).all()
        tag_list = [tag.name for tag in container_tag_list]
        
        container_info = container_schema.ContainerInfo(
            pid_id = container.InternalContainerId[0].pid_id,
            mnt_id = container.InternalContainerId[0].mnt_id,
            cgroup_id = container.InternalContainerId[0].cgroup_id,
            tag = tag_list,
            create_at = container.create_at,
            req_time = container.InternalContainerId[0].req_time
        )
        
        res.containers.append(container_info)
        
    res.cnt = len(res.containers)
        
    
    return res

# ===================== Tag =====================
    
def update_container_tag(db: Session, data: container_schema.ContainerTagUpdate):
    try:
        # 모든 작업을 하나의 트랜잭션으로 처리
        tag_id_set = get_tag_id_set(db, data.tags)
        
        # 컨테이너 ID들을 한 번에 조회
        container_query = db.query(models.Container).filter(
            models.Container.id.in_(data.containers)
        ).all()
        
        # 실제 존재하는 컨테이너 ID 집합
        found_container_ids = {container.id for container in container_query}
        
        # 요청된 컨테이너 중 존재하지 않는 것이 있는지 확인
        missing_containers = set(data.containers) - found_container_ids
        if missing_containers:
            raise HTTPException(
                status_code=404, 
                detail=f"Containers not found: {missing_containers}"
            )
        
        # 기존 태그 관계를 한 번에 삭제
        db.query(models.ContainerTag).filter(
            models.ContainerTag.container_id.in_(data.containers)
        ).delete(synchronize_session=False)
        
        # 새로운 태그 관계를 한 번에 추가
        new_container_tags = [
            models.ContainerTag(container_id=container_id, tag_id=tag_id)
            for container_id in data.containers
            for tag_id in tag_id_set
        ]
        
        db.bulk_save_objects(new_container_tags)
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update container tags: {str(e)}"
        )
        
    return None
    

def add_container_tag(db: Session, data: container_schema.ContainerTagUpdate):
    tag_id_set = get_tag_id_set(db, data.tags)
        
    # get container id list from data
    for container in data.containers:
        container_id = db.query(models.Container).filter(models.Container.id == container).first().id
        
        if container_id is None:
            raise HTTPException(status_code=404, detail="Container not found")

        for tag_id in tag_id_set:
            db.add(models.ContainerTag(
                container_id=container_id,
                tag_id=tag_id
            ))
        
        db.commit()