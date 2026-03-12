# F-04 근로계약서 자동 생성 — 테스트 명세

## 참조
- 설계서: docs/specs/F-04-contract/design.md
- 인수조건: docs/project/features.md #F-04
- API 컨벤션: docs/system/api-conventions.md

---

## 1. 단위 테스트

### 1.1 ContractService

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| `create_contract` | 정규직 계약서 생성 (정상) | employee_id, contract_type="regular", base_wage=2500000 | Contract 생성, status="draft" |
| `create_contract` | 계약직 계약서 생성 (end_date 포함) | contract_type="fixed_term", end_date="2026-12-31" | Contract 생성, end_date 저장 |
| `create_contract` | 최저임금 미달 (시급제) | wage_type="hourly", base_wage=9000 | MinimumWageError (E-5001) |
| `create_contract` | 최저임금 미달 (월급제) | wage_type="monthly", base_wage=1500000, work_hours_per_week=40 | MinimumWageError (E-5001) |
| `create_contract` | 주 52시간 초과 | work_hours_per_week=60 | WorkHoursExceededError (E-5002) |
| `create_contract` | 존재하지 않는 직원 | employee_id="invalid-uuid" | NotFoundError (E-4004) |
| `create_contract` | 다른 사업장 직원 | employee_id (다른 company) | ForbiddenError (E-2005) |
| `generate_content` | Claude API 정상 호출 | contract_id, language="ko" | sections 배열 반환 |
| `generate_content` | 다국어 생성 (영어) | language="en" | 영어로 된 sections 반환 |
| `generate_content` | 다국어 생성 (중국어) | language="zh" | 중국어로 된 sections 반환 |
| `generate_content` | 다국어 생성 (베트남어) | language="vi" | 베트남어로 된 sections 반환 |
| `generate_content` | draft가 아닌 계약서 | status="signed" | ValidationError |
| `create_docx` | Word 파일 생성 | contract_id | S3 URL 반환 |
| `create_pdf` | PDF 파일 생성 | contract_id | S3 URL 반환 |
| `update_contract` | draft 상태 수정 | contract_id, base_wage=3000000 | 수정 성공 |
| `update_contract` | signed 상태 수정 시도 | status="signed" | ValidationError |
| `get_expiring_contracts` | D-30 계약서 조회 | days=30 | 30일 내 만료 계약서 목록 |
| `get_expiring_contracts` | D-7 계약서 조회 | days=7 | 7일 내 만료 계약서 목록 |

### 1.2 WageValidator

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| `validate_minimum_wage` | 시급제 정상 (2026년) | hourly=10030 | True |
| `validate_minimum_wage` | 시급제 미달 (2026년) | hourly=9000 | MinimumWageError |
| `validate_minimum_wage` | 월급제 정상 변환 | monthly=2090000, hours=40 | True (시급 9,860원 이상) |
| `validate_minimum_wage` | 월급제 미달 변환 | monthly=1500000, hours=40 | MinimumWageError |
| `validate_work_hours` | 40시간 (정상) | 40 | (True, "ok") |
| `validate_work_hours` | 52시간 (경계) | 52 | (True, "ok") |
| `validate_work_hours` | 52시간 초과 | 53 | (False, "error") |
| `calculate_hourly_wage` | 월급 → 시급 변환 | monthly=2090000, hours=40 | Decimal("10048.08") |
| `calculate_hourly_wage` | 일급 → 시급 변환 | daily=80240 | Decimal("10030") |

### 1.3 DocumentService

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| `generate_docx` | 기본 계약서 생성 | contract with sections | .docx 파일 바이트 |
| `generate_docx` | 비밀유지 조항 포함 | nda_included=True | N 섹션 포함 |
| `generate_docx` | 경업금지 조항 포함 | non_compete_included=True | 경업금지 섹션 포함 |
| `generate_docx` | 수습기간 조항 포함 | probation_months=3 | 수습기간 섹션 포함 |
| `generate_pdf` | HTML → PDF 변환 | html_content | .pdf 파일 바이트 |
| `upload_to_s3` | S3 업로드 성공 | file_bytes, filename | S3 URL 반환 |
| `generate_presigned_url` | URL 생성 | s3_key | 24시간 유효 URL |

### 1.4 NotificationService

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| `send_expiry_notice` | D-30 알림 발송 | contract, days=30 | 알림 발송 성공, notice_30_sent=True |
| `send_expiry_notice` | D-7 알림 발송 | contract, days=7 | 알림 발송 성공, notice_7_sent=True |
| `send_expiry_notice` | 이미 발송된 알림 | notice_30_sent=True | 중복 발송 방지 |

### 1.5 Claude Prompt (contract_prompt.py)

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| `build_prompt` | 기본 프롬프트 생성 | contract_data | 시스템 프롬프트 + 컨텍스트 |
| `build_prompt` | 다국어 프롬프트 | language="en" | 영어 출력 지시 포함 |
| `build_prompt` | 특약 사항 포함 | additional_terms="재택근무" | 특약 섹션 지시 포함 |
| `parse_response` | 섹션 파싱 | Claude 응답 텍스트 | sections 배열 |

---

## 2. 통합 테스트

### 2.1 POST /api/v1/contracts

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /contracts | 정상 생성 (정규직) | employee_id, contract_type="regular", base_wage=2500000 | 201, {id, status="draft"} |
| POST /contracts | 정상 생성 (계약직) | contract_type="fixed_term", end_date="2026-12-31" | 201, end_date 포함 |
| POST /contracts | 정상 생성 (파트타임) | contract_type="part_time", work_hours=20 | 201 |
| POST /contracts | 정상 생성 (일용직) | contract_type="daily", wage_type="daily" | 201 |
| POST /contracts | 정상 생성 (수습) | contract_type="probation", probation_months=3 | 201, probation_months=3 |
| POST /contracts | 외국인 근로자 | nationality="chinese", language="zh" | 201 |
| POST /contracts | 최저임금 미달 | base_wage=1000000, work_hours=40 | 422, E-5001 |
| POST /contracts | 주 52시간 초과 | work_hours_per_week=60 | 422, E-5002 |
| POST /contracts | 인증 없음 | Authorization 헤더 없음 | 401, E-2001 |
| POST /contracts | 다른 사업장 직원 | employee_id (다른 company) | 403, E-2005 |
| POST /contracts | Rate Limit 초과 | 11회 연속 요청 | 429, E-2006 |

### 2.2 POST /api/v1/contracts/{id}/generate

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /contracts/{id}/generate | 정상 생성 | contract_id (draft) | 200, {sections[]} |
| POST /contracts/{id}/generate | 다국어 (영어) | language="en" | 200, 영어 sections |
| POST /contracts/{id}/generate | 다국어 (중국어) | language="zh" | 200, 중국어 sections |
| POST /contracts/{id}/generate | 다국어 (베트남어) | language="vi" | 200, 베트남어 sections |
| POST /contracts/{id}/generate | 존재하지 않는 계약서 | invalid_id | 404, E-5003 |
| POST /contracts/{id}/generate | draft가 아님 | status="signed" | 400, E-1001 |
| POST /contracts/{id}/generate | Claude API 타임아웃 | - | 502, E-6002 |

### 2.3 POST /api/v1/contracts/{id}/generate-docx

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /contracts/{id}/generate-docx | 정상 생성 | contract_id | 200, {download_url, expires_at} |
| POST /contracts/{id}/generate-docx | URL 24시간 유효 | - | expires_at = now + 24h |
| POST /contracts/{id}/generate-docx | S3 업로드 실패 | - | 502, E-8001 |
| POST /contracts/{id}/generate-docx | 생성된 본문 없음 | generated_content=NULL | 400, "먼저 본문을 생성하세요" |

### 2.4 POST /api/v1/contracts/{id}/generate-pdf

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /contracts/{id}/generate-pdf | 정상 생성 | contract_id | 200, {download_url, expires_at} |
| POST /contracts/{id}/generate-pdf | WeasyPrint 오류 | - | 500, E-9001 |

### 2.5 GET /api/v1/contracts

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| GET /contracts | 전체 목록 | - | 200, contracts[] |
| GET /contracts | 직원별 필터 | employee_id=xxx | 200, 해당 직원 계약서만 |
| GET /contracts | 상태별 필터 | status=draft | 200, draft만 |
| GET /contracts | 만료 예정 필터 | expiring_within_days=30 | 200, 30일 내 만료만 |
| GET /contracts | 페이지네이션 | limit=10, cursor=xxx | 200, pagination 포함 |

### 2.6 GET /api/v1/contracts/{id}

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| GET /contracts/{id} | 정상 조회 | contract_id | 200, 전체 계약서 정보 |
| GET /contracts/{id} | 생성된 본문 포함 | contract_id | 200, generated_content 포함 |
| GET /contracts/{id} | 존재하지 않음 | invalid_id | 404, E-5003 |
| GET /contracts/{id} | 다른 사업장 | contract_id (다른 company) | 403, E-2005 |

### 2.7 PATCH /api/v1/contracts/{id}

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| PATCH /contracts/{id} | draft 수정 | base_wage=3000000 | 200, 수정된 정보 |
| PATCH /contracts/{id} | signed 상태 수정 | status="signed" | 400, "draft 상태만 수정 가능" |
| PATCH /contracts/{id} | 최저임금 미달로 수정 | base_wage=1000000 | 422, E-5001 |

### 2.8 GET /api/v1/contracts/templates

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| GET /contracts/templates | 템플릿 목록 | - | 200, 6개 템플릿 (regular, fixed_term, part_time, daily, probation, foreign_worker) |

---

## 3. 경계 조건 / 에러 케이스

### 3.1 입력 검증

| 케이스 | 입력 | 예상 결과 |
|--------|------|-----------|
| employee_id 누락 | {} | 400, E-1003 |
| base_wage 음수 | base_wage=-1000000 | 400, E-1001 |
| work_hours 음수 | work_hours_per_week=-10 | 400, E-1001 |
| start_date > end_date | start_date="2026-12-31", end_date="2026-01-01" | 400, E-1001 |
| work_days 형식 오류 | work_days="monday" | 400, E-1001 |
| language 미지원 | language="ja" | 400, E-1001 |

### 3.2 비즈니스 로직

| 케이스 | 상황 | 예상 결과 |
|--------|------|-----------|
| 퇴직한 직원 계약서 생성 | employee.is_active=False | 400, "퇴직한 직원입니다" |
| 이미 계약서 존재 | 같은 기간 중복 | 409, "해당 기간에 이미 계약서가 있습니다" |
| Claude API 한도 초과 | Anthropic 할당량 초과 | 502, E-6002 |
| S3 용량 초과 | 버킷 용량 부족 | 502, E-8001 |

### 3.3 동시성

| 케이스 | 상황 | 예상 결과 |
|--------|------|-----------|
| 동시 생성 요청 | 같은 직원에 2개 계약서 동시 생성 | 하나만 성공, 하나는 409 |
| 동시 수정 요청 | 같은 계약서 동시 수정 | 마지막 요청 반영 (버전 관리) |

---

## 4. E2E 테스트 시나리오

### 4.1 정상 플로우: 계약서 생성 → 다운로드

```
1. 사용자 로그인
2. 사업장 선택
3. 직원 선택 (또는 신규 등록)
4. 계약서 생성 요청
   - 고용형태: 정규직
   - 근무지: 서울시 강남구
   - 근무시간: 09:00-18:00
   - 주 40시간
   - 월급: 2,500,000원
   - 수습기간: 3개월
   - 비밀유지: 포함
5. 계약서 본문 생성 (Claude API)
6. Word 파일 생성
7. PDF 파일 생성
8. 다운로드 링크 확인
9. 파일 다운로드 성공
```

### 4.2 경고 플로우: 최저임금 미달

```
1. 사용자 로그인
2. 계약서 생성 요청
   - 월급: 1,500,000원
   - 주 40시간
3. 422 응답 확인
   - error.code: E-5001
   - error.message: "최저임금 기준 미달입니다."
   - error.details.minimum_wage: 10030
   - error.details.current_hourly: 7200
4. 급여 수정 후 재요청
5. 정상 생성 확인
```

### 4.3 다국어 플로우: 외국인 근로자

```
1. 중국인 직원 등록 (nationality="chinese")
2. 계약서 생성 (language="zh")
3. Claude API로 중국어 본문 생성
4. Word/PDF 다운로드
5. 내용이 중국어로 작성됨 확인
```

### 4.4 알림 플로우: 만료 예정

```
1. 계약서 생성 (end_date = 오늘 + 30일)
2. 스케줄러 실행 (매일 09:00)
3. D-30 알림 발송 확인
4. 카카오 알림톡 또는 이메일 수신
5. expiry_notice_30_sent = True 확인
```

---

## 5. 성능 테스트

| 시나리오 | 조건 | 목표 |
|----------|------|------|
| 계약서 생성 API | 100 RPS | 응답 시간 < 500ms |
| Claude API 호출 | 단일 요청 | 응답 시간 < 5s |
| Word 생성 | 단일 요청 | 응답 시간 < 2s |
| PDF 생성 | 단일 요청 | 응답 시간 < 3s |
| 만료 알림 스케줄러 | 1000개 계약서 | 실행 시간 < 60s |

---

## 6. 품질 목표

### 6.1 노무사 검토 통과율

| 항목 | 목표 | 측정 방법 |
|------|------|----------|
| 법정 필수 기재사항 포함 | 100% | 자동화 테스트 |
| 문구 정확성 | 95% | 노무사 리뷰 |
| 형식 적합성 | 95% | 노무사 리뷰 |
| 전체 통과율 | 95% 이상 | 노무사 검토 |

### 6.2 테스트 커버리지

| 레이어 | 목표 |
|--------|------|
| Service | 90% |
| API | 100% (주요 엔드포인트) |
| Validator | 100% |
| Repository | 80% |

---

## 7. 테스트 데이터

### 7.1 샘플 직원

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "홍길동",
  "nationality": "korean",
  "employment_type": "regular",
  "hire_date": "2026-03-01",
  "department": "개발팀",
  "position": "사원"
}
```

### 7.2 샘플 계약서 요청

```json
{
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "contract_type": "regular",
  "start_date": "2026-03-02",
  "work_location": "서울시 강남구 테헤란로 123",
  "work_hours_per_week": 40,
  "work_start_time": "09:00",
  "work_end_time": "18:00",
  "break_minutes": 60,
  "work_days": "mon,tue,wed,thu,fri",
  "wage_type": "monthly",
  "base_wage": 2500000,
  "meal_allowance": 100000,
  "transport_allowance": 50000,
  "probation_months": 3,
  "nda_included": true,
  "non_compete_included": false,
  "language": "ko"
}
```

### 7.3 최저임금 데이터 (2026년)

```json
{
  "rate_type": "minimum_wage",
  "value": 10030,
  "effective_year": 2026,
  "effective_month": 1
}
```

---

## 8. 테스트 실행 명령

```bash
# 단위 테스트
cd backend
pytest tests/unit/test_contract_service.py -v
pytest tests/unit/test_wage_validator.py -v
pytest tests/unit/test_document_service.py -v

# 통합 테스트
pytest tests/integration/test_contract_api.py -v

# E2E 테스트
pytest tests/e2e/test_contract_flow.py -v

# 커버리지
pytest --cov=app/services/contract_service --cov-report=html
```

---

## 변경 이력

| 날짜 | 변경 내용 | 이유 |
|------|----------|------|
| 2026-03-02 | 초기 작성 | F-04 테스트 명세 |
