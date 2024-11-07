import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from starlette import status
from sqlalchemy.orm import Session
from pydantic_yaml import parse_yaml_raw_as, to_yaml_str
from ruamel.yaml import YAML

from database.database import get_db
from schema import policy_schema
from crud import policy_crud

router = APIRouter(
    prefix="/policy",
    tags=["Policy"]
)

# Create
@router.post("/custom", status_code=status.HTTP_201_CREATED, response_model=policy_schema.ContainerPolicyCreateRes)
def create_policy(policy: policy_schema.ServerPolicy, db: Session = Depends(get_db)):
    """
    Create a custom policy.

        Args:
            policy (policy_schema.ServerPolicy): 추가할 사용자 정의 정책
            db (Session, optional): Defaults to Depends(get_db).

        Returns:
            policy_schema.ContainerPolicyCreateRes: 추가에 실패한 사용자 정의 정책 목록
            
        Raises:
            HTTPException: 409 Conflict : 기존 정책이 존재하는 경우
            HTTPException: 422 - 잘못된 요청
            HTTPException: 500 - 서버 내부 오류
    """
    return {"containers": policy_crud.create_custom_policy(db, policy)}

@router.post("/upload/", response_model=policy_schema.ContainerPolicyCreateRes)
async def create_upload_policy(file: UploadFile, db: Session = Depends(get_db)):
    """
    Create a custom policy using a yaml

        Args:
            file (UploadFile): 정책 yaml 파일

        Returns:
            policy_schema.ContainerPolicyCreateRes: 업로드에 실패한 정책 목록
            
        Raises:
            HTTPException: 409 Conflict : 기존 정책이 존재하는 경우
            HTTPException: 422 - 잘못된 요청
            HTTPException: 500 - 서버 내부 오류
    """
    content = await file.read()
    policy = parse_yaml_raw_as(policy_schema.ServerPolicy, content) 
    
    return {"containers": policy_crud.create_custom_policy(db, policy)}

@router.post("/apply/{server_id}")
def apply_policy(server_id: int, db: Session=Depends(get_db)):
    """
    정책을 server_id 서버에 전달합니다.

    Args:
        server_id (int): 정책을 전달 받을 서버의 id
        db (Session, optional): Defaults to Depends(get_db).
    """
    return policy_crud.apply_policy(db, server_id)

# Read
@router.get("/server/{server_id}", response_model=policy_schema.PolicyRes)
def get_server_policy(server_id: int, db: Session = Depends(get_db)) -> policy_schema.ServerPolicy:
    """
    Get the policy applied to the server.

        Args:
            server_id (int): 정책을 조회할 서버의 id
            db (Session, optional): Defaults to Depends(get_db).

        Returns:
            policy_schema.PolicyRes: 조회된 정책
            
        Raises:
            HTTPException: 404 Not Found : 서버가 존재하지 않는 경우
            HTTPException: 422 - 잘못된 요청
            HTTPException: 500 - 서버 내부 오류
    """
    return policy_crud.get_server_policy(db, server_id)

@router.get("/container/{container_id}", response_model=policy_schema.PolicyRes)
def get_container_policy(container_id: int, db: Session = Depends(get_db)) -> policy_schema.ContainerPolicy:
    """
    Get the policy applied to the container.

        Args:
            container_id (int): 정책을 조회할 컨테이너의 id
            db (Session, optional): Defaults to Depends(get_db).

        Returns:
            policy_schema.PolicyRes: 조회된 정책
            
        Raises:
            HTTPException: 404 Not Found : 서버 또는 컨테이너가 존재하지 않는 경우
            HTTPException: 422 - 잘못된 요청
            HTTPException: 500 - 서버 내부 오류
    """
    return policy_crud.get_container_policy(db, container_id)

@router.get("/")
def get_policy_list(db: Session = Depends(get_db)):
    """
    Get the list of policies.

        Args:
            db (Session, optional): Defaults to Depends(get_db).

        Returns:
            List[policy_schema.PolicyRes]: 정책 목록
            
        Raises:
            HTTPException: 500 - 서버 내부 오류
    """
    return policy_crud.get_policy_list(db)

@router.get("/{policy_id}", response_model=policy_schema.ServerPolicy)
def get_policy_by_policy_id(policy_name: str, db: Session = Depends(get_db)):
    return policy_crud.get_policy_by_policy_id(db, policy_name)


# @router.patch("/rawtp/{server_id}/{container_id}")
# def update_raw_tracepoint(server_id: int, container_id: int):
#     return {"container": container_id}

@router.post("/conflict/{server_id}")
def check_conflict(server_id: int, policy: policy_schema.ServerPolicy, db: Session = Depends(get_db)):
    """
    (작업중 변경 사항 발생 가능성 있음)
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
    (작업 전 변동사항 있을 수 있음음)
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
