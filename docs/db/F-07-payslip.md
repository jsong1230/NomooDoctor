# F-07 급여명세서 생성 및 발송 — DB 스키마 확정본

## payslips 테이블

급여명세서 데이터를 저장합니다.

```sql
CREATE TABLE payslips (
    -- 식별자
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id     UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    company_id      UUID NOT NULL REFERENCES companies(id),

    -- 급여 기간
    pay_year        INTEGER NOT NULL,
    pay_month       INTEGER NOT NULL,

    -- 지급 항목
    base_pay            NUMERIC(12, 0) NOT NULL,
    holiday_pay         NUMERIC(12, 0) DEFAULT 0,  -- 주휴수당
    overtime_pay        NUMERIC(12, 0) DEFAULT 0,
    night_pay           NUMERIC(12, 0) DEFAULT 0,
    holiday_work_pay    NUMERIC(12, 0) DEFAULT 0,  -- 휴일근로수당
    meal_allowance      NUMERIC(10, 0) DEFAULT 0,
    transport_allowance NUMERIC(10, 0) DEFAULT 0,
    other_allowance     NUMERIC(10, 0) DEFAULT 0,
    gross_pay           NUMERIC(12, 0) NOT NULL,   -- 지급총액 (자동 계산)

    -- 공제 항목
    national_pension    NUMERIC(10, 0) DEFAULT 0,
    health_insurance    NUMERIC(10, 0) DEFAULT 0,
    long_term_care      NUMERIC(10, 0) DEFAULT 0,
    employment_insurance NUMERIC(10, 0) DEFAULT 0,
    income_tax          NUMERIC(10, 0) DEFAULT 0,
    local_income_tax    NUMERIC(10, 0) DEFAULT 0,
    total_deduction     NUMERIC(12, 0) NOT NULL,   -- 공제총액 (자동 계산)
    net_pay             NUMERIC(12, 0) NOT NULL,   -- 실수령액 (자동 계산)

    -- 발송 상태
    sent_at     TIMESTAMP WITH TIME ZONE,
    sent_via    VARCHAR(20),                       -- 'email' | 'kakao'
    send_status VARCHAR(20) DEFAULT 'pending',     -- 'pending' | 'sent' | 'failed'
    pdf_url     TEXT,

    -- 메타데이터
    calculation_detail  JSONB,
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- 제약 조건
    CONSTRAINT ck_payslip_month CHECK (pay_month BETWEEN 1 AND 12),
    CONSTRAINT ck_send_status CHECK (send_status IN ('pending', 'sent', 'failed'))
);
```

## 인덱스

```sql
-- 직원별 급여 기간 유일성 보장 (같은 직원, 같은 월에 중복 명세서 방지)
CREATE UNIQUE INDEX idx_payslips_unique
    ON payslips (employee_id, pay_year, pay_month);

-- 회사별 급여 기간 조회 최적화
CREATE INDEX idx_payslips_company_period
    ON payslips (company_id, pay_year, pay_month);
```

## 컬럼 설명

| 컬럼 | 설명 |
|------|------|
| holiday_pay | 주휴수당 (API에서는 weekly_allowance로 노출) |
| holiday_work_pay | 휴일근로수당 (API에서는 holiday_pay로 노출) |
| gross_pay | 지급 항목 합산 (자동 계산, API: total_payment) |
| total_deduction | 공제 항목 합산 (자동 계산) |
| net_pay | 실수령액 = gross_pay - total_deduction (자동 계산, API: net_salary) |
| send_status | 발송 상태: pending(초기)/sent(성공)/failed(실패) |
| sent_via | 실제 발송된 채널: email/kakao |

## 발송 흐름

```
생성 시: send_status = 'pending'
발송 성공: send_status = 'sent', sent_via = 'email'|'kakao', sent_at = NOW()
발송 실패: send_status = 'failed'
```

## 자동 계산 로직 (Repository)

```python
gross_pay = (
    base_pay + holiday_pay + overtime_pay + night_pay +
    holiday_work_pay + meal_allowance + transport_allowance
)
total_deduction = (
    national_pension + health_insurance + long_term_care +
    employment_insurance + income_tax + local_income_tax
)
net_pay = gross_pay - total_deduction
```
