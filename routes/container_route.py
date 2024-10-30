from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from schema import container_schema
from crud import container_crud


router = APIRouter(
    prefix="/container",
    tags=["Container"]
)

# Create
@router.post("/")
def add_container(data: container_schema.BaseContainer) -> container_schema.ContainerAddRes:
    """
    새로운 컨테이너를 추가합니다

        Args:
            data (container_schema.BaseContainer): 추가할 컨테이너 정보

        Returns:
            container_schema.ContainerAddRes: 추가된 컨테이너 정보
    """
    
    return container_crud.add_container(data)

# Read
@router.get("/{server_id}")
def container_info_to_server(server_id: int) -> container_schema.ContainerInfo:
    """
    서버에 저장된 컨테이너 정보를 가져옵니다

        Args:
            server_id (int): servrer_id

        Returns:
            container_schema.ContainerInfo: 서버에 속한 컨테이너 정보
    """
    
    return container_crud.get_container_info(server_id)


# Update
@router.put("/tag", status_code=status.HTTP_205_RESET_CONTENT)
def update_container_tag(data: container_schema.ContainerTagUpdate) -> None:
    """컨테이너에 태그 정보를 변경합니다

    Args:
        data (container_schema.ContainerTagUpdate): _description_
    """
    container_crud.update_container_tag(data)


@router.patch("/tag", status_code=status.HTTP_206_PARTIAL_CONTENT)
def add_container_tag(data: container_schema.ContainerTagUpdate) -> None:
    """컨테이너에 태그 정보를 추가합니다

    Args:
        data (container_schema.ContainerTagUpdate): _description_
    """
    container_crud.add_container_tag(data)

# Delete