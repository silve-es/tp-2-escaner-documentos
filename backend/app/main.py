from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import detect, scan

app = FastAPI(title="DocScan API")

app.mount("/media", StaticFiles(directory="storage"), name="media")

app.include_router(detect.router)
app.include_router(scan.router)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}