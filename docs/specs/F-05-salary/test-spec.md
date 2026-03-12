# F-05 급여 자동 계산기 — 테스트 명세

## 참조
- 설계서: docs/specs/F-05-salary/design.md
- 인수조건: docs/project/features.md #F-05
- API 컨벤션: docs/system/api-conventions.md

---

## 단위 테스트

### 수당 계산 (app/utils/wage_calculator.py)

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| calculate_hourly_rate | 월급제 통상시급 계산 | base_wage=2090000, wage_type='monthly', weekly_hours=40, meal=100000, transport=100000 | 10204 (10원 단위 절사) |
| calculate_hourly_rate | 시급제 통상시급 계산 | base_wage=10030, wage_type='hourly' | 10030 |
| calculate_hourly_rate | 일급제 통상시급 계산 | base_wage=89500, wage_type='daily', weekly_hours=40 | 약 10204 |
| calculate_overtime_pay | 연장수당 계산 (정상) | hourly_rate=10000, overtime_hours=10 | 150000 (10000 * 10 * 1.5) |
| calculate_overtime_pay | 연장수당 계산 (0시간) | hourly_rate=10000, overtime_hours=0 | 0 |
| calculate_night_pay | 야간수당 계산 (정상) | hourly_rate=10000, night_hours=8 | 40000 (10000 * 8 * 0.5) |
| calculate_night_pay | 야간수당 계산 (0시간) | hourly_rate=10000, night_hours=0 | 0 |
| calculate_holiday_pay | 휴일수당 계산 (8시간 이내) | hourly_rate=10000, holiday_hours=6 | 90000 (10000 * 6 * 1.5) |
| calculate_holiday_pay | 휴일수당 계산 (8시간 초과) | hourly_rate=10000, holiday_hours=10 | 160000 (10000 * 8 * 1.5 + 10000 * 2 * 2.0) |
| calculate_holiday_pay | 휴일수당 계산 (0시간) | hourly_rate=10000, holiday_hours=0 | 0 |
| calculate_weekly_holiday_pay | 주휴수당 계산 (개근) | hourly_rate=10000, daily_hours=8, is_full_attendance=True | 80000 |
| calculate_weekly_holiday_pay | 주휴수당 계산 (미개근) | hourly_rate=10000, daily_hours=8, is_full_attendance=False | 0 |
| floor_to_10_won | 10원 미만 절사 (정상) | amount=12345 | 12340 |
| floor_to_10_won | 10원 단위 (변화 없음) | amount=12340 | 12340 |
| floor_to_10_won | 0원 | amount=5 | 0 |

### 세금 계산 (app/utils/tax_calculator.py)

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| calculate_national_pension | 국민연금 계산 (정상) | monthly_wage=3000000, rate=0.045 | 135000 |
| calculate_national_pension | 국민연금 계산 (하한 적용) | monthly_wage=1000000, rate=0.045 | 상한/하한 검증 필요 |
| calculate_health_insurance | 건강보험 계산 | monthly_wage=3000000, rate=0.03545 | 106350 (10원 절사: 106350) |
| calculate_long_term_care | 장기요양보험 계산 | health_insurance=106350, rate=0.1295 | 13772 (10원 절사) |
| calculate_employment_insurance | 고용보험 계산 | monthly_wage=3000000, rate=0.009 | 27000 |
| calculate_income_tax | 소득세 계산 (1인) | monthly_wage=3000000, family_count=1 | 간이세액표 기준 값 |
| calculate_income_tax | 소득세 계산 (4인) | monthly_wage=3000000, family_count=4 | 1인보다 감액 |
| calculate_local_income_tax | 지방소득세 계산 | income_tax=100000 | 10000 |

### 비즈니스 규칙 검증

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| validate_minimum_wage | 최저임금 충족 | hourly_rate=10030, year=2026 | True |
| validate_minimum_wage | 최저임금 미달 | hourly_rate=9000, year=2026 | False |
| is_eligible_for_weekly_holiday_pay | 주휴수당 지급 대상 (15시간 이상, 개근) | weekly_hours=20, is_full_attendance=True | True |
| is_eligible_for_weekly_holiday_pay | 주휴수당 미지급 (14시간) | weekly_hours=14, is_full_attendance=True | False |
| is_eligible_for_weekly_holiday_pay | 주휴수당 미지급 (미개근) | weekly_hours=20, is_full_attendance=False | False |
| apply_non_taxable_limit | 비과세 한도 내 | meal=100000, transport=100000 | (100000, 100000) |
| apply_non_taxable_limit | 비과세 한도 초과 | meal=300000, transport=250000 | (200000, 200000) |

---

## 통합 테스트

### POST /api/v1/payroll/calculate

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| /payroll/calculate | 정상 계산 (월급제) | employee_id, pay_year=2026, pay_month=3, work_records_summary | 200 OK, payments/deductions/net_pay 계산됨 |
| /payroll/calculate | 정상 계산 (시급제) | employee_id (hourly), ... | 200 OK, 시급 기반 계산 |
| /payroll/calculate | 정상 계산 (일급제) | employee_id (daily), ... | 200 OK, 일급 기반 계산 |
| /payroll/calculate | 연장/야간/휴일 포함 | overtime_hours=20, night_hours=10, holiday_hours=8 | 200 OK, 각 수당 반영 |
| /payroll/calculate | 최저임금 미달 | base_wage가 최저임금 이하인 직원 | 422, E-5001 에러 |
| /payroll/calculate | 존재하지 않는 직원 | employee_id=invalid-uuid | 404, E-4004 에러 |
| /payroll/calculate | 타 사업장 직원 | employee_id가 다른 company 소속 | 403, E-2005 에러 |
| /payroll/calculate | 인증 없음 | Authorization 헤더 없음 | 401, E-2001 에러 |
| /payroll/calculate | Rate Limit 초과 | 101회 요청 | 429, E-2006 에러 |
| /payroll/calculate | 잘못된 월 | pay_month=13 | 400, E-1001 에러 |
| /payroll/calculate | 잘못된 연도 | pay_year=2020 (과거) | 200 OK (과거 요율로 계산) |

### GET /api/v1/payroll/rates

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| /payroll/rates | 현재 연도 요율 조회 | year 생략 | 200 OK, 2026년 요율 |
| /payroll/rates | 특정 연도 요율 조회 | year=2025 | 200 OK, 2025년 요율 |
| /payroll/rates | 인증 없음 | Authorization 헤더 없음 | 401, E-2001 에러 |

### POST /api/v1/payslips

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| /payslips | 정상 생성 | employee_id, pay_year, pay_month, calculation_result | 201 Created |
| /payslips | 중복 생성 방지 | 같은 employee_id, pay_year, pay_month | 409, E-3001 에러 |
| /payslips | 인증 없음 | Authorization 헤더 없음 | 401, E-2001 에러 |

### GET /api/v1/payslips

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| /payslips | 전체 목록 조회 | 필터 없음 | 200 OK, 페이징된 목록 |
| /payslips | 직원별 필터 | employee_id=xxx | 200 OK, 해당 직원만 |
| /payslips | 연월 필터 | pay_year=2026, pay_month=3 | 200 OK, 해당 월만 |
| /payslips | 복합 필터 | employee_id + pay_year + pay_month | 200 OK |
| /payslips | 페이지네이션 | limit=10, cursor=xxx | 200 OK, 다음 페이지 |

### GET /api/v1/payslips/{id}

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| /payslips/{id} | 정상 조회 | 유효한 id | 200 OK, 상세 정보 |
| /payslips/{id} | 존재하지 않는 ID | invalid-id | 404, E-3002 에러 |
| /payslips/{id} | 타 사업장 급여명세서 | 다른 company 소속 | 403, E-2005 에러 |

---

## 경계 조건 / 에러 케이스

### 수당 계산 경계값

| 케이스 | 입력 | 예상 결과 |
|--------|------|-----------|
| 연장근무 0시간 | overtime_hours=0 | overtime_pay=0 |
| 연장근무 1시간 | overtime_hours=1 | hourly_rate * 1 * 1.5 |
| 야간근무 0시간 | night_hours=0 | night_pay=0 |
| 야간근무 1시간 | night_hours=1 | hourly_rate * 1 * 0.5 |
| 휴일근무 8시간 경계 | holiday_hours=8 | hourly_rate * 8 * 1.5 |
| 휴일근무 8시간 초과 | holiday_hours=8.5 | hourly_rate * 8 * 1.5 + hourly_rate * 0.5 * 2.0 |
| 주 15시간 미만 | weekly_hours=14 | 주휴수당=0 |
| 주 15시간 경계 | weekly_hours=15 | 주휴수당 지급 (개근 시) |
| 급여 0원 | base_wage=0 | 최저임금 미달 에러 |

### 금액 절사 테스트

| 케이스 | 입력 | 예상 결과 |
|--------|------|-----------|
| 1원 단위 | amount=12345 | 12340 |
| 10원 단위 | amount=12340 | 12340 |
| 100원 단위 | amount=12300 | 12300 |
| 1000원 단위 | amount=12000 | 12000 |
| 소수점 포함 | amount=12345.67 | 12340 |

### 동시성 테스트

| 케이스 | 시나리오 | 예상 결과 |
|--------|----------|-----------|
| 동일 직원 동일 월 중복 생성 | 2개 요청 동시 전송 | 1개만 성공, 1개는 409 Conflict |
| 요율 캐시 갱신 | 캐시 만료 중 요청 | DB 조회 후 캐시 갱신 |

---

## Redis 캐싱 테스트

| 케이스 | 시나리오 | 예상 결과 |
|--------|----------|-----------|
| 캐시 히트 | 이미 캐시된 요율 조회 | DB 조회 없이 캐시 반환 |
| 캐시 미스 | 처음 요율 조회 | DB 조회 후 캐시 저장 |
| 캐시 만료 | TTL 24시간 경과 | DB 재조회 후 캐시 갱신 |
| 캐시 무효화 | 요율 업데이트 시 | 기존 캐시 삭제 |

---

## 성능 테스트

| 케이스 | 조건 | 기준 |
|--------|------|------|
| 급여 계산 응답 시간 | 단일 직원 | 500ms 이내 |
| 급여 계산 응답 시간 | 캐시 히트 시 | 100ms 이내 |
| 급여명세서 목록 조회 | 100건 | 200ms 이내 |
| 동시 요청 | 100명 동시 계산 요청 | 5초 이내 완료 |

---

## 보안 테스트

| 케이스 | 시나리오 | 예상 결과 |
|--------|----------|-----------|
| SQL Injection | employee_id에 SQL 구문 포함 | 400 에러, 실행 차단 |
| 타 사업장 접근 | 다른 company의 급여 조회 시도 | 403 Forbidden |
| 권한 없는 사용자 | employee 권한으로 급여 계산 시도 | 플랜에 따른 접근 제어 |
| 토큰 변조 | JWT payload 변조 | 401 Unauthorized |

---

## 감사 로그 테스트

| 케이스 | 시나리오 | 검증 항목 |
|--------|----------|-----------|
| 급여 계산 | 계산 요청 | user_id, employee_id, timestamp 로깅 |
| 급여명세서 생성 | 생성 요청 | user_id, payslip_id, net_pay 로깅 |
| 급여명세서 조회 | 상세 조회 | user_id, payslip_id, timestamp 로깅 |
| 요율 변경 | 요율 업데이트 | admin_user_id, rate_type, old_value, new_value 로깅 |

---

## 테스트 데이터

### 직원 더미 데이터
```json
{
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "홍길동",
  "employment_type": "regular",
  "wage_type": "monthly",
  "base_wage": 2500000,
  "meal_allowance": 200000,
  "transport_allowance": 100000,
  "income_tax_family_count": 2
}
```

### 근태 기록 더미 데이터
```json
{
  "scheduled_hours": 209,
  "actual_hours": 230,
  "overtime_hours": 21,
  "night_hours": 15,
  "holiday_hours": 8,
  "is_full_attendance": true
}
```

### 노동법 요율 더미 데이터 (2026년)
```json
{
  "minimum_wage": 10030,
  "national_pension_employee": 0.045,
  "health_insurance_employee": 0.03545,
  "long_term_care_rate": 0.1295,
  "employment_insurance_employee": 0.009
}
```

---

## 테스트 커버리지 목표

| 모듈 | 목표 커버리지 |
|------|---------------|
| wage_calculator.py | 95% |
| tax_calculator.py | 95% |
| payroll_service.py | 90% |
| payslip_service.py | 90% |
| payroll API | 100% (Happy Path) |
| payslips API | 100% (Happy Path) |

---

## 변경 이력

| 날짜 | 변경 내용 | 이유 |
|------|-----------|------|
| 2026-03-02 | 초기 작성 | F-05 테스트 명세 |
