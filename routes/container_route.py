from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.orm import Session

from database.database import get_db

from schema import container_schema
from crud import container_crud


router = APIRouter(
    prefix="/container",
    tags=["Container"]
)

# Create
@router.post("/")
def add_container(data: container_schema.ContainerAddReq, db=Depends(get_db)) -> container_schema.ContainerAddRes:
    """
    새로운 컨테이너를 추가합니다

        Args:
            data (container_schema.ContainerInfo): 추가할 컨테이너 정보

        Returns:
            container_schema.ContainerAddRes: 추가된 컨테이너 정보
    """
    
    return container_crud.add_container(db, data)

# Read
@router.get("/{server_id}")
def container_info_to_server(server_id: int, db=Depends(get_db)) -> container_schema.ServerContainerInfoRes:
    """
    서버에 저장된 컨테이너 정보를 가져옵니다

        Args:
            server_id (int): servrer_id

        Returns:
            container_schema.ContainerInfo: 서버에 속한 컨테이너 정보
    """
    
    return container_crud.get_server_container_info(db, server_id)


# Update
@router.put("/tag", status_code=status.HTTP_200_OK)
def update_container_tag(
    data: container_schema.ContainerTagUpdate,
    db: Session = Depends(get_db)
) -> dict:
    """
    컨테이너들의 태그 정보를 일괄 변경합니다

        Args:
            data (container_schema.ContainerTagUpdate): 컨테이너 ID 목록과 적용할 태그 목록
            db (Session): 데이터베이스 세션

        Returns:
            dict: 성공 메시지
            
        Raises:
            HTTPException: 404 - 컨테이너를 찾을 수 없음
            HTTPException: 500 - 서버 내부 오류
        """
    container_crud.update_container_tag(db, data)
    return {"message": "Container tags updated successfully"}


@router.patch("/tag", status_code=status.HTTP_206_PARTIAL_CONTENT)
def add_container_tag(data: container_schema.ContainerTagUpdate, db=Depends(get_db)) -> None:
    """컨테이너에 태그 정보를 추가합니다

    Args:
        data (container_schema.ContainerTagUpdate): _description_
    """
    return container_crud.add_container_tag(db, data)

# Delete