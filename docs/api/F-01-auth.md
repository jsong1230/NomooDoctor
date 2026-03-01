# F-01 사용자 인증 — API 스펙

## 참조
- 설계서: docs/specs/F-01-auth/design.md
- 인수조건: docs/project/features.md #F-01

---

## 1. 개요

사용자 인증 및 계정 관리 API 스펙입니다.

---

## 2. 인증 API (Auth)

### 2.1 POST /api/v1/auth/register

회원가입

**요청:**
```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123",
  "name": "홍길동",
  "phone": "010-1234-5678"
}
```

**응답 (201 Created):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-4466554400000",
      "email": "user@example.com",
      "name": "홍길동",
      "phone": "010-1234-5678",
      "role": "owner",
      "plan": "free",
      "plan_expires_at": null,
      "is_active": true,
      "created_at": "2026-03-01T10:00:00Z",
      "updated_at": "2026-03-01T10:00:00Z"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "rt_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  },
  "message": "회원가입이 완료되었습니다."
}
```

**에러:**
| 코드 | HTTP | 메시지 |
|------|------|--------|
| E-1001 | 400 | 입력값이 올바르지 않습니다. |
| E-1003 | 400 | 필수 필드가 누락되었습니다. |
| E-3001 | 409 | 이미 등록된 이메일입니다. |
| E-2006 | 429 | 요청 횟수를 초과했습니다. |

---

### 2.2 POST /api/v1/auth/login

로그인

**요청:**
```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123"
}
```

**응답 (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-4466554400000",
      "email": "user@example.com",
      "name": "홍길동",
      "phone": "010-1234-5678",
      "role": "owner",
      "plan": "standard",
      "plan_expires_at": "2026-04-01T00:00:00Z",
      "is_active": true,
      "created_at": "2026-01-15T09:30:00Z",
      "updated_at": "2026-03-01T10:00:00Z"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "rt_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  },
  "message": "로그인되었습니다."
}
```

**에러:**
| 코드 | HTTP | 메시지 |
|------|------|--------|
| E-1001 | 400 | 입력값이 올바르지 않습니다. |
| E-3002 | 404 | 사용자를 찾을 수 없습니다. |
| E-3003 | 401 | 비밀번호가 일치하지 않습니다. |
| E-3004 | 401 | 비활성화된 계정입니다. |
| E-2006 | 429 | 요청 횟수를 초과했습니다. |

---

### 2.3 POST /api/v1/auth/refresh

토큰 갱신 (Refresh Token Rotation)

**요청:**
```json
{
  "refresh_token": "rt_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**응답 (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "rt_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

**에러:**
| 코드 | HTTP | 메시지 |
|------|------|--------|
| E-2002 | 401 | 리프레시 토큰이 만료되었습니다. |
| E-2004 | 401 | 유효하지 않은 리프레시 토큰입니다. |

---

### 2.4 POST /api/v1/auth/logout

로그아웃

**요청:**
```
Authorization: Bearer {access_token}
```

**응답 (200 OK):**
```json
{
  "success": true,
  "data": null,
  "message": "로그아웃되었습니다."
}
```

**에러:**
| 코드 | HTTP | 메시지 |
|------|------|--------|
| E-2001 | 401 | 인증이 필요합니다. |

---

## 3. 사용자 API (Users)

### 3.1 GET /api/v1/users/me

내 정보 조회

**요청:**
```
Authorization: Bearer {access_token}
```

**응답 (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-4466554400000",
    "email": "user@example.com",
    "name": "홍길동",
    "phone": "010-1234-5678",
    "role": "owner",
    "plan": "standard",
    "plan_expires_at": "2026-04-01T00:00:00Z",
    "is_active": true,
    "created_at": "2026-01-15T09:30:00Z",
    "updated_at": "2026-03-01T10:00:00Z"
  }
}
```

**에러:**
| 코드 | HTTP | 메시지 |
|------|------|--------|
| E-2001 | 401 | 인증이 필요합니다. |
| E-2002 | 401 | 토큰이 만료되었습니다. |
| E-2005 | 403 | 접근 권한이 없습니다. |

---

### 3.2 PATCH /api/v1/users/me

내 정보 수정

**요청:**
```json
{
  "name": "홍길동",
  "phone": "010-9876-5432"
}
```

**응답 (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-4466554400000",
    "email": "user@example.com",
    "name": "홍길동",
    "phone": "010-9876-5432",
    "role": "owner",
    "plan": "standard",
    "plan_expires_at": "2026-04-01T00:00:00Z",
    "is_active": true,
    "created_at": "2026-01-15T09:30:00Z",
    "updated_at": "2026-03-01T11:00:00Z"
  },
  "message": "정보가 수정되었습니다."
}
```

**에러:**
| 코드 | HTTP | 메시지 |
|------|------|--------|
| E-2001 | 401 | 인증이 필요합니다. |
| E-2002 | 401 | 토큰이 만료되었습니다. |

---

### 3.3 POST /api/v1/users/me/password

비밀번호 변경

**요청:**
```json
{
  "current_password": "SecureP@ss123",
  "new_password": "NewSecureP@ss456"
}
```

**응답 (200 OK):**
```json
{
  "success": true,
  "data": null,
  "message": "비밀번호가 변경되었습니다."
}
```

**에러:**
| 코드 | HTTP | 메시지 |
|------|------|--------|
| E-2001 | 401 | 인증이 필요합니다. |
| E-1001 | 400 | 현재 비밀번호가 일치하지 않습니다. |
| E-1001 | 400 | 비밀번호는 8자 이상이어야 합니다. |

---

## 4. Rate Limiting

| 엔드포인트 | 제한 | 기준 |
|------------|------|------|
| POST /auth/register | 3회/시간 | IP |
| POST /auth/login | 5회/분 | IP |
| POST /auth/refresh | 30회/시간 | User ID |

---

## 5. 인증 헤더

```
Authorization: Bearer {access_token}
```

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|-----------|
| 2026-03-01 | 1.0.0 | 초기 작성 |
