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
    (세부 사항 합의 필요)
    서버의 상태 정보를 반환합니다.

        Args:
            server_id (int): 상태를 반환받을 서버의 id를 입력합니다.
            unit (heartbeat_schema.TimeUnit): 시간의 주기를 입력합니다.
            function_name (heartbeat_schema.funcList): 어떤 함수를 사용할지 입력합니다.
            db (Session, optional): Defaults to Depends(get_db).

        Raises:
            HTTPException: 404 - 서버를 찾을 수 없음
            HTTPException: 422 - 잘못된 요청
            HTTPException: 500 - 서버 내부 오류

        Returns:
            dict: 서버의 상태 정보를 반환합니다.
            ex)
            [
                {
                    "time": "2024-11-06T00:00:00+09:00",
                    "cpu1": 22.775,
                    "cpu2": 3.525,
                    "cpu3": 5.7,
                    "cpu4": 10.525,
                    "cpu5": 2.525,
                    "cpu6": 44.5,
                    "cpu7": 46,
                    "cpu8": 29.025,
                    "cpu9": 5.8
                },
                {
                    "time": "2024-11-06T01:00:00+09:00",
                    "cpu1": 16.97222222222222,
                    "cpu2": 10.061111111111112,
                    "cpu3": 14.516666666666666,
                    "cpu4": 29.272222222222222,
                    "cpu5": 10.733333333333333,
                    "cpu6": 19.916666666666668,
                    "cpu7": 25.425,
                    "cpu8": 15.411111111111111,
                    "cpu9": 14.313888888888888
                }
            ]
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
def get_container_stats(container_id: int, unit:heartbeat_schema.TimeUnit, 
                    function_name: heartbeat_schema.funcList, db: Session=Depends(get_db)):
    """
    (작업중 변경 사항 발생 가능성 있음)
    컨테이너의 상태 정보를 반환합니다.

        Args:
            container_id (int): 컨테이너의 id를 입력합니다.
            unit (heartbeat_schema.TimeUnit): 시간의 주기를 입력합니다.
            function_name (heartbeat_schema.funcList): 어떤 함수를 사용할지 입력합니다.
            db (_type_, optional): 서버에서 DI하는 정보입니다. Defaults to Depends(get_db).
            
        Returns:
            server_schema.ContainerInfo: 컨테이너의 상태 정보를 반환합니다.
        
        Raises:
            HTTPException: 404 - 컨테이너를 찾을 수 없음
    """
    container = server_crud.get_container_info(db, container_id)
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    
    if function_name not in funcList:
        raise HTTPException(status_code=422, detail="Invalid function name")
    
    if unit not in TimeUnit:
        raise HTTPException(status_code=422, detail="Invalid time unit")
    
    return heartbeat_crud.get_container_stats(db, container_id, unit.value, func_dict[function_name])



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
        서버와 내부의 컨테이너의 상태 정보를 스트리밍합니다.
        
        Args:
            None
        
        Returns:
            StreamingResponse: 서버와 내부 컨테이너 상태 정보를 스트리밍합니다.
        
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
