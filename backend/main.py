from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
import time
import requests
import threading

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
        response = requests.get(url, timeout=5, allow_redirects=True)
        latency = round((time.time() - start_time) * 1000) # Convert to milliseconds
        
        if 200 <= response.status_code < 400:
            return "Operational", f"{latency} ms"
        else:
            return "Down", f"{latency} ms"
    except requests.RequestException:
        return "Down", "N/A"

# Background worker thread to continuously re-check all URLs every 10 seconds
def background_monitor_worker():
    while True:
        time.sleep(10)
        db = SessionLocal()
        try:
            monitors = db.query(models.Monitor).all()
            for monitor in monitors:
                status, response_time = check_url_health(monitor.url)
                monitor.status = status
                monitor.response_time = response_time
                db.commit()
        except Exception as e:
            print(f"Background monitor error: {e}")
        finally:
            db.close()

# Start background thread when FastAPI boots up
@app.on_event("startup")
async def startup_event():
    worker_thread = threading.Thread(target=background_monitor_worker, daemon=True)
    worker_thread.start()

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

# API: Add a new monitor endpoint and do initial check
@app.post("/api/monitors")
async def create_monitor(monitor: MonitorCreate, db: Session = Depends(get_db)):
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

# API: Delete a monitor endpoint by ID
@app.delete("/api/monitors/{monitor_id}")
async def delete_monitor(monitor_id: int, db: Session = Depends(get_db)):
    monitor = db.query(models.Monitor).filter(models.Monitor.id == monitor_id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    db.delete(monitor)
    db.commit()
    return {"message": "Monitor deleted successfully"}
