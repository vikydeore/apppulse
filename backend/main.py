from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import engine, SessionLocal, Base
import models

# Create database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AppPulse", version="1.0.0")
templates = Jinja2Templates(directory="templates")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic schema for incoming requests
class MonitorCreate(BaseModel):
    name: str
    url: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
async def health_check():
    return {"status": "online", "service": "AppPulse API"}

# API: Get all monitored endpoints
@app.get("/api/monitors")
async def get_monitors(db: Session = Depends(get_db)):
    monitors = db.query(models.Monitor).all()
    return monitors

# API: Add a new monitor endpoint
@app.post("/api/monitors")
async def create_monitor(monitor: MonitorCreate, db: Session = Depends(get_db)):
    db_monitor = models.Monitor(name=monitor.name, url=monitor.url, status="Operational", response_time="35 ms")
    db.add(db_monitor)
    db.commit()
    db.refresh(db_monitor)
    return db_monitor
