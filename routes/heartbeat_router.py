from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from starlette import status
from sqlalchemy.orm import Session

from schema import server_schema, heartbeat_schema
from database.database import get_db
from crud import server_crud, heartbeat_crud

from collections import deque

router = APIRouter(
    prefix="/heartbeat",
    tags=["Heartbeat"]
)

queue = list()

@router.post("/heartbeat", status_code=status.HTTP_201_CREATED)
def add_heartbeat(req: Request, heartbeat: heartbeat_schema.InfoReq, db:Session=Depends(get_db)) -> str:
    """
    서버의 현재 상태를 기록합니다.

        Args:
            heartbeat (heartbeat_schema.Heartbeat): 서버의 상태 정보로 ip, status를 포함합니다.
            db (_type_, optional): 서버에서 DI하는 정보입니다. Defaults to Depends(get_db).
            
        Returns:
            str: 요청한 클라이언트의 ip를 반환합니다
        
        Raises:
            HTTPException: 422 - 잘못된 요청
            HTTPException: 500 - 서버 내부 오류
    """
    heartbeat_crud.add_heartbeat(db, req, heartbeat)
    queue.append(heartbeat)
    
    return req.client.host

# Read server stats info with streaming
@router.get("/stream", response_class=StreamingResponse)
async def get_server_stats():
    """
        서버의 상태 정보를 스트리밍합니다.
        
        Args:
            None
        
        Returns:
            StreamingResponse: 서버의 상태 정보를 스트리밍합니다.
        
        Raises:
            None
    """
    def generate():
        while True:
            if queue:
                print("tast")
                yield f"{str(queue.pop().__dict__)}"
            else:
                yield ""
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
