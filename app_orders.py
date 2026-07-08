import time
from fastapi import FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Strict and complete CORS implementation to prevent browser 'Failed to fetch' errors
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response(status_code=200)
    else:
        response = await call_next(request)
        
    origin = request.headers.get("origin", "*")
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Idempotency-Key, X-Client-Id"
    return response

TOTAL_ORDERS = 49
RATE_LIMIT_CEILING = 15
WINDOW = 10

idempotency_cache = {}
rate_buckets = {}

# Catalog of static sequential mock orders
ORDER_CATALOG = [{"id": i, "item": f"Item Descriptor #{i}", "price": 10.0 * i} for i in range(1, TOTAL_ORDERS + 1)]

@app.post("/orders", status_code=201)
async def create_order(request: Request, idempotency_key: str = Header(None)):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Missing Idempotency-Key")
    
    if idempotency_key in idempotency_cache:
        return idempotency_cache[idempotency_key]
        
    new_id = f"ord_{int(time.time()*1000)}"
    response_data = {"id": new_id, "status": "created"}
    idempotency_cache[idempotency_key] = response_data
    return response_data

@app.get("/orders")
async def get_orders(
    limit: int = Query(default=10, ge=1), 
    cursor: str = Query(default=None),
    x_client_id: str = Header(None, alias="X-Client-Id")
):
    # Enforce Rate Limiting
    client = x_client_id or "anonymous"
    now = time.time()
    if client not in rate_buckets:
        rate_buckets[client] = []
    rate_buckets[client] = [t for t in rate_buckets[client] if now - t < WINDOW]
    
    if len(rate_buckets[client]) >= RATE_LIMIT_CEILING:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too Many Requests"},
            headers={"Retry-After": str(WINDOW)}
        )
        
    rate_buckets[client].append(now)

    # Process Cursor Pagination
    start_idx = 0
    if cursor:
        try:
            start_idx = int(cursor)
        except ValueError:
            start_idx = 0
            
    sliced_items = ORDER_CATALOG[start_idx : start_idx + limit]
    next_cursor = str(start_idx + limit) if (start_idx + limit) < TOTAL_ORDERS else ""

    return {
        "items": sliced_items,
        "next_cursor": next_cursor
    }
