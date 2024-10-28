from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from schema import heartbeat_schema

from database.database import get_db
from crud import heartbeat_crud

router = APIRouter(
    prefix="/heartbeat",
    tags=["Heartbeat"]
)

# Create
@router.post("/", status_code=status.HTTP_201_CREATED)
def add_heartbeat(heartbeat: heartbeat_schema.Heartbeat, db=Depends(get_db)):
    """add heartbeat info

    Args:
        heartbeat (heartbeat_schema.Heartbeat): 서버의 상태 정보를 기록합니다.
    """
    heartbeat_crud.create_heartbeat(db, heartbeat)
    return
