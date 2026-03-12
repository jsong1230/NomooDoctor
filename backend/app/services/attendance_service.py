# 근태 관리 서비스
from datetime import date, time, datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, extract, func, case
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.db.models.salary import WorkRecord
from app.db.models.employee import Employee
from app.repositories.work_record_repo import WorkRecordRepository
from app.repositories.employee_repo import EmployeeRepository
from app.core.exceptions import NotFoundError, ConflictError, ValidationError


class WorkTimeResult(BaseModel):
    """근무 시간 계산 결과"""
    total_work_minutes: int
    overtime_minutes: int
    night_minutes: int
    holiday_minutes: int


class AttendanceService:
    """근태 관리 비즈니스 로직"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.work_record_repo = WorkRecordRepository(db)
        self.employee_repo = EmployeeRepository(db)

    def calculate_work_times(
        self,
        actual_start: time | None,
        actual_end: time | None,
        scheduled_start: time,
        scheduled_end: time,
        break_minutes: int,
        is_holiday: bool
    ) -> WorkTimeResult:
        """
        연장/야간/휴일 시간 자동 계산

        Args:
            actual_start: 실제 출근 시간
            actual_end: 실제 퇴근 시간
            scheduled_start: 예정 출근 시간
            scheduled_end: 예정 퇴근 시간
            break_minutes: 휴게 시간 (분)
            is_holiday: 휴일 여부

        Returns:
            WorkTimeResult (total_work_minutes, overtime_minutes, night_minutes, holiday_minutes)
        """
        # 실제 근무 시간이 미확정이면 0 반환
        if not actual_start or not actual_end:
            return WorkTimeResult(
                total_work_minutes=0,
                overtime_minutes=0,
                night_minutes=0,
                holiday_minutes=0
            )

        # 1. 총 근무 시간 계산
        start_min = actual_start.hour * 60 + actual_start.minute
        end_min = actual_end.hour * 60 + actual_end.minute

        # 야간을 걸쳐서 다음날 근무하는 경우 (end_min < start_min이면 +24시간)
        if end_min <= start_min:
            end_min += 1440  # +24시간

        total_work_minutes = max(0, end_min - start_min - break_minutes)

        # 2. 야간근무 시간 계산 (22:00 ~ 06:00)
        night_minutes = self._calculate_night_minutes(actual_start, actual_end)

        # 3. 연장근무 시간 계산 (소정근로시간 초과분)
        scheduled_start_min = scheduled_start.hour * 60 + scheduled_start.minute
        scheduled_end_min = scheduled_end.hour * 60 + scheduled_end.minute

        # 소정근로 시간이 다음날에 걸치는 경우
        if scheduled_end_min <= scheduled_start_min:
            scheduled_end_min += 1440

        scheduled_work_minutes = scheduled_end_min - scheduled_start_min - break_minutes
        overtime_minutes = max(0, total_work_minutes - scheduled_work_minutes)

        # 4. 휴일근무 시간 계산
        if is_holiday:
            holiday_minutes = total_work_minutes
        else:
            holiday_minutes = 0

        return WorkTimeResult(
            total_work_minutes=total_work_minutes,
            overtime_minutes=overtime_minutes,
            night_minutes=night_minutes,
            holiday_minutes=holiday_minutes
        )

    def _calculate_night_minutes(self, actual_start: time, actual_end: time) -> int:
        """
        야간근무 시간 계산 (22:00 ~ 06:00)

        알고리즘:
        - 시간을 분 단위로 변환 (0:00 = 0, 24:00 = 1440)
        - 야근으로 다음날까지 근무하는 경우 end_min += 1440
        - 야간 시간대: 22:00(1320분) ~ 06:00(1800분=30:00)
        - 당일 야간대(22:00~24:00)와 다음날 야간대(0:00~6:00)의 교집합 계산
        """
        start_min = actual_start.hour * 60 + actual_start.minute
        end_min = actual_end.hour * 60 + actual_end.minute

        # 야근으로 다음날까지 근무하는 경우
        if end_min <= start_min:
            end_min += 1440  # +24시간

        # 야간 시간대: 22:00(1320분) ~ 06:00(1800분=30:00)
        night_start = 1320  # 22:00
        night_end = 1800    # 06:00 (다음날)

        # 당일 야간대 (22:00~24:00)
        overlap1 = max(0, min(end_min, 1440) - max(start_min, night_start))

        # 다음날 야간대 (0:00~6:00) -- end_min이 1440 초과인 경우
        if end_min > 1440:
            # 다음날 근무 시간: end_min - 1440
            # 다음날 야간: 0 ~ 360(6시간)
            next_day_start = max(0, start_min - 1440 if start_min > 1440 else 0)
            next_day_end = min(end_min - 1440, 360)
            overlap2 = max(0, next_day_end - next_day_start)
        else:
            overlap2 = 0

        return max(0, overlap1 + overlap2)

    async def create_record(
        self,
        company_id: UUID,
        employee_id: UUID,
        work_date: date,
        scheduled_start: time,
        scheduled_end: time,
        actual_start: time | None = None,
        actual_end: time | None = None,
        break_minutes: int = 60,
        is_holiday: bool = False,
        memo: str | None = None
    ) -> WorkRecord:
        """근무 기록 생성"""
        # 1. 직원 존재 및 소속 확인
        employee = await self.employee_repo.get_by_id_and_company(employee_id, company_id)
        if not employee:
            raise NotFoundError("직원을 찾을 수 없습니다.")

        # 2. 중복 날짜 확인
        existing = await self.work_record_repo.get_by_employee_and_date(employee_id, work_date)
        if existing:
            raise ConflictError(
                message="해당 날짜에 이미 근무 기록이 존재합니다.",
                details=[{"field": "work_date", "message": "이미 근무 기록이 존재합니다."}]
            )

        # 3. 시간 자동 계산
        time_result = self.calculate_work_times(
            actual_start=actual_start,
            actual_end=actual_end,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            break_minutes=break_minutes,
            is_holiday=is_holiday
        )

        # 4. DB 저장
        record = await self.work_record_repo.create(
            employee_id=employee_id,
            company_id=company_id,
            work_date=work_date,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            actual_start=actual_start,
            actual_end=actual_end,
            break_minutes=break_minutes,
            overtime_minutes=time_result.overtime_minutes,
            night_minutes=time_result.night_minutes,
            holiday_minutes=time_result.holiday_minutes,
            is_holiday=is_holiday,
            memo=memo
        )

        await self.db.commit()
        return record

    async def update_record(
        self,
        company_id: UUID,
        record_id: UUID,
        work_date: date | None = None,
        scheduled_start: time | None = None,
        scheduled_end: time | None = None,
        actual_start: time | None = None,
        actual_end: time | None = None,
        break_minutes: int | None = None,
        is_holiday: bool | None = None,
        memo: str | None = None
    ) -> WorkRecord:
        """근무 기록 수정"""
        # 1. 권한 확인
        record = await self.work_record_repo.get_by_id_and_company(record_id, company_id)
        if not record:
            raise NotFoundError("근무 기록을 찾을 수 없습니다.")

        # 2. 필드 업데이트
        if work_date is not None:
            record.work_date = work_date
        if scheduled_start is not None:
            record.scheduled_start = scheduled_start
        if scheduled_end is not None:
            record.scheduled_end = scheduled_end
        if actual_start is not None:
            record.actual_start = actual_start
        if actual_end is not None:
            record.actual_end = actual_end
        if break_minutes is not None:
            record.break_minutes = break_minutes
        if is_holiday is not None:
            record.is_holiday = is_holiday
        if memo is not None:
            record.memo = memo

        # 3. 시간 재계산
        time_result = self.calculate_work_times(
            actual_start=record.actual_start,
            actual_end=record.actual_end,
            scheduled_start=record.scheduled_start,
            scheduled_end=record.scheduled_end,
            break_minutes=record.break_minutes,
            is_holiday=record.is_holiday
        )

        record.overtime_minutes = time_result.overtime_minutes
        record.night_minutes = time_result.night_minutes
        record.holiday_minutes = time_result.holiday_minutes
        record.updated_at = datetime.utcnow()

        await self.db.commit()
        return record

    async def delete_record(self, company_id: UUID, record_id: UUID) -> None:
        """근무 기록 삭제"""
        record = await self.work_record_repo.get_by_id_and_company(record_id, company_id)
        if not record:
            raise NotFoundError("근무 기록을 찾을 수 없습니다.")

        await self.work_record_repo.delete(record)
        await self.db.commit()

    async def get_monthly_summary(
        self,
        company_id: UUID,
        year: int,
        month: int,
        employee_id: UUID | None = None
    ) -> dict:
        """월별 근무 기록 요약"""
        # 조건 설정
        conditions = [
            WorkRecord.company_id == company_id,
            extract('year', WorkRecord.work_date) == year,
            extract('month', WorkRecord.work_date) == month,
        ]

        if employee_id:
            conditions.append(WorkRecord.employee_id == employee_id)

        # 상세 데이터 조회 (employee 관계 미리 로드)
        detail_stmt = select(WorkRecord).options(selectinload(WorkRecord.employee)).where(and_(*conditions))
        detail_result = await self.db.execute(detail_stmt)
        records = detail_result.scalars().all()

        # 직원별로 집계
        employee_data = {}
        for record in records:
            emp_id = record.employee_id
            if emp_id not in employee_data:
                employee_data[emp_id] = {
                    "work_days": 0,
                    "total_work_minutes": 0,
                    "total_overtime_minutes": 0,
                    "total_night_minutes": 0,
                    "total_holiday_minutes": 0,
                    "total_break_minutes": 0,
                    "late_count": 0,
                    "early_leave_count": 0,
                    "employee": record.employee,
                }

            employee_data[emp_id]["work_days"] += 1
            employee_data[emp_id]["total_overtime_minutes"] += record.overtime_minutes
            employee_data[emp_id]["total_night_minutes"] += record.night_minutes
            employee_data[emp_id]["total_holiday_minutes"] += record.holiday_minutes
            employee_data[emp_id]["total_break_minutes"] += record.break_minutes

            # 총 근무 시간 계산
            if record.actual_start and record.actual_end:
                start_min = record.actual_start.hour * 60 + record.actual_start.minute
                end_min = record.actual_end.hour * 60 + record.actual_end.minute
                if end_min <= start_min:
                    end_min += 1440
                total_mins = max(0, end_min - start_min - record.break_minutes)
                employee_data[emp_id]["total_work_minutes"] += total_mins

            # 지각/조퇴 카운트
            if record.actual_start and record.actual_start > record.scheduled_start:
                employee_data[emp_id]["late_count"] += 1
            if record.actual_end and record.actual_end < record.scheduled_end:
                employee_data[emp_id]["early_leave_count"] += 1

        # 응답 구성
        employees_summary = []
        for emp_id, data in employee_data.items():
            emp = data["employee"]
            if emp:
                employees_summary.append({
                    "employee_id": str(emp_id),
                    "employee_name": emp.name,
                    "employment_type": emp.employment_type,
                    "total_work_days": data["work_days"],
                    "total_work_minutes": data["total_work_minutes"],
                    "total_overtime_minutes": data["total_overtime_minutes"],
                    "total_night_minutes": data["total_night_minutes"],
                    "total_holiday_minutes": data["total_holiday_minutes"],
                    "total_break_minutes": data["total_break_minutes"],
                    "late_count": data["late_count"],
                    "early_leave_count": data["early_leave_count"],
                    "absent_count": 0,  # 별도 로직 필요
                })

        # 전체 집계
        total_work_minutes = sum(e.get("total_work_minutes", 0) for e in employees_summary)
        total_employees = len(employee_data)

        company_total = {
            "total_employees": total_employees,
            "avg_work_minutes_per_day": int(total_work_minutes / len(records)) if records else 0,
            "total_overtime_minutes": sum(r.overtime_minutes for r in records),
            "total_night_minutes": sum(r.night_minutes for r in records),
            "total_holiday_minutes": sum(r.holiday_minutes for r in records),
        }

        return {
            "year": year,
            "month": month,
            "employees": employees_summary,
            "company_total": company_total,
        }

    async def get_employee_analysis(
        self,
        company_id: UUID,
        employee_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None
    ) -> dict:
        """직원별 근무 패턴 분석"""
        # 직원 확인
        employee = await self.employee_repo.get_by_id_and_company(employee_id, company_id)
        if not employee:
            raise NotFoundError("직원을 찾을 수 없습니다.")

        # 기본 날짜 범위 (3개월)
        if not to_date:
            to_date = date.today()
        if not from_date:
            from_date = to_date - timedelta(days=90)

        # 근무 기록 조회
        conditions = [
            WorkRecord.employee_id == employee_id,
            WorkRecord.work_date >= from_date,
            WorkRecord.work_date <= to_date,
            WorkRecord.actual_start.is_not(None),
            WorkRecord.actual_end.is_not(None),
        ]

        stmt = select(WorkRecord).where(and_(*conditions)).order_by(WorkRecord.work_date)
        result = await self.db.execute(stmt)
        records = result.scalars().all()

        if not records:
            return {
                "employee_id": str(employee_id),
                "employee_name": employee.name,
                "period": {
                    "from": from_date.isoformat(),
                    "to": to_date.isoformat(),
                },
                "pattern": {
                    "avg_start_time": "00:00",
                    "avg_end_time": "00:00",
                    "avg_work_minutes_per_day": 0,
                    "avg_overtime_minutes_per_month": 0,
                    "overtime_trend": [],
                    "weekday_distribution": {
                        "mon": 0, "tue": 0, "wed": 0, "thu": 0, "fri": 0, "sat": 0, "sun": 0
                    },
                    "weekly_hours_warning": False,
                },
                "alerts": [],
            }

        # 평균 출퇴근 시간 계산
        start_times = [r.actual_start for r in records if r.actual_start]
        end_times = [r.actual_end for r in records if r.actual_end]

        avg_start_min = sum(s.hour * 60 + s.minute for s in start_times) // len(start_times) if start_times else 0
        avg_end_min = sum(e.hour * 60 + e.minute for e in end_times) // len(end_times) if end_times else 0

        avg_start_time = f"{avg_start_min // 60:02d}:{avg_start_min % 60:02d}"
        avg_end_time = f"{avg_end_min // 60:02d}:{avg_end_min % 60:02d}"

        # 월별 집계
        overtime_trend = []
        monthly_totals = {}

        for record in records:
            month_key = (record.work_date.year, record.work_date.month)
            if month_key not in monthly_totals:
                monthly_totals[month_key] = 0
            monthly_totals[month_key] += record.overtime_minutes

        for (year, month), total_minutes in sorted(monthly_totals.items()):
            overtime_trend.append({
                "year": year,
                "month": month,
                "total_minutes": total_minutes,
            })

        # 요일별 분포
        weekday_dist = {
            "mon": 0, "tue": 0, "wed": 0, "thu": 0, "fri": 0, "sat": 0, "sun": 0
        }
        weekday_map = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

        for record in records:
            weekday_idx = record.work_date.weekday()
            if weekday_idx < 7:
                weekday_dist[weekday_map[weekday_idx]] += 1

        # 주 52시간 경고
        avg_overtime_per_month = sum(r.overtime_minutes for r in records) / max(len(set((r.work_date.year, r.work_date.month) for r in records)), 1)
        weekly_hours_warning = avg_overtime_per_month > 180  # 180분 = 3시간

        # 경고 메시지
        alerts = []
        if sum(r.overtime_minutes for r in records) / len(set((r.work_date.year, r.work_date.month) for r in records)) > 3600:  # 60시간
            alerts.append({
                "type": "overtime_high",
                "message": "최근 기간 평균 연장근무가 월 60시간을 초과합니다.",
            })

        return {
            "employee_id": str(employee_id),
            "employee_name": employee.name,
            "period": {
                "from": from_date.isoformat(),
                "to": to_date.isoformat(),
            },
            "pattern": {
                "avg_start_time": avg_start_time,
                "avg_end_time": avg_end_time,
                "avg_work_minutes_per_day": sum(r.overtime_minutes for r in records) // len(records) if records else 0,
                "avg_overtime_minutes_per_month": int(avg_overtime_per_month),
                "overtime_trend": overtime_trend,
                "weekday_distribution": weekday_dist,
                "weekly_hours_warning": weekly_hours_warning,
            },
            "alerts": alerts,
        }
