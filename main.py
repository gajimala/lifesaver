import json
import time
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import asyncpg  # PostgreSQL 연결을 위한 라이브러리

app = FastAPI()


# PostgreSQL 데이터베이스 연결 함수
async def connect_db():
    return await asyncpg.connect(
        user="kcg_lifesaver_user",  # Render에서 제공한 유저명
        password="ljdJkWKbKFxyyzQhMZn4Nz4c9gH3A6rW",  # Render에서 제공한 비밀번호
        database="kcg_lifesaver",  # Render에서 생성한 DB명
        host="dpg-d0ccuc3uibrs73ccqhe0-a",  # Render에서 제공한 호스트
        port=5432  # 기본 포트 5432
    )

# 데이터 모델 정의
class HelpRequest(BaseModel):
    lat: float
    lng: float
    timestamp: float  # ms

@app.post("/request-help")
async def request_help(data: HelpRequest):
    try:
        conn = await connect_db()

        # 데이터베이스에 요청 데이터 삽입
        await conn.execute("""
            INSERT INTO requests(lat, lon, timestamp)
            VALUES($1, $2, $3)
        """, data.lat, data.lng, data.timestamp)

        await conn.close()
        return {"status": "ok", "message": "Request processed successfully"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/requests")
async def get_requests():
    """구조 요청 확인용 엔드포인트"""
    try:
        conn = await connect_db()
        result = await conn.fetch("SELECT * FROM requests")
        await conn.close()

        return {"requests": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/lifesavers")
async def get_lifesavers():
    try:
        with open("public/lifesavers.json", encoding="utf-8") as f:
            data = json.load(f)

        # 'lon'을 'lng'로 수정
        for item in data:
            if "lon" in item:
                item["lng"] = item.pop("lon")

# 정적 파일 서빙
app.mount("/", StaticFiles(directory="public", html=True), name="static")
        return data
    except Exception as e:
        return {"status": "error", "message": str(e)}
