import json
import os
import time
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

# 정적 파일 서빙 (index.html이 기본으로 로드되도록 설정)
app.mount("/", StaticFiles(directory="public", html=True), name="static")

REQUESTS_FILE = "public/requests.json"

class HelpRequest(BaseModel):
    lat: float
    lng: float
    timestamp: float  # ms

@app.post("/request-help")
def request_help(data: HelpRequest):
    try:
        if not os.path.exists(REQUESTS_FILE):
            with open(REQUESTS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

        with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
            requests = json.load(f)

        now = time.time() * 1000  # 현재 시간을 ms로 계산
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
        lifesavers_file_path = os.path.join("public", "lifesavers.json")
        with open(lifesavers_file_path, encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            if "lon" in item:
                item["lng"] = item.pop("lon")

        return data

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # os.environ.get() 대신 os.getenv() 사용
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
