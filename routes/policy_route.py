from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.orm import Session

from database.database import get_db
from schema import policy_schema
from crud import policy_crud

router = APIRouter(
    prefix="/policy",
    tags=["Policy"]
)

# Create
@router.post("/custom", status_code=status.HTTP_201_CREATED)
def create_policy(policy: policy_schema.ServerPolicy, db: Session = Depends(get_db)):
    return policy_crud.create_custom_policy(db, policy)

# Read
@router.get("/server/{server_id}", response_model=policy_schema.ServerPolicy)
def get_server_policy(server_id: int, db: Session = Depends(get_db)) -> policy_schema.ServerPolicy:
    """
    Get the policy applied to the server.

        Args:
            server_id (int): 정책을 조회할 서버의 id
            db (Session, optional): Defaults to Depends(get_db).

        Returns:
            policy_schema.ServerPolicy: 조회된 정책
            
        Raises:
            HTTPException: 404 Not Found : 서버가 존재하지 않는 경우
            HTTPException: 422 - 잘못된 요청
            HTTPException: 500 - 서버 내부 오류
    """
    return policy_crud.get_server_policy(db, server_id)

@router.get("/container/{container_id}", response_model=policy_schema.ContainerPolicyRes)
def get_container_policy(server_id: int, container_id: int, db: Session = Depends(get_db)) -> policy_schema.ContainerPolicy:
    """
    Get the policy applied to the container.

        Args:
            server_id (int): 정책을 조회할 서버의 id
            container_id (int): 정책을 조회할 컨테이너의 id
            db (Session, optional): Defaults to Depends(get_db).

        Returns:
            policy_schema.ContainerPolicy: 조회된 정책
            
        Raises:
            HTTPException: 404 Not Found : 서버 또는 컨테이너가 존재하지 않는 경우
            HTTPException: 422 - 잘못된 요청
            HTTPException: 500 - 서버 내부 오류
    """
    return policy_crud.get_container_policy(db, server_id, container_id)

# @router.patch("/rawtp/{server_id}/{container_id}")
# def update_raw_tracepoint(server_id: int, container_id: int):
#     return {"container": container_id}

@router.post("/conflict/{server_id}")
def check_conflict(server_id: int, policy: policy_schema.ServerPolicy, db: Session = Depends(get_db)):
    """
    입력된 정책이 해당 서버에 기존 적용된 정책과 충돌하는지 확인합니다.

        Args:
            server_id (int): 비교를 진행할 서버의 id
            policy (policy_schema.ServerPolicy): 비교할 정책
            db (Session, optional): Defaults to Depends(get_db).

        Returns:
            dict: 충돌하는 기존 정책 목록 - 작업 중
        
        Raises:
            HTTPException: 404 Not Found : 서버가 존재하지 않는 경우
            HTTPException: 409 Conflict : 정책이 충돌하는 경우
            HTTPException: 422 - 잘못된 요청
            HTTPException: 500 - 서버 내부 오류
    """
    
    return policy_crud.check_conflict(db, server_id)


@router.post("/conflict/{server_id}/{container_id}")
def check_conflict(server_id: int, container_id: int, db: Session = Depends(get_db)):
    """
    Check if the input policy conflicts with the existing policy applied to the server.

        Args:
            server_id (int): 정책을 비교할 서버의 id
            container_id (int): 정책을 비교할 컨테이너의 id
            db (Session, optional): Defaults to Depends(get_db).

        Returns:
            dict: 충돌하는 기존 정책 목록
            
        Raises:
            HTTPException: 404 Not Found : 서버 또는 컨테이너가 존재하지 않는 경우
            HTTPException: 409 Conflict : 정책이 충돌하는 경우
            HTTPException: 422 - 잘못된 요청
            HTTPException: 500 - 서버 내부 오류
    """
    return policy_crud.check_conflict(db, server_id, container_id)


# # Update
# @router.put("/log_lev/{server_id}/{policy_id}")
# def update_policy_log_level(server_id: int, policy_id: int):
#     return {"container": server_id, "policy": policy_id}

# # Delete
# @router.delete("/{server_id}/{policy_id}")
# def delete_policy(server_id: int, policy_id: int):
#     return {"container": server_id, "policy": policy_id}
