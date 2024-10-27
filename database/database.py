from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = "postgresql://postgres:yamong@localhost:5432/yamong"

engine = {
    'project': create_engine(DB_URL),
}

project_base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False)
SessionLocal.configure(binds={
    project_base: engine['project']
})


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()