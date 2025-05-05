import json
import os
import time
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# FastAPI 애플리케이션 설정
app = FastAPI()

# CORS 설정 (모든 도메인에서 접근 가능)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 요청을 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 정적 파일 서빙
app.mount("/", StaticFiles(directory="public", html=True), name="static")

REQUESTS_FILE = "public/requests.json"

class HelpRequest(BaseModel):
    lat: float
    lon: float
    timestamp: float  # ms

@app.get("/request-help")
def request_help(lat: float, lon: float, timestamp: float):
    try:
        # 요청 데이터 처리 (POST 대신 GET으로 처리)
        if not os.path.exists(REQUESTS_FILE):
            with open(REQUESTS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

        with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
            requests = json.load(f)

        now = time.time() * 1000  # 현재 시간을 ms로 계산
        recent_requests = [
            r for r in requests if now - r.get("timestamp", 0) < 86400000
        ]

        # 새 요청 추가
        recent_requests.append({"lat": lat, "lon": lon, "timestamp": timestamp})

        # 파일에 저장
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

        # lon을 lng로 바꾸는 작업
        for item in data:
            if "lon" in item:
                item["lng"] = item.pop("lon")

        return data

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # 포트 번호를 환경 변수에서 가져오거나 기본값 8000으로 설정
    port = int(os.getenv("PORT", 8000))  # 환경 변수 PORT가 없으면 8000 포트로 설정
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
