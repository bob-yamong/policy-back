from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

username = os.getenv("POSTGRESQL_USERNAME")
password = os.getenv("POSTGRESQL_PASSWORD")
host = os.getenv("POSTGRESQL_HOST")
database = os.getenv("POSTGRESQL_DB")
port = os.getenv("POSTGRESQL_PORT", "5432")

if not username or not password or not host or not database:
    raise ValueError("Please set the environment variables for the database")

DB_URL = f"postgresql://{username}:{password}@{host}:{port}/{database}"

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