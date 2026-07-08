import time
import uuid
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI()

ALLOWED_CORS = "https://app-rjyb5e.example.com"
RATE_LIMIT = 9
WINDOW = 10
buckets = {}

@app.middleware("http")
async def master_middleware(request: Request, call_next):
    # 1. Request Context Identifier
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = req_id
    
    # 2. Rate Limiting Check
    client_id = request.headers.get("X-Client-Id", "anonymous")
    now = time.time()
    
    if client_id not in buckets:
        buckets[client_id] = []
    # Clear out older timestamps outside the window
    buckets[client_id] = [t for t in buckets[client_id] if now - t < WINDOW]
    
    if len(buckets[client_id]) >= RATE_LIMIT:
        return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})
        
    buckets[client_id].append(now)
    
    # Process Endpoint Execution
    if request.method == "OPTIONS":
        response = Response()
    else:
        response = await call_next(request)
        
    # Append Context and Custom Headers
    response.headers["X-Request-ID"] = req_id
    
    # 3. CORS Handling Execution
    origin = request.headers.get("origin")
    if origin == ALLOWED_CORS or "ds.study.iitm.ac.in" in str(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "X-Client-Id, X-Request-ID, Content-Type"
        
    return response

@app.get("/ping")
async def ping(request: Request):
    return {
        "email": "25f1002774@ds.study.iitm.ac.in",
        "request_id": request.state.request_id
    }
