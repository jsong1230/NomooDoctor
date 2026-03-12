# F-07 급여명세서 생성 및 발송

## 개요
계산된 급여를 법정 명세서 형태로 생성하고 직원에게 이메일/카카오 알림톡으로 발송합니다.

## API 설계

### 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/v1/payslips/` | 급여명세서 생성 |
| GET | `/api/v1/payslips/` | 급여명세서 목록 조회 |
| GET | `/api/v1/payslips/{payslip_id}` | 급여명세서 상세 조회 |
| GET | `/api/v1/payslips/{payslip_id}/pdf` | PDF 다운로드 |
| POST | `/api/v1/payslips/{payslip_id}/send` | 발송 (이메일/알림톡) |
| GET | `/api/v1/employees/{employee_id}/payslips` | 직원별 급여 히스토리 |

### Request/Response 스키마

#### 급여명세서 생성 요청
```python
class PayslipCreateRequest(BaseModel):
    employee_id: UUID
    year: int  # 급여 연도
    month: int  # 급여 월 (1-12)
    payment_date: date  # 실제 지급일
    payroll_data: PayrollData  # F-05에서 계산된 급여 데이터
```

#### 급여명세서 응답
```python
class PayslipResponse(BaseModel):
    id: UUID
    employee_id: UUID
    employee_name: str
    company_name: str
    year: int
    month: int
    payment_date: date
    # 지급 항목
    base_salary: Decimal
    weekly_allowance: Decimal
    overtime_pay: Decimal
    night_pay: Decimal
    holiday_pay: Decimal
    meal_allowance: Decimal
    transport_allowance: Decimal
    total_payment: Decimal
    # 공제 항목
    national_pension: Decimal
    health_insurance: Decimal
    long_term_care: Decimal
    employment_insurance: Decimal
    income_tax: Decimal
    local_income_tax: Decimal
    total_deduction: Decimal
    # 실수령액
    net_salary: Decimal
    # 발송 상태
    send_status: str  # pending/sent/failed
    sent_at: datetime | None
    sent_via: str | None  # email/kakao
    created_at: datetime
```

#### 발송 요청
```python
class SendPayslipRequest(BaseModel):
    method: str  # "email" | "kakao" | "both"
    email: str | None = None  # 이메일 발송 시 (없으면 직원 이메일 사용)
```

## 법정 기재사항 (근로기준법 제48조)

급여명세서에 반드시 포함되어야 할 항목:
1. 근로자의 성명
2. 근로계약상의 임금 산정 기준
3. 근로시간 (소정근로, 연장, 야간, 휴일)
4. 임금의 각 구분별 금액
5. 임금 총액
6. 공제 항목 및 금액
7. 실수령액
8. 지급일
9. 사업장명

## DB 설계

### payslips 테이블 확장
```sql
-- 기존 payslips 테이블에 발송 관련 컬럼 추가
ALTER TABLE payslips ADD COLUMN IF NOT EXISTS send_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE payslips ADD COLUMN IF NOT EXISTS sent_at TIMESTAMP;
ALTER TABLE pays NOT EXISTS sent_via VARCHAR(20);
ALTER TABLE payslips ADD COLUMN IF NOT EXISTS email_sent_to VARCHAR(255);
ALTER TABLE payslips ADD COLUMN IF NOT EXISTS kakao_sent_to VARCHAR(20);
```

## 발송 플로우

### 1. 이메일 발송
```
1. SMTP 설정 확인 (환경변수)
2. Jinja2 템플릿으로 HTML 이메일 생성
3. PDF 첨부파일 생성 (WeasyPrint)
4. 발송 실행
5. 결과 DB 기록
```

### 2. 카카오 알림톡 발송
```
1. 카카오 API 설정 확인
2. 템플릿 메시지 구성
3. 알림톡 발송 API 호출
4. 실패 시 3회 재시도
5. 실패 시 이메일 Fallback
6. 결과 DB 기록
```

### 3. Fallback 정책
- 카카오 알림톡 3회 실패 → 자동 이메일 발송
- 발송 실패 시 관리자에게 알림

## 기술 스택

- PDF 생성: WeasyPrint (기존 F-04와 동일)
- 이메일: SMTP (smtplib + email)
- 카카오 알림톡: 카카오 비즈니스 API
- 템플릿: Jinja2

## 의존성

- F-05 급여 자동 계산기 (완료)
- F-03 직원 관리 (완료)
- F-02 사업장 관리 (완료)
