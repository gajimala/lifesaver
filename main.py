import json
import time
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# 정적 파일 서빙
app.mount("/", StaticFiles(directory="public", html=True), name="static")

REQUESTS_FILE = "public/requests.json"  # Render에서 사용할 경로

class HelpRequest(BaseModel):
    lat: float
    lon: float
    timestamp: float  # ms

@app.post("/request-help")
def request_help(data: HelpRequest):
    try:
        # 요청 기록 파일이 없으면 새로 생성
        if not os.path.exists(REQUESTS_FILE):
            with open(REQUESTS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

        # 기존 요청들 불러오기
        with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
            requests = json.load(f)

        # 현재 시간을 밀리초로 가져오기
        now = time.time() * 1000  # 밀리초

        # 24시간 이내의 요청만 필터링
        recent_requests = [
            r for r in requests if now - r.get("timestamp", 0) < 86400000  # 24시간
        ]

        # 새 요청 추가
        recent_requests.append(data.dict())

        # 파일에 업데이트된 요청들 저장
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

        # 'lon'을 'lng'로 수정
        for item in data:
            if "lon" in item:
                item["lng"] = item.pop("lon")

        return data
    except Exception as e:
        return {"status": "error", "message": str(e)}
