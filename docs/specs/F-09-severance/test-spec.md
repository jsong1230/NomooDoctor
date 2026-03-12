# F-09 퇴직금/해고 계산기 -- 테스트 명세

## 참조

- 설계서: docs/specs/F-09-severance/design.md
- 인수조건: docs/project/features.md #F-09

---

## 1. 단위 테스트

### 1.1 퇴직금 계산 로직 (SeveranceService)

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| compute_total_service_days | 정상 재직기간 계산 | hire=2023-01-02, resign=2026-03-31 | 1184일 |
| compute_total_service_days | 정확히 1년 | hire=2025-01-01, resign=2026-01-01 | 366일 (2025는 평년, 0-indexed date diff) |
| compute_total_service_days | 윤년 포함 | hire=2024-01-01, resign=2025-01-01 | 366일 |
| compute_average_daily_wage | 기본 평균임금 계산 | 3개월 각 300만원, bonus=0, days=31+28+31=90 | 9,000,000 / 90 = 100,000원 |
| compute_average_daily_wage | 상여금 포함 | 3개월 각 300만원, bonus=1,200,000, days=90 | (9,000,000 + 300,000) / 90 = 103,333원 |
| compute_average_daily_wage | 상여금 3/12 반영 확인 | annual_bonus=1,200,000 | bonus_3m_share = 1,200,000 * 3/12 = 300,000 |
| compute_severance_pay | 기본 퇴직금 계산 | avg_daily=100,000, service_days=365 | 100,000 * 30 * (365/365) = 3,000,000원 |
| compute_severance_pay | 2년 근무 | avg_daily=100,000, service_days=730 | 100,000 * 30 * (730/365) = 6,000,000원 |
| compute_severance_pay | 1년 6개월 근무 | avg_daily=100,000, service_days=548 | 100,000 * 30 * (548/365) = 4,504,109원 (10원 절사) |
| compute_severance_pay | 10원 미만 절사 검증 | avg_daily=103,333, service_days=547 | 정확한 10원 단위 |
| compute_unused_leave_pay | 미사용 연차 5일 | avg_daily=100,000, days=5 | 500,000원 |
| compute_unused_leave_pay | 미사용 연차 0일 | avg_daily=100,000, days=0 | 0원 |
| compute_unused_leave_pay | 미사용 연차 15일 | avg_daily=103,333, days=15 | 1,549,990원 (10원 절사) |
| compute_payment_deadline | 지급 기한 계산 | resign=2026-03-31 | 2026-04-14 |
| compute_payment_deadline | 월말 경계 | resign=2026-02-15 | 2026-03-01 |
| truncate_to_10_won | 10원 절사 | 3,141,592 | 3,141,590 |
| truncate_to_10_won | 이미 10원 단위 | 3,000,000 | 3,000,000 |
| truncate_to_10_won | 5원 절사 | 3,000,005 | 3,000,000 |

### 1.2 위험도 판정 로직

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| _detect_risk_level | 자발적 퇴사 + 위험 요소 없음 | type=resignation, all False | LOW |
| _detect_risk_level | 해고 + 위험 요소 없음 | type=dismissal, all False | MEDIUM |
| _detect_risk_level | 해고 + 노조원 | type=dismissal, union=True | HIGH |
| _detect_risk_level | 해고 + 임신 | type=dismissal, pregnant=True | EMERGENCY |
| _detect_risk_level | 권고사직 + 육아휴직 중 | type=mutual_agreement, parental=True | EMERGENCY |
| _detect_risk_level | 해고 + 복합 위험(임신+노조) | type=dismissal, pregnant=True, union=True | EMERGENCY (최고 등급) |
| _detect_risk_level | 계약만료 + 위험 요소 없음 | type=contract_expiry, all False | LOW |
| _detect_risk_level | 정년퇴직 + 위험 요소 없음 | type=retirement, all False | LOW |
| _detect_risk_level | 해고 + 내부고발자 | type=dismissal, whistleblower=True | HIGH |
| _detect_risk_level | 해고 + 산재 | type=dismissal, workplace_injury=True | EMERGENCY |

### 1.3 체크리스트 생성

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| _build_checklist | 자발적 퇴사 | type=resignation | 퇴직금 지급, 실업급여 안내 등 포함 |
| _build_checklist | 해고 | type=dismissal | 해고사유 정당성, 서면통지, 해고예고 등 포함 |
| _build_checklist | 권고사직 | type=mutual_agreement | 합의서 작성, 실업급여 자격 안내 포함 |
| _build_checklist | 계약만료 | type=contract_expiry | 갱신 여부 확인, 퇴직금 지급 안내 포함 |

---

## 2. 통합 테스트

### 2.1 퇴직금 계산 API (POST /retirement/calculate)

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /retirement/calculate | 정상 계산 (수동 입력) | employee_id, resign_date, monthly_wages 3개월 | 200, 퇴직금 계산 결과 반환 |
| POST /retirement/calculate | 정상 계산 (payslips 자동) | employee_id, resign_date, monthly_wages=null | 200, payslips 기반 자동 계산 |
| POST /retirement/calculate | 상여금 포함 계산 | annual_bonus=2,400,000 | 200, bonus_included=600,000 반영 |
| POST /retirement/calculate | 연차 미사용 수당 포함 | unused_annual_leave_days=10 | 200, unused_leave_pay > 0 |
| POST /retirement/calculate | 재직기간 1년 미만 | hire=2026-01-01, resign=2026-06-01 | 422, E-5010 |
| POST /retirement/calculate | 퇴사일 < 입사일 | resign < hire | 422, E-5011 |
| POST /retirement/calculate | 급여 데이터 없음 | payslips 없고 monthly_wages 미입력 | 422, E-5012 |
| POST /retirement/calculate | 직원 없음 | invalid employee_id | 404, E-4004 |
| POST /retirement/calculate | 다른 회사 직원 | 타사 employee_id | 404, E-4004 |
| POST /retirement/calculate | 인증 없음 | Authorization 헤더 없음 | 401 |
| POST /retirement/calculate | 회사 미선택 | company_id 없는 토큰 | 403 |

### 2.2 퇴직금 저장 API (POST /retirement/severance)

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /retirement/severance | 정상 저장 | 유효한 계산 요청 | 201, id 포함된 결과 |
| POST /retirement/severance | 중복 저장 | 동일 employee_id + resign_date | 409, E-5015 |
| POST /retirement/severance | 저장 후 DB 확인 | 유효 요청 | 201, DB에 severance_records 행 생성 확인 |

### 2.3 퇴직금 조회 API

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| GET /retirement/severance/{id} | 정상 조회 | 유효 severance_id | 200, 상세 정보 |
| GET /retirement/severance/{id} | 존재하지 않는 ID | random UUID | 404, E-5013 |
| GET /retirement/severance/{id} | 다른 회사 기록 | 타사 severance_id | 404, E-5013 |
| GET /retirement/severance | 목록 조회 | company_id 기준 | 200, 목록 반환 |
| GET /retirement/severance | employee_id 필터 | ?employee_id=uuid | 200, 해당 직원 기록만 |
| GET /retirement/severance | status 필터 | ?status=calculated | 200, calculated 상태만 |

### 2.4 해고 절차 가이드 API (POST /retirement/termination-guide)

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /termination-guide | 자발적 퇴사 | type=resignation, risk 없음 | 200, risk_level=LOW |
| POST /termination-guide | 해고 기본 | type=dismissal, risk 없음 | 200, risk_level=MEDIUM, 해고 체크리스트 |
| POST /termination-guide | 임신 직원 해고 시도 | type=dismissal, pregnant=true | 200, risk_level=EMERGENCY, 경고 메시지 |
| POST /termination-guide | 노조원 해고 | type=dismissal, union=true | 200, risk_level=HIGH |
| POST /termination-guide | 해고예고수당 계산 | type=dismissal | 200, advance_notice.required=true, pay > 0 |
| POST /termination-guide | 계약만료 | type=contract_expiry | 200, risk_level=LOW, advance_notice.required=false |
| POST /termination-guide | 면책 문구 확인 | 모든 요청 | 200, disclaimer 필드 존재 및 비어있지 않음 |
| POST /termination-guide | 법 조항 인용 확인 | type=dismissal | 200, law_references 1개 이상 |
| POST /termination-guide | 실업급여 가이드 | type=dismissal | 200, unemployment_benefit_guide.eligible=true |
| POST /termination-guide | Claude API 실패 시 | Claude mock 에러 | 502, E-6002 |

### 2.5 서류 생성 API (POST /retirement/documents/generate)

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /documents/generate | 해고예고통지서 생성 | type=dismissal_notice, pdf | 200, download_url 반환 |
| POST /documents/generate | 권고사직서 생성 | type=resignation_agreement, pdf | 200, download_url 반환 |
| POST /documents/generate | 잘못된 서류 유형 | type=invalid | 400, E-1001 |

---

## 3. 경계 조건 / 에러 케이스

### 3.1 퇴직금 계산 경계

- 정확히 1년(365일) 재직 시 퇴직금 = 평균임금 * 30 (재직비율 1.0)
- 정확히 364일 재직 시 퇴직금 미해당 (E-5010)
- 윤년 포함 재직기간: 2024-01-01 ~ 2025-01-01 = 366일
- 평균임금 0원 불가 (월 급여 > 0 필수)
- 상여금 0원은 정상 (기본값)
- 미사용 연차 0일은 정상 (기본값)
- 미사용 연차 최대 40일 제한

### 3.2 금액 정밀도

- 모든 금액 계산은 Decimal 타입 사용 (float 금지)
- 최종 금액은 10원 미만 절사 (truncate_to_10_won)
- 평균임금 중간 계산 과정에서 소수점 유지, 최종 결과에서만 절사
- 퇴직금 공식: `평균임금 * 30 * (재직일수 / 365)` - 순서 주의 (나눗셈 마지막)

### 3.3 날짜 경계

- 퇴사일 = 입사일 + 365일: 퇴직금 해당 (재직일수 = 365)
- 퇴사일 = 입사일 + 364일: 퇴직금 미해당
- 퇴사일 = 입사일: 에러 (E-5011, 재직기간 0일)
- 퇴사일이 미래: 허용 (시뮬레이션 목적)
- 지급 기한이 월말을 넘어가는 경우: 정상 처리

### 3.4 위험 케이스

- 위험 요소 복합 발생 시 최고 등급 적용 (EMERGENCY > HIGH > MEDIUM > LOW)
- EMERGENCY 케이스 시 노무사 상담 권장 메시지 필수 포함
- 모든 가이드에 면책 문구 100% 삽입 확인

### 3.5 데이터 격리

- company_id가 다른 직원의 퇴직금을 계산/조회할 수 없음
- severance_records 조회 시 company_id 필터 필수

---

## 4. 계산 정확도 테스트

### 4.1 표준 시나리오 (수기 검증 대조)

| 시나리오 | 입사일 | 퇴사일 | 월급여 | 상여금(연) | 미사용연차 | 예상 퇴직금 | 예상 총지급액 |
|----------|--------|--------|--------|-----------|-----------|-----------|-------------|
| 기본 (1년) | 2025-01-01 | 2026-01-01 | 3,000,000 | 0 | 0 | 3,000,000 (30 * 100,000 * 366/365) | 3,002,739 |
| 2년 근무 | 2024-01-01 | 2026-01-01 | 3,000,000 | 0 | 0 | 6,000,000 (30 * 100,000 * 731/365) | 6,008,219 |
| 상여금 포함 | 2024-01-01 | 2026-01-01 | 3,000,000 | 6,000,000 | 0 | 상여 3/12=1,500,000 포함 | - |
| 연차 미사용 | 2024-01-01 | 2026-01-01 | 3,000,000 | 0 | 15 | 퇴직금 + 연차수당 | - |
| 최저임금 수준 | 2025-01-01 | 2026-01-01 | 2,096,270 | 0 | 0 | 약 2,098,000 | - |
| 고임금 | 2023-01-01 | 2026-01-01 | 10,000,000 | 12,000,000 | 25 | - | - |

### 4.2 수기 계산 검증 (상세)

**시나리오: 입사 2024-04-01, 퇴사 2026-03-31, 월급 3,500,000, 상여금(연) 4,200,000, 미사용연차 12일**

1. 재직일수: 2024-04-01 ~ 2026-03-31 = 730일
2. 최근 3개월 (2026-01, 02, 03): 총급여 = 3,500,000 * 3 = 10,500,000
3. 최근 3개월 일수: 31 + 28 + 31 = 90일
4. 상여금 3/12: 4,200,000 * 3/12 = 1,050,000
5. 평균임금(일): (10,500,000 + 1,050,000) / 90 = 128,333.33...
6. 퇴직금: 128,333 * 30 * (730/365) = 7,699,980 -> 10원 절사 -> 7,699,980
7. 연차미사용수당: 128,333 * 12 = 1,539,996 -> 10원 절사 -> 1,539,990
8. 총 지급액: 7,699,980 + 1,539,990 = 9,239,970
9. 지급 기한: 2026-04-14

(주의: 위 계산은 설계 시점 추정이며, 구현 후 정확한 Decimal 연산으로 재검증 필요)

---

## 5. 테스트 파일 구조

```
backend/tests/
    unit/
        test_severance_calculator.py      -- 계산 로직 단위 테스트
        test_risk_detection.py            -- 위험도 판정 단위 테스트
    api/
        test_retirement_api.py            -- 통합 API 테스트
        conftest.py                       -- 직원+급여 fixture 추가
```

### 5.1 Fixture 요구사항

```python
# conftest.py 추가 fixture

@pytest.fixture
async def employee_with_payslips():
    """3개월치 payslips가 있는 직원 (퇴직금 자동 계산 테스트용)"""
    # employee: hire_date=2024-01-01
    # payslips: 2026-01, 2026-02, 2026-03 각 3,000,000원

@pytest.fixture
async def employee_short_tenure():
    """재직기간 1년 미만 직원"""
    # hire_date=2025-10-01

@pytest.fixture
async def resigned_employee():
    """이미 퇴직 처리된 직원"""
    # is_active=False, resign_date=2026-01-31
```

---

## 6. 테스트 우선순위

### P0 (필수)

1. 퇴직금 계산 정확도 -- Decimal 정밀도 + 10원 절사
2. 재직기간 1년 미만 검증 (E-5010)
3. 평균임금 계산 (상여금 포함/미포함)
4. 위험도 판정 (EMERGENCY 케이스)
5. 면책 문구 100% 삽입
6. company_id 기반 데이터 격리

### P1 (중요)

7. payslips 자동 조회 fallback
8. 해고예고수당 계산
9. 퇴직금 저장 + 중복 방지
10. 경계 날짜 테스트 (365일 vs 364일)

### P2 (보통)

11. 해고 서류 생성 (PDF URL 반환)
12. 실업급여 가이드 내용 확인
13. 목록 조회 + 필터

---

## 변경 이력

| 날짜 | 변경 내용 | 이유 |
|------|-----------|------|
| 2026-03-12 | 초기 테스트 명세 작성 | F-09 기능 구현 준비 |
