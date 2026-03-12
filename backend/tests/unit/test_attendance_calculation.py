"""
F-13 근태 관리 — 시간 계산 단위 테스트
"""

import pytest
from datetime import time
from app.services.attendance_service import AttendanceService
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


@pytest.fixture
async def service():
    """AttendanceService 인스턴스 (DB 없이)"""
    # 실제 DB 연결 없이 서비스의 계산 로직만 테스트
    # DB 세션 mock
    class MockDB:
        pass

    return AttendanceService(MockDB())


class TestCalculateWorkTimes:
    """calculate_work_times() 테스트"""

    async def test_정상_근무_9시_18시(self, service):
        """정상 근무 (9~18, 휴게 60분)"""
        result = service.calculate_work_times(
            actual_start=time(9, 0),
            actual_end=time(18, 0),
            scheduled_start=time(9, 0),
            scheduled_end=time(18, 0),
            break_minutes=60,
            is_holiday=False
        )

        assert result.total_work_minutes == 480
        assert result.overtime_minutes == 0
        assert result.night_minutes == 0
        assert result.holiday_minutes == 0

    async def test_연장근무_2시간(self, service):
        """연장근무 2시간"""
        result = service.calculate_work_times(
            actual_start=time(9, 0),
            actual_end=time(20, 0),
            scheduled_start=time(9, 0),
            scheduled_end=time(18, 0),
            break_minutes=60,
            is_holiday=False
        )

        assert result.total_work_minutes == 600
        assert result.overtime_minutes == 120
        assert result.night_minutes == 0
        assert result.holiday_minutes == 0

    async def test_야간근무_포함(self, service):
        """야간근무 포함 (18~23시)"""
        result = service.calculate_work_times(
            actual_start=time(18, 0),
            actual_end=time(23, 0),
            scheduled_start=time(18, 0),
            scheduled_end=time(22, 0),
            break_minutes=30,
            is_holiday=False
        )

        assert result.total_work_minutes == 270  # 5시간 - 30분
        assert result.overtime_minutes == 60  # 22:00 이후 1시간
        assert result.night_minutes == 60  # 22:00 ~ 23:00 = 60분 (break 미차감)
        assert result.holiday_minutes == 0

    async def test_야간_자정경계_22시_02시(self, service):
        """야간 자정 경계 (22~02시)"""
        result = service.calculate_work_times(
            actual_start=time(22, 0),
            actual_end=time(2, 0),  # 다음날 02:00
            scheduled_start=time(22, 0),
            scheduled_end=time(2, 0),
            break_minutes=0,
            is_holiday=False
        )

        assert result.total_work_minutes == 240  # 4시간
        assert result.overtime_minutes == 0
        assert result.night_minutes == 240  # 전부 야간
        assert result.holiday_minutes == 0

    async def test_휴일근무(self, service):
        """휴일근무"""
        result = service.calculate_work_times(
            actual_start=time(9, 0),
            actual_end=time(18, 0),
            scheduled_start=time(9, 0),
            scheduled_end=time(18, 0),
            break_minutes=60,
            is_holiday=True
        )

        assert result.total_work_minutes == 480
        assert result.overtime_minutes == 0
        assert result.night_minutes == 0
        assert result.holiday_minutes == 480

    async def test_휴일_연장_야간(self, service):
        """휴일 + 연장 + 야간"""
        result = service.calculate_work_times(
            actual_start=time(9, 0),
            actual_end=time(23, 0),
            scheduled_start=time(9, 0),
            scheduled_end=time(18, 0),
            break_minutes=60,
            is_holiday=True
        )

        assert result.total_work_minutes == 780  # 14시간 - 60분
        assert result.overtime_minutes == 300  # 18:00 초과분
        assert result.night_minutes == 60  # 22:00 ~ 23:00
        assert result.holiday_minutes == 780  # 전부 휴일

    async def test_출근만_기록_actual_end_None(self, service):
        """출근만 기록 (actual_end=None)"""
        result = service.calculate_work_times(
            actual_start=time(9, 0),
            actual_end=None,
            scheduled_start=time(9, 0),
            scheduled_end=time(18, 0),
            break_minutes=60,
            is_holiday=False
        )

        assert result.total_work_minutes == 0
        assert result.overtime_minutes == 0
        assert result.night_minutes == 0
        assert result.holiday_minutes == 0

    async def test_휴게시간_0분(self, service):
        """휴게시간 0분"""
        result = service.calculate_work_times(
            actual_start=time(9, 0),
            actual_end=time(18, 0),
            scheduled_start=time(9, 0),
            scheduled_end=time(18, 0),
            break_minutes=0,
            is_holiday=False
        )

        assert result.total_work_minutes == 540  # 9시간
        assert result.overtime_minutes == 0  # 소정근로 = 9시간 (break=0이므로)
        assert result.night_minutes == 0
        assert result.holiday_minutes == 0

    async def test_야간_전체_22시_06시(self, service):
        """야간 전체 (22~06시 근무)"""
        result = service.calculate_work_times(
            actual_start=time(22, 0),
            actual_end=time(6, 0),  # 다음날 06:00
            scheduled_start=time(22, 0),
            scheduled_end=time(6, 0),
            break_minutes=60,
            is_holiday=False
        )

        assert result.total_work_minutes == 420  # 8시간 - 60분
        assert result.overtime_minutes == 0
        assert result.night_minutes == 480  # 전부 야간 (22:00~06:00 = 8시간, break 미차감)
        assert result.holiday_minutes == 0

    async def test_짧은_근무_4시간(self, service):
        """짧은 근무 (4시간)"""
        result = service.calculate_work_times(
            actual_start=time(9, 0),
            actual_end=time(13, 0),
            scheduled_start=time(9, 0),
            scheduled_end=time(18, 0),
            break_minutes=0,
            is_holiday=False
        )

        assert result.total_work_minutes == 240
        assert result.overtime_minutes == 0
        assert result.night_minutes == 0
        assert result.holiday_minutes == 0

    async def test_새벽_출근_05시_14시(self, service):
        """새벽 출근 (05:00~14:00)"""
        result = service.calculate_work_times(
            actual_start=time(5, 0),
            actual_end=time(14, 0),
            scheduled_start=time(6, 0),
            scheduled_end=time(15, 0),
            break_minutes=60,
            is_holiday=False
        )

        assert result.total_work_minutes == 480  # 9시간 - 60분
        assert result.overtime_minutes == 0  # 소정근로 9시간 (6~15시 - 60분 = 480분)
        assert result.night_minutes == 0  # 05:00~06:00은 야간이 아님 (22:00~06:00만 야간)
        assert result.holiday_minutes == 0
