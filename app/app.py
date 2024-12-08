from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# React 빌드된 정적 파일 서빙
app.mount("/static", StaticFiles(directory="build/static"), name="static")

@app.get("/")
async def serve_react():
    # React의 index.html 반환
    return FileResponse("build/index.html")

# origins = [
#     "http://localhost:3000",  # 로컬 프론트엔드 서버
#     "http://localhost:8000"
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 허용할 도메인 리스트 (현재는 모든 도메인 허용)
    allow_credentials=True,
    allow_methods=["*"],  # 허용할 HTTP 메서드 (GET, POST 등)
    allow_headers=["*"],  # 허용할 HTTP 헤더
)