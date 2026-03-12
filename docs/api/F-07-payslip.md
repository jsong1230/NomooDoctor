# F-07 급여명세서 생성 및 발송 — API 스펙 확정본

## 개요

급여명세서를 생성하고 이메일 또는 카카오 알림톡으로 발송하는 API입니다.
근로기준법 제48조에 따른 법정 기재사항을 모두 포함합니다.

## 공통 규격

- Base URL: `/api/v1`
- 인증: `Authorization: Bearer {access_token}` (회사 컨텍스트 토큰 필요)
- 응답 형식: `{ success: boolean, data?: T, error?: { code, message, details } }`

---

## 엔드포인트

### POST /payslips/

급여명세서를 생성합니다.

**Request Body**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| employee_id | UUID | 필수 | 직원 ID |
| year | int | 필수 | 급여 연도 |
| month | int (1-12) | 필수 | 급여 월 |
| payment_date | date | 필수 | 실제 지급일 |
| base_salary | int | 선택 | 기본급 (default: 0) |
| weekly_allowance | int | 선택 | 주휴수당 (default: 0) |
| overtime_pay | int | 선택 | 연장수당 (default: 0) |
| night_pay | int | 선택 | 야간수당 (default: 0) |
| holiday_pay | int | 선택 | 휴일근로수당 (default: 0) |
| meal_allowance | int | 선택 | 식대 (default: 0) |
| transport_allowance | int | 선택 | 교통비 (default: 0) |
| national_pension | int | 선택 | 국민연금 (default: 0) |
| health_insurance | int | 선택 | 건강보험 (default: 0) |
| long_term_care | int | 선택 | 장기요양보험 (default: 0) |
| employment_insurance | int | 선택 | 고용보험 (default: 0) |
| income_tax | int | 선택 | 소득세 (default: 0) |
| local_income_tax | int | 선택 | 지방소득세 (default: 0) |

**Response 201**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "employee_id": "uuid",
    "employee_name": "김직원",
    "company_name": "테스트사업장",
    "year": 2024,
    "month": 12,
    "payment_date": null,
    "base_salary": 2500000,
    "weekly_allowance": 0,
    "overtime_pay": 150000,
    "night_pay": 0,
    "holiday_pay": 0,
    "meal_allowance": 100000,
    "transport_allowance": 50000,
    "total_payment": 2800000,
    "national_pension": 112500,
    "health_insurance": 88625,
    "long_term_care": 11487,
    "employment_insurance": 22500,
    "income_tax": 13210,
    "local_income_tax": 1321,
    "total_deduction": 249643,
    "net_salary": 2550357,
    "send_status": "pending",
    "sent_at": null,
    "sent_via": null,
    "created_at": "2024-12-01T00:00:00Z"
  },
  "meta": { "message": "급여명세서가 생성되었습니다." }
}
```

**Error**

| 코드 | HTTP | 설명 |
|------|------|------|
| E-2001 | 401 | 인증 필요 |
| E-2005 | 403 | 사업장 미선택 (company_id 없는 토큰) |
| E-3002 | 404 | 직원을 찾을 수 없음 |

---

### GET /payslips/

사업장의 급여명세서 목록을 조회합니다.

**Query Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| year | int | 연도 필터 (optional) |
| month | int | 월 필터 (optional) |
| employee_id | UUID | 직원 필터 (optional) |
| page | int | 페이지 번호 (default: 1) |
| per_page | int | 페이지 크기 (default: 20, max: 100) |

**Response 200**

```json
{
  "success": true,
  "data": [ /* PayslipResponse 배열 */ ]
}
```

---

### GET /payslips/{payslip_id}

급여명세서 상세 정보를 조회합니다.

**Response 200**

```json
{
  "success": true,
  "data": { /* PayslipResponse */ }
}
```

**Error**

| 코드 | HTTP | 설명 |
|------|------|------|
| E-3002 | 404 | 급여명세서를 찾을 수 없음 |

---

### GET /payslips/{payslip_id}/pdf

급여명세서를 PDF로 다운로드합니다.

**Response 200**

- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename=payslip_{payslip_id}.pdf`

ReportLab으로 생성된 PDF (A4 사이즈, 근로기준법 제48조 법정 기재사항 포함).

---

### POST /payslips/{payslip_id}/send

급여명세서를 이메일 또는 카카오 알림톡으로 발송합니다.

**Request Body**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| method | string | 필수 | 발송 방식: "email" / "kakao" / "both" |
| email | string | 선택 | 이메일 주소 (없으면 직원 이메일 사용) |

**발송 정책**

- `email`: 이메일 발송. SMTP 미설정 시 mock 모드 (로그만 출력, `sent` 반환)
- `kakao`: 카카오 알림톡 발송 (3회 재시도). 실패 시 이메일 fallback. 현재 mock 모드
- `both`: 이메일 + 카카오 알림톡 모두 시도

**상태 코드**

| 상태 | 설명 |
|------|------|
| sent | 발송 성공 |
| failed | 모든 발송 방법 실패 |
| pending | 발송 전 초기 상태 |

**Response 200**

```json
{
  "success": true,
  "data": {
    "send_status": "sent",
    "sent_via": "email",
    "sent_at": "2024-12-01T10:00:00Z"
  },
  "meta": { "message": "급여명세서가 발송되었습니다." }
}
```

---

### GET /employees/{employee_id}/payslips

직원별 급여 히스토리를 조회합니다.

**Query Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| limit | int | 조회 개수 (default: 24) |

**Response 200**

```json
{
  "success": true,
  "data": [ /* PayslipResponse 배열, 최신 순 정렬 */ ]
}
```

**Error**

| 코드 | HTTP | 설명 |
|------|------|------|
| E-3002 | 404 | 직원을 찾을 수 없거나 다른 회사 직원 |

---

## Rate Limit

| 엔드포인트 | 제한 |
|----------|------|
| POST /payslips/ | 50회/시간 |
| GET /payslips/ | 100회/분 |
| GET /payslips/{id} | 100회/분 |
| GET /payslips/{id}/pdf | 50회/시간 |
| POST /payslips/{id}/send | 30회/시간 |
