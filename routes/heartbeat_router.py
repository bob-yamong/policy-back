from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from starlette import status
from sqlalchemy.orm import Session
from statistics import mean, median

from schema.heartbeat_schema import TimeUnit, funcList
from schema import server_schema, heartbeat_schema
from database.database import get_db
from crud import server_crud, heartbeat_crud


router = APIRouter(
    prefix="/heartbeat",
    tags=["Heartbeat"]
)

func_dict = {
    funcList.MAX: max,
    funcList.MEDIAN: median,
    funcList.MEAN: mean
}

queue = list()

@router.get("/server/{server_id}")
def get_server_stats(server_id: int, unit:heartbeat_schema.TimeUnit, 
                    function_name: heartbeat_schema.funcList, 
                    db: Session=Depends(get_db)):
    """
    서버의 최근 상태 정보를 반환합니다.

        Args:
            server_id (int): 서버의 id를 입력합니다.
            db (_type_, optional): 서버에서 DI하는 정보입니다. Defaults to Depends(get_db).
            
        Returns:
            server_schema.ServerInfo: 서버의 상태 정보를 반환합니다.
        
        Raises:
            HTTPException: 404 - 서버를 찾을 수 없음
    """
    server = server_crud.get_server_info(db, server_id)
    if not server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
     
    if function_name not in funcList:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid function name")
    
    if unit not in TimeUnit:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid time unit")

    return heartbeat_crud.get_server_stats(db, server_id, unit.value, func_dict[function_name])


@router.get("/container/{container_id}")
def get_container_stats(container_id: int, db: Session=Depends(get_db)):
    """
    컨테이너의 상태 정보를 반환합니다.

        Args:
            container_id (int): 컨테이너의 id를 입력합니다.
            db (_type_, optional): 서버에서 DI하는 정보입니다. Defaults to Depends(get_db).
            
        Returns:
            server_schema.ContainerInfo: 컨테이너의 상태 정보를 반환합니다.
        
        Raises:
            HTTPException: 404 - 컨테이너를 찾을 수 없음
    """
    container = server_crud.get_container_info(db, container_id)
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    
    return container



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
