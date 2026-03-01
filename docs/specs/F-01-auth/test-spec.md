# F-01 사용자 인증 및 계정 관리 — 테스트 명세

## 참조
- 설계서: docs/specs/F-01-auth/design.md
- 인수조건: docs/project/features.md #F-01
- API 컨벤션: docs/system/api-conventions.md

---

## 1. 단위 테스트

### 1.1 비밀번호 해싱 (core/security.py)

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| `hash_password` | 일반 비밀번호 해싱 | `"SecureP@ss123"` | bcrypt 해시 문자열 (60자) |
| `hash_password` | 동일 비밀번호 다른 해시 | `"SecureP@ss123"` 두 번 호출 | 서로 다른 해시 (salt 차이) |
| `verify_password` | 올바른 비밀번호 검증 | `("SecureP@ss123", hashed)` | `True` |
| `verify_password` | 잘못된 비밀번호 검증 | `("WrongP@ss", hashed)` | `False` |
| `verify_password` | 빈 비밀번호 검증 | `("", hashed)` | `False` |

### 1.2 JWT 생성/검증 (core/security.py)

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| `create_access_token` | 정상 토큰 생성 | `user_id, company_id, plan, role` | JWT 문자열 반환 |
| `create_access_token` | 토큰 만료시간 확인 | 생성 후 1시간 | 만료됨 |
| `decode_token` | 유효한 토큰 디코딩 | 유효한 JWT | payload dict 반환 |
| `decode_token` | 만료된 토큰 디코딩 | 만료된 JWT | `ExpiredSignatureError` |
| `decode_token` | 변조된 토큰 디코딩 | 서명 변조 JWT | `InvalidSignatureError` |
| `decode_token` | 잘못된 형식 토큰 | `"invalid.token"` | `DecodeError` |

### 1.3 Rate Limiting (core/rate_limit.py)

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| `check_rate_limit` | 제한 내 요청 | 5회 중 3회 요청 | 통과 (예외 없음) |
| `check_rate_limit` | 제한 초과 요청 | 6회 요청 | `HTTPException(429)` |
| `check_rate_limit` | TTL 만료 후 재요청 | 1분 대기 후 재요청 | 카운터 리셋, 통과 |
| `check_rate_limit` | 동시 요청 처리 | 5회 동시 요청 | 모두 통과 또는 1개 초과 |

### 1.4 사용자 스키마 검증 (schemas/user.py)

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| `UserCreate.email` | 유효한 이메일 | `"user@example.com"` | 검증 통과 |
| `UserCreate.email` | 잘못된 이메일 형식 | `"invalid-email"` | `ValidationError` |
| `UserCreate.password` | 유효한 비밀번호 | `"SecureP@ss123"` | 검증 통과 |
| `UserCreate.password` | 8자 미만 | `"Short1!"` | `ValidationError` |
| `UserCreate.password` | 복잡성 부족 (숫자 없음) | `"SecurePass@"` | `ValidationError` |
| `UserCreate.password` | 복잡성 부족 (특수문자 없음) | `"SecurePass12"` | `ValidationError` |
| `UserCreate.phone` | 유효한 전화번호 | `"010-1234-5678"` | 검증 통과 |
| `UserCreate.phone` | 잘못된 전화번호 | `"01012345678"` | `ValidationError` |

### 1.5 OAuth State 검증 (services/auth_service.py)

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| `create_oauth_state` | state 생성 | user_ip | 32자 URL-safe 토큰 |
| `verify_oauth_state` | 유효한 state | 생성된 state, 동일 IP | `True` |
| `verify_oauth_state` | 만료된 state | 10분 경과 | `False` |
| `verify_oauth_state` | 다른 IP | 생성된 state, 다른 IP | `False` |
| `verify_oauth_state` | 존재하지 않는 state | 임의 문자열 | `False` |

---

## 2. 통합 테스트

### 2.1 회원가입 API (POST /api/v1/auth/register)

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /auth/register | 정상 회원가입 | `{email, password, name, phone}` | 201, user + tokens 반환 |
| POST /auth/register | 중복 이메일 | 기존 가입된 이메일 | 409, E-3001 |
| POST /auth/register | 잘못된 이메일 형식 | `"invalid"` | 400, E-1001 |
| POST /auth/register | 비밀번호 정책 위반 | `"simple"` | 400, E-1001 |
| POST /auth/register | 필수 필드 누락 | `{email}` 만 | 400, E-1003 |
| POST /auth/register | Rate Limit 초과 | 4회 요청 | 429, E-2006 (4번째) |

### 2.2 로그인 API (POST /api/v1/auth/login)

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /auth/login | 정상 로그인 | `{email, password}` | 200, user + tokens 반환 |
| POST /auth/login | 존재하지 않는 이메일 | `{email: "none@test.com", password}` | 404, E-3002 |
| POST /auth/login | 비밀번호 불일치 | `{email, password: "wrong"}` | 401, E-3003 |
| POST /auth/login | 비활성 계정 | `is_active=false` 계정 | 401, E-3004 |
| POST /auth/login | Rate Limit 초과 | 6회 실패 요청 | 429, E-2006 (6번째) |
| POST /auth/login | 로그인 성공 시 Rate Limit 리셋 | 5회 실패 후 성공 | 200, 카운터 리셋 |

### 2.3 토큰 갱신 API (POST /api/v1/auth/refresh)

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /auth/refresh | 정상 갱신 | 유효한 refresh_token | 200, 새 tokens 반환 |
| POST /auth/refresh | 만료된 refresh_token | 30일 경과 토큰 | 401, E-2002 |
| POST /auth/refresh | 잘못된 refresh_token | 임의 문자열 | 401, E-2004 |
| POST /auth/refresh | 재사용 감지 (토큰 탈취 시나리오) | 이전 refresh_token 재사용 | 401, E-2004, 현재 토큰 무효화 |
| POST /auth/refresh | Rotation 확인 | 갱신 후 이전 토큰 사용 | 401, E-2004 |
| POST /auth/refresh | 비활성 계정 | `is_active=false` | 401, E-3004 |

### 2.4 로그아웃 API (POST /api/v1/auth/logout)

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /auth/logout | 정상 로그아웃 | 유효한 access_token | 200, 토큰 무효화 |
| POST /auth/logout | 로그아웃된 토큰 재사용 | 블랙리스트 토큰 | 401, E-2003 |
| POST /auth/logout | 인증 없이 요청 | Authorization 헤더 없음 | 401, E-2001 |

### 2.5 카카오 OAuth (GET /api/v1/auth/kakao, /callback)

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| GET /auth/kakao | 정상 리다이렉트 | 요청 | 302, 카카오 인증 URL |
| GET /auth/kakao/callback | 신규 회원 가입 | 유효한 code, state | 302, /dashboard, 토큰 설정 |
| GET /auth/kakao/callback | 기존 회원 로그인 | 유효한 code, state | 302, /dashboard, 토큰 설정 |
| GET /auth/kakao/callback | state 불일치 | 잘못된 state | 302, /login?error=E-2001 |
| GET /auth/kakao/callback | 카카오 API 오류 | 잘못된 code | 302, /login?error=E-8001 |
| GET /auth/kakao/callback | 카카오 사용자 정보 없음 | email 미제공 동의 | 302, /login?error=E-1001 |

### 2.6 비밀번호 재설정 API

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /auth/password/reset | 정상 요청 | 존재하는 email | 200, 이메일 발송 메시지 |
| POST /auth/password/reset | 존재하지 않는 이메일 | 없는 email | 200, 동일 메시지 (보안) |
| POST /auth/password/reset | Rate Limit 초과 | 4회 요청 | 429, E-2006 |
| POST /auth/password/confirm | 정상 변경 | 유효한 token, new_password | 200, 변경 완료 |
| POST /auth/password/confirm | 만료된 토큰 | 1시간 경과 | 401, E-2002 |
| POST /auth/password/confirm | 정책 위반 비밀번호 | `"simple"` | 400, E-1001 |

### 2.7 사용자 정보 API (GET, PUT, DELETE /api/v1/users/me)

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| GET /users/me | 정상 조회 | 유효한 토큰 | 200, user 정보 반환 |
| GET /users/me | 인증 없음 | 토큰 없음 | 401, E-2001 |
| GET /users/me | 만료된 토큰 | 만료된 access_token | 401, E-2002 |
| PUT /users/me | 정상 수정 | `{name, phone}` | 200, 수정된 user 반환 |
| PUT /users/me | 이메일 변경 시도 | `{email: "new@test.com"}` | 400, E-1001 (이메일 변경 불가) |
| DELETE /users/me | 정상 탈퇴 | `{password, reason}` | 200, 탈퇴 완료 |
| DELETE /users/me | 비밀번호 불일치 | `{password: "wrong"}` | 401, E-3003 |
| DELETE /users/me | OAuth 계정 비밀번호 없이 | kakao 계정 | 200, 별도 검증 없이 탈퇴 |

---

## 3. E2E 테스트

### 3.1 회원가입 → 사업장 등록 플로우

| 시나리오 | 단계 | 예상 결과 |
|----------|------|-----------|
| 신규 사용자 온보딩 | 1. /register 접속 | 회원가입 폼 표시 |
| | 2. 유효한 정보 입력 후 제출 | /company/new 리다이렉트 |
| | 3. 사업장 정보 입력 후 제출 | /dashboard 리다이렉트 |
| | 4. 대시보드 확인 | 사용자 이름, 사업장명 표시 |

### 3.2 로그인 → 대시보드 플로우

| 시나리오 | 단계 | 예상 결과 |
|----------|------|-----------|
| 기존 회원 로그인 | 1. /login 접속 | 로그인 폼 표시 |
| | 2. 이메일/비밀번호 입력 후 제출 | /dashboard 리다이렉트 |
| | 3. 페이지 새로고침 | 로그인 상태 유지 |
| | 4. 브라우저 종료 후 재접속 | 로그인 상태 유지 (refresh token) |

### 3.3 토큰 만료 → 자동 갱신 플로우

| 시나리오 | 단계 | 예상 결과 |
|----------|------|-----------|
| Access Token 만료 자동 갱신 | 1. 로그인 후 1시간 대기 | Access Token 만료 |
| | 2. API 요청 (예: GET /users/me) | 401 응답 |
| | 3. 자동 refresh 요청 | 새 tokens 발급 |
| | 4. 원래 요청 재시도 | 정상 응답 |

### 3.4 카카오 OAuth 로그인 플로우

| 시나리오 | 단계 | 예상 결과 |
|----------|------|-----------|
| 카카오 신규 회원 | 1. /login 접속 | "카카오 로그인" 버튼 표시 |
| | 2. 버튼 클릭 | 카카오 인증 페이지 리다이렉트 |
| | 3. 카카오 로그인 및 동의 | /callback/kakao 리다이렉트 |
| | 4. 콜백 처리 | /company/new 리다이렉트 (신규) |
| 카카오 기존 회원 | 1~3 동일 | /dashboard 리다이렉트 (기존) |

### 3.5 로그아웃 플로우

| 시나리오 | 단계 | 예상 결과 |
|----------|------|-----------|
| 정상 로그아웃 | 1. 로그인 상태에서 로그아웃 클릭 | /login 리다이렉트 |
| | 2. 뒤로가기 시도 | /login 유지 (인증 필요) |
| | 3. 이전 토큰으로 API 요청 | 401 응답 (블랙리스트) |

### 3.6 Rate Limiting 검증

| 시나리오 | 단계 | 예상 결과 |
|----------|------|-----------|
| 로그인 Rate Limit | 1. 5회 연속 로그인 실패 | 5회까지 401 응답 |
| | 2. 6회째 시도 | 429 응답, 에러 메시지 표시 |
| | 3. 1분 대기 후 재시도 | 정상 응답 (카운터 리셋) |

---

## 4. 경계 조건 / 에러 케이스

### 4.1 입력값 경계

| 케이스 | 입력 | 예상 결과 |
|--------|------|-----------|
| 이메일 최대 길이 | 255자 이메일 | 검증 통과 |
| 이메일 초과 | 256자 이메일 | 400, E-1001 |
| 비밀번호 최소 길이 | 8자 | 검증 통과 |
| 비밀번호 미달 | 7자 | 400, E-1001 |
| 이름 최대 길이 | 100자 | 검증 통과 |
| 이름 초과 | 101자 | 400, E-1001 |
| 전화번호 형식 | `"010-1234-5678"` | 검증 통과 |
| 전화번호 하이픈 없음 | `"01012345678"` | 400, E-1001 |

### 4.2 동시성 시나리오

| 케이스 | 시나리오 | 예상 결과 |
|--------|----------|-----------|
| 동시 로그인 | 동일 계정 2개 기기에서 동시 로그인 | 모두 성공, 이전 refresh 무효화 |
| 동시 토큰 갱신 | 동일 refresh_token으로 2회 동시 갱신 | 1개만 성공, 나머지 E-2004 |
| 동시 비밀번호 변경 | 동시에 2회 변경 요청 | 모두 성공 (마지막 적용) |

### 4.3 보안 에지 케이스

| 케이스 | 시나리오 | 예상 결과 |
|--------|----------|-----------|
| SQL Injection 시도 | 이메일에 `' OR '1'='1` 포함 | 400, E-1001 (검증 실패) |
| XSS 시도 | 이름에 `<script>` 포함 | 저장 시 이스케이프, 반영 시 안전 |
| JWT 조작 | payload 변조 | 401, E-2003 (서명 검증 실패) |
| Refresh Token 탈취 | 공격자가 탈취한 토큰 사용 | 정상 사용자 갱신 시 무효화 |

---

## 5. 성능 테스트

### 5.1 부하 테스트 기준

| 엔드포인트 | 목표 TPS | 평균 응답시간 | 최대 응답시간 |
|------------|----------|---------------|---------------|
| POST /auth/login | 100 | < 200ms | < 500ms |
| POST /auth/register | 50 | < 300ms | < 800ms |
| POST /auth/refresh | 200 | < 100ms | < 300ms |
| GET /users/me | 500 | < 50ms | < 200ms |

### 5.2 동시 사용자 테스트

| 시나리오 | 사용자 수 | 목표 |
|----------|-----------|------|
| 동시 로그인 | 1,000 | 95% 요청 1초 내 응답 |
| 동시 토큰 갱신 | 5,000 | 99% 요청 500ms 내 응답 |
| Rate Limit 정확성 | 100 (동시) | 제한 정확히 적용 |

---

## 6. 보안 테스트

### 6.1 인증 바이패스 시도

| 시나리오 | 입력 | 예상 결과 |
|----------|------|-----------|
| 토큰 없이 보호된 API 접근 | Authorization 헤더 없음 | 401, E-2001 |
| 변조된 토큰으로 접근 | 서명 변조 JWT | 401, E-2003 |
| 만료된 토큰으로 접근 | 1시간 경과 토큰 | 401, E-2002 |
| 블랙리스트 토큰으로 접근 | 로그아웃된 토큰 | 401, E-2003 |

### 6.2 권한 상승 시도

| 시나리오 | 입력 | 예상 결과 |
|----------|------|-----------|
| 일반 사용자가 admin API 접근 | owner 권한으로 /admin 요청 | 403, E-2005 |
| 타 사용자 정보 조회 | 다른 user_id로 /users/{id} | 403, E-2005 |
| 플랜 권한 상승 시도 | JWT payload 변조 | 401, E-2003 |

### 6.3 무차별 대입 공격 방어

| 시나리오 | 입력 | 예상 결과 |
|----------|------|-----------|
| 비밀번호 무차별 대입 | 100회 연속 로그인 시도 | 5회 후 429 응답 |
| 이메일 열거 방지 | 존재/미존재 이메일 비교 | 동일한 응답 시간, 메시지 |
| 계정 잠금 없음 | 반복 실패 | Rate Limit만 적용, 잠금 없음 |

---

## 7. 테스트 데이터

### 7.1 표준 테스트 사용자

```json
{
  "email": "test@example.com",
  "password": "TestP@ss123",
  "name": "테스트사용자",
  "phone": "010-1234-5678"
}
```

### 7.2 경계값 테스트 데이터

```json
{
  "email_max_length": "a@b.c... (255자)",
  "password_min": "Abc123!@",
  "password_max": "A1!... (128자)",
  "name_max": "가나다라... (100자)",
  "phone_valid": "010-1234-5678"
}
```

### 7.3 비정상 입력 데이터

```json
{
  "email_invalid": ["invalid", "a@b", "@example.com", "a b@test.com"],
  "password_weak": ["12345678", "abcdefgh", "ABCDEFGH", "abc12345"],
  "phone_invalid": ["01012345678", "010-123-4567", "011-1234-5678"]
}
```

---

## 8. 테스트 실행 환경

### 8.1 Backend 테스트

```bash
# 단위 테스트
pytest tests/unit/test_security.py -v
pytest tests/unit/test_rate_limit.py -v
pytest tests/unit/test_schemas.py -v

# 통합 테스트
pytest tests/integration/test_auth_api.py -v
pytest tests/integration/test_users_api.py -v

# 커버리지
pytest --cov=app --cov-report=html
```

### 8.2 Frontend 테스트

```bash
# 단위 테스트
npm run test -- auth-store.test.ts
npm run test -- login-form.test.tsx

# E2E 테스트
npx playwright test tests/e2e/auth.spec.ts
```

### 8.3 E2E 테스트 시나리오 파일

```typescript
// tests/e2e/auth.spec.ts 예시
test('회원가입 플로우', async ({ page }) => {
  await page.goto('/register');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'TestP@ss123');
  await page.fill('[name="name"]', '테스트사용자');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/company/new');
});
```

---

## 9. 테스트 체크리스트

### 9.1 기능 테스트
- [ ] 이메일/비밀번호 회원가입 성공
- [ ] 중복 이메일 회원가입 실패
- [ ] 로그인 성공
- [ ] 잘못된 비밀번호 로그인 실패
- [ ] 카카오 OAuth 로그인 성공
- [ ] Access Token 만료 후 자동 갱신
- [ ] Refresh Token Rotation 동작
- [ ] 로그아웃 후 토큰 무효화
- [ ] 비밀번호 재설정 이메일 발송
- [ ] 비밀번호 재설정 완료

### 9.2 보안 테스트
- [ ] Rate Limiting 5회/분 동작
- [ ] bcrypt 해싱 rounds=12 적용
- [ ] JWT 서명 검증
- [ ] 블랙리스트 토큰 차단
- [ ] OAuth state CSRF 방지
- [ ] SQL Injection 방어
- [ ] XSS 방어

### 9.3 성능 테스트
- [ ] 로그인 API < 200ms
- [ ] 토큰 갱신 API < 100ms
- [ ] 동시 1,000 사용자 로그인 처리

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 이유 |
|------|------|-----------|------|
| 2026-03-01 | 1.0.0 | 초기 테스트 명세 작성 | F-01 기능 구현 |
