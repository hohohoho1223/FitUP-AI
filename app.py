from fastapi import FastAPI
from dotenv import load_dotenv
from routes import register_routes
from models import initialize_db

# 환경변수 로딩
load_dotenv()

# FastAPI 앱 초기화
app = FastAPI()

# 데이터베이스 초기화
initialize_db()

# 라우트 등록
register_routes(app)
