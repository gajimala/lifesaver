import json
import os
import time
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# 정적 파일 서빙
app.mount("/", StaticFiles(directory="public", html=True), name="static")

REQUESTS_FILE = "public/requests.json"

class HelpRequest(BaseModel):
    lat: float
    lon: float
    timestamp: float  # ms

@app.post("/request-help")
def request_help(data: HelpRequest):
    try:
        if not os.path.exists(REQUESTS_FILE):
            with open(REQUESTS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

        with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
            requests = json.load(f)

        now = time.time() * 1000
        recent_requests = [
            r for r in requests if now - r.get("timestamp", 0) < 86400000
        ]

        recent_requests.append(data.dict())

        with open(REQUESTS_FILE, "w", encoding="utf-8") as f:
            json.dump(recent_requests, f, ensure_ascii=False, indent=2)

        return {"status": "ok", "count": len(recent_requests)}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/lifesavers")
def get_lifesavers():
    try:
        with open("public/lifesavers.json", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            if "lon" in item:
                item["lng"] = item.pop("lon")

        return data
    except Exception as e:
        return {"status": "error", "message": str(e)}
