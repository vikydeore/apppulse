from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base

class Monitor(Base):
    __tablename__ = "monitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    url = Column(String, nullable=False)
    status = Column(String, default="Pending")  # Operational, Down, Pending
    response_time = Column(String, default="N/A")
    created_at = Column(DateTime, default=datetime.utcnow)
