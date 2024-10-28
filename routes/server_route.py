from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from schema import server_schema

from database.database import get_db
from crud import server_crud


router = APIRouter(
    prefix="/server",
    tags=["Server"]
)

# Create
@router.post("/", status_code=status.HTTP_201_CREATED)
def add_server(server: server_schema.Server, db=Depends(get_db)):
    """
    새로운 컨테이너 호스트 서버를 추가합니다.

        
    """
    server_crud.create_server(db, server)
    return

# Read
@router.get("/")
def get_server_list():
    """
    컨테이너 호스트 서버 목록을 반환합니다.
    """
    return {
        "count": 0,
        "server": [
            {
                "id": 1,
                "ip": "10.0.1.1",
                "name": "container_host_1",
                "status": "running",
                "create_at": "2021-01-01 00:00:00",
                "last_heartbeat": "2021-01-01 00:00:00"
            },
            {
                "id": 2,
                "ip": "10.0.1.2",
                "name": "container_host_2",
                "status": "unknown",
                "create_at": "2021-01-01 00:00:00",
                "last_heartbeat": "2021-01-01 00:00:00"
            },
            {
                "id": 3,
                "ip": "10.0.1.3",
                "name": "container_host_3",
                "status": "running",
                "create_at": "2021-01-01 00:00:00" ,
                "last_heartbeat": "2021-01-01 00:00:00"
            },
            {
                "id": 4,
                "ip": "10.0.1.4",
                "name": "container_host_4",
                "status": "running",
                "create_at": "2021-01-01 00:00:00" ,
                "last_heartbeat": "2021-01-01 00:00:00"
            },
        ]
    }


# Update

# Delete
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_server():
    pass