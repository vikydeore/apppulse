from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
import time
import requests

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

# Helper function to check live URL status and latency
def check_url_health(url: str):
    start_time = time.time()
    try:
        # Send a GET request with a 5-second timeout
        response = requests.get(url, timeout=5, allow_redirects=True)
        latency = round((time.time() - start_time) * 1000) # Convert to milliseconds
        
        # Consider 2xx and 3xx status codes as operational
        if 200 <= response.status_code < 400:
            return "Operational", f"{latency} ms"
        else:
            return "Down", f"{latency} ms"
    except requests.RequestException:
        # Connection error, timeout, or invalid domain name
        return "Down", "N/A"

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

# API: Add a new monitor endpoint and perform live check
@app.post("/api/monitors")
async def create_monitor(monitor: MonitorCreate, db: Session = Depends(get_db)):
    # Perform real-time health check on the provided URL
    status, response_time = check_url_health(monitor.url)
    
    db_monitor = models.Monitor(
        name=monitor.name, 
        url=monitor.url, 
        status=status, 
        response_time=response_time
    )
    db.add(db_monitor)
    db.commit()
    db.refresh(db_monitor)
    return db_monitor
