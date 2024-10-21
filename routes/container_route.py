from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status


router = APIRouter(
    prefix="/container",
    tags=["Container"]
)

# SSE
@router.get("/{container_id}/logs")
def get_container_sse(container_id: int):
    return {"container": container_id}

# health check
@router.get("/health/{container_id}")
def get_container_health(container_id: int):
    return {"container": container_id}

@router.get("/health")
def get_container_health():
    return {"": container_id}

# Read
@router.get("/")
def get_container_list():
    return {"container": "list"}

@router.get("/{container_id}")
def get_container(container_id: int):
    return {"container": container_id}

