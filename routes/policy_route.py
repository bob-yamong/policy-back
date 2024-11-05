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
# @router.post("/{server_id}")
# def create_policy(container_id: int):
#     return {"container": container_id}

# Read
@router.get("/{server_id}", response_model=policy_schema.ServerPolicy)
def get_server_policy(server_id: int, db: Session = Depends(get_db)):
    return policy_crud.get_server_policy(db, server_id)

@router.get("/{server_id}/{container_id}", response_model=policy_schema.ContainerPolicy)
def get_container_policy(server_id: int, container_id: int, db: Session = Depends(get_db)):
    return 

@router.patch("rawtp/{server_id}/{container_id}")
def update_raw_tracepoint(server_id: int, container_id: int):
    return {"container": container_id}


# # Update
# @router.put("/log_lev/{server_id}/{policy_id}")
# def update_policy_log_level(server_id: int, policy_id: int):
#     return {"container": server_id, "policy": policy_id}

# # Delete
# @router.delete("/{server_id}/{policy_id}")
# def delete_policy(server_id: int, policy_id: int):
#     return {"container": server_id, "policy": policy_id}
