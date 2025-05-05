import json
import time
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()

# 요청 기록 파일 경로 설정
REQUESTS_FILE = "public/requests.json"

# 데이터 모델 정의
class HelpRequest(BaseModel):
    lat: float
    lon: float
    timestamp: float  # 밀리초로 타임스탬프

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

        now = time.time() * 1000  # 현재 시간을 밀리초로
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

@app.get("/requests")
def get_requests():
    """구조 요청 확인용 엔드포인트"""
    try:
        with open(REQUESTS_FILE, encoding="utf-8") as f:
            requests = json.load(f)

        return requests
    except Exception as e:
        return {"status": "error", "message": str(e)}
