# pytest 설정
import sys
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport
from dotenv import load_dotenv

# backend 루트 디렉토리를 PYTHONPATH에 추가
backend_root = Path(__file__).parent
sys.path.insert(0, str(backend_root))

# .env 파일 로드
load_dotenv(backend_root / ".env")


@pytest.fixture
async def client():
    """테스트용 AsyncClient - 실제 FastAPI 앱 사용"""
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db():
    """테스트용 DB 세션"""
    from app.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
