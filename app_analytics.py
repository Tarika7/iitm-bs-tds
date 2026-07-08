from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

API_KEY = "ak_y1vrlkqc2thdz21byvuunpxk"

class Event(BaseModel):
    user: str
    amount: float
    ts: int

class Batch(BaseModel):
    events: List[Event]

@app.post("/analytics")
async def process_analytics(x_api_key: str = Header(None), batch: Batch = None):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    events = batch.events
    total_events = len(events)
    unique_users = len(set(e.user for e in events))
    
    revenue = sum(e.amount for e in events if e.amount > 0)
    
    user_revenue: Dict[str, float] = {}
    for e in events:
        if e.amount > 0:
            user_revenue[e.user] = user_revenue.get(e.user, 0.0) + e.amount
            
    top_user = max(user_revenue, key=user_revenue.get) if user_revenue else ""
    
    return {
        "email": "25f1002774@ds.study.iitm.ac.in",
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": revenue,
        "top_user": top_user
    }
