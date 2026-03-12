# pytest 설정
import sys
from pathlib import Path
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from dotenv import load_dotenv
from unittest.mock import AsyncMock, MagicMock

# backend 루트 디렉토리를 PYTHONPATH에 추가
backend_root = Path(__file__).parent
sys.path.insert(0, str(backend_root))

# .env 파일 로드
load_dotenv(backend_root / ".env")


class MockRedis:
    """테스트용 Mock Redis"""
    def __init__(self):
        self.data = {}

    async def get(self, key: str):
        return self.data.get(key)

    async def set(self, key: str, value: str):
        self.data[key] = value

    async def setex(self, key: str, time: int, value: str):
        self.data[key] = value

    async def delete(self, key: str):
        if key in self.data:
            del self.data[key]

    async def exists(self, key: str):
        return key in self.data

    async def expire(self, key: str, time: int):
        pass

    async def incr(self, key: str):
        self.data[key] = self.data.get(key, 0) + 1
        return self.data[key]

    async def ttl(self, key: str) -> int:
        return -1  # 영구 TTL


@pytest.fixture(scope="session")
def event_loop():
    """세션 스코프 이벤트 루프"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
async def mock_redis():
    """Mock Redis fixture"""
    return MockRedis()


@pytest.fixture
async def client(mock_redis):
    """테스트용 AsyncClient - 실제 FastAPI 앱 사용"""
    # Redis 의존성 mock 설정
    from app import main

    # get_redis 함수를 mock으로 교체
    async def mock_get_redis():
        return mock_redis

    from app.core import rate_limit
    rate_limit.get_redis = mock_get_redis
    from app.core import dependencies
    dependencies.get_redis = mock_get_redis

    # Rate limit 체크를 비활성화하는 patch
    from app.core import rate_limit as rate_limit_module
    original_check = rate_limit_module.check_rate_limit
    rate_limit_module.check_rate_limit = AsyncMock(return_value=None)

    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    rate_limit_module.check_rate_limit = original_check


@pytest.fixture
async def db():
    """테스트용 DB 세션"""
    from app.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_user(client: AsyncClient):
    """테스트 사용자 생성 및 로그인"""
    import random

    # 고유한 이메일 생성
    email = f"test_user_fixture_{random.randint(10000, 99999)}@example.com"

    # 사용자 등록
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "TestP@ss123",
            "name": "테스트사용자"
        }
    )

    # 로그인
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "TestP@ss123"
        }
    )

    if login_response.status_code == 200:
        data = login_response.json()
        token = data.get("data", {}).get("access_token")
        return {
            "email": email,
            "password": "TestP@ss123",
            "name": "테스트사용자",
            "token": token
        }

    return None


@pytest.fixture
async def auth_headers(test_user):
    """인증 헤더 생성"""
    if test_user and test_user.get("token"):
        return {"Authorization": f"Bearer {test_user['token']}"}
    return {}


@pytest.fixture
async def auth_token_and_company(client: AsyncClient, test_user):
    """인증 토큰과 사업장 ID 반환"""
    import random

    auth_token = test_user.get("token") if test_user else None

    business_number = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10000, 99999)}"

    response = await client.post(
        "/api/v1/companies/",
        json={
            "business_name": "테스트사업장",
            "business_number": business_number,
            "representative_name": "테스트대표",
            "industry_type": "manufacturing",
            "employee_count": 15,
            "address": "테스트주소",
            "postal_code": "12345",
            "phone": "02-1234-5678"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    company_id = None
    selected_token = auth_token
    if response.status_code == 201:
        company = response.json()["data"]
        company_id = company["id"]
        # 사업장 선택
        select_response = await client.post(
            f"/api/v1/companies/{company['id']}/select",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if select_response.status_code == 200:
            selected_token = select_response.json()["data"]["access_token"]

    return {"token": selected_token, "company_id": company_id}


@pytest.fixture
async def auth_token(auth_token_and_company):
    """인증 토큰 (사업장 선택됨)"""
    return auth_token_and_company["token"]


@pytest.fixture
async def company_id(auth_token_and_company):
    """테스트 사업장 ID"""
    return auth_token_and_company["company_id"]


@pytest.fixture(autouse=True)
async def clean_db_before_test(request):
    """각 테스트 전에 DB 정리 (autouse, but only for employee and contracts tests)"""
    from app.db.session import AsyncSessionLocal
    from sqlalchemy import text

    # 현재 테스트 노드 이름 확인
    test_node_name = request.node.nodeid

    # employee, contracts, work_rules 테스트만 클린업
    if any(x in test_node_name for x in ("test_employees_api", "test_contracts_api", "test_work_rules_api")):
        async with AsyncSessionLocal() as session:
            try:
                # contracts, work_rules는 employees, companies와 종속되므로 먼저 삭제
                await session.execute(text("DELETE FROM contracts"))
                await session.execute(text("DELETE FROM work_rules"))
                await session.execute(text("DELETE FROM employees"))
                await session.execute(text("DELETE FROM companies"))
                await session.execute(text("DELETE FROM users"))
                await session.commit()
            except Exception:
                await session.rollback()
        yield
    else:
        yield
