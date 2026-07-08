import os
from fastapi import FastAPI, HTTPException
from redis import Redis

app = FastAPI()

# Connects to the 'redis' service defined in docker-compose
redis_host = os.getenv("REDIS_HOST", "redis")
r = Redis(host=redis_host, port=6379, decode_responses=True)

@app.post("/hit/{key}")
async def hit_key(key: str):
    count = r.incr(f"counter:{key}")
    return {"key": key, "count": count}

@app.get("/count/{key}")
async def get_count(key: str):
    count = r.get(f"counter:{key}")
    return {"key": key, "count": int(count) if count else 0}

@app.get("/healthz")
async def healthz():
    try:
        r.ping()
        return {"status": "ok", "redis": "up"}
    except Exception:
        raise HTTPException(status_code=500, detail={"status": "error", "redis": "down"})
