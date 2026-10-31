from fastapi import FastAPI, requests
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="AppPulse", version="1.0.0")

# Setup templates directory
templates = Jinja2Templates(directory="templates") 

@app.get("/", response_class=HTMLResponse) 
async def read_root(request: requests):
    return templates.TemplateResponse("index.html", {"request": request}) 

@app.get("/api/health") 
async def health_check():
    return {"status": "online", "service": "AppPulse API"}
