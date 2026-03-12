# F-05 급여 자동 계산기 DB 스키마

## 개요
급여 자동 계산기 기능은 기존 `salary_settings`, `work_records`, `payslips` 테이블을 사용합니다. 별도의 테이블 추가는 없습니다.

---

## 테이블 정의

### salary_settings (급여 설정 테이블)

직원별 급여 설정 정보를 저장합니다.

| 컬럼명 | 타입 | 설명 | 제약조건 |
|--------|------|------|----------|
| id | UUID | 기본키 | PRIMARY KEY |
| employee_id | UUID | 직원 ID | FK → employees.id ON DELETE CASCADE, NOT NULL |
| effective_from | date | 적용 시작일 | NOT NULL |
| effective_to | date | 적용 종료일 | NULLABLE |
| wage_type | varchar(20) | 급여 유형 | 'monthly', 'hourly', 'daily', NOT NULL |
| base_wage | numeric(12,0) | 기본급 | NOT NULL |
| meal_allowance | numeric(10,0) | 식대 | DEFAULT 0 |
| transport_allowance | numeric(10,0) | 교통비 | DEFAULT 0 |
| income_tax_family_count | integer | 소득세 가족수 | DEFAULT 1 |
| created_at | timestamp | 생성일자 | NOT NULL |

**인덱스**:
- `idx_salary_settings_employee`: (employee_id, effective_from)

**제약조건**:
- `ck_salary_wage_type`: wage_type IN ('monthly', 'hourly', 'daily')

**관계**:
- employee: → Employee (back_populates: salary_settings)

---

### work_records (근무 기록 테이블)

일일 근무 기록을 저장합니다.

| 컬럼명 | 타입 | 설명 | 제약조건 |
|--------|------|------|----------|
| id | UUID | 기본키 | PRIMARY KEY |
| employee_id | UUID | 직원 ID | FK → employees.id ON DELETE CASCADE, NOT NULL |
| company_id | UUID | 사업장 ID | FK → companies.id, NOT NULL |
| work_date | date | 근무일 | NOT NULL |
| scheduled_start | time | 계획 시작시간 | NOT NULL |
| scheduled_end | time | 계획 종료시간 | NOT NULL |
| actual_start | time | 실제 시작시간 | NULLABLE |
| actual_end | time | 실제 종료시간 | NULLABLE |
| break_minutes | integer | 휴게시간(분) | DEFAULT 60 |
| overtime_minutes | integer | 연장근무(분) | DEFAULT 0 |
| night_minutes | integer | 야간근무(분) | DEFAULT 0 |
| holiday_minutes | integer | 휴일근무(분) | DEFAULT 0 |
| is_holiday | boolean | 휴일 여부 | DEFAULT false |
| memo | text | 메모 | NULLABLE |
| created_at | timestamp | 생성일자 | NOT NULL |

**인덱스**:
- `idx_work_records_employee_date`: (employee_id, work_date)
- `idx_work_records_company_date`: (company_id, work_date)

**관계**:
- employee: → Employee (back_populates: work_records)

---

### payslips (급여명세서 테이블)

월별 급여명세서를 저장합니다.

| 컬럼명 | 타입 | 설명 | 제약조건 |
|--------|------|------|----------|
| id | UUID | 기본키 | PRIMARY KEY |
| employee_id | UUID | 직원 ID | FK → employees.id ON DELETE CASCADE, NOT NULL |
| company_id | UUID | 사업장 ID | FK → companies.id, NOT NULL |
| pay_year | integer | 급여 연도 | NOT NULL |
| pay_month | integer | 급여 월 | NOT NULL, 1~12 |
| base_pay | numeric(12,0) | 기본급 | NOT NULL |
| holiday_pay | numeric(12,0) | 휴일수당 | DEFAULT 0 |
| overtime_pay | numeric(12,0) | 연장수당 | DEFAULT 0 |
| night_pay | numeric(12,0) | 야간수당 | DEFAULT 0 |
| holiday_work_pay | numeric(12,0) | 휴일근무수당 | DEFAULT 0 |
| meal_allowance | numeric(10,0) | 식대 | DEFAULT 0 |
| transport_allowance | numeric(10,0) | 교통비 | DEFAULT 0 |
| other_allowance | numeric(10,0) | 기타수당 | DEFAULT 0 |
| gross_pay | numeric(12,0) | 총지급액 | NOT NULL |
| national_pension | numeric(10,0) | 국민연금 | DEFAULT 0 |
| health_insurance | numeric(10,0) | 건강보험 | DEFAULT 0 |
| long_term_care | numeric(10,0) | 장기요양보험 | DEFAULT 0 |
| employment_insurance | numeric(10,0) | 고용보험 | DEFAULT 0 |
| income_tax | numeric(10,0) | 소득세 | DEFAULT 0 |
| local_income_tax | numeric(10,0) | 지방소득세 | DEFAULT 0 |
| total_deduction | numeric(12,0) | 총공제액 | NOT NULL |
| net_pay | numeric(12,0) | 실수령액 | NOT NULL |
| sent_at | timestamp | 발송일자 | NULLABLE |
| sent_via | varchar(20) | 발송경로 | NULLABLE |
| send_status | varchar(20) | 발송상태 | DEFAULT 'pending' |
| pdf_url | text | PDF URL | NULLABLE |
| calculation_detail | jsonb | 계산상세 | NULLABLE |
| created_at | timestamp | 생성일자 | NOT NULL |

**인덱스**:
- `idx_payslips_unique`: (employee_id, pay_year, pay_month) UNIQUE
- `idx_payslips_company_period`: (company_id, pay_year, pay_month)

**제약조건**:
- `ck_payslip_month`: pay_month BETWEEN 1 AND 12
- `ck_send_status`: send_status IN ('pending', 'sent', 'failed')

**관계**:
- employee: → Employee (back_populates: payslips)

---

## 계산 상세 (calculation_detail JSONB)

급여 계산 시 `calculation_detail` 필드에 계산 과정을 저장할 수 있습니다.

```json
{
  "hourly_wage": 11961.72,
  "overtime_hours": 10,
  "overtime_rate": 1.5,
  "night_hours": 0,
  "night_rate": 0.5,
  "holiday_hours": 0,
  "holiday_rate_normal": 1.5,
  "holiday_rate_over": 2.0,
  "taxable_income": 2577990,
  "personal_deduction": 1500000,
  "tax_base": 1092430,
  "income_tax_bracket": "6%"
}
```

---

## 데이터 타입

### Numeric
- `numeric(12,0)`: 급여 관련 금액 (최대 12자리, 소수점 없음)
- `numeric(10,0)`: 수당 및 공제 관련 금액

### Decimal 연산
Python `decimal.Decimal` 사용하여 정밀 계산 수행:
```python
from decimal import Decimal

# 통상시급 계산
hourly_wage = Decimal(base_wage) / Decimal("209")

# 10원 미만 절사
truncated = (value / Decimal("10")).quantize(Decimal("0"), rounding=ROUND_DOWN) * Decimal("10")
```

---

## 관련 ERD

```
Employee (1) ----< (N) SalarySetting
       |
       |----< (N) WorkRecord
       |
       |----< (N) Payslip

Company (1) ----< (N) WorkRecord
       |
       |----< (N) Payslip
```
