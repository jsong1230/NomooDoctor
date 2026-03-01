# API 컨벤션

## 참조
- 시스템 설계: docs/system/system-design.md
- 기능 명세: docs/project/features.md

---

## 1. API 응답 포맷

### 1.1 성공 응답 구조

모든 API는 일관된 응답 구조를 사용합니다.

```typescript
interface ApiResponse<T> {
  success: true;
  data: T;
  message?: string;  // 선택적 성공 메시지
}
```

**예시: 단일 리소스 조회**

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "홍길동",
    "email": "hong@example.com"
  }
}
```

**예시: 리스트 조회**

```json
{
  "success": true,
  "data": [
    { "id": "uuid-1", "name": "직원1" },
    { "id": "uuid-2", "name": "직원2" }
  ]
}
```

### 1.2 에러 응답 구조

```typescript
interface ApiErrorResponse {
  success: false;
  error: {
    code: string;        // 커스텀 에러 코드 (E-XXXX)
    message: string;     // 사용자 친화적 메시지
    details?: unknown;   // 선택적 상세 정보 (검증 오류 등)
  };
  requestId: string;     // 요청 추적용 UUID
}
```

**예시: 검증 오류**

```json
{
  "success": false,
  "error": {
    "code": "E-1001",
    "message": "입력값이 올바르지 않습니다.",
    "details": [
      { "field": "email", "message": "유효한 이메일 형식이 아닙니다." },
      { "field": "password", "message": "비밀번호는 8자 이상이어야 합니다." }
    ]
  },
  "requestId": "req-550e8400-e29b-41d4-a716"
}
```

**예시: 비즈니스 로직 오류**

```json
{
  "success": false,
  "error": {
    "code": "E-4001",
    "message": "최저임금 기준 미달입니다. 시급을 확인해주세요."
  },
  "requestId": "req-550e8400-e29b-41d4-a716"
}
```

### 1.3 페이지네이션 응답

리스트 조회 시 커서 기반 페이지네이션을 사용합니다.

```typescript
interface PaginatedResponse<T> {
  success: true;
  data: T[];
  pagination: {
    cursor: string | null;   // 다음 페이지 요청용 커서
    hasNext: boolean;        // 다음 페이지 존재 여부
    limit: number;           // 요청한 페이지 크기
    totalCount?: number;     // 전체 개수 (선택적)
  };
}
```

**예시**

```json
{
  "success": true,
  "data": [
    { "id": "uuid-1", "name": "직원1" },
    { "id": "uuid-2", "name": "직원2" }
  ],
  "pagination": {
    "cursor": "eyJpZCI6InV1aWQtMiJ9",
    "hasNext": true,
    "limit": 20,
    "totalCount": 45
  }
}
```

**요청 파라미터**

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `limit` | int | 20 | 페이지 크기 (최대 100) |
| `cursor` | string | null | 이전 응답의 cursor 값 |

---

## 2. 인증 패턴

### 2.1 JWT 구조

**Access Token (1시간 유효)**

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "company_id": "660e8400-e29b-41d4-a716-446655440001",
  "plan": "standard",
  "role": "owner",
  "exp": 1700000000,
  "iat": 1699996400,
  "jti": "550e8400-e29b-41d4-a716-446655440002"
}
```

**JWT Payload 필드**

| 필드 | 타입 | 설명 |
|------|------|------|
| `sub` | string (UUID) | 사용자 고유 ID |
| `company_id` | string (UUID) | 현재 선택된 사업장 ID |
| `plan` | enum | 구독 플랜 (starter/basic/standard/premium) |
| `role` | enum | 사용자 역할 (owner/admin/labor_attorney) |
| `exp` | int | 만료 시간 (Unix timestamp) |
| `iat` | int | 발급 시간 (Unix timestamp) |
| `jti` | string (UUID) | 토큰 고유 ID (블랙리스트 관리용) |

**Refresh Token (30일 유효)**

- Redis에 저장: `refresh:{user_id}` → 토큰 값
- Refresh Token Rotation 적용 (재사용 방지)

### 2.2 Authorization 헤더 형식

```
Authorization: Bearer <access_token>
```

**요청 예시**

```http
GET /api/v1/employees HTTP/1.1
Host: api.nomoodoc.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### 2.3 토큰 갱신 플로우

```
┌─────────┐                    ┌─────────┐                    ┌───────┐
│ Client  │                    │ Backend │                    │ Redis │
└────┬────┘                    └────┬────┘                    └───┬───┘
     │                              │                             │
     │ POST /auth/refresh           │                             │
     │ { refresh_token }            │                             │
     │─────────────────────────────>│                             │
     │                              │  GET refresh:{user_id}      │
     │                              │────────────────────────────>│
     │                              │                             │
     │                              │  토큰 값 일치 확인           │
     │                              │<────────────────────────────│
     │                              │                             │
     │                              │  DEL refresh:{user_id}      │
     │                              │────────────────────────────>│
     │                              │                             │
     │                              │  SET refresh:{user_id}      │
     │                              │  (새 리프레시 토큰)          │
     │                              │────────────────────────────>│
     │                              │                             │
     │  { access_token,             │                             │
     │    refresh_token }           │                             │
     │<─────────────────────────────│                             │
     │                              │                             │
```

**갱신 API**

```http
POST /api/v1/auth/refresh HTTP/1.1
Content-Type: application/json

{
  "refresh_token": "rt_550e8400e29b41d4a716..."
}
```

**응답**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "rt_660e8400e29b41d4...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

### 2.4 로그아웃 (토큰 무효화)

```
POST /api/v1/auth/logout
```

- Access Token의 `jti`를 Redis 블랙리스트에 추가
- Refresh Token 삭제

---

## 3. API 버전 체계

### 3.1 URL 버전 관리

모든 API는 URL 경로에 버전을 포함합니다.

```
/api/v1/{resource}
/api/v2/{resource}  (향후)
```

### 3.2 하위 호환성 정책

| 변경 유형 | 호환성 | 버전 업 필요 |
|-----------|--------|--------------|
| 새 엔드포인트 추가 | 호환 | 아니오 |
| 새 응답 필드 추가 | 호환 | 아니오 |
| 선택적 요청 필드 추가 | 호환 | 아니오 |
| 필수 요청 필드 추가 | 비호환 | 예 |
| 응답 필드 삭제/변경 | 비호환 | 예 |
| 엔드포인트 삭제 | 비호환 | 예 |
| 에러 코드 변경 | 비호환 | 예 |

**버전 업 절차**

1. 새 버전 API 추가 (`/api/v2/...`)
2. 최소 6개월간 두 버전 병행 운영
3. Deprecated 응답 헤더로 마이그레이션 안내
4. v1 종료 3개월 전 사용자 알림

---

## 4. 에러 코드 체계

### 4.1 HTTP 상태 코드 사용 규칙

| 상태 코드 | 사용 상황 |
|-----------|-----------|
| `200 OK` | 요청 성공 (GET, PUT, PATCH) |
| `201 Created` | 리소스 생성 성공 (POST) |
| `204 No Content` | 성공 (응답 본문 없음, DELETE) |
| `400 Bad Request` | 요청 형식 오류, 검증 실패 |
| `401 Unauthorized` | 인증 필요, 토큰 만료 |
| `403 Forbidden` | 권한 없음 |
| `404 Not Found` | 리소스 없음 |
| `409 Conflict` | 리소스 충돌 (중복 등) |
| `422 Unprocessable Entity` | 비즈니스 로직 검증 실패 |
| `429 Too Many Requests` | Rate Limit 초과 |
| `500 Internal Server Error` | 서버 오류 |
| `502 Bad Gateway` | 외부 서비스 오류 |
| `503 Service Unavailable` | 서비스 점검 |

### 4.2 커스텀 에러 코드 (E-XXXX)

| 코드 범위 | 카테고리 |
|-----------|----------|
| `E-1xxx` | 공통 / 검증 오류 |
| `E-2xxx` | 인증 / 인가 오류 |
| `E-3xxx` | 사용자 / 계정 오류 |
| `E-4xxx` | 사업장 / 직원 오류 |
| `E-5xxx` | 근로계약서 / 급여 오류 |
| `E-6xxx` | AI 챗봇 오류 |
| `E-7xxx` | 결제 / 구독 오류 |
| `E-8xxx` | 외부 서비스 오류 |
| `E-9xxx` | 서버 내부 오류 |

**상세 에러 코드**

| 코드 | HTTP | 메시지 | 설명 |
|------|------|--------|------|
| `E-1001` | 400 | 입력값이 올바르지 않습니다. | 요청 검증 실패 |
| `E-1002` | 400 | JSON 파싱 오류입니다. | 잘못된 JSON 형식 |
| `E-1003` | 400 | 필수 필드가 누락되었습니다. | Required 필드 없음 |
| `E-2001` | 401 | 인증이 필요합니다. | 토큰 없음 |
| `E-2002` | 401 | 토큰이 만료되었습니다. | Access Token 만료 |
| `E-2003` | 401 | 유효하지 않은 토큰입니다. | 토큰 서명 오류 등 |
| `E-2004` | 401 | 리프레시 토큰이 유효하지 않습니다. | 재사용 감지 등 |
| `E-2005` | 403 | 접근 권한이 없습니다. | 권한 부족 |
| `E-2006` | 429 | 요청 횟수를 초과했습니다. | Rate Limit |
| `E-3001` | 409 | 이미 등록된 이메일입니다. | 이메일 중복 |
| `E-3002` | 404 | 사용자를 찾을 수 없습니다. | 사용자 없음 |
| `E-3003` | 401 | 비밀번호가 일치하지 않습니다. | 로그인 실패 |
| `E-3004` | 401 | 비활성화된 계정입니다. | 계정 정지 |
| `E-4001` | 404 | 사업장을 찾을 수 없습니다. | 사업장 없음 |
| `E-4002` | 409 | 이미 등록된 사업자등록번호입니다. | 사업장 중복 |
| `E-4003` | 422 | 사업자등록번호 형식이 올바르지 않습니다. | 형식 오류 |
| `E-4004` | 404 | 직원을 찾을 수 없습니다. | 직원 없음 |
| `E-4005` | 400 | 퇴직 처리된 직원입니다. | 이미 퇴직 |
| `E-5001` | 422 | 최저임금 기준 미달입니다. | 시급 검증 실패 |
| `E-5002` | 422 | 주 52시간을 초과합니다. | 근로시간 초과 |
| `E-5003` | 404 | 근로계약서를 찾을 수 없습니다. | 계약서 없음 |
| `E-5004` | 400 | 급여 계산 오류입니다. | 계산 로직 오류 |
| `E-6001` | 429 | AI 상담 요청 횟수를 초과했습니다. | 플랜 제한 |
| `E-6002` | 502 | AI 서비스 일시 오류입니다. | Claude API 오류 |
| `E-6003` | 500 | 답변 생성 중 오류가 발생했습니다. | 스트리밍 오류 |
| `E-7001` | 402 | 결제가 필요합니다. | 구독 만료 |
| `E-7002` | 402 | 결제에 실패했습니다. | 결제 오류 |
| `E-7003` | 404 | 구독 정보를 찾을 수 없습니다. | 구독 없음 |
| `E-7004` | 409 | 이미 구독 중인 플랜입니다. | 중복 구독 |
| `E-8001` | 502 | 카카오 알림톡 발송 실패입니다. | 카카오 API 오류 |
| `E-8002` | 502 | 이메일 발송 실패입니다. | SendGrid 오류 |
| `E-8003` | 502 | 전자서명 요청 실패입니다. | 모두싸인 오류 |
| `E-9001` | 500 | 내부 서버 오류입니다. | 예상치 못한 오류 |
| `E-9002` | 503 | 서비스 점검 중입니다. | 점검 모드 |

### 4.3 에러 메시지 형식

**원칙**
- 사용자 친화적 메시지 (기술 용어 지양)
- 구체적인 해결 방법 제시
- 다국어 지원 준비 (한국어 기본)

**예시**

```json
{
  "success": false,
  "error": {
    "code": "E-5001",
    "message": "최저임금 기준 미달입니다. 2024년 최저임금은 시급 9,860원입니다."
  },
  "requestId": "req-..."
}
```

---

## 5. 공통 헤더

### 5.1 필수 헤더

| 헤더 | 값 | 설명 |
|------|-----|------|
| `Content-Type` | `application/json` | 요청/응답 본문 형식 |
| `Authorization` | `Bearer {token}` | 인증 토큰 (인증 필요 API) |

### 5.2 선택 헤더

| 헤더 | 값 | 설명 |
|------|-----|------|
| `Accept-Language` | `ko`, `en` | 응답 언어 (기본: ko) |
| `X-Request-ID` | UUID | 요청 추적용 (미제공 시 서버 생성) |
| `X-Client-Version` | `1.0.0` | 클라이언트 버전 |
| `X-Device-ID` | UUID | 디바이스 식별자 |

### 5.3 응답 헤더

| 헤더 | 설명 |
|------|------|
| `X-Request-ID` | 요청 추적용 UUID |
| `X-RateLimit-Limit` | Rate Limit 한도 |
| `X-RateLimit-Remaining` | 남은 요청 횟수 |
| `X-RateLimit-Reset` | Rate Limit 초기화 시간 (Unix timestamp) |
| `X-API-Version` | API 버전 (예: 1.0.0) |
| `Deprecated` | (선택) 폐지 예정 API 표시 |

---

## 6. Rate Limiting

### 6.1 엔드포인트별 제한

| 엔드포인트 | 제한 | 기준 | 플랜별 차등 |
|------------|------|------|-------------|
| `POST /auth/login` | 5회/분 | IP | 없음 |
| `POST /auth/register` | 3회/시간 | IP | 없음 |
| `POST /auth/refresh` | 30회/시간 | User ID | 없음 |
| `POST /chat/sessions/{id}/messages` | 30회/시간 | User ID | 플랜별 |
| `POST /contracts/generate` | 10회/시간 | User ID | 플랜별 |
| `POST /payslips/send` | 50회/일 | User ID | 플랜별 |
| 일반 API | 100회/분 | User ID | 없음 |

**플랜별 차등 적용**

| 플랜 | 채팅/시간 | 계약서/시간 | 명세서 발송/일 |
|------|-----------|-------------|----------------|
| Starter | 10 | 2 | 0 |
| Basic | 무제한 | 무제한 | 10 |
| Standard | 무제한 | 무제한 | 100 |
| Premium | 무제한 | 무제한 | 무제한 |

### 6.2 429 응답 처리

**응답 예시**

```json
{
  "success": false,
  "error": {
    "code": "E-2006",
    "message": "요청 횟수를 초과했습니다. 1분 후 다시 시도해주세요.",
    "details": {
      "retry_after": 60,
      "limit": 5,
      "remaining": 0
    }
  },
  "requestId": "req-..."
}
```

**응답 헤더**

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1700000060
Retry-After: 60
```

---

## 7. API 엔드포인트 목록

### 7.1 기능별 엔드포인트 개요

#### 인증 (Auth)

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| POST | `/auth/register` | 회원가입 | 불필요 |
| POST | `/auth/login` | 로그인 | 불필요 |
| POST | `/auth/logout` | 로그아웃 | 필요 |
| POST | `/auth/refresh` | 토큰 갱신 | 불필요 |
| GET | `/auth/kakao` | 카카오 OAuth 시작 | 불필요 |
| GET | `/auth/kakao/callback` | 카카오 OAuth 콜백 | 불필요 |
| POST | `/auth/password/reset` | 비밀번호 재설정 요청 | 불필요 |
| POST | `/auth/password/confirm` | 비밀번호 재설정 확인 | 불필요 |

#### 사용자 (Users)

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| GET | `/users/me` | 내 정보 조회 | 필요 |
| PUT | `/users/me` | 내 정보 수정 | 필요 |
| DELETE | `/users/me` | 계정 탈퇴 | 필요 |

#### 사업장 (Companies)

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| GET | `/companies` | 사업장 목록 | 필요 |
| POST | `/companies` | 사업장 등록 | 필요 |
| GET | `/companies/{id}` | 사업장 상세 | 필요 |
| PUT | `/companies/{id}` | 사업장 수정 | 필요 |
| DELETE | `/companies/{id}` | 사업장 삭제 | 필요 |
| POST | `/companies/{id}/select` | 현재 사업장 선택 | 필요 |

#### 직원 (Employees)

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| GET | `/employees` | 직원 목록 | 필요 |
| POST | `/employees` | 직원 등록 | 필요 |
| GET | `/employees/{id}` | 직원 상세 | 필요 |
| PUT | `/employees/{id}` | 직원 수정 | 필요 |
| DELETE | `/employees/{id}` | 직원 삭제 | 필요 |
| POST | `/employees/{id}/resign` | 퇴직 처리 | 필요 |
| POST | `/employees/import` | 엑셀 일괄 등록 | 필요 |

#### 근로계약서 (Contracts)

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| GET | `/contracts` | 계약서 목록 | 필요 |
| POST | `/contracts` | 계약서 생성 | 필요 |
| GET | `/contracts/{id}` | 계약서 상세 | 필요 |
| PUT | `/contracts/{id}` | 계약서 수정 | 필요 |
| DELETE | `/contracts/{id}` | 계약서 삭제 | 필요 |
| POST | `/contracts/{id}/generate-docx` | Word 생성 | 필요 |
| POST | `/contracts/{id}/generate-pdf` | PDF 생성 | 필요 |
| GET | `/contracts/{id}/download/{type}` | 파일 다운로드 | 필요 |
| GET | `/contracts/templates` | 템플릿 목록 | 필요 |

#### 급여 (Payroll)

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| POST | `/payroll/calculate` | 급여 계산 | 필요 |
| GET | `/payslips` | 급여명세서 목록 | 필요 |
| POST | `/payslips` | 급여명세서 생성 | 필요 |
| GET | `/payslips/{id}` | 급여명세서 상세 | 필요 |
| POST | `/payslips/{id}/send` | 명세서 발송 | 필요 |
| GET | `/payslips/{id}/download` | PDF 다운로드 | 필요 |
| GET | `/work-records` | 근무 기록 목록 | 필요 |
| POST | `/work-records` | 근무 기록 등록 | 필요 |
| POST | `/work-records/import` | 엑셀 일괄 등록 | 필요 |

#### AI 챗봇 (Chat)

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| GET | `/chat/sessions` | 세션 목록 | 필요 |
| POST | `/chat/sessions` | 새 세션 생성 | 필요 |
| GET | `/chat/sessions/{id}` | 세션 상세 + 메시지 | 필요 |
| DELETE | `/chat/sessions/{id}` | 세션 삭제 | 필요 |
| POST | `/chat/sessions/{id}/messages` | 메시지 전송 (SSE) | 필요 |
| GET | `/chat/sessions/{id}/stream` | 스트리밍 연결 | 필요 |
| GET | `/chat/faq` | 자주 묻는 질문 | 필요 |

#### 취업규칙 (Work Rules)

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| GET | `/work-rules` | 취업규칙 목록 | 필요 |
| POST | `/work-rules` | 취업규칙 생성 | 필요 |
| GET | `/work-rules/{id}` | 취업규칙 상세 | 필요 |
| PUT | `/work-rules/{id}` | 취업규칙 수정 | 필요 |
| DELETE | `/work-rules/{id}` | 취업규칙 삭제 | 필요 |
| POST | `/work-rules/{id}/generate` | AI 초안 생성 | 필요 |
| GET | `/work-rules/{id}/download/{type}` | 파일 다운로드 | 필요 |
| GET | `/work-rules/templates` | 업종별 템플릿 | 필요 |

#### 퇴직금/해고 (Retirement)

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| POST | `/retirement/calculate` | 퇴직금 계산 | 필요 |
| POST | `/retirement/severance` | 퇴직금 저장 | 필요 |
| POST | `/retirement/termination-guide` | 해고 절차 가이드 | 필요 |
| GET | `/retirement/severance/{id}` | 퇴직금 상세 | 필요 |

#### 노무사 (Attorneys)

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| GET | `/attorneys` | 노무사 목록 | 필요 |
| GET | `/attorneys/{id}` | 노무사 상세 | 필요 |
| POST | `/attorney-cases` | 상담 케이스 생성 | 필요 |
| GET | `/attorney-cases/{id}` | 케이스 상세 | 필요 |
| POST | `/attorney-cases/{id}/book` | 상담 예약 | 필요 |
| POST | `/attorney-cases/{id}/review` | 리뷰 작성 | 필요 |

#### 구독 (Subscriptions)

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| GET | `/subscriptions/plans` | 플랜 목록 | 필요 |
| GET | `/subscriptions/me` | 내 구독 정보 | 필요 |
| POST | `/subscriptions` | 구독 시작 | 필요 |
| PUT | `/subscriptions` | 플랜 변경 | 필요 |
| DELETE | `/subscriptions` | 구독 해지 | 필요 |
| POST | `/subscriptions/billing-key` | 빌링키 등록 | 필요 |
| GET | `/subscriptions/history` | 결제 내역 | 필요 |

#### 웹훅 (Webhooks)

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| POST | `/webhooks/toss` | 토스페이먼츠 웹훅 | 서명 검증 |
| POST | `/webhooks/kakao` | 카카오 웹훅 | 서명 검증 |
| POST | `/webhooks/modusign` | 모두싸인 웹훅 | 서명 검증 |

### 7.2 RESTful 네이밍 규칙

**원칙**

1. **명사 사용**: 동사 대신 명사로 리소스 표현
   - O: `/employees`
   - X: `/getEmployees`

2. **복수형 사용**: 컬렉션은 복수형
   - O: `/employees/{id}`
   - X: `/employee/{id}`

3. **계층 구조**: 관계를 URL에 표현
   - `/companies/{id}/employees`
   - `/employees/{id}/contracts`

4. **동작은 서브리소스로**: 복잡한 동작은 서브리소스 활용
   - `POST /employees/{id}/resign`
   - `POST /contracts/{id}/generate-pdf`

5. **필터링은 쿼리 파라미터**: 검색, 필터링
   - `/employees?status=active&department=개발`
   - `/contracts?from_date=2024-01-01&to_date=2024-12-31`

6. **버전은 URL에**: 헤더가 아닌 URL로 버전 관리
   - `/api/v1/employees`
   - `/api/v2/employees`

**URL 패턴**

```
/api/v1/{resource}
/api/v1/{resource}/{id}
/api/v1/{resource}/{id}/{sub-resource}
/api/v1/{resource}/{id}/{sub-resource}/{sub-id}
```

**쿼리 파라미터 표준**

| 파라미터 | 용도 | 예시 |
|----------|------|------|
| `limit` | 페이지 크기 | `?limit=20` |
| `cursor` | 페이지네이션 커서 | `?cursor=abc123` |
| `sort` | 정렬 필드 | `?sort=created_at` |
| `order` | 정렬 방향 | `?order=desc` |
| `fields` | 응답 필드 선택 | `?fields=id,name` |
| `search` | 전체 검색 | `?search=홍길동` |
| `{field}` | 필드별 필터 | `?status=active` |

---

## 8. SSE (Server-Sent Events) 규칙

AI 챗봇 스트리밍 응답에 사용합니다.

### 8.1 연결 설정

```http
GET /api/v1/chat/sessions/{id}/stream HTTP/1.1
Authorization: Bearer {token}
Accept: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

### 8.2 이벤트 포맷

```
event: {event_type}
data: {json_data}

```

### 8.3 이벤트 타입

| 이벤트 | 설명 | 데이터 |
|--------|------|--------|
| `message` | 텍스트 청크 | `{ "content": "안녕" }` |
| `law_reference` | 법령 인용 | `{ "law_name": "근로기준법", "article": "제55조" }` |
| `risk_level` | 위험도 분류 | `{ "level": "HIGH" }` |
| `done` | 완료 | `{ "message_id": "uuid" }` |
| `error` | 오류 | `{ "code": "E-6002", "message": "..." }` |

### 8.4 예시

```
event: message
data: {"content": "최저임금에 "}

event: message
data: {"content": "대한 답변입니다."}

event: law_reference
data: {"law_name": "최저임금법", "article": "제4조", "content": "최저임금은..."}

event: risk_level
data: {"level": "LOW"}

event: done
data: {"message_id": "550e8400-e29b-41d4-a716-446655440000"}

```

---

## 9. 파일 업로드/다운로드

### 9.1 파일 업로드

**요청 (multipart/form-data)**

```http
POST /api/v1/work-records/import HTTP/1.1
Authorization: Bearer {token}
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="records.xlsx"
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

(binary data)
------WebKitFormBoundary--
```

**제한**

| 항목 | 제한 |
|------|------|
| 최대 파일 크기 | 10MB |
| 허용 확장자 | xlsx, csv, pdf, docx |
| 최대 파일 개수 | 1개 (일반), 10개 (이미지) |

### 9.2 파일 다운로드

**Presigned URL 방식**

```json
{
  "success": true,
  "data": {
    "download_url": "https://s3.amazonaws.com/bucket/contracts/xxx.pdf?X-Amz-Signature=...",
    "expires_at": "2024-01-01T12:00:00Z",
    "filename": "근로계약서_홍길동.pdf"
  }
}
```

- URL 유효 시간: 24시간
- 일회용 다운로드 권장

---

## 10. 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2026-03-01 | 1.0.0 | 초기 작성 | architect |
