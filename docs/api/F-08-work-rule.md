# F-08 취업규칙 자동화 - API 스펙 확정본

## 개요
취업규칙 자동화 기능의 API 엔드포인트 명세입니다. 모든 엔드포인트는 JWT 인증이 필요하며, company_id는 JWT payload에서 추출됩니다.

---

## 엔드포인트 목록

### 1. GET /api/v1/work-rules/templates
**목적**: 업종별 표준 취업규칙 템플릿 조회

**인증**: 필수 (Bearer Token)

**Query Parameters**:
- `industry_type` (선택): 업종 필터 (manufacturing | food_service | service | it)

**Response 200**:
```json
{
  "success": true,
  "data": [
    {
      "industry_type": "manufacturing",
      "industry_name": "제조업",
      "description": "제조업 사업장 표준 취업규칙",
      "sections": [
        {
          "section_number": 1,
          "title": "업무의 시작과 종료 시각, 휴게시간, 휴일, 휴가 및 교대근로에 관한 사항",
          "description": "근로기준법 제93조 제1호"
        }
      ]
    }
  ]
}
```

---

### 2. POST /api/v1/work-rules
**목적**: 취업규칙 초안 생성 (템플릿 기반)

**인증**: 필수

**Request Body**:
```json
{
  "industry_type": "manufacturing",
  "effective_date": "2026-04-01"
}
```

**Response 201**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "company_id": "uuid",
    "version": 1,
    "status": "draft",
    "industry_type": "manufacturing",
    "content": {
      "sections": [
        {
          "section_number": 1,
          "title": "총칙",
          "content_html": "<p>제1조(목적) 이 규칙은...</p>",
          "is_required": true,
          "law_reference": "근로기준법 제93조 제1호"
        }
      ]
    },
    "effective_date": "2026-04-01",
    "created_at": "2026-03-12T10:00:00Z",
    "updated_at": "2026-03-12T10:00:00Z",
    "ai_generated": false,
    "ai_model": null,
    "docx_url": null,
    "pdf_url": null
  },
  "meta": {
    "message": "취업규칙 초안이 생성되었습니다."
  }
}
```

**에러**:
- `E-1001` (400): 잘못된 industry_type
- `E-2005` (403): 사업장 미선택
- `E-4001` (404): 사업장 없음

---

### 3. GET /api/v1/work-rules
**목적**: 취업규칙 목록 조회

**인증**: 필수

**Query Parameters**:
- `status` (선택): 상태 필터 (draft | under_review | active | superseded)
- `page` (선택, 기본값 1): 페이지 번호
- `per_page` (선택, 기본값 20): 한 페이지의 아이템 수

**Response 200**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "version": 2,
      "status": "active",
      "industry_type": "manufacturing",
      "effective_date": "2026-04-01",
      "approval_date": "2026-03-25",
      "worker_consent_count": 8,
      "ai_generated": false,
      "filed_at": "2026-03-26T09:00:00Z",
      "created_at": "2026-03-12T10:00:00Z",
      "updated_at": "2026-03-25T14:00:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "limit": 20,
      "skip": 0,
      "total": 2,
      "hasNext": false
    }
  }
}
```

---

### 4. GET /api/v1/work-rules/{id}
**목적**: 취업규칙 상세 조회 (전체 content 포함)

**인증**: 필수

**Response 200**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "company_id": "uuid",
    "version": 1,
    "status": "draft",
    "industry_type": "manufacturing",
    "content": {
      "sections": [
        {
          "section_number": 1,
          "title": "총칙",
          "content_html": "<p>제1조(목적) 이 규칙은...</p>",
          "is_required": true,
          "law_reference": "근로기준법 제93조 제1호"
        }
      ]
    },
    "effective_date": "2026-04-01",
    "approval_date": null,
    "worker_consent_count": null,
    "total_worker_count": null,
    "revision_reason": null,
    "ai_generated": false,
    "ai_model": null,
    "docx_url": null,
    "pdf_url": null,
    "filed_at": null,
    "created_at": "2026-03-12T10:00:00Z",
    "updated_at": "2026-03-12T10:00:00Z"
  }
}
```

**에러**:
- `E-4001` (404): 취업규칙 없음

---

### 5. PUT /api/v1/work-rules/{id}
**목적**: 취업규칙 수정 (draft/under_review 상태에서만 가능)

**인증**: 필수

**Request Body**:
```json
{
  "content": {
    "sections": [
      {
        "section_number": 1,
        "title": "총칙",
        "content_html": "<p>수정된 내용...</p>",
        "is_required": true,
        "law_reference": "근로기준법 제93조 제1호"
      }
    ]
  },
  "effective_date": "2026-04-01",
  "status": "under_review",
  "worker_consent_count": 8,
  "total_worker_count": 15,
  "approval_date": "2026-03-25"
}
```

**Response 200**: 수정된 work_rule 전체 데이터

**에러**:
- `E-1001` (400): active/superseded 상태에서 수정 시도
- `E-4001` (404): 취업규칙 없음

---

### 6. DELETE /api/v1/work-rules/{id}
**목적**: 취업규칙 삭제 (draft 상태에서만 가능)

**인증**: 필수

**Response 200**:
```json
{
  "success": true,
  "data": null,
  "meta": {
    "message": "취업규칙이 삭제되었습니다."
  }
}
```

**에러**:
- `E-1001` (400): draft 외 상태에서 삭제 시도
- `E-4001` (404): 취업규칙 없음

---

### 7. POST /api/v1/work-rules/{id}/generate
**목적**: AI 초안 생성 (Claude API)

**인증**: 필수

**조건**: draft 상태에서만 호출 가능

**Request Body**:
```json
{
  "industry_type": "manufacturing",
  "additional_context": "직원 15명, 교대근무 운영, 기숙사 제공"
}
```

**Response 200**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "company_id": "uuid",
    "version": 1,
    "status": "draft",
    "industry_type": "manufacturing",
    "content": {
      "sections": [...]
    },
    "ai_generated": true,
    "ai_model": "claude-sonnet-4-20250514",
    "created_at": "2026-03-12T10:00:00Z",
    "updated_at": "2026-03-12T10:05:00Z"
  },
  "meta": {
    "message": "AI 초안이 생성되었습니다."
  }
}
```

**에러**:
- `E-6002` (502): Claude API 오류
- `E-1001` (400): draft 외 상태에서 생성 시도
- `E-4001` (404): 취업규칙 없음

**Rate Limiting**: 5회/시간

---

### 8. GET /api/v1/work-rules/{id}/download/{type}
**목적**: Word(.docx) 또는 PDF 다운로드

**인증**: 필수

**Path Parameters**:
- `type`: "docx" | "pdf"

**Response 200**:
```json
{
  "success": true,
  "data": {
    "download_url": "https://s3.../work-rules/xxx.docx?...",
    "filename": "취업규칙_테스트사업장_v2.docx",
    "expires_at": "2026-03-13T10:00:00Z"
  }
}
```

**에러**:
- `E-1001` (400): 지원하지 않는 파일 타입
- `E-4001` (404): 취업규칙 없음

**Rate Limiting**: 20회/시간

---

### 9. POST /api/v1/work-rules/{id}/revise
**목적**: 새 버전 생성 (개정)

**인증**: 필수

**조건**: active 상태의 취업규칙만 개정 가능. 기존 active를 superseded로 변경하고 새 draft 생성

**Request Body**:
```json
{
  "revision_reason": "근로시간 변경에 따른 개정",
  "effective_date": "2026-07-01"
}
```

**Response 201**:
```json
{
  "success": true,
  "data": {
    "id": "new-uuid",
    "company_id": "uuid",
    "version": 2,
    "status": "draft",
    "industry_type": "manufacturing",
    "revision_reason": "근로시간 변경에 따른 개정",
    "effective_date": "2026-07-01",
    "created_at": "2026-03-12T10:10:00Z"
  },
  "meta": {
    "message": "새 버전이 생성되었습니다."
  }
}
```

**에러**:
- `E-1001` (400): active 상태가 아님
- `E-4001` (404): 취업규칙 없음

---

### 10. GET /api/v1/work-rules/consent-checklist
**목적**: 근로자 과반수 동의 절차 체크리스트

**인증**: 필수

**Response 200**:
```json
{
  "success": true,
  "data": {
    "checklist": [
      {
        "step": 1,
        "title": "취업규칙 변경(안) 작성",
        "description": "변경할 내용을 명확히 작성합니다.",
        "law_reference": "근로기준법 제94조",
        "is_required": true
      },
      {
        "step": 2,
        "title": "근로자 의견 청취 / 동의 절차",
        "description": "불이익 변경 시 근로자 과반수 동의 필요, 비불이익 변경 시 의견 청취.",
        "law_reference": "근로기준법 제94조 제1항",
        "is_required": true
      },
      {
        "step": 3,
        "title": "고용노동부 신고",
        "description": "취업규칙을 작성/변경 시 관할 지방고용노동청에 신고합니다.",
        "law_reference": "근로기준법 제93조",
        "is_required": true
      }
    ],
    "employee_count": 15,
    "consent_threshold": 8,
    "consent_type": "majority"
  }
}
```

---

### 11. POST /api/v1/work-rules/{id}/file
**목적**: 고용노동부 신고용 커버 서류 생성

**인증**: 필수

**조건**: status가 active일 때만 생성 가능

**Response 200**:
```json
{
  "success": true,
  "data": {
    "cover_document_url": "https://s3.../cover_xxx.docx?...",
    "filename": "취업규칙_신고서_테스트사업장.docx",
    "expires_at": "2026-03-13T10:00:00Z"
  }
}
```

**에러**:
- `E-1001` (400): active 상태가 아님
- `E-4001` (404): 취업규칙 없음

---

## 공통 사항

### 인증
모든 엔드포인트는 Authorization 헤더에 Bearer Token을 요구합니다:
```
Authorization: Bearer <jwt_token>
```

### 컨텍스트 추출
company_id는 JWT payload에서 자동으로 추출되므로 요청 본문에 포함하지 않습니다.
사업장을 선택하지 않은 상태에서는 E-2005 (Forbidden) 오류가 반환됩니다.

### 에러 응답 포맷
```json
{
  "success": false,
  "error": {
    "code": "E-XXXX",
    "message": "에러 메시지",
    "details": [
      {
        "field": "필드명",
        "message": "상세 메시지"
      }
    ]
  }
}
```

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 비고 |
|------|------|----------|------|
| 2026-03-12 | 1.0 | 초기 API 스펙 작성 | F-08 구현 완료 |
