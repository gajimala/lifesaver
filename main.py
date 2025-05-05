import requests
import json
import base64
from fastapi import FastAPI
from pydantic import BaseModel
import os
import time

app = FastAPI()

# GitHub API와 연결할 정보
repo_owner = "gajimala"  # GitHub 사용자명
repo_name = "lifesaver"  # GitHub 리포지토리명
token = os.getenv("MY_TOKEN")  # 환경변수에서 GitHub Personal Access Token 가져오기

if not token:
    raise Exception("GitHub token is not set. Please set the GITHUB_TOKEN environment variable.")

# GitHub에 파일을 업로드하는 함수
def update_github_file(file_path, content, sha=None):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}'
    headers = {'Authorization': f'token {token}'}
    
    # GitHub API는 Base64로 인코딩된 데이터를 필요로 함
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

    # GitHub에서 파일을 업데이트할 때 사용되는 데이터
    payload = {
        "message": "Update structure data",
        "content": encoded_content,
        "sha": sha  # 파일의 이전 sha 값 (수정할 때 사용)
    }

    response = requests.put(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()  # 성공적으로 업데이트된 파일 정보 반환
    else:
        raise Exception(f"GitHub API error: {response.status_code}, {response.text}")

# GitHub에서 파일 읽기
def read_github_file(file_path):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}'
    headers = {'Authorization': f'token {token}'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        file_data = response.json()
        file_content = base64.b64decode(file_data['content']).decode('utf-8')
        sha = file_data['sha']  # 파일의 sha 값을 반환
        return json.loads(file_content), sha  # JSON 형식으로 반환 및 sha 값 반환
    else:
        raise Exception(f"GitHub API error: {response.status_code}, {response.text}")


REQUESTS_FILE = "public/requests.json"

class HelpRequest(BaseModel):
    lat: float
    lon: float
    timestamp: float  # ms

@app.post("/request-help")
def request_help(data: HelpRequest):
    try:
        # GitHub에서 기존 요청 데이터를 읽음 및 sha 값 가져오기
        requests_data, sha = read_github_file(REQUESTS_FILE)

        now = time.time() * 1000
        recent_requests = [
            r for r in requests_data if now - r.get("timestamp", 0) < 86400000
        ]

        # 새로운 요청 데이터 추가
        recent_requests.append(data.dict())

        # GitHub에 업데이트된 데이터를 업로드
        update_github_file(REQUESTS_FILE, json.dumps(recent_requests, ensure_ascii=False, indent=2), sha)

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
 
