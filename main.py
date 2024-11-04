from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# from database.database import engine
# from database import models
from routes import routers

API_VERSION = "v1"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # models.Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(root_path=f"/api/{API_VERSION}", lifespan=lifespan)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in routers:
    app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)