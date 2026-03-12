# API 테스트용 conftest.py
import pytest


@pytest.fixture(autouse=True)
async def clean_db_before_test(request):
    """각 테스트 전에 DB 정리"""
    from sqlalchemy import text
    import sys
    from pathlib import Path

    # backend 루트 디렉토리를 PYTHONPATH에 추가
    backend_root = Path(__file__).parent.parent
    sys.path.insert(0, str(backend_root))

    try:
        from app.db.session import AsyncSessionLocal
    except ImportError:
        yield
        return

    # 현재 테스트 노드 이름 확인
    test_node_name = request.node.nodeid

    # payroll, payslips, compliance, 또는 chat 테스트 클린업
    if any(x in test_node_name for x in ("test_payroll_api", "test_payslips_api", "test_compliance_api", "test_chat_api")):
        async with AsyncSessionLocal() as session:
            try:
                await session.execute(text("DELETE FROM chat_messages"))
                await session.execute(text("DELETE FROM chat_sessions"))
                await session.execute(text("DELETE FROM payslips"))
                await session.execute(text("DELETE FROM work_rules"))
                await session.execute(text("DELETE FROM contracts"))
                await session.execute(text("DELETE FROM employees"))
                await session.execute(text("DELETE FROM companies"))
                await session.execute(text("DELETE FROM users"))
                await session.commit()
            except Exception:
                await session.rollback()
        yield
    else:
        yield
