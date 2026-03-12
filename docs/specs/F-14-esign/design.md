# F-14 전자서명 연동 — 기술 설계서

## 1. 개요

모두싸인 API를 연동하여 근로계약서에 전자서명을 요청하고, 서명 완료 시 상태를 자동 업데이트하는 기능.
API 키 미설정 시 Mock 모드로 동작 (개발/테스트 환경 지원).

## 2. 기존 인프라 활용

- `contracts.status`: draft → **sent** → **signed** / expired / terminated
- `contracts.signed_at`: 서명 완료 일시
- `contracts.sign_service_ref`: 모두싸인 문서 ID
- `settings.MODUSIGN_API_KEY`: 이미 config에 등록됨

## 3. API 엔드포인트

### 3.1 전자서명 요청 발송
```
POST /api/v1/contracts/{contract_id}/sign-request
Authorization: Bearer {token}
Body: {
  "signer_name": "홍길동",
  "signer_email": "hong@example.com",
  "signer_phone": "01012345678"  // 선택
}
Response 201: {
  "success": true,
  "data": {
    "contract_id": "uuid",
    "sign_service_ref": "modusign_doc_xxx",
    "status": "sent",
    "signing_url": "https://..."  // 서명 페이지 URL
  }
}
```

### 3.2 서명 상태 조회
```
GET /api/v1/contracts/{contract_id}/sign-status
Authorization: Bearer {token}
Response 200: {
  "success": true,
  "data": {
    "contract_id": "uuid",
    "status": "sent" | "signed",
    "sign_service_ref": "modusign_doc_xxx",
    "signed_at": "2026-03-12T..."  // signed일 때만
  }
}
```

### 3.3 서명 완료 웹훅
```
POST /api/v1/webhooks/modusign
Body: {
  "event": "document.completed",
  "document_id": "modusign_doc_xxx",
  "completed_at": "2026-03-12T..."
}
Response 200: { "success": true }
```

### 3.4 서명된 PDF 다운로드
```
GET /api/v1/contracts/{contract_id}/signed-pdf
Authorization: Bearer {token}
Response 200: PDF file (application/pdf)
```

## 4. 에러 코드

| 코드 | 설명 | HTTP |
|------|------|------|
| E-9001 | 계약서를 찾을 수 없음 | 404 |
| E-9002 | 전자서명 발송 불가 (draft 상태가 아님) | 400 |
| E-9003 | 모두싸인 API 연결 실패 | 502 |
| E-9004 | 이미 서명 완료된 계약서 | 409 |
| E-9005 | PDF 파일 없음 (서명 전) | 400 |
| E-9006 | 웹훅 검증 실패 | 400 |

## 5. 모두싸인 클라이언트 (Mock 모드 포함)

`backend/app/external/modusign_client.py`:
- TossClient 패턴 동일
- MODUSIGN_API_KEY 미설정 시 Mock 응답
- Mock: 즉시 signing_url 반환, 상태 조회 시 signed 반환

## 6. 서비스 흐름

1. **서명 요청**: draft 상태 확인 → 모두싸인 API 호출 → status='sent' + sign_service_ref 저장
2. **상태 조회**: sign_service_ref로 모두싸인 API 폴링 → 상태 반환
3. **웹훅**: document_id로 계약서 조회 → status='signed' + signed_at 업데이트
4. **PDF 다운로드**: signed 상태 확인 → 모두싸인에서 PDF 가져오기 (또는 기존 pdf_url)
