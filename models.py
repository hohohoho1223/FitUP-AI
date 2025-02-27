import sqlite3
from config import DATABASE_NAME
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
import openai

# 환경변수 로딩
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# LLM 초기화
model = init_chat_model("gpt-4o-mini", model_provider="openai")

def call_llm(user_message):
    prompt = f"""
    사용자가 요청한 내용: {user_message}
    너는 사람들의 운동을 돕는 게임 기반의 퀘스트 생성 시스템이야.
    너가 수행해야 할 역할은 퀘스트 생성이야.
    {{
      "user_id": "12345",
      "gender": "male",
      "chronic": "척추 측만증",
      "stats": {{
        "strength": 70,
        "stamina": 60,
        "endurance": 50
      }},
      "main_category": "헬스",
      "sub_category": "하체",
      "user_request": "오늘은 하체 운동을 하고 싶어",
      "goal": "근력 증가",
      "last_quest_status": {{
        "completed": ["벤치프레스 60kg 5세트"],
        "failed": ["하루 2L 물 섭취"]
      }}
    }}
    다음과 같은 입력 데이터를 받아서
    {{
      "user_id": "12345",
      "daily_quests": {{
        "fitness": {{
          1: {{ "contents": "스쿼트 80kg 5세트 수행", "points": 10 }},
          2: {{ "contents": "레그 익스텐션 50kg 5세트", "points": 5 }},
          3: {{ "contents": "레그프레스 160kg 5세트", "points": 20 }}
        }},
        "sleep": {{ "contents": "수면 8시간 유지", "points": 5 }},
        "daily": {{ "contents": "아침 공복에 물 500ml 마시기", "points": 5 }}
      }}
    }}
    형태의 출력을 내도록 할거야.

    모든 출력은 설명 및 상세 분석이 없이 단순 JSON만 반환해줘.
    """
    
    response = model.invoke(prompt)
    return response

def embed_text(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"  # 사용할 임베딩 모델
    )
    return response['data'][0]['embedding']  # 임베딩 결과 반환

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)  # 데이터베이스 연결
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형태로 반환
    return conn

def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            recommendation TEXT NOT NULL,
            embedding BLOB NOT NULL,  -- 임베딩 저장을 위한 BLOB 필드 추가
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_recommendation(user_message, recommendation):
    embedding = embed_text(user_message)  # 사용자 메시지 임베딩
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO recommendations (user_message, recommendation, embedding) VALUES (?, ?, ?)",
                   (user_message, recommendation, embedding))  # 임베딩 저장
    conn.commit()
    conn.close()

def search_recommendation(user_query):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT recommendation FROM recommendations WHERE user_message LIKE ?", ('%' + user_query + '%',))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "추천할 수 있는 운동이 없습니다."
