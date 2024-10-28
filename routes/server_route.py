from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.orm import Session

from schema import server_schema
from database.database import get_db
from crud import server_crud


router = APIRouter(
    prefix="/server",
    tags=["Server"]
)

# Create
@router.post("/", status_code=status.HTTP_201_CREATED)
def add_server(server: server_schema.Server, db:Session=Depends(get_db)) -> server_schema.ServerInfo:
    """
    새로운 컨테이너 호스트 서버를 추가합니다.

        Args:
            server (server_schema.Server): 추가 할 서버의 정보로 ip, name을 포함합니다.
            db (Session, optional): 서버에서 추가되는 db DI 정보입니다. Defaults to Depends(get_db).

        Returns:
            server_schema.ServerInfo: 추가된 서버의 정보를 반환합니다.
    """
    return server_crud.create_server(db, server)
    

# Read
@router.get("/", response_model=server_schema.ServerList)
def get_server_list(db:Session=Depends(get_db)) -> server_schema.ServerList:
    """
    서버 목록을 조회합니다.

        Args:
            db (Session, optional): 서버에서 추가되는 db DI 정보입니다. Defaults to Depends(get_db).

        Returns:
            server_schema.ServerList: 관리되는 서버 목록을 반환합니다.
    """
    return server_crud.get_server_list(db)


# Update

# Delete
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_server(server_id: int, db:Session=Depends(get_db)) -> None:
    """관리 서버에서 입력된 서버를 제거합니다

        Args:
            server_id (int): 제거할 서버 id
            db (Session, optional): 서버에서 추가되는 db DI 정보입니다. Defaults to Depends(get_db).
    """
    server_crud.delete_server(db, server_id)
    return