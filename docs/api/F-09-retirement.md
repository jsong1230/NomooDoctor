# F-09 퇴직금/해고 계산기 API 스펙

**최종 확정본** | 2026-03-12

---

## 1. 개요

F-09는 퇴직금 정확 계산 및 합법적 해고 절차 가이드 생성 기능을 제공합니다.

### 주요 기능
- **퇴직금 시뮬레이션**: 실시간 퇴직금 계산 (DB 저장 없음)
- **퇴직금 확정 저장**: 계산 결과를 DB에 저장하여 법적 증빙
- **해고 절차 가이드**: Claude API 기반 상세 가이드 생성
- **위험도 판정**: 임신, 노조, 산재 등 법적 위험 자동 감지
- **해고 서류 생성**: 해고예고통지서, 권고사직서 (미구현, 스케줄)

---

## 2. 엔드포인트

### 2.1 POST /api/v1/retirement/calculate

**목적**: 퇴직금 시뮬레이션 (미리보기, DB 저장 안 함)

**요청**:
```json
{
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "resign_date": "2026-03-31",
  "annual_bonus": 0,
  "unused_annual_leave_days": 0,
  "monthly_wages": [
    {
      "year": 2026,
      "month": 1,
      "total_wage": 3000000,
      "days_in_month": 31
    },
    {
      "year": 2026,
      "month": 2,
      "total_wage": 3000000,
      "days_in_month": 28
    },
    {
      "year": 2026,
      "month": 3,
      "total_wage": 3000000,
      "days_in_month": 31
    }
  ]
}
```

**응답 200**:
```json
{
  "success": true,
  "data": {
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "employee_name": "홍길동",
    "hire_date": "2024-01-15",
    "resign_date": "2026-03-31",
    "total_service_days": 806,
    "average_daily_wage": 100000,
    "severance_pay": 2633150,
    "unused_leave_pay": 0,
    "bonus_included": 0,
    "total_payment": 2633150,
    "payment_deadline": "2026-04-14",
    "eligible": true,
    "calculation_detail": {
      "last_3_months_total_wage": 9000000,
      "last_3_months_total_days": 90,
      "bonus_3_months_share": 0,
      "average_daily_wage": 100000,
      "severance_formula": "100000 * 30 * (806 / 365)",
      "unused_leave_formula": "100000 * 0"
    }
  }
}
```

**에러**:
| HTTP | 코드 | 상황 |
|------|------|------|
| 422 | E-5010 | 재직기간 1년 미만 |
| 422 | E-5011 | 퇴사일이 입사일 이전 |
| 422 | E-5012 | 최근 3개월 급여 데이터 부족 |
| 404 | E-4004 | 직원 없음 |
| 400 | E-1001 | 입력값 검증 실패 |

---

### 2.2 POST /api/v1/retirement/severance

**목적**: 퇴직금 산출 결과 확정 및 DB 저장

**요청**: calculate와 동일

**응답 201**:
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "employee_name": "홍길동",
    "hire_date": "2024-01-15",
    "resign_date": "2026-03-31",
    "total_service_days": 806,
    "average_daily_wage": 100000,
    "severance_pay": 2633150,
    "unused_leave_pay": 0,
    "bonus_included": 0,
    "total_payment": 2633150,
    "payment_deadline": "2026-04-14",
    "eligible": true,
    "calculation_detail": { ... },
    "status": "calculated",
    "created_at": "2026-03-12T10:00:00Z"
  }
}
```

**에러**:
| HTTP | 코드 | 상황 |
|------|------|------|
| 409 | E-5015 | 동일 직원의 퇴직금 이미 존재 |
| (외) | (동위) | calculate와 동일 |

---

### 2.3 GET /api/v1/retirement/severance/{id}

**목적**: 저장된 퇴직금 상세 조회

**응답 200**: 2.2와 동일 구조

**에러**:
| HTTP | 코드 | 상황 |
|------|------|------|
| 404 | E-5013 | 퇴직금 기록 없음 |

---

### 2.4 GET /api/v1/retirement/severance

**목적**: 사업장 퇴직금 목록 조회

**쿼리**:
- `employee_id` (선택)
- `status` (선택): calculated, paid, overdue
- `limit` (기본: 20)
- `offset` (기본: 0)

**응답 200**:
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "employee_id": "550e8400-e29b-41d4-a716-446655440000",
      "employee_name": "홍길동",
      "resign_date": "2026-03-31",
      "total_payment": 2633150,
      "status": "calculated",
      "payment_deadline": "2026-04-14",
      "created_at": "2026-03-12T10:00:00Z"
    }
  ],
  "meta": {
    "total": 1,
    "limit": 20,
    "offset": 0
  }
}
```

---

### 2.5 POST /api/v1/retirement/termination-guide

**목적**: 해고/퇴직 절차 가이드 생성

**요청**:
```json
{
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "termination_type": "dismissal",
  "reason": "경영상 사유로 인한 해고",
  "risk_factors": {
    "is_pregnant": false,
    "is_on_parental_leave": false,
    "is_union_member": false,
    "is_workplace_injury": false,
    "is_whistleblower": false
  }
}
```

**응답 200**:
```json
{
  "success": true,
  "data": {
    "termination_type": "dismissal",
    "risk_level": "MEDIUM",
    "checklist": [
      {
        "step": 1,
        "title": "해고 사유 정당성 확인",
        "description": "근로기준법 제23조에 따라 정당한 사유가 있는지 확인",
        "required": true,
        "completed": false
      }
    ],
    "advance_notice": {
      "required": true,
      "notice_days": 30,
      "notice_pay_amount": 3000000,
      "description": "30일 전 서면 예고 또는 30일분 통상임금 지급"
    },
    "risk_warnings": [
      {
        "type": "dismissal",
        "severity": "MEDIUM",
        "message": "해고는 신중한 법적 검토가 필요합니다.",
        "recommendation": "노무사 상담을 권장합니다."
      }
    ],
    "documents": [
      {
        "type": "dismissal_notice",
        "name": "해고예고통지서",
        "available": true
      },
      {
        "type": "resignation_agreement",
        "name": "권고사직서",
        "available": true
      }
    ],
    "unemployment_benefit_guide": {
      "eligible": true,
      "conditions": "비자발적 이직(해고) 시 실업급여 수급 가능",
      "required_documents": ["이직확인서", "구직신청서", "신분증"]
    },
    "ai_guide": "해고/퇴직 유형: dismissal\n\n법적 검토:\n근로기준법 제23조에 따르면 해고는 정당한 사유가 있어야 합니다...",
    "law_references": [
      {
        "law_name": "근로기준법",
        "article": "제23조",
        "content": "해고는 정당한 사유 없이 하지 못합니다."
      },
      {
        "law_name": "근로기준법",
        "article": "제26조",
        "content": "사용자가 근로자를 해고하고자 할 때에는 적어도 30일 전에 예고하거나 30일 이상의 통상임금을 지급해야 합니다."
      }
    ],
    "disclaimer": "본 가이드는 참고용이며, 법적 효력이 없습니다. 구체적 사안에 대해서는 전문 노무사와 상담하시기 바랍니다."
  }
}
```

**위험도 판정**:
- `LOW`: 자발적 퇴사, 계약만료, 정년퇴직
- `MEDIUM`: 해고(일반)
- `HIGH`: 노조활동, 내부고발자
- `EMERGENCY`: 임신, 육아휴직, 산재 중

**에러**:
| HTTP | 코드 | 상황 |
|------|------|------|
| 404 | E-4004 | 직원 없음 |
| 422 | E-5014 | 이미 퇴직 처리된 직원 |
| 502 | E-6002 | Claude API 오류 (향후) |

---

### 2.6 POST /api/v1/retirement/documents/generate

**목적**: 해고 관련 서류 생성

**요청**:
```json
{
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_type": "dismissal_notice",
  "termination_date": "2026-04-30",
  "reason": "경영상 사유",
  "format": "pdf"
}
```

**응답 200**:
```json
{
  "success": true,
  "data": {
    "download_url": "https://s3.example.com/documents/dismissal_notice_xxxxx.pdf",
    "expires_at": "2026-03-13T10:00:00Z",
    "filename": "해고예고통지서_홍길동_20260312.pdf",
    "document_type": "dismissal_notice"
  }
}
```

**에러**:
| HTTP | 코드 | 상황 |
|------|------|------|
| 400 | E-1001 | 유효하지 않은 document_type |

---

## 3. 인증 및 권한

모든 엔드포인트는 JWT 인증 필요:
```
Authorization: Bearer {access_token}
```

**회사 선택 필수**: JWT payload에 `company_id` 포함 필요

---

## 4. Rate Limiting

| 엔드포인트 | 제한 |
|-----------|------|
| POST /retirement/calculate | 30회/시간 |
| POST /retirement/severance | 10회/시간 |
| POST /retirement/termination-guide | 10회/시간 |
| POST /retirement/documents/generate | 10회/시간 |
| GET /retirement/severance* | 100회/분 |

---

## 5. 데이터 타입

### MonthlyWageInput
```json
{
  "year": 2026,
  "month": 1,
  "total_wage": 3000000,
  "days_in_month": 31
}
```

### SeveranceRecord (DB)
- id: UUID
- employee_id: UUID
- company_id: UUID
- hire_date: Date
- resign_date: Date
- total_service_days: Integer
- average_daily_wage: Numeric(12,0)
- severance_pay: Numeric(14,0)
- unused_leave_pay: Numeric(12,0)
- total_payment: Numeric(14,0)
- payment_deadline: Date
- status: enum('calculated', 'paid', 'overdue')
- calculation_detail: JSONB
- created_at: Timestamp
- updated_at: Timestamp

---

## 6. 퇴직금 계산 공식

```
평균임금(일) = (최근 3개월 총 임금 + 상여금 × 3/12) / 최근 3개월 총 일수

퇴직금 = 평균임금(일) × 30 × (총 재직일수 / 365)

연차미사용수당 = 평균임금(일) × 미사용 연차일수

총 지급액 = 퇴직금 + 연차미사용수당

금액 정밀도: 10원 미만 절사 (truncate)
```

### 예시
```
입사: 2024-01-15
퇴사: 2026-03-31
총 재직일수: 806일

최근 3개월 (2026-01~03):
  1월: 3,000,000원 / 31일
  2월: 3,000,000원 / 28일
  3월: 3,000,000원 / 31일
  합계: 9,000,000원 / 90일

평균임금 = 9,000,000 / 90 = 100,000원/일
퇴직금 = 100,000 × 30 × (806 / 365) = 2,633,150원
지급 기한 = 2026-04-14 (퇴직일 + 14일)
```

---

## 7. 제약조건

### 퇴직금 수급 자격
- **최소 재직기간**: 1년 이상 (365일)
- **예외**: 1년 미만 시 E-5010 오류

### 중복 방지
- 동일 직원 + 퇴사일 조합은 유니크 (중복 저장 방지)
- 중복 시 E-5015 오류

### 데이터 격리
- company_id 기반 접근 제어 필수
- 타회사 퇴직금 조회 불가

---

## 8. 입력 검증

### 필수 필드
- employee_id: UUID 형식
- resign_date: YYYY-MM-DD
- monthly_wages (선택): min_length=3, max_length=3

### 값의 범위
- annual_bonus: >= 0
- unused_annual_leave_days: 0 ~ 40
- total_wage: > 0
- days_in_month: 28 ~ 31

---

## 변경 이력

| 날짜 | 변경 | 이유 |
|------|------|------|
| 2026-03-12 | API 스펙 확정 | F-09 구현 완료 |
