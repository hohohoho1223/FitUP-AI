from fastapi import APIRouter, HTTPException
from models import search_recommendation, insert_recommendation, call_llm

router = APIRouter()

@router.get("/")
async def home():
    return {"message": "RAG API에 오신 것을 환영합니다. /generate_quests를 사용하여 퀘스트를 생성하세요."}

@router.post("/generate_quests")
async def generate_quests_endpoint(input_data: dict):
    if not input_data:
        raise HTTPException(status_code=400, detail="유효한 입력 데이터가 필요합니다.")
    
    try:
        # 사용자 요청에 대한 추천 운동 검색
        recommendation = search_recommendation(input_data["user_request"])
        
        # LLM을 통해 퀘스트 생성
        quests = call_llm(recommendation)

        # 데이터베이스에 사용자 요청과 추천 운동 저장
        insert_recommendation(input_data["user_request"], recommendation)

        return {
            "status": "success",
            "data": {
                "user_id": input_data["user_id"],
                "daily_quests": quests
            },
            "message": "퀘스트가 성공적으로 생성되었습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def register_routes(app):
    app.include_router(router)
