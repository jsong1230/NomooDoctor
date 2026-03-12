# F-05 급여 자동 계산기 API 스펙

## 개요
노동법 기준 급여 자동 계산 API입니다. 연장수당, 야간수당, 휴일수당 및 4대 보험료, 소득세 등을 자동 계산합니다.

## 기본 URL
```
/api/v1/payroll
```

## 인증
- 모든 엔드포인트는 Bearer Token 인증 필요
- 사업장 선택 필수 (JWT의 `company_id` 필요)

---

## POST /calculate - 급여 계산

급여 계산을 수행합니다.

### Request
**Method**: `POST`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Body (JSON)**:
```json
{
  "employee_id": "uuid",
  "pay_year": 2024,
  "pay_month": 1,
  "base_wage": 2500000,
  "overtime_minutes": 600,
  "night_minutes": 0,
  "holiday_minutes": 0,
  "meal_allowance": 100000,
  "transport_allowance": 50000,
  "income_tax_family_count": 1
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| employee_id | string | O | 직원 ID (UUID) |
| pay_year | integer | O | 급여 연도 (2020~2099) |
| pay_month | integer | O | 급여 월 (1~12) |
| base_wage | number | O | 기본급 (초과 0) |
| overtime_minutes | integer | X | 연장근무 시간(분), 기본값 0 |
| night_minutes | integer | X | 야간근무 시간(분), 기본값 0 |
| holiday_minutes | integer | X | 휴일근무 시간(분), 기본값 0 |
| meal_allowance | number | X | 식대, 기본값 0 |
| transport_allowance | number | X | 교통비, 기본값 0 |
| income_tax_family_count | integer | X | 소득세 가족 수(본인 포함 1~10), 기본값 1 |

### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "employee_id": "uuid",
    "pay_year": 2024,
    "pay_month": 1,
    "base_wage": 2500000,
    "overtime_pay": 17990,
    "night_pay": 0,
    "holiday_pay": 0,
    "meal_allowance": 100000,
    "transport_allowance": 50000,
    "total_gross": 2677990,
    "national_pension": 111600,
    "health_insurance": 87960,
    "long_term_care": 11390,
    "employment_insurance": 24100,
    "income_tax": 63830,
    "local_income_tax": 6380,
    "total_deduction": 305260,
    "net_pay": 2372730
  }
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| base_wage | integer | 기본급 |
| overtime_pay | integer | 연장수당 |
| night_pay | integer | 야간수당 |
| holiday_pay | integer | 휴일수당 |
| meal_allowance | integer | 식대 |
| transport_allowance | integer | 교통비 |
| total_gross | integer | 총 지급액 |
| national_pension | integer | 국민연금료 |
| health_insurance | integer | 건강보험료 |
| long_term_care | integer | 장기요양보험료 |
| employment_insurance | integer | 고용보험료 |
| income_tax | integer | 소득세 |
| local_income_tax | integer | 지방소득세 |
| total_deduction | integer | 총 공제액 |
| net_pay | integer | 실수령액 |

### Error Responses

**401 Unauthorized**:
```json
{
  "success": false,
  "error": {
    "code": "E-2001",
    "message": "인증이 필요합니다."
  }
}
```

**403 Forbidden**:
```json
{
  "success": false,
  "error": {
    "code": "E-2005",
    "message": "사업장이 선택되지 않았습니다."
  }
}
```

**404 Not Found**:
```json
{
  "success": false,
  "error": {
    "code": "E-3002",
    "message": "직원을 찾을 수 없습니다."
  }
}
```

**422 Unprocessable Entity**:
```json
{
  "success": false,
  "error": {
    "code": "E-1003",
    "message": "필수 필드가 누락되었습니다.",
    "details": [
      {
        "field": "body -> base_wage",
        "message": "Field required"
      }
    ]
  }
}
```

---

## GET /rates - 요율 조회

급여 계산에 사용되는 요율 정보를 조회합니다.

### Request
**Method**: `GET`

**Headers**:
```
Authorization: Bearer <access_token>
```

### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "national_pension_rate": "0.045",
    "health_insurance_rate": "0.03545",
    "long_term_care_rate": "0.1295",
    "employment_insurance_rate": "0.009",
    "local_income_tax_rate": "0.1",
    "overtime_rate": "1.5",
    "night_rate": "0.5",
    "holiday_rate_normal": "1.5",
    "holiday_rate_over": "2.0"
  }
}
```

| 필드 | 값 | 설명 |
|------|-----|------|
| national_pension_rate | "0.045" | 국민연금 4.5% |
| health_insurance_rate | "0.03545" | 건강보험 3.545% |
| long_term_care_rate | "0.1295" | 장기요양 12.95% |
| employment_insurance_rate | "0.009" | 고용보험 0.9% |
| local_income_tax_rate | "0.1" | 지방소득세 10% |
| overtime_rate | "1.5" | 연장수당 1.5배 |
| night_rate | "0.5" | 야간수당 0.5배 (추가분) |
| holiday_rate_normal | "1.5" | 휴일수당 8시간 이내 1.5배 |
| holiday_rate_over | "2.0" | 휴일수당 8시간 초과 2.0배 |

### Error Responses

**401 Unauthorized**:
```json
{
  "success": false,
  "error": {
    "code": "E-2001",
    "message": "인증이 필요합니다."
  }
}
```

---

## 계산 로직

### 통상시급 계산
```
통상시급 = 기본급 / 209시간
```

### 연장수당 계산
```
연장수당 = 통상시급 × 연장시간 × 1.5
```

### 야간수당 계산
```
야간수당 = 통상시급 × 야간시간 × 0.5
```

### 휴일수당 계산
```
휴일수당 = (통상시급 × min(휴일시간, 8) × 1.5) + (통상시급 × max(휴일시간 - 8, 0) × 2.0)
```

### 사회보험료 계산
```
국민연금 = 기준소득월액 × 0.045
건강보험 = 기준소득월액 × 0.03545
장기요양 = 건강보험 × 0.1295
고용보험 = 월보수 × 0.009
```

### 소득세 계산 (간이세액표)
```
인적공제 = 1,500,000원 × 가족수
과세표준 = 과세소득 - 인적공제 - 사회보험료

과세표준별 세율:
- 0 ~ 1,200만원: 6%
- 1,200만원 ~ 4,600만원: 15% (누진공제 108만원)
- 4,600만원 ~ 8,800만원: 24% (누진공제 522만원)
- 8,800만원 ~ 1.5억원: 35% (누진공제 1,490만원)
- 1.5억원 ~ 3억원: 38% (누진공제 1,940만원)
- 3억원 ~ 5억원: 40% (누진공제 2,540만원)
- 5억원 ~ 10억원: 42% (누진공제 3,540만원)
- 10억원 초과: 45% (누진공제 6,540만원)

지방소득세 = 소득세 × 0.1
```

### 절사 규칙
- 모든 계산 결과는 10원 미만 절사

### 비과세 항목
- 식대: 100,000원까지 비과세
