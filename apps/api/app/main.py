import os
import socket
import time

from fastapi import FastAPI, HTTPException

app = FastAPI(title="dockyard api", version=os.getenv("APP_VERSION", "dev"))

STARTED_AT = time.time()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "uptime_s": round(time.time() - STARTED_AT, 1),
    }


@app.get("/ready")
def ready():
    # Week 2: this will also check the database and the queue.
    return {"ready": True}


@app.get("/work")
def work(n: int = 1):
    if n < 1 or n > 100:
        raise HTTPException(status_code=400, detail="n must be between 1 and 100")
    return {
        "processed": n,
        "host": socket.gethostname(),
        "version": os.getenv("APP_VERSION", "dev"),
    }
