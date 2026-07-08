import time
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from typing import List

app = FastAPI()

START_TIME = time.time()
HTTP_REQUESTS_TOTAL = 0
LOG_STORAGE: List[dict] = []

def log_event(level: str, path: str, req_id: str):
    LOG_STORAGE.append({
        "level": level,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "path": path,
        "request_id": req_id
    })

@app.middleware("http")
async def track_metrics_and_logs(request: Request, call_next):
    global HTTP_REQUESTS_TOTAL
    HTTP_REQUESTS_TOTAL += 1
    
    req_id = request.headers.get("X-Request-ID", "internal-id")
    log_event("info", request.url.path, req_id)
    
    response = await call_next(request)
    return response

@app.get("/work")
async def do_work(n: int = 1):
    return {"email": "25f1002774@ds.study.iitm.ac.in", "done": n}

@app.get("/metrics")
async def metrics():
    # Standard Prometheus plain text format representation
    lines = [
        "# HELP http_requests_total Total number of HTTP requests processed.",
        "# TYPE http_requests_total counter",
        f"http_requests_total {HTTP_REQUESTS_TOTAL}"
    ]
    return Response(content="\n".join(lines) + "\n", media_type="text/plain")

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "uptime_s": time.time() - START_TIME}

@app.get("/logs/tail")
async def tail_logs(limit: int = 10):
    return LOG_STORAGE[-limit:]
