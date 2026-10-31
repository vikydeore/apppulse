import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Uses environment variable or defaults to your docker-compose postgres service
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/apppulse")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
