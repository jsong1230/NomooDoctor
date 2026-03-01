# F-01 사용자 인증 — DB 스키마

## 참조
- 설계서: docs/specs/F-01-auth/design.md
- ERD: docs/system/erd.md

---

## 1. users 테이블

### 1.1 테이블 구조

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    kakao_id VARCHAR(100) UNIQUE,
    role VARCHAR(20) NOT NULL DEFAULT 'owner',
    plan VARCHAR(20) NOT NULL DEFAULT 'free',
    plan_expires_at TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 1.2 컬럼 설명

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| `id` | UUID | PK | 사용자 고유 식별자 |
| `email` | VARCHAR(255) | UK, NOT NULL | 이메일 (로그인 ID) |
| `hashed_password` | VARCHAR(255) | | bcrypt 해시된 비밀번호 (OAuth 시 NULL) |
| `name` | VARCHAR(100) | NOT NULL | 사용자명 |
| `phone` | VARCHAR(20) | | 전화번호 |
| `kakao_id` | VARCHAR(100) | UK | 카카오 사용자 ID |
| `role` | VARCHAR(20) | NOT NULL | 역할 (owner/manager/employee/admin) |
| `plan` | VARCHAR(20) | NOT NULL | 플랜 (free/basic/standard/premium/enterprise) |
| `plan_expires_at` | TIMESTAMPTZ | | 플랜 만료일시 |
| `is_active` | BOOLEAN | NOT NULL | 활성 여부 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 생성일시 |
| `updated_at` | TIMESTAMPTZ | NOT NULL | 수정일시 |

### 1.3 인덱스

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_kakao_id ON users(kakao_id) WHERE kakao_id IS NOT NULL;
CREATE INDEX idx_users_is_active ON users(is_active);
```

### 1.4 제약조건

| 제약조건 | 설명 |
|----------|------|
| `users_email_key` | 이메일 중복 방지 |
| `users_kakao_id_key` | 카카오 ID 중복 방지 |

---

## 2. Redis 스키마

### 2.1 Key 패턴

| Key 패턴 | 타입 | TTL | 설명 |
|----------|------|-----|------|
| `refresh:{user_id}` | String | 30일 | 리프레시 토큰 저장 (Rotation 지원) |
| `blacklist:{token_jti}` | String | 1시간 | 로그아웃 토큰 블랙리스트 |
| `ratelimit:login:{ip}` | String | 1분 | 로그인 시도 횟수 |
| `ratelimit:register:{ip}` | String | 1시간 | 회원가입 시도 횟수 |
| `oauth_state:{state}` | String | 10분 | OAuth state (CSRF 방지) |

### 2.2 Value 구조

- **refresh:{user_id}**: JWT 토큰 값 (rt_ 접두사 없이)
- **blacklist:{token_jti}**: "1" (플래그)
- **ratelimit:login:{ip}**: 현재 시도 횟수 (정수)
- **ratelimit:register:{ip}**: 현재 시도 횟수 (정수)
- **oauth_state:{state}**: 사용자 IP 주소

---

## 3. JWT Payload 구조

### 3.1 Access Token

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "company_id": "660e8400-e29b-41d4-a716-4466554400001",
  "plan": "standard",
  "role": "owner",
  "exp": 1700000000,
  "iat": 1699996400,
  "jti": "550e8400-e29b-41d4-a716-4466554400002"
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `sub` | string (UUID) | 사용자 고유 ID |
| `company_id` | string (UUID) | 현재 선택된 사업장 ID (선택) |
| `plan` | string | 구독 플랜 |
| `role` | string | 사용자 역할 |
| `exp` | int (Unix timestamp) | 만료 시간 |
| `iat` | int (Unix timestamp) | 발급 시간 |
| `jti` | string (UUID) | 토큰 고유 ID (블랙리스트용) |

### 3.2 Refresh Token

```json
{
  "sub": "550e8400-e29b-41d4-a716-4466554400000",
  "exp": 1700000000,
  "iat": 1699996400,
  "jti": "550e8400-e29b-41d4-a716-4466554400002",
  "type": "refresh"
}
```

---

## 4. 데이터 관계

```
users (1) ----< (N) companies (사용자가 소유한 사업장)
  |                      |
  |                      +---- (1) owner
  |
  +---- (1) chat_sessions (사용자의 채팅 세션)
  |
  +---- (1) subscriptions (사용자의 구독)
```

---

## 5. 보안 고려사항

### 5.1 비밀번호
- **해싱**: bcrypt (rounds=12)
- **규칙**: 최소 8자, 영문 대소문자/숫자/특수문자 중 3가지 이상 조합

### 5.2 JWT
- **알고리즘**: HS256
- **Access Token 유효기간**: 60분 (설정 가능)
- **Refresh Token 유효기간**: 30일
- **Refresh Token Rotation**: 적용 (재사용 감지 시 전체 폐기)

### 5.3 Rate Limiting
- **로그인**: 5회/분 (IP 기준)
- **회원가입**: 3회/시간 (IP 기준)
- **토큰 갱신**: 30회/시간 (User ID 기준)

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|-----------|
| 2026-03-01 | 1.0.0 | 초기 작성 |
