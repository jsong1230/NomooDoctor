# F-13 근태 관리 -- 기술 설계서

## 1. 참조
- 인수조건: docs/project/features.md #F-13
- 시스템 설계: docs/system/system-design.md
- ERD: docs/system/erd.md
- API 컨벤션: docs/system/api-conventions.md
- 의존성: F-03 (직원 관리) -- 완료, F-05 (급여 자동 계산기) -- 완료

## 2. 아키텍처 결정

### 결정 1: work_records 테이블 스키마 변경 여부
- **선택지**: A) 기존 001 마이그레이션의 work_records 테이블 그대로 사용 / B) 컬럼 추가 마이그레이션
- **결정**: A) 기존 스키마 그대로 사용 + updated_at 컬럼 1개 추가
- **근거**: 기존 work_records에 이미 scheduled_start/end, actual_start/end, break_minutes, overtime/night/holiday_minutes, is_holiday, memo가 정의되어 있어 F-13 인수조건을 충족함. 단, 수정 이력 추적을 위해 updated_at만 추가.

### 결정 2: 연장/야간/휴일 시간 자동 계산 방식
- **선택지**: A) 프론트엔드에서 계산 후 전송 / B) 백엔드 Service 레이어에서 actual_start/end 기반 자동 계산
- **결정**: B) 백엔드 Service 레이어에서 자동 계산
- **근거**: 근로기준법 기준 시간 판정(야간 22:00~06:00, 소정근로시간 초과분 연장 등)은 비즈니스 로직이므로 서버 단에서 일관성 보장. 프론트엔드는 미리보기만 제공.

### 결정 3: 엑셀 업로드 파싱 라이브러리
- **선택지**: A) openpyxl만 사용 / B) openpyxl + csv 모듈 병행
- **결정**: B) openpyxl(xlsx) + csv 모듈(csv) 병행
- **근거**: 인수조건에 xlsx, csv 모두 지원 명시. openpyxl은 csv를 지원하지 않으므로 파일 확장자별 분기 처리.

### 결정 4: 월별 요약/패턴 분석 계산 방식
- **선택지**: A) 실시간 쿼리 계산 / B) Materialized View / C) 캐싱
- **결정**: A) 실시간 쿼리 계산
- **근거**: 50인 미만 사업장 대상으로 월별 work_records 최대 ~1,500건(50명 x 30일). 인덱스 기반 쿼리로 충분한 성능.

### 결정 5: work_records의 UNIQUE 제약
- **선택지**: A) (employee_id, work_date) UNIQUE / B) 동일 날짜 복수 레코드 허용
- **결정**: A) (employee_id, work_date) UNIQUE
- **근거**: 1일 1근무 기록 원칙. 분할 근무(오전/오후)는 하나의 레코드로 통합 관리. 중복 입력 방지.

---

## 3. API 설계

### 3.1 POST /api/v1/attendance/records
- **목적**: 근무 기록 수동 입력 (단건)
- **인증**: 필요 (JWT, company_id)
- **Request Body**:
```json
{
  "employee_id": "uuid",
  "work_date": "2026-03-01",
  "scheduled_start": "09:00",
  "scheduled_end": "18:00",
  "actual_start": "08:55",
  "actual_end": "20:30",
  "break_minutes": 60,
  "is_holiday": false,
  "memo": "프로젝트 마감"
}
```
- **Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "employee_id": "uuid",
    "employee_name": "홍길동",
    "work_date": "2026-03-01",
    "scheduled_start": "09:00",
    "scheduled_end": "18:00",
    "actual_start": "08:55",
    "actual_end": "20:30",
    "break_minutes": 60,
    "total_work_minutes": 635,
    "overtime_minutes": 150,
    "night_minutes": 0,
    "holiday_minutes": 0,
    "is_holiday": false,
    "memo": "프로젝트 마감",
    "created_at": "2026-03-01T09:00:00Z"
  }
}
```
- **에러 케이스**:

| HTTP | 코드 | 상황 |
|------|------|------|
| 400 | E-1001 | 입력값 검증 실패 (시간 형식 오류 등) |
| 404 | E-4004 | 직원을 찾을 수 없음 |
| 409 | E-4010 | 해당 날짜에 이미 근무 기록 존재 |
| 422 | E-4011 | actual_end가 actual_start 이전 |

### 3.2 POST /api/v1/attendance/records/batch
- **목적**: 근무 기록 일괄 입력 (여러 건)
- **인증**: 필요
- **Request Body**:
```json
{
  "records": [
    {
      "employee_id": "uuid",
      "work_date": "2026-03-01",
      "scheduled_start": "09:00",
      "scheduled_end": "18:00",
      "actual_start": "09:00",
      "actual_end": "18:00",
      "break_minutes": 60,
      "is_holiday": false
    }
  ]
}
```
- **Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "total": 10,
    "created": 8,
    "skipped": 2,
    "errors": [
      { "index": 3, "employee_id": "uuid", "work_date": "2026-03-03", "reason": "이미 근무 기록이 존재합니다." },
      { "index": 7, "employee_id": "uuid", "work_date": "2026-03-07", "reason": "직원을 찾을 수 없습니다." }
    ]
  }
}
```

### 3.3 GET /api/v1/attendance/records
- **목적**: 근무 기록 목록 조회 (사업장 전체 또는 직원별)
- **인증**: 필요
- **Query Parameters**:

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| employee_id | uuid | N | - | 직원 필터 |
| from_date | date | N | 해당월 1일 | 시작일 |
| to_date | date | N | 해당월 말일 | 종료일 |
| year | int | N | - | 연도 필터 (from/to 대신 사용) |
| month | int | N | - | 월 필터 (year와 함께 사용) |
| limit | int | N | 50 | 페이지 크기 (최대 200) |
| cursor | string | N | - | 페이지네이션 커서 |

- **Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "employee_id": "uuid",
      "employee_name": "홍길동",
      "work_date": "2026-03-01",
      "scheduled_start": "09:00",
      "scheduled_end": "18:00",
      "actual_start": "08:55",
      "actual_end": "20:30",
      "break_minutes": 60,
      "total_work_minutes": 635,
      "overtime_minutes": 150,
      "night_minutes": 0,
      "holiday_minutes": 0,
      "is_holiday": false,
      "memo": "프로젝트 마감"
    }
  ],
  "pagination": {
    "cursor": "...",
    "hasNext": true,
    "limit": 50
  }
}
```

### 3.4 GET /api/v1/attendance/records/{id}
- **목적**: 근무 기록 단건 조회
- **인증**: 필요
- **Response**: 3.1의 data와 동일 구조

### 3.5 PUT /api/v1/attendance/records/{id}
- **목적**: 근무 기록 수정
- **인증**: 필요
- **Request Body**: 3.1과 동일 (employee_id 제외, 부분 업데이트 지원)
- **Response** (200): 3.1의 data와 동일 구조

### 3.6 DELETE /api/v1/attendance/records/{id}
- **목적**: 근무 기록 삭제
- **인증**: 필요
- **Response** (204 No Content)

### 3.7 POST /api/v1/attendance/import
- **목적**: 엑셀/CSV 파일로 근무 기록 일괄 업로드
- **인증**: 필요
- **Request**: multipart/form-data
  - `file`: xlsx 또는 csv 파일 (최대 10MB)
- **Response** (200):
```json
{
  "success": true,
  "data": {
    "total_rows": 150,
    "created": 140,
    "updated": 5,
    "skipped": 5,
    "errors": [
      { "row": 12, "column": "actual_start", "value": "abc", "reason": "시간 형식이 올바르지 않습니다. (HH:MM)" },
      { "row": 25, "column": "employee_id", "value": "홍길동", "reason": "직원을 찾을 수 없습니다." },
      { "row": 48, "row_data": "...", "reason": "필수 필드(work_date)가 누락되었습니다." }
    ]
  }
}
```
- **에러 케이스**:

| HTTP | 코드 | 상황 |
|------|------|------|
| 400 | E-1001 | 파일 형식 오류 (xlsx/csv 외) |
| 400 | E-4012 | 파일 파싱 실패 (손상된 파일) |
| 413 | E-1004 | 파일 크기 초과 (10MB) |

### 3.8 GET /api/v1/attendance/import/template
- **목적**: 엑셀 업로드용 템플릿 다운로드
- **인증**: 필요
- **Response**: xlsx 파일 직접 반환 (Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)

### 3.9 GET /api/v1/attendance/summary
- **목적**: 월별 근무 기록 요약
- **인증**: 필요
- **Query Parameters**:

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| year | int | Y | - | 연도 |
| month | int | Y | - | 월 |
| employee_id | uuid | N | - | 직원 필터 (미지정 시 전체) |

- **Response** (200):
```json
{
  "success": true,
  "data": {
    "year": 2026,
    "month": 3,
    "employees": [
      {
        "employee_id": "uuid",
        "employee_name": "홍길동",
        "employment_type": "regular",
        "total_work_days": 22,
        "total_work_minutes": 10560,
        "total_overtime_minutes": 600,
        "total_night_minutes": 120,
        "total_holiday_minutes": 480,
        "total_break_minutes": 1320,
        "late_count": 2,
        "early_leave_count": 0,
        "absent_count": 1
      }
    ],
    "company_total": {
      "total_employees": 15,
      "avg_work_minutes_per_day": 480,
      "total_overtime_minutes": 3200,
      "total_night_minutes": 800,
      "total_holiday_minutes": 1920
    }
  }
}
```

### 3.10 GET /api/v1/attendance/analysis
- **목적**: 직원별 근무 패턴 분석
- **인증**: 필요
- **Query Parameters**:

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| employee_id | uuid | Y | - | 직원 ID |
| from_date | date | N | 3개월 전 | 분석 시작일 |
| to_date | date | N | 오늘 | 분석 종료일 |

- **Response** (200):
```json
{
  "success": true,
  "data": {
    "employee_id": "uuid",
    "employee_name": "홍길동",
    "period": { "from": "2026-01-01", "to": "2026-03-31" },
    "pattern": {
      "avg_start_time": "08:52",
      "avg_end_time": "18:15",
      "avg_work_minutes_per_day": 498,
      "avg_overtime_minutes_per_month": 320,
      "overtime_trend": [
        { "year": 2026, "month": 1, "total_minutes": 280 },
        { "year": 2026, "month": 2, "total_minutes": 350 },
        { "year": 2026, "month": 3, "total_minutes": 330 }
      ],
      "weekday_distribution": {
        "mon": 95, "tue": 96, "wed": 97, "thu": 96, "fri": 94, "sat": 10, "sun": 2
      },
      "weekly_hours_warning": false
    },
    "alerts": [
      { "type": "overtime_high", "message": "최근 3개월 평균 연장근무가 월 20시간을 초과합니다." }
    ]
  }
}
```

---

## 4. DB 설계

### 4.1 기존 테이블: work_records (변경)

work_records 테이블은 001 마이그레이션에 이미 존재. 아래 변경 사항 적용.

#### 마이그레이션 004: F-13 근태 관리 스키마 변경

```python
"""004_f13_attendance_schema.py"""

def upgrade():
    # 1. updated_at 컬럼 추가
    op.add_column('work_records',
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    # 2. UNIQUE 제약 추가 (employee_id + work_date 중복 방지)
    op.create_index(
        'idx_work_records_unique_date',
        'work_records',
        ['employee_id', 'work_date'],
        unique=True
    )

    # 3. is_holiday 기본값 확인 -- 이미 존재

def downgrade():
    op.drop_index('idx_work_records_unique_date', 'work_records')
    op.drop_column('work_records', 'updated_at')
```

#### work_records 최종 스키마

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 기록 고유 식별자 |
| employee_id | UUID | FK, NOT NULL | 직원 ID |
| company_id | UUID | FK, NOT NULL | 사업장 ID |
| work_date | DATE | NOT NULL | 근무일 |
| scheduled_start | TIME | NOT NULL | 예정 출근시간 |
| scheduled_end | TIME | NOT NULL | 예정 퇴근시간 |
| actual_start | TIME | | 실제 출근시간 |
| actual_end | TIME | | 실제 퇴근시간 |
| break_minutes | INTEGER | DEFAULT 60 | 휴게시간 (분) |
| overtime_minutes | INTEGER | DEFAULT 0 | 연장근무시간 (분) -- 자동 계산 |
| night_minutes | INTEGER | DEFAULT 0 | 야간근무시간 (분) -- 자동 계산 |
| holiday_minutes | INTEGER | DEFAULT 0 | 휴일근무시간 (분) -- 자동 계산 |
| is_holiday | BOOLEAN | DEFAULT FALSE | 휴일 여부 |
| memo | TEXT | | 비고 |
| created_at | TIMESTAMPTZ | NOT NULL | 생성일시 |
| updated_at | TIMESTAMPTZ | | 수정일시 (신규) |

#### 인덱스

| 인덱스 | 컬럼 | 유형 | 용도 |
|--------|------|------|------|
| idx_work_records_employee_date | employee_id, work_date | B-Tree | 직원별 날짜 조회 (기존) |
| idx_work_records_company_date | company_id, work_date | B-Tree | 사업장별 날짜 조회 (기존) |
| idx_work_records_unique_date | employee_id, work_date | B-Tree UNIQUE | 중복 방지 (신규) |

---

## 5. Service 레이어 설계

### 5.1 AttendanceService

```
backend/app/services/attendance_service.py
```

#### 핵심 메서드

##### calculate_work_times(actual_start, actual_end, scheduled_start, scheduled_end, break_minutes, is_holiday) -> WorkTimeResult

연장/야간/휴일근무 시간 자동 계산 로직:

```
WorkTimeResult:
  total_work_minutes: int     # 총 근무시간 (분)
  overtime_minutes: int       # 연장근무시간 (분)
  night_minutes: int          # 야간근무시간 (분)
  holiday_minutes: int        # 휴일근무시간 (분)
```

**계산 규칙:**

1. **총 근무시간**: actual_start ~ actual_end - break_minutes
   - 야간을 걸치는 경우(actual_end < actual_start): 다음날로 간주 (+24시간)

2. **연장근무 (overtime_minutes)**:
   - 소정근로시간 = scheduled_start ~ scheduled_end - break_minutes
   - 연장근무 = max(0, 총 근무시간 - 소정근로시간)
   - 휴일이 아닌 경우에만 연장근무로 분류

3. **야간근무 (night_minutes)**:
   - 22:00 ~ 06:00 사이 실제 근무한 시간
   - actual_start/end 구간과 [22:00, 30:00(=06:00)] 구간의 교집합
   - 휴게시간은 야간 시간에서 비례 차감하지 않음 (보수적 계산)

4. **휴일근무 (holiday_minutes)**:
   - is_holiday=true인 경우: 총 근무시간 전체가 휴일근무
   - 연장근무와 중복 가능 (휴일 연장 = 휴일수당 + 연장수당)

**야간근무 계산 상세 알고리즘:**

```
def calculate_night_minutes(actual_start: time, actual_end: time) -> int:
    # 시간을 분 단위로 변환 (0:00 = 0, 24:00 = 1440)
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
        overlap2 = max(0, min(end_min - 1440, 360) - max(start_min - 1440 if start_min > 1440 else 0, 0))
    else:
        overlap2 = 0

    return max(0, overlap1) + max(0, overlap2)
```

##### create_record(db, company_id, data) -> WorkRecord
- 직원 존재 및 소속 확인
- 중복 날짜 확인 (employee_id + work_date)
- calculate_work_times()로 자동 계산
- DB 저장

##### update_record(db, company_id, record_id, data) -> WorkRecord
- 권한 확인
- 자동 시간 재계산
- updated_at 갱신

##### delete_record(db, company_id, record_id) -> None
- 권한 확인 후 삭제

##### get_monthly_summary(db, company_id, year, month, employee_id=None) -> MonthlySummary
- work_records 집계 쿼리
- 지각/조퇴/결근 판정:
  - 지각: actual_start > scheduled_start
  - 조퇴: actual_end < scheduled_end
  - 결근: 해당 날짜 work_record 없음 (근무일인데 기록 없는 경우)

##### get_employee_analysis(db, company_id, employee_id, from_date, to_date) -> AnalysisResult
- 평균 출퇴근 시간: AVG(actual_start), AVG(actual_end)
- 월별 연장근무 추세
- 요일별 근무일 분포
- 주 52시간 경고 체크

### 5.2 ExcelImportService

```
backend/app/services/excel_import_service.py
```

#### 엑셀 템플릿 컬럼 정의

| 컬럼 순서 | 헤더명 | 타입 | 필수 | 비고 |
|-----------|--------|------|------|------|
| A | employee_name | 문자열 | Y | 직원명 (매칭용) |
| B | work_date | 날짜 | Y | YYYY-MM-DD |
| C | scheduled_start | 시간 | Y | HH:MM |
| D | scheduled_end | 시간 | Y | HH:MM |
| E | actual_start | 시간 | N | HH:MM |
| F | actual_end | 시간 | N | HH:MM |
| G | break_minutes | 정수 | N | 기본 60 |
| H | is_holiday | 예/아니오 | N | 기본: 아니오 |
| I | memo | 문자열 | N | |

#### 핵심 메서드

##### parse_file(file: UploadFile) -> list[ParsedRow]
- 파일 확장자로 분기 (xlsx -> openpyxl, csv -> csv 모듈)
- 각 행 파싱, 타입 변환, 오류 수집
- ParsedRow: { row_number, data, errors }

##### validate_rows(db, company_id, rows) -> ValidationResult
- employee_name -> employee_id 매칭 (사업장 내 이름 검색)
  - 동명이인 시 에러 (행 번호 + "동일 이름의 직원이 여러 명입니다. employee_id를 사용해주세요.")
- 중복 날짜 검증 (파일 내 중복 + DB 기존 데이터)
- 시간 논리 검증 (actual_end > actual_start 등)

##### import_records(db, company_id, validated_rows) -> ImportResult
- 유효한 행만 일괄 INSERT
- 오류 행은 건너뛰고 결과에 포함
- 트랜잭션: 유효 행 전체 성공 or 전체 실패 (partial commit 없음)

##### generate_template(company_id) -> BytesIO
- openpyxl로 빈 템플릿 생성
- 첫 행에 헤더, 두 번째 행에 예시 데이터
- 직원 목록 시트 추가 (employee_name, employee_id 매핑 참조용)

---

## 6. Repository 설계

### 6.1 WorkRecordRepository

```
backend/app/repositories/work_record_repo.py
```

```python
class WorkRecordRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, record_id: UUID) -> WorkRecord | None
    async def get_by_id_and_company(self, record_id: UUID, company_id: UUID) -> WorkRecord | None
    async def get_by_employee_and_date(self, employee_id: UUID, work_date: date) -> WorkRecord | None

    async def list_by_company(
        self, company_id: UUID,
        employee_id: UUID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 50,
        cursor: str | None = None
    ) -> tuple[list[WorkRecord], str | None]  # (records, next_cursor)

    async def create(self, **kwargs) -> WorkRecord
    async def create_batch(self, records: list[dict]) -> list[WorkRecord]
    async def update(self, record: WorkRecord, **kwargs) -> WorkRecord
    async def delete(self, record: WorkRecord) -> None

    # 집계 쿼리
    async def get_monthly_aggregation(
        self, company_id: UUID, year: int, month: int,
        employee_id: UUID | None = None
    ) -> list[dict]
    # SQL: GROUP BY employee_id, SUM(overtime_minutes), SUM(night_minutes), ...

    async def get_employee_stats(
        self, employee_id: UUID,
        from_date: date, to_date: date
    ) -> dict
    # AVG(actual_start), AVG(actual_end), 요일별 분포 등

    async def count_late_early_absent(
        self, employee_id: UUID, year: int, month: int
    ) -> dict  # { "late": int, "early_leave": int, "absent": int }
```

---

## 7. Schema(Pydantic) 설계

```
backend/app/schemas/attendance.py
```

```python
# === Request Schemas ===

class WorkRecordCreate(BaseModel):
    employee_id: UUID
    work_date: date
    scheduled_start: time  # HH:MM
    scheduled_end: time
    actual_start: time | None = None
    actual_end: time | None = None
    break_minutes: int = Field(default=60, ge=0, le=480)
    is_holiday: bool = False
    memo: str | None = Field(default=None, max_length=500)

class WorkRecordUpdate(BaseModel):
    work_date: date | None = None
    scheduled_start: time | None = None
    scheduled_end: time | None = None
    actual_start: time | None = None
    actual_end: time | None = None
    break_minutes: int | None = Field(default=None, ge=0, le=480)
    is_holiday: bool | None = None
    memo: str | None = Field(default=None, max_length=500)

class WorkRecordBatchCreate(BaseModel):
    records: list[WorkRecordCreate] = Field(..., min_length=1, max_length=500)

class AttendanceSummaryRequest(BaseModel):
    year: int = Field(..., ge=2020, le=2099)
    month: int = Field(..., ge=1, le=12)
    employee_id: UUID | None = None

class AttendanceAnalysisRequest(BaseModel):
    employee_id: UUID
    from_date: date | None = None
    to_date: date | None = None

# === Response Schemas ===

class WorkRecordResponse(BaseModel):
    id: UUID
    employee_id: UUID
    employee_name: str
    work_date: date
    scheduled_start: time
    scheduled_end: time
    actual_start: time | None
    actual_end: time | None
    break_minutes: int
    total_work_minutes: int  # 계산 필드
    overtime_minutes: int
    night_minutes: int
    holiday_minutes: int
    is_holiday: bool
    memo: str | None
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True

class ImportResultResponse(BaseModel):
    total_rows: int
    created: int
    updated: int
    skipped: int
    errors: list[ImportErrorDetail]

class ImportErrorDetail(BaseModel):
    row: int
    column: str | None = None
    value: str | None = None
    reason: str

class EmployeeMonthlySummary(BaseModel):
    employee_id: UUID
    employee_name: str
    employment_type: str
    total_work_days: int
    total_work_minutes: int
    total_overtime_minutes: int
    total_night_minutes: int
    total_holiday_minutes: int
    total_break_minutes: int
    late_count: int
    early_leave_count: int
    absent_count: int

class CompanyTotalSummary(BaseModel):
    total_employees: int
    avg_work_minutes_per_day: int
    total_overtime_minutes: int
    total_night_minutes: int
    total_holiday_minutes: int

class MonthlySummaryResponse(BaseModel):
    year: int
    month: int
    employees: list[EmployeeMonthlySummary]
    company_total: CompanyTotalSummary

class OvertimeTrend(BaseModel):
    year: int
    month: int
    total_minutes: int

class PatternData(BaseModel):
    avg_start_time: str  # "HH:MM"
    avg_end_time: str
    avg_work_minutes_per_day: int
    avg_overtime_minutes_per_month: int
    overtime_trend: list[OvertimeTrend]
    weekday_distribution: dict[str, int]  # {"mon": 95, ...}
    weekly_hours_warning: bool  # 주 52시간 초과 경고

class AnalysisAlert(BaseModel):
    type: str  # "overtime_high", "night_frequent", "weekly_52h_exceeded"
    message: str

class EmployeeAnalysisResponse(BaseModel):
    employee_id: UUID
    employee_name: str
    period: dict[str, str]  # {"from": "...", "to": "..."}
    pattern: PatternData
    alerts: list[AnalysisAlert]
```

---

## 8. 시퀀스 흐름

### 8.1 근무 기록 수동 입력

```
사용자 → Frontend(입력 폼)
  → POST /api/v1/attendance/records
  → API Layer: JWT 검증, company_id 추출
  → AttendanceService.create_record()
    → EmployeeRepository.get_by_id_and_company() (직원 확인)
    → WorkRecordRepository.get_by_employee_and_date() (중복 확인)
    → AttendanceService.calculate_work_times() (시간 자동 계산)
    → WorkRecordRepository.create() (DB 저장)
  → 201 Created 응답
```

### 8.2 엑셀 업로드

```
사용자 → Frontend(파일 선택)
  → POST /api/v1/attendance/import (multipart/form-data)
  → API Layer: JWT 검증, 파일 크기/형식 확인
  → ExcelImportService.parse_file() (파싱 + 타입 변환)
  → ExcelImportService.validate_rows() (직원 매칭, 중복 확인, 로직 검증)
  → ExcelImportService.import_records() (유효 행 일괄 INSERT)
  → 200 OK (결과 + 에러 목록)
```

### 8.3 급여 계산 연동 (기존 F-05와 연동)

```
사용자 → Frontend(급여 계산 페이지)
  → GET /api/v1/attendance/summary?year=2026&month=3&employee_id=xxx
  → 월별 연장/야간/휴일 합계 확인
  → POST /api/v1/payroll/calculate
    (overtime_minutes, night_minutes, holiday_minutes 값을 근태 요약에서 가져옴)
```

---

## 9. 영향 범위

### 수정 필요 파일
| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/api/v1/router.py` | attendance 라우터 등록 |
| `backend/app/db/models/salary.py` | WorkRecord 모델에 updated_at 추가 |
| `backend/app/db/models/__init__.py` | 변경 없음 (WorkRecord 이미 존재) |
| `backend/requirements.txt` | openpyxl 추가 |

### 신규 생성 파일

**Backend:**
| 파일 | 설명 |
|------|------|
| `backend/alembic/versions/004_f13_attendance_schema.py` | 마이그레이션 |
| `backend/app/api/v1/attendance.py` | API 라우터 |
| `backend/app/schemas/attendance.py` | Pydantic 스키마 |
| `backend/app/services/attendance_service.py` | 근태 비즈니스 로직 |
| `backend/app/services/excel_import_service.py` | 엑셀 파싱/임포트 |
| `backend/app/repositories/work_record_repo.py` | 데이터 접근 |

**Frontend:**
| 파일 | 설명 |
|------|------|
| `frontend/app/(main)/attendance/page.tsx` | 근태 관리 메인 페이지 (Server Component) |
| `frontend/components/attendance/attendance-table.tsx` | 근무 기록 테이블 |
| `frontend/components/attendance/record-form.tsx` | 근무 기록 입력/수정 폼 |
| `frontend/components/attendance/record-form-dialog.tsx` | 폼 다이얼로그 래퍼 |
| `frontend/components/attendance/excel-upload.tsx` | 엑셀 업로드 컴포넌트 |
| `frontend/components/attendance/monthly-summary.tsx` | 월별 요약 카드 |
| `frontend/components/attendance/analysis-chart.tsx` | 패턴 분석 차트 |
| `frontend/components/attendance/date-range-picker.tsx` | 날짜 범위 선택 |
| `frontend/lib/api/attendance.ts` | API 클라이언트 |
| `frontend/lib/stores/attendance-store.ts` | Zustand 스토어 |
| `frontend/types/attendance.ts` | TypeScript 타입 |

---

## 10. 성능 설계

### 10.1 인덱스 계획
- 기존 인덱스 활용: `idx_work_records_employee_date`, `idx_work_records_company_date`
- 신규: `idx_work_records_unique_date` (UNIQUE, 중복 방지 겸 조회 최적화)

### 10.2 쿼리 최적화
- 월별 요약: employee_id GROUP BY 집계 쿼리 (인덱스 스캔)
- 패턴 분석: date_part() 함수로 시간 추출, 3개월 범위 제한

### 10.3 엑셀 업로드 최적화
- 최대 10MB / 약 5,000행 제한
- 파싱 단계에서 스트리밍 (openpyxl read_only=True)
- 일괄 INSERT 시 executemany 사용
- 대규모 파일은 메모리 사용 제한 (행 단위 처리)

### 10.4 캐싱 전략
- 월별 요약은 Redis 캐싱 불필요 (실시간 데이터 요구, 쿼리 성능 충분)
- 엑셀 템플릿은 서버 메모리 캐싱 (직원 목록은 요청마다 갱신)

---

## 11. Frontend 설계

### 11.1 페이지 구조

```
/attendance (근태 관리 메인)
  ├── 월 선택 (year/month picker)
  ├── 탭: [근무 기록] [월별 요약] [패턴 분석]
  ├── [근무 기록 탭]
  │   ├── 직원 필터 드롭다운
  │   ├── 근무 기록 테이블 (DataTable)
  │   │   └── 행 클릭 → 수정 다이얼로그
  │   ├── [+ 기록 추가] 버튼 → 입력 다이얼로그
  │   └── [엑셀 업로드] 버튼 → 업로드 다이얼로그
  ├── [월별 요약 탭]
  │   ├── 사업장 전체 통계 카드
  │   └── 직원별 요약 테이블
  └── [패턴 분석 탭]
      ├── 직원 선택
      ├── 기간 선택
      ├── 연장근무 추세 차트 (recharts Bar)
      ├── 요일별 분포 차트
      └── 경고 알림 배너
```

### 11.2 컴포넌트 상세

**attendance-table.tsx**
- shadcn/ui DataTable 기반
- 컬럼: 날짜, 직원명, 출근, 퇴근, 근무시간, 연장, 야간, 휴일, 상태
- 상태 배지: 정상(green), 지각(yellow), 조퇴(orange), 결근(red)
- 행 클릭 시 수정 다이얼로그 오픈

**record-form.tsx**
- React Hook Form + Zod 유효성 검증
- 시간 입력: shadcn/ui Input (HH:MM 형식)
- 연장/야간/휴일 시간 실시간 미리보기 (프론트엔드 계산, 서버 계산과 동일 로직)
- 직원 선택: Combobox (검색 가능)

**excel-upload.tsx**
- 드래그앤드롭 영역 + 파일 선택 버튼
- 업로드 진행률 표시
- 결과 화면: 성공/실패 건수 + 에러 상세 테이블
- 템플릿 다운로드 링크

---

## 변경 이력

| 날짜 | 변경 내용 | 이유 |
|------|-----------|------|
| 2026-03-12 | 초기 작성 | F-13 근태 관리 기능 설계 |
