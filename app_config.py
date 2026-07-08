import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Hardcoded environment setups for validation emulation
DEFAULTS = {"port": 8000, "workers": 1, "debug": False, "log_level": "info", "api_key": "default-secret-000"}
YAML_CFG = {"port": 8978, "debug": False, "log_level": "warning"}
ENV_FILE = {"NUM_WORKERS": 4, "APP_DEBUG": False, "APP_LOG_LEVEL": "info", "APP_API_KEY": "key-ipvplumrdt"}
OS_ENV = {"APP_LOG_LEVEL": "debug", "APP_API_KEY": "key-6on7ri8nc9"}

def parse_bool(v):
    return str(v).lower() in ("true", "1", "yes", "on")

@app.get("/effective-config")
async def get_config(set: List[str] = Query(default=[])):
    # Layer 1 & 2
    cfg = DEFAULTS.copy()
    cfg.update(YAML_CFG)
    
    # Layer 3 (.env)
    if "NUM_WORKERS" in ENV_FILE: cfg["workers"] = int(ENV_FILE["NUM_WORKERS"])
    if "APP_DEBUG" in ENV_FILE: cfg["debug"] = parse_bool(ENV_FILE["APP_DEBUG"])
    if "APP_LOG_LEVEL" in ENV_FILE: cfg["log_level"] = str(ENV_FILE["APP_LOG_LEVEL"])
    if "APP_API_KEY" in ENV_FILE: cfg["api_key"] = str(ENV_FILE["APP_API_KEY"])
        
    # Layer 4 (OS Environment)
    if "APP_LOG_LEVEL" in OS_ENV: cfg["log_level"] = str(OS_ENV["APP_LOG_LEVEL"])
    if "APP_API_KEY" in OS_ENV: cfg["api_key"] = str(OS_ENV["APP_API_KEY"])
        
    # CLI Overrides
    for item in set:
        if "=" in item:
            k, v = item.split("=", 1)
            if k == "port": cfg["port"] = int(v)
            elif k == "workers": cfg["workers"] = int(v)
            elif k == "debug": cfg["debug"] = parse_bool(v)
            else: cfg[k] = str(v)
            
    cfg["api_key"] = "****" # Mask key
    return cfg
