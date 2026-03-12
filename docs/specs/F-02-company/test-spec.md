# F-02 사업장 관리 — 테스트 명세

## 참조
- 설계서: docs/specs/F-02-company/design.md
- 인수조건: docs/project/features.md #F-02
- API 컨벤션: docs/system/api-conventions.md

---

## 1. 단위 테스트

### 1.1 사업자등록번호 검증 (schemas/company.py)

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| `CompanyCreate.business_number` | 유효한 형식 | `"123-45-67890"` | 검증 통과 |
| `CompanyCreate.business_number` | 하이픈 없음 | `"1234567890"` | `ValidationError` |
| `CompanyCreate.business_number` | 자릿수 부족 | `"123-45-6789"` | `ValidationError` |
| `CompanyCreate.business_number` | 자릿수 초과 | `"1234-45-67890"` | `ValidationError` |
| `CompanyCreate.business_number` | 문자 포함 | `"123-AB-67890"` | `ValidationError` |
| `CompanyCreate.business_number` | 빈 문자열 | `""` | `ValidationError` |
| `CompanyCreate.business_number` | 앞뒤 공백 | `" 123-45-67890 "` | `ValidationError` |

### 1.2 업종 검증 (schemas/company.py)

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| `CompanyCreate.industry_type` | 유효한 업종 (제조) | `"manufacturing"` | 검증 통과 |
| `CompanyCreate.industry_type` | 유효한 업종 (IT) | `"it"` | 검증 통과 |
| `CompanyCreate.industry_type` | 유효한 업종 (기타) | `"other"` | 검증 통과 |
| `CompanyCreate.industry_type` | 유효하지 않은 업종 | `"finance"` | `ValidationError` |
| `CompanyCreate.industry_type` | 대소문자 구분 | `"IT"` | `ValidationError` |
| `CompanyCreate.industry_type` | 빈 문자열 | `""` | `ValidationError` |

### 1.3 직원 수 검증 (schemas/company.py)

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| `CompanyCreate.employee_count` | 유효한 값 (0) | `0` | 검증 통과 |
| `CompanyCreate.employee_count` | 유효한 값 (9) | `9` | 검증 통과 |
| `CompanyCreate.employee_count` | 경계값 (10) | `10` | 검증 통과 |
| `CompanyCreate.employee_count` | 최대값 (1000) | `1000` | 검증 통과 |
| `CompanyCreate.employee_count` | 음수 | `-1` | `ValidationError` |
| `CompanyCreate.employee_count` | 최대값 초과 | `1001` | `ValidationError` |

### 1.4 work_rule_required 자동 계산 (models/company.py)

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| `Company.work_rule_required` | 직원 수 9인 | `employee_count=9` | `FALSE` |
| `Company.work_rule_required` | 직원 수 10인 | `employee_count=10` | `TRUE` |
| `Company.work_rule_required` | 직원 수 15인 | `employee_count=15` | `TRUE` |
| `Company.work_rule_required` | 직원 수 변경 9→10 | `9`에서 `10`으로 수정 | `TRUE`로 자동 변경 |
| `Company.work_rule_required` | 직원 수 변경 10→9 | `10`에서 `9`로 수정 | `FALSE`로 자동 변경 |

### 1.5 사업장 소유권 검증 (services/company_service.py)

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| `verify_company_ownership` | 소유자 일치 | `owner_id == user_id` | `Company` 반환 |
| `verify_company_ownership` | 소유자 불일치 | `owner_id != user_id` | `ForbiddenError` |
| `verify_company_ownership` | 삭제된 사업장 | `is_deleted=TRUE` | `NotFoundError` |
| `verify_company_ownership` | 존재하지 않는 ID | 잘못된 `company_id` | `NotFoundError` |

---

## 2. 통합 테스트

### 2.1 사업장 등록 API (POST /api/v1/companies)

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /companies | 정상 등록 | `{business_name, business_number, ...}` | 201, company 반환 |
| POST /companies | 중복 사업자등록번호 | 기존 등록된 번호 | 409, E-4002 |
| POST /companies | 잘못된 사업자등록번호 형식 | `"1234567890"` | 422, E-4003 |
| POST /companies | 필수 필드 누락 | `{business_name}` 만 | 400, E-1003 |
| POST /companies | 인증 없음 | Authorization 헤더 없음 | 401, E-2001 |
| POST /companies | Rate Limit 초과 | 11회 요청 | 429, E-2006 (11번째) |
| POST /companies | 10인 이상 등록 | `employee_count=15` | 201, work_rule_required=TRUE |

### 2.2 사업장 목록 API (GET /api/v1/companies)

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| GET /companies | 정상 조회 | 인증된 사용자 | 200, 사용자 사업장 목록 |
| GET /companies | 빈 목록 | 등록된 사업장 없음 | 200, 빈 배열 |
| GET /companies | 삭제된 사업장 제외 | 삭제된 사업장 존재 | 삭제되지 않은 사업장만 반환 |
| GET /companies | 페이지네이션 | `limit=10` | 최대 10개 반환 |
| GET /companies | 커서 기반 페이지네이션 | `cursor=xxx` | 다음 페이지 데이터 |
| GET /companies | 인증 없음 | Authorization 헤더 없음 | 401, E-2001 |

### 2.3 사업장 상세 API (GET /api/v1/companies/{id})

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| GET /companies/{id} | 정상 조회 | 본인 소유 사업장 ID | 200, company 상세 |
| GET /companies/{id} | 존재하지 않는 ID | 잘못된 UUID | 404, E-4001 |
| GET /companies/{id} | 타인 사업장 | 다른 사용자 소유 사업장 | 403, E-2005 |
| GET /companies/{id} | 삭제된 사업장 | `is_deleted=TRUE` | 404, E-4001 |
| GET /companies/{id} | 인증 없음 | Authorization 헤더 없음 | 401, E-2001 |

### 2.4 사업장 수정 API (PUT /api/v1/companies/{id})

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| PUT /companies/{id} | 정상 수정 | `{employee_count: 15}` | 200, 수정된 company |
| PUT /companies/{id} | 10인 미만→이상 전환 | `employee_count: 5→15` | 200, work_rule_required=TRUE |
| PUT /companies/{id} | 10인 이상→미만 전환 | `employee_count: 15→5` | 200, work_rule_required=FALSE |
| PUT /companies/{id} | 사업자등록번호 변경 시도 | `{business_number: "..."}` | 400, E-1001 (변경 불가) |
| PUT /companies/{id} | 타인 사업장 수정 | 다른 사용자 소유 | 403, E-2005 |
| PUT /companies/{id} | 존재하지 않는 ID | 잘못된 UUID | 404, E-4001 |
| PUT /companies/{id} | 인증 없음 | Authorization 헤더 없음 | 401, E-2001 |

### 2.5 사업장 삭제 API (DELETE /api/v1/companies/{id})

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| DELETE /companies/{id} | 정상 삭제 | `{confirmation: "사업장명"}` | 200, is_deleted=TRUE |
| DELETE /companies/{id} | 확인 문구 불일치 | `{confirmation: "잘못된문구"}` | 400, E-1001 |
| DELETE /companies/{id} | 타인 사업장 삭제 | 다른 사용자 소유 | 403, E-2005 |
| DELETE /companies/{id} | 이미 삭제된 사업장 | `is_deleted=TRUE` | 404, E-4001 |
| DELETE /companies/{id} | 존재하지 않는 ID | 잘못된 UUID | 404, E-4001 |
| DELETE /companies/{id} | 인증 없음 | Authorization 헤더 없음 | 401, E-2001 |

### 2.6 사업장 선택 API (POST /api/v1/companies/{id}/select)

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /companies/{id}/select | 정상 선택 | 본인 소유 사업장 ID | 200, 새 tokens 반환 |
| POST /companies/{id}/select | JWT company_id 변경 확인 | 토큰 디코딩 | `company_id`가 선택한 ID로 변경 |
| POST /companies/{id}/select | 타인 사업장 선택 | 다른 사용자 소유 | 403, E-2005 |
| POST /companies/{id}/select | 존재하지 않는 ID | 잘못된 UUID | 404, E-4001 |
| POST /companies/{id}/select | 삭제된 사업장 선택 | `is_deleted=TRUE` | 404, E-4001 |

---

## 3. E2E 테스트

### 3.1 사업장 등록 플로우

| 시나리오 | 단계 | 예상 결과 |
|----------|------|-----------|
| 신규 사업장 등록 | 1. 로그인 후 /company/new 접속 | 사업장 등록 폼 표시 |
| | 2. 사업장 정보 입력 | 입력값 실시간 검증 |
| | 3. 사업자등록번호 형식 오류 | 즉시 에러 메시지 표시 |
| | 4. 올바른 형식으로 수정 | 에러 해제 |
| | 5. 제출 | /dashboard 리다이렉트 |
| | 6. 대시보드 확인 | 등록한 사업장명 표시 |

### 3.2 10인 이상 사업장 등록 플로우

| 시나리오 | 단계 | 예상 결과 |
|----------|------|-----------|
| 취업규칙 의무 안내 | 1. 직원 수 15명 입력 | - |
| | 2. 등록 완료 | 취업규칙 작성 안내 배너 표시 |
| | 3. 배너 확인 | "10인 이상 사업장은 취업규칙 작성이 의무입니다" 메시지 |
| | 4. 취업규칙 작성 버튼 클릭 | /work-rules/new 리다이렉트 |

### 3.3 사업장 전환 플로우

| 시나리오 | 단계 | 예상 결과 |
|----------|------|-----------|
| 다중 사업장 전환 | 1. 2개 이상 사업장 등록 상태 | 사업장 선택 드롭다운 표시 |
| | 2. 드롭다운 클릭 | 등록된 사업장 목록 표시 |
| | 3. 다른 사업장 선택 | 토큰 재발급, UI 갱신 |
| | 4. 페이지 새로고침 | 선택한 사업장 컨텍스트 유지 |
| | 5. API 요청 | 선택한 사업장 데이터 조회 |

### 3.4 사업장 수정 플로우

| 시나리오 | 단계 | 예상 결과 |
|----------|------|-----------|
| 직원 수 증가로 취업규칙 의무화 | 1. 9인 사업장 상세 페이지 접속 | - |
| | 2. 직원 수를 15로 수정 | - |
| | 3. 저장 | 취업규칙 작성 안내 모달 표시 |
| | 4. work_rule_required 확인 | TRUE로 변경됨 |

### 3.5 사업장 삭제 플로우

| 시나리오 | 단계 | 예상 결과 |
|----------|------|-----------|
| 사업장 삭제 | 1. 사업장 상세 페이지 접속 | - |
| | 2. 삭제 버튼 클릭 | 확인 모달 표시 |
| | 3. 확인 문구 입력 요구 | 사업장명 입력 필드 표시 |
| | 4. 잘못된 문구 입력 | 삭제 버튼 비활성화 |
| | 5. 올바른 문구 입력 | 삭제 버튼 활성화 |
| | 6. 삭제 실행 | 30일 복구 가능 안내 토스트 |

---

## 4. 경계 조건 / 에러 케이스

### 4.1 입력값 경계

| 케이스 | 입력 | 예상 결과 |
|--------|------|-----------|
| 사업장명 최소 길이 | 1자 | 검증 통과 |
| 사업장명 최대 길도 | 200자 | 검증 통과 |
| 사업장명 초과 | 201자 | 400, E-1001 |
| 대표자명 최대 길이 | 100자 | 검증 통과 |
| 대표자명 초과 | 101자 | 400, E-1001 |
| 직원 수 0 | `employee_count=0` | 검증 통과, work_rule_required=FALSE |
| 직원 수 최대 | `employee_count=1000` | 검증 통과 |
| 주소 최대 길이 | TEXT 최대 | 검증 통과 |
| 우편번호 형식 | `"06123"` | 검증 통과 |
| 전화번호 형식 | `"02-1234-5678"` | 검증 통과 |

### 4.2 동시성 시나리오

| 케이스 | 시나리오 | 예상 결과 |
|--------|----------|-----------|
| 동시 사업장 등록 | 동일 사업자등록번호로 2회 동시 등록 | 1개만 성공, 1개 E-4002 |
| 동시 사업장 수정 | 동일 사업장 2회 동시 수정 | 모두 성공 (마지막 적용) |
| 동시 삭제 및 수정 | 삭제와 수정 동시 요청 | 하나만 성공 |

### 4.3 데이터 무결성

| 케이스 | 시나리오 | 예상 결과 |
|--------|----------|-----------|
| 삭제된 사업장 직원 조회 | 사업장 삭제 후 직원 목록 | 직원도 조회 안됨 (cascade) |
| 삭제된 사업장 계약서 조회 | 사업장 삭제 후 계약서 목록 | 계약서도 조회 안됨 (cascade) |
| 사업장 소유자 탈퇴 | 사용자 탈퇴 시 사업장 | 사업장도 삭제 (ondelete CASCADE) |

---

## 5. 성능 테스트

### 5.1 부하 테스트 기준

| 엔드포인트 | 목표 TPS | 평균 응답시간 | 최대 응답시간 |
|------------|----------|---------------|---------------|
| POST /companies | 50 | < 300ms | < 800ms |
| GET /companies | 200 | < 100ms | < 300ms |
| GET /companies/{id} | 200 | < 50ms | < 200ms |
| PUT /companies/{id} | 100 | < 200ms | < 500ms |
| DELETE /companies/{id} | 50 | < 200ms | < 500ms |
| POST /companies/{id}/select | 100 | < 100ms | < 300ms |

### 5.2 대량 데이터 테스트

| 시나리오 | 데이터 수 | 목표 |
|----------|-----------|------|
| 사용자당 다수 사업장 조회 | 50개 사업장 | < 200ms |
| 커서 기반 페이지네이션 | 1000개 사업장 | 20개씩 < 100ms |
| 사업장 목록 캐시 적중 | 캐시된 데이터 | < 20ms |

---

## 6. 보안 테스트

### 6.1 접근 제어 테스트

| 시나리오 | 입력 | 예상 결과 |
|----------|------|-----------|
| 타인 사업장 조회 | 다른 user_id의 company_id | 403, E-2005 |
| 타인 사업장 수정 | 다른 user_id의 company_id | 403, E-2005 |
| 타인 사업장 삭제 | 다른 user_id의 company_id | 403, E-2005 |
| JWT company_id 변조 | 변조된 company_id | 401, E-2003 (서명 검증 실패) |

### 6.2 입력 검증 테스트

| 시나리오 | 입력 | 예상 결과 |
|----------|------|-----------|
| SQL Injection 시도 | business_name에 `' OR '1'='1` | 400, E-1001 |
| XSS 시도 | business_name에 `<script>` | 저장 시 이스케이프 |
| JSON Injection | 중첩 JSON 구조 | 400, E-1001 |
| 대용량 요청 | 10MB 이상 body | 413 Payload Too Large |

### 6.3 Rate Limiting 검증

| 시나리오 | 요청 수 | 예상 결과 |
|----------|---------|-----------|
| POST /companies 제한 | 10회/시간 | 11회째 429 |
| PUT /companies/{id} 제한 | 30회/시간 | 31회째 429 |
| DELETE /companies/{id} 제한 | 5회/시간 | 6회째 429 |

---

## 7. 테스트 데이터

### 7.1 표준 테스트 사업장

```json
{
  "business_name": "테스트사업장",
  "business_number": "123-45-67890",
  "representative_name": "홍길동",
  "industry_type": "it",
  "employee_count": 5,
  "address": "서울특별시 강남구 테헤란로 123",
  "postal_code": "06123",
  "phone": "02-1234-5678"
}
```

### 7.2 10인 이상 사업장 (취업규칙 의무)

```json
{
  "business_name": "중견기업사업장",
  "business_number": "987-65-43210",
  "representative_name": "김대표",
  "industry_type": "manufacturing",
  "employee_count": 50,
  "address": "경기도 성남시 분당구 판교로 456",
  "postal_code": "13494",
  "phone": "031-123-4567"
}
```

### 7.3 업종별 테스트 데이터

```json
{
  "industries": [
    {"industry_type": "manufacturing", "name": "제조업체"},
    {"industry_type": "food_service", "name": "식당"},
    {"industry_type": "retail", "name": "편의점"},
    {"industry_type": "service", "name": "서비스업체"},
    {"industry_type": "it", "name": "IT회사"},
    {"industry_type": "construction", "name": "건설회사"},
    {"industry_type": "healthcare", "name": "병원"},
    {"industry_type": "other", "name": "기타업체"}
  ]
}
```

### 7.4 비정상 입력 데이터

```json
{
  "business_number_invalid": [
    "1234567890",
    "123-45-6789",
    "1234-56-78901",
    "ABC-DE-FGHIJ",
    "123-45-67890 ",
    " 123-45-67890"
  ],
  "industry_type_invalid": [
    "finance",
    "IT",
    "It",
    "",
    "unknown"
  ],
  "employee_count_invalid": [
    -1,
    1001,
    999999
  ]
}
```

---

## 8. 테스트 실행 환경

### 8.1 Backend 테스트

```bash
# 단위 테스트
pytest tests/unit/test_company_schema.py -v
pytest tests/unit/test_company_model.py -v
pytest tests/unit/test_company_service.py -v

# 통합 테스트
pytest tests/integration/test_company_api.py -v

# 커버리지
pytest --cov=app --cov-report=html tests/

# 특정 테스트만 실행
pytest tests/integration/test_company_api.py::test_create_company -v
```

### 8.2 Frontend 테스트

```bash
# 단위 테스트
npm run test -- company-store.test.ts
npm run test -- company-form.test.tsx

# E2E 테스트
npx playwright test tests/e2e/company.spec.ts

# 특정 시나리오
npx playwright test tests/e2e/company.spec.ts -g "사업장 등록"
```

### 8.3 E2E 테스트 시나리오 파일

```typescript
// tests/e2e/company.spec.ts 예시
import { test, expect } from '@playwright/test';

test.describe('사업장 관리', () => {
  test.beforeEach(async ({ page }) => {
    // 로그인
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'TestP@ss123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('사업장 등록 플로우', async ({ page }) => {
    await page.goto('/company/new');

    // 폼 입력
    await page.fill('[name="business_name"]', '테스트사업장');
    await page.fill('[name="business_number"]', '123-45-67890');
    await page.fill('[name="representative_name"]', '홍길동');
    await page.selectOption('[name="industry_type"]', 'it');
    await page.fill('[name="employee_count"]', '5');

    // 제출
    await page.click('button[type="submit"]');

    // 리다이렉트 확인
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('text=테스트사업장')).toBeVisible();
  });

  test('10인 이상 사업장 등록 시 취업규칙 안내', async ({ page }) => {
    await page.goto('/company/new');

    await page.fill('[name="business_name"]', '중견기업');
    await page.fill('[name="business_number"]', '987-65-43210');
    await page.fill('[name="representative_name"]', '김대표');
    await page.selectOption('[name="industry_type"]', 'manufacturing');
    await page.fill('[name="employee_count"]', '15');

    await page.click('button[type="submit"]');

    // 취업규칙 안내 배너 확인
    await expect(page.locator('text=취업규칙')).toBeVisible();
  });

  test('사업자등록번호 형식 검증', async ({ page }) => {
    await page.goto('/company/new');

    await page.fill('[name="business_number"]', '1234567890');
    await page.blur('[name="business_number"]');

    // 에러 메시지 확인
    await expect(page.locator('text=사업자등록번호 형식')).toBeVisible();
  });
});
```

---

## 9. 테스트 체크리스트

### 9.1 기능 테스트
- [ ] 사업장 정상 등록
- [ ] 사업자등록번호 중복 검사
- [ ] 사업자등록번호 형식 검증 (프론트/백엔드)
- [ ] 업종 선택 (8개 업종)
- [ ] 10인 이상 사업장 자동 감지
- [ ] 취업규칙 의무 안내 표시
- [ ] 사업장 정보 수정
- [ ] 직원 수 변경 시 work_rule_required 자동 재계산
- [ ] 사업장 Soft Delete
- [ ] 삭제 확인 문구 검증
- [ ] 사업장 선택 (컨텍스트 변경)
- [ ] JWT company_id 변경 확인
- [ ] 사업장별 데이터 격리

### 9.2 보안 테스트
- [ ] 타인 사업장 접근 차단
- [ ] SQL Injection 방어
- [ ] XSS 방어
- [ ] Rate Limiting 적용
- [ ] 인증 없는 요청 차단

### 9.3 성능 테스트
- [ ] 사업장 등록 < 300ms
- [ ] 사업장 목록 조회 < 100ms
- [ ] 사업장 상세 조회 < 50ms
- [ ] 커서 기반 페이지네이션 정상 동작

### 9.4 데이터 무결성
- [ ] Generated Column 자동 계산 확인
- [ ] Soft Delete 후 데이터 유지
- [ ] 삭제된 사업장 관련 데이터 격리

---

## 10. 인수조건 매핑

| 인수조건 | 테스트 케이스 | 상태 |
|----------|---------------|------|
| 사업장명, 사업자등록번호, 대표자명, 업종, 직원 수 입력 | POST /companies 정상 등록 | [ ] |
| 사업자등록번호 형식 검증 (xxx-xx-xxxxx) | 사업자등록번호 검증 테스트 | [ ] |
| 업종 선택 (8개) | 업종 검증 테스트 | [ ] |
| 10인 이상 사업장 자동 감지 → 취업규칙 의무 안내 | work_rule_required 자동 계산 | [ ] |
| 사업장 정보 수정 가능 | PUT /companies/{id} | [ ] |
| 사업장 삭제 (Soft Delete) | DELETE /companies/{id} | [ ] |
| 사업장별 데이터 격리 (company_id 기반) | 타인 사업장 접근 차단 | [ ] |
| company_id를 JWT payload에 포함 | 사업장 선택 API | [ ] |

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 이유 |
|------|------|-----------|------|
| 2026-03-02 | 1.0.0 | 초기 테스트 명세 작성 | F-02 기능 구현 |
