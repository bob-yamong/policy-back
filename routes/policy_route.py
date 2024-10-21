from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status


router = APIRouter(
    prefix="/policy",
    tags=["Policy"]
)

# Create
@router.post("/{container_id}")
def create_policy(container_id: int):
    return {"container": container_id}

# Read
@router.get("/{container_id}/{policy_id}")
def get_policy(container_id: int, policy_id: int):
    return {"container": container_id, "policy": policy_id}

# Update
@router.put("/log_lev/{container_id}/{policy_id}")
def update_policy_log_level(container_id: int, policy_id: int):
    return {"container": container_id, "policy": policy_id}

# Delete
@router.delete("/{container_id}/{policy_id}")
def delete_policy(container_id: int, policy_id: int):
    return {"container": container_id, "policy": policy_id}
