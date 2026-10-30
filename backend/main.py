from fastapi import FastAPI
import requests

app = FastAPI(title="AppPulse Backend", version="1.0")

@app.get("/")
def read_root():
    return {"status": "online", "service": "AppPulse API"}

@app.get("/check")
def check_url(url: str):
    try:
        response = requests.get(url, timeout=5)
        return {
            "url": url,
            "status_code": response.status_code,
            "healthy": response.status_code == 200
        }
    except Exception as e:
        return {"url": url, "healthy": False, "error": str(e)}
