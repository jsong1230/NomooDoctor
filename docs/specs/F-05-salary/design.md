# F-05 급여 자동 계산기 — 기술 설계서

## 1. 참조
- 인수조건: docs/project/features.md #F-05
- 시스템 설계: docs/system/system-design.md
- ERD: docs/system/erd.md
- API 컨벤션: docs/system/api-conventions.md

---

## 2. 아키텍처 결정

### 결정 1: 계산 로직 위치
- **선택지**: A) Service 레이어에 직접 구현 / B) 별도 Calculator 클래스로 분리
- **결정**: B) 별도 Calculator 클래스로 분리
- **근거**:
  - 계산 로직이 복잡하고 다양한 수당/공제 항목이 존재
  - 단위 테스트 용이성 확보
  - 향후 근로기준법 개정 시 수정 범위 최소화
  - 재사용성 (F-07 급여명세서, F-09 퇴직금 계산에서 활용)

### 결정 2: 요율 관리 방식
- **선택지**: A) 코드 내 상수 관리 / B) DB 테이블(labor_law_rates) 관리
- **결정**: B) DB 테이블(labor_law_rates) 관리
- **근거**:
  - 연도별 최저임금, 4대보험료율 변경 용이
  - 관리자 페이지를 통한 요율 업데이트 가능
  - 과거 연도 급여 재계산 시 해당 연도 요율 적용 가능
  - Redis 캐싱으로 조회 성능 확보

### 결정 3: 소수점 처리 방식
- **선택지**: A) 반올림 / B) 올림 / C) 버림(절사)
- **결정**: C) 버림(절사) - 10원 미만 절사
- **근거**:
  - 근로기준법 및 통상적 관행 준수
  - 모든 계산은 Decimal 타입 사용으로 부동소수점 오차 방지

### 결정 4: 통상시급 계산 시점
- **선택지**: A) 급여 계산 시 실시간 계산 / B) 급여 설정 저장 시 미리 계산
- **결정**: A) 급여 계산 시 실시간 계산
- **근거**:
  - 근태 기록(연장/야간/휴일근무)에 따라 주 소정근로시간이 변동 가능
  - 정확한 계산을 위해 해당 월의 실제 근무 데이터 기반 계산 필요

---

## 3. API 설계

### POST /api/v1/payroll/calculate
- **목적**: 급여 계산 (실시간 미리보기)
- **인증**: 필요 (JWT)
- **Rate Limit**: 100회/시간 (User ID)

**Request Body:**
```json
{
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "pay_year": 2026,
  "pay_month": 3,
  "work_records_summary": {
    "scheduled_hours": 209,
    "actual_hours": 220,
    "overtime_hours": 11,
    "night_hours": 8,
    "holiday_hours": 5,
    "is_full_attendance": true
  },
  "allowances": {
    "meal": 200000,
    "transport": 100000,
    "other": 0
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "employee_name": "홍길동",
    "pay_year": 2026,
    "pay_month": 3,
    "wage_type": "monthly",
    "hourly_rate": 10204,
    "payments": {
      "base_pay": 2500000,
      "holiday_pay": 326531,
      "overtime_pay": 168366,
      "night_pay": 40816,
      "holiday_work_pay": 76531,
      "meal_allowance": 200000,
      "transport_allowance": 100000,
      "non_taxable_allowance": 200000,
      "gross_pay": 3412244
    },
    "deductions": {
      "national_pension": 112500,
      "health_insurance": 88520,
      "long_term_care": 11465,
      "employment_insurance": 22500,
      "income_tax": 95700,
      "local_income_tax": 9570,
      "total_deduction": 340255
    },
    "net_pay": 3071989,
    "warnings": [],
    "calculation_detail": {
      "minimum_wage_check": {
        "applied_rate": 10030,
        "calculated_hourly": 10204,
        "is_compliant": true
      },
      "standard_monthly_hours": 209,
      "overtime_calculation": {
        "hours": 11,
        "rate": 1.5,
        "amount": 168366
      },
      "insurance_base": {
        "national_pension_base": 2500000,
        "health_insurance_base": 2495700
      }
    }
  }
}
```

**에러 케이스:**

| 코드 | HTTP | 상황 | 메시지 |
|------|------|------|--------|
| E-4004 | 404 | 직원 없음 | 직원을 찾을 수 없습니다. |
| E-5001 | 422 | 최저임금 미달 | 최저임금 기준 미달입니다. 2026년 최저임금은 시급 10,030원입니다. |
| E-5004 | 400 | 계산 오류 | 급여 계산 중 오류가 발생했습니다. |

### GET /api/v1/payroll/rates
- **목적**: 현재 적용 중인 노동법 요율 조회
- **인증**: 필요 (JWT)
- **Rate Limit**: 100회/분 (User ID)

**Query Parameters:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| year | int | 아니오 | 조회 연도 (기본: 현재 연도) |

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "year": 2026,
    "rates": {
      "minimum_wage": 10030,
      "national_pension_employee": 0.045,
      "national_pension_employer": 0.045,
      "health_insurance_employee": 0.03545,
      "health_insurance_employer": 0.03545,
      "long_term_care_rate": 0.1295,
      "employment_insurance_employee": 0.009,
      "employment_insurance_employer": 0.009
    },
    "effective_date": "2026-01-01",
    "source_url": "https://www.moel.go.kr/..."
  }
}
```

### GET /api/v1/payslips
- **목적**: 급여명세서 목록 조회
- **인증**: 필요 (JWT)
- **Rate Limit**: 100회/분 (User ID)

**Query Parameters:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| employee_id | uuid | 아니오 | 직원 ID 필터 |
| pay_year | int | 아니오 | 연도 필터 |
| pay_month | int | 아니오 | 월 필터 |
| limit | int | 아니오 | 페이지 크기 (기본: 20, 최대: 100) |
| cursor | string | 아니오 | 페이지네이션 커서 |

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "employee_id": "...",
      "employee_name": "홍길동",
      "pay_year": 2026,
      "pay_month": 2,
      "gross_pay": 3400000,
      "total_deduction": 338000,
      "net_pay": 3062000,
      "send_status": "sent",
      "created_at": "2026-02-25T10:00:00Z"
    }
  ],
  "pagination": {
    "cursor": null,
    "has_next": false,
    "limit": 20
  }
}
```

### POST /api/v1/payslips
- **목적**: 급여명세서 생성 (계산 결과 저장)
- **인증**: 필요 (JWT)
- **Rate Limit**: 50회/시간 (User ID)

**Request Body:**
```json
{
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "pay_year": 2026,
  "pay_month": 3,
  "calculation_result": {
    // POST /payroll/calculate 응답의 data 필드
  }
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "pay_year": 2026,
    "pay_month": 3,
    "net_pay": 3071989,
    "send_status": "pending"
  },
  "message": "급여명세서가 생성되었습니다."
}
```

### GET /api/v1/payslips/{id}
- **목적**: 급여명세서 상세 조회
- **인증**: 필요 (JWT)
- **Rate Limit**: 100회/분 (User ID)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "employee": {
      "id": "550e8400-...",
      "name": "홍길동",
      "employment_type": "regular"
    },
    "company": {
      "id": "...",
      "business_name": "(주)노무닥터"
    },
    "pay_year": 2026,
    "pay_month": 3,
    "payments": {
      "base_pay": 2500000,
      "holiday_pay": 326531,
      "overtime_pay": 168366,
      "night_pay": 40816,
      "holiday_work_pay": 76531,
      "meal_allowance": 200000,
      "transport_allowance": 100000,
      "other_allowance": 0,
      "gross_pay": 3412244
    },
    "deductions": {
      "national_pension": 112500,
      "health_insurance": 88520,
      "long_term_care": 11465,
      "employment_insurance": 22500,
      "income_tax": 9570,
      "local_income_tax": 9570,
      "total_deduction": 340255
    },
    "net_pay": 3071989,
    "calculation_detail": { ... },
    "send_status": "pending",
    "pdf_url": null,
    "created_at": "2026-03-25T10:00:00Z"
  }
}
```

---

## 4. DB 설계

### 기존 테이블 활용

#### salary_settings (급여 설정) - 기존
| 컬럼 | 타입 | 설명 |
|------|------|------|
| employee_id | UUID | 직원 ID (FK) |
| wage_type | VARCHAR(20) | 임금 유형 (monthly/hourly/daily) |
| base_wage | NUMERIC(12,0) | 기본급 |
| meal_allowance | NUMERIC(10,0) | 식대 |
| transport_allowance | NUMERIC(10,0) | 교통비 |
| income_tax_family_count | INTEGER | 부양가족 수 |

#### work_records (근태 기록) - 기존
| 컬럼 | 타입 | 설명 |
|------|------|------|
| employee_id | UUID | 직원 ID (FK) |
| work_date | DATE | 근무일 |
| overtime_minutes | INTEGER | 연장근무시간 (분) |
| night_minutes | INTEGER | 야간근무시간 (분) |
| holiday_minutes | INTEGER | 휴일근무시간 (분) |
| is_holiday | BOOLEAN | 휴일 여부 |

#### payslips (급여명세서) - 기존
| 컬럼 | 타입 | 설명 |
|------|------|------|
| employee_id | UUID | 직원 ID (FK) |
| pay_year | INTEGER | 지급 연도 |
| pay_month | INTEGER | 지급 월 (1-12) |
| base_pay | NUMERIC(12,0) | 기본급 |
| holiday_pay | NUMERIC(12,0) | 주휴수당 |
| overtime_pay | NUMERIC(12,0) | 연장수당 |
| night_pay | NUMERIC(12,0) | 야간수당 |
| holiday_work_pay | NUMERIC(12,0) | 휴일수당 |
| meal_allowance | NUMERIC(10,0) | 식대 |
| transport_allowance | NUMERIC(10,0) | 교통비 |
| gross_pay | NUMERIC(12,0) | 지급 합계 |
| national_pension | NUMERIC(10,0) | 국민연금 |
| health_insurance | NUMERIC(10,0) | 건강보험 |
| long_term_care | NUMERIC(10,0) | 장기요양보험 |
| employment_insurance | NUMERIC(10,0) | 고용보험 |
| income_tax | NUMERIC(10,0) | 소득세 |
| local_income_tax | NUMERIC(10,0) | 지방소득세 |
| total_deduction | NUMERIC(12,0) | 공제 합계 |
| net_pay | NUMERIC(12,0) | 실수령액 |
| calculation_detail | JSONB | 계산 상세 내역 |

### 신규 테이블: labor_law_rates (노동법 요율 마스터)

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 요율 고유 식별자 |
| rate_type | VARCHAR(50) | NOT NULL | 요율 유형 |
| value | NUMERIC(10,4) | NOT NULL | 금액 또는 요율 |
| effective_year | INTEGER | NOT NULL | 적용 연도 |
| effective_month | INTEGER | NOT NULL, DEFAULT 1 | 적용 월 |
| source_url | TEXT | | 출처 URL |
| created_at | TIMESTAMPTZ | NOT NULL | 생성일시 |

**rate_type enum 값:**
| 값 | 설명 | 단위 |
|----|------|------|
| minimum_wage | 최저임금 | 원/시간 |
| national_pension_employee | 국민연금(근로자) | 비율 |
| national_pension_employer | 국민연금(사업주) | 비율 |
| health_insurance_employee | 건강보험(근로자) | 비율 |
| health_insurance_employer | 건강보험(사업주) | 비율 |
| long_term_care_rate | 장기요양보험율 | 비율 |
| employment_insurance_employee | 고용보험(근로자) | 비율 |
| employment_insurance_employer | 고용보험(사업주) | 비율 |

**인덱스:**
```sql
CREATE UNIQUE INDEX idx_rates_unique ON labor_law_rates(rate_type, effective_year, effective_month);
CREATE INDEX idx_rates_year ON labor_law_rates(effective_year);
```

**초기 데이터 (2026년 기준):**
```sql
INSERT INTO labor_law_rates (rate_type, value, effective_year, effective_month, source_url) VALUES
('minimum_wage', 10030, 2026, 1, 'https://www.moel.go.kr/...'),
('national_pension_employee', 0.045, 2026, 1, 'https://www.nps.or.kr/...'),
('national_pension_employer', 0.045, 2026, 1, 'https://www.nps.or.kr/...'),
('health_insurance_employee', 0.03545, 2026, 1, 'https://www.nhis.or.kr/...'),
('health_insurance_employer', 0.03545, 2026, 1, 'https://www.nhis.or.kr/...'),
('long_term_care_rate', 0.1295, 2026, 1, 'https://www.nhis.or.kr/...'),
('employment_insurance_employee', 0.009, 2026, 1, 'https://www.moel.go.kr/...'),
('employment_insurance_employer', 0.009, 2026, 1, 'https://www.moel.go.kr/...');
```

---

## 5. 시퀀스 흐름

### 급여 계산 시퀀스

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌───────┐
│ Frontend│     │  API    │     │ Service │     │Calculator│    │ Redis │
└────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘     └───┬───┘
     │               │               │               │              │
     │ POST /payroll/calculate       │               │              │
     │──────────────>│               │               │              │
     │               │               │               │              │
     │               │ Rate Limit    │               │              │
     │               │─────────────────────────────────────────────>│
     │               │               │               │              │
     │               │ validate & call service       │              │
     │               │──────────────>│               │              │
     │               │               │               │              │
     │               │               │ get rates (cached)           │
     │               │               │─────────────────────────────>│
     │               │               │               │              │
     │               │               │ (cache miss: DB query)       │
     │               │               │──────────────>│              │
     │               │               │               │              │
     │               │               │ get employee salary_settings │
     │               │               │──────────────>│              │
     │               │               │               │              │
     │               │               │ get work_records (month)     │
     │               │               │──────────────>│              │
     │               │               │               │              │
     │               │               │ calculate()   │              │
     │               │               │──────────────>│              │
     │               │               │               │              │
     │               │               │  result       │              │
     │               │               │<──────────────│              │
     │               │               │               │              │
     │  response     │               │               │              │
     │<──────────────│               │               │              │
     │               │               │               │              │
```

### 계산 로직 상세

```python
# 1. 통상시급 계산
def calculate_hourly_rate(base_wage, wage_type, weekly_hours, meal_allowance, transport_allowance):
    """
    통상시급 = (기본급 + 고정수당) / (주 소정근로시간 × 52 / 12 + 주휴수당 시간)
    """
    if wage_type == 'hourly':
        return base_wage

    # 고정수당 (비과세 한도 적용)
    fixed_allowance = min(meal_allowance, 200000) + min(transport_allowance, 200000)

    # 월 소정근로시간 = 주 소정근로시간 × 52 / 12
    monthly_hours = weekly_hours * 52 / 12

    # 주휴수당 시간 (주 15시간 이상 근무 시)
    weekly_holiday_hours = weekly_hours / 5 if weekly_hours >= 15 else 0
    monthly_holiday_hours = weekly_holiday_hours * 52 / 12

    hourly_rate = (base_wage + fixed_allowance) / (monthly_hours + monthly_holiday_hours)
    return floor_to_10_won(hourly_rate)

# 2. 수당 계산
def calculate_overtime_pay(hourly_rate, overtime_hours):
    """연장수당 = 연장시간 × 시급 × 1.5"""
    return floor_to_10_won(hourly_rate * overtime_hours * Decimal('1.5'))

def calculate_night_pay(hourly_rate, night_hours):
    """야간수당 = 야간시간 × 시급 × 0.5 (가산분만)"""
    return floor_to_10_won(hourly_rate * night_hours * Decimal('0.5'))

def calculate_holiday_pay(hourly_rate, holiday_hours):
    """
    휴일수당:
    - 8시간 이내: 휴일시간 × 시급 × 1.5
    - 8시간 초과: 8시간 × 시급 × 1.5 + 초과시간 × 시급 × 2.0
    """
    if holiday_hours <= 8:
        return floor_to_10_won(hourly_rate * holiday_hours * Decimal('1.5'))
    else:
        base = hourly_rate * 8 * Decimal('1.5')
        extra = hourly_rate * (holiday_hours - 8) * Decimal('2.0')
        return floor_to_10_won(base + extra)

def calculate_weekly_holiday_pay(hourly_rate, daily_hours, is_full_attendance):
    """
    주휴수당 = 1일 소정근로시간 × 시급 (주 15시간 이상, 개근 시)
    """
    if not is_full_attendance:
        return Decimal('0')
    return floor_to_10_won(hourly_rate * daily_hours)

# 3. 4대보험 계산
def calculate_national_pension(monthly_wage, rate):
    """국민연금 = 기준소득월액 × 4.5%"""
    # 기준소득월액 상한/하한 적용 필요
    return floor_to_10_won(monthly_wage * rate)

def calculate_health_insurance(monthly_wage, rate):
    """건강보험 = 보수월액 × 3.545%"""
    return floor_to_10_won(monthly_wage * rate)

def calculate_long_term_care(health_insurance, rate):
    """장기요양보험 = 건강보험료 × 12.95%"""
    return floor_to_10_won(health_insurance * rate)

def calculate_employment_insurance(monthly_wage, rate):
    """고용보험 = 월보수 × 0.9%"""
    return floor_to_10_won(monthly_wage * rate)

# 4. 소득세 계산 (간이세액표)
def calculate_income_tax(monthly_wage, family_count):
    """
    소득세 = 간이세액표 기준 (가족수 반영)
    근로소득 간이세액표 lookup
    """
    # 간이세액표는 DB 또는 코드로 관리
    tax_table = get_simplified_tax_table()
    tax = lookup_tax(tax_table, monthly_wage, family_count)
    return floor_to_10_won(tax)

def calculate_local_income_tax(income_tax):
    """지방소득세 = 소득세 × 10%"""
    return floor_to_10_won(income_tax * Decimal('0.1'))

# 5. 10원 미만 절사
def floor_to_10_won(amount: Decimal) -> Decimal:
    """10원 미만 절사"""
    return (amount // 10) * 10
```

---

## 6. 영향 범위

### 수정 필요 파일
| 파일 | 변경 내용 |
|------|-----------|
| app/db/models/__init__.py | LaborLawRate 모델 추가 |
| app/api/v1/router.py | payroll 라우터 추가 |
| app/core/exceptions.py | 급여 관련 예외 추가 (MinimumWageViolationError 등) |

### 신규 생성 파일
| 파일 | 설명 |
|------|------|
| app/db/models/labor_law.py | LaborLawRate 모델 |
| app/schemas/payroll.py | 급여 계산 요청/응답 스키마 |
| app/schemas/payslip.py | 급여명세서 스키마 |
| app/api/v1/payroll.py | 급여 계산 API |
| app/api/v1/payslips.py | 급여명세서 API |
| app/services/payroll_service.py | 급여 계산 서비스 |
| app/services/payslip_service.py | 급여명세서 서비스 |
| app/repositories/labor_law_repo.py | 노동법 요율 리포지토리 |
| app/repositories/payslip_repo.py | 급여명세서 리포지토리 |
| app/utils/wage_calculator.py | 수당 계산 유틸리티 |
| app/utils/tax_calculator.py | 세금 계산 유틸리티 |
| alembic/versions/003_add_labor_law_rates.py | 요율 테이블 마이그레이션 |

---

## 7. 성능 설계

### 인덱스 계획
- `labor_law_rates`: (rate_type, effective_year, effective_month) UNIQUE
- `payslips`: (employee_id, pay_year, pay_month) UNIQUE (기존)

### 캐싱 전략
| 대상 | Key 패턴 | TTL | 설명 |
|------|----------|-----|------|
| 노동법 요율 | `cache:labor_rates:{year}` | 24시간 | 연도별 요율 캐싱 |
| 급여 계산 결과 | `cache:payroll:{employee_id}:{year}:{month}` | 1시간 | 미리보기 결과 캐싱 |

### Redis 캐싱 구현
```python
async def get_labor_rates(year: int, redis: Redis) -> dict:
    cache_key = f"cache:labor_rates:{year}"
    cached = await redis.get(cache_key)

    if cached:
        return json.loads(cached)

    rates = await labor_law_repo.get_rates_by_year(year)
    await redis.setex(cache_key, 86400, json.dumps(rates))  # 24시간
    return rates
```

---

## 8. 비즈니스 규칙

### 최저임금 검증
```python
def validate_minimum_wage(hourly_rate: Decimal, year: int) -> bool:
    """최저임금 이상 여부 검증"""
    minimum_wage = get_minimum_wage(year)
    return hourly_rate >= minimum_wage

def calculate_effective_hourly_rate(
    base_wage: Decimal,
    wage_type: str,
    weekly_hours: Decimal,
    allowances: dict
) -> Decimal:
    """
    실질 시급 계산 (최저임금 검증용)
    """
    # 통상시급 계산 로직
    ...
```

### 비과세 한도 적용
```python
def apply_non_taxable_limit(meal: Decimal, transport: Decimal) -> tuple[Decimal, Decimal]:
    """
    식대, 교통비 비과세 한도 적용
    - 각 항목 월 20만원까지 비과세
    """
    non_taxable_meal = min(meal, Decimal('200000'))
    non_taxable_transport = min(transport, Decimal('200000'))
    return non_taxable_meal, non_taxable_transport
```

### 주휴수당 조건
```python
def is_eligible_for_weekly_holiday_pay(
    weekly_hours: Decimal,
    is_full_attendance: bool
) -> bool:
    """
    주휴수당 지급 조건:
    - 주 15시간 이상 근무
    - 해당 주 개근
    """
    return weekly_hours >= 15 and is_full_attendance
```

---

## 9. 보안 고려사항

### 데이터 접근 제어
- 사업장별 급여 데이터 격리 (company_id 기반)
- JWT payload의 company_id와 요청 데이터 검증

### 민감 정보 처리
- 급여 정보는 민감 정보로 분류
- 로깅 시 금액 정보 마스킹
- 감사 로그 필수 기록

---

## 변경 이력

| 날짜 | 변경 내용 | 이유 |
|------|-----------|------|
| 2026-03-02 | 초기 작성 | F-05 기능 설계 |
