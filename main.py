from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
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

for router in routers:
    app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)