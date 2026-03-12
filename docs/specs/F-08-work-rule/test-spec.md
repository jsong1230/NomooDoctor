# F-08 취업규칙 자동화 -- 테스트 명세

## 참조
- 설계서: docs/specs/F-08-work-rule/design.md
- 인수조건: docs/project/features.md #F-08

---

## 단위 테스트

### WorkRuleService 단위 테스트

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| create_work_rule | 제조업 템플릿으로 생성 | industry_type="manufacturing" | 14개 섹션 포함 JSONB, status=draft, version=1 |
| create_work_rule | IT업 템플릿으로 생성 | industry_type="it" | IT업종 특화 내용 포함 14개 섹션 |
| create_work_rule | 잘못된 업종 | industry_type="invalid" | ValidationError |
| get_templates | 전체 템플릿 조회 | industry_type=None | 4개 업종 템플릿 반환 |
| get_templates | 특정 업종 필터 | industry_type="manufacturing" | 제조업 템플릿 1개 반환 |
| get_consent_checklist | 15명 사업장 | employee_count=15 | consent_threshold=8, consent_type="majority" |
| get_consent_checklist | 10명 사업장 | employee_count=10 | consent_threshold=6, consent_type="majority" |
| update_work_rule | draft 상태에서 수정 | status=draft, content 변경 | 정상 수정 |
| update_work_rule | active 상태에서 수정 시도 | status=active, content 변경 | ValidationError ("수정 불가") |
| update_work_rule | superseded 상태에서 수정 시도 | status=superseded | ValidationError ("수정 불가") |
| delete_work_rule | draft 삭제 | status=draft | 정상 삭제 |
| delete_work_rule | active 삭제 시도 | status=active | ValidationError ("삭제 불가") |
| revise_work_rule | active 버전 개정 | 기존 active 존재 | 기존 superseded, 새 draft 생성 (version+1) |
| revise_work_rule | active 없이 개정 시도 | 기존 active 없음 | NotFoundError 또는 ValidationError |

### 템플릿 데이터 검증

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| WORK_RULE_TEMPLATES | 각 업종 템플릿 구조 검증 | 4개 업종 각각 | 14개 섹션 포함, section_number 1-14, title/law_reference 존재 |
| WORK_RULE_TEMPLATES | 법정 필수 항목 누락 검증 | 모든 템플릿 | 제93조 제1호~제13호 전부 매핑됨 |

---

## 통합 테스트 (API)

### TestWorkRuleTemplatesAPI

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| GET /work-rules/templates | 전체 템플릿 목록 조회 | 인증 토큰 | 200, 4개 업종 템플릿 |
| GET /work-rules/templates?industry_type=it | 업종 필터 | industry_type=it | 200, IT 템플릿 1개 |
| GET /work-rules/templates | 인증 없이 | 토큰 없음 | 401, E-2001 |

### TestCreateWorkRuleAPI

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /work-rules | 정상 생성 (제조업) | industry_type="manufacturing" | 201, 14개 섹션, status=draft, version=1 |
| POST /work-rules | 정상 생성 (IT) | industry_type="it" | 201, IT 템플릿 기반 |
| POST /work-rules | 인증 없이 | 토큰 없음 | 401, E-2001 |
| POST /work-rules | 사업장 미선택 | company_id 없는 토큰 | 403, E-2005 |
| POST /work-rules | 잘못된 업종 | industry_type="invalid" | 400, E-1001 |
| POST /work-rules | effective_date 포함 생성 | effective_date="2026-04-01" | 201, effective_date 설정됨 |

### TestListWorkRulesAPI

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| GET /work-rules | 빈 목록 | 취업규칙 없음 | 200, data=[] |
| GET /work-rules | 2건 존재 시 목록 조회 | 2건 생성 후 | 200, 2건 반환 |
| GET /work-rules?status=draft | 상태 필터 | draft 1건, active 1건 | 200, draft 1건만 반환 |
| GET /work-rules | 인증 없이 | 토큰 없음 | 401 |
| GET /work-rules | 다른 사업장 데이터 격리 | 사용자A 사업장, 사용자B 조회 | 200, data=[] (빈 목록) |

### TestGetWorkRuleAPI

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| GET /work-rules/{id} | 정상 상세 조회 | 존재하는 ID | 200, content 포함 전체 데이터 |
| GET /work-rules/{id} | 존재하지 않는 ID | fake UUID | 404 |
| GET /work-rules/{id} | 다른 사업장의 취업규칙 | 사용자B의 work_rule ID | 404 |

### TestUpdateWorkRuleAPI

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| PUT /work-rules/{id} | 섹션 내용 수정 (draft) | content.sections[0].content_html 변경 | 200, 수정된 내용 반영 |
| PUT /work-rules/{id} | 상태 변경 draft -> under_review | status="under_review" | 200, 상태 변경됨 |
| PUT /work-rules/{id} | 상태 변경 under_review -> active | status="active", approval_date, worker_consent_count | 200, 상태 active |
| PUT /work-rules/{id} | active 상태에서 수정 시도 | active 상태, content 변경 | 400, "수정 불가" |
| PUT /work-rules/{id} | effective_date 수정 | effective_date="2026-05-01" | 200, 날짜 변경됨 |
| PUT /work-rules/{id} | worker_consent_count 설정 | worker_consent_count=8, total_worker_count=15 | 200, 동의 수 기록 |

### TestDeleteWorkRuleAPI

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| DELETE /work-rules/{id} | draft 삭제 | draft 상태 | 204 |
| DELETE /work-rules/{id} | active 삭제 시도 | active 상태 | 400, "삭제 불가" |
| DELETE /work-rules/{id} | 존재하지 않는 ID | fake UUID | 404 |

### TestGenerateAiDraftAPI

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /work-rules/{id}/generate | 정상 AI 생성 | draft 상태, industry_type="manufacturing" | 200, ai_generated=true, 14개 섹션 |
| POST /work-rules/{id}/generate | 추가 컨텍스트 포함 | additional_context="교대근무, 기숙사" | 200, 컨텍스트 반영된 내용 |
| POST /work-rules/{id}/generate | active 상태에서 시도 | active 상태 | 400, "draft 상태에서만 가능" |
| POST /work-rules/{id}/generate | Claude API 오류 시 | mock: API 에러 | 502, E-6002 |

### TestReviseWorkRuleAPI

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /work-rules/{id}/revise | 정상 개정 | active 상태, revision_reason="근로시간 변경" | 201, 새 버전(version+1), status=draft |
| POST /work-rules/{id}/revise | 개정 후 기존 버전 확인 | 개정 실행 후 기존 ID 조회 | 기존 status=superseded |
| POST /work-rules/{id}/revise | draft에서 개정 시도 | draft 상태 | 400, "active만 개정 가능" |
| POST /work-rules/{id}/revise | 개정 사유 누락 | revision_reason 없음 | 400, 필수 필드 누락 |

### TestDownloadWorkRuleAPI

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| GET /work-rules/{id}/download/docx | Word 다운로드 | 존재하는 ID | 200, download_url, filename |
| GET /work-rules/{id}/download/pdf | PDF 다운로드 | 존재하는 ID | 200, download_url, filename |
| GET /work-rules/{id}/download/invalid | 잘못된 type | type="txt" | 400 |

### TestConsentChecklistAPI

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| GET /work-rules/consent-checklist | 15명 사업장 | employee_count=15 (company에서) | 200, consent_threshold=8 |
| GET /work-rules/consent-checklist | 10명 사업장 | employee_count=10 | 200, consent_threshold=6 |
| GET /work-rules/consent-checklist | 인증 없이 | 토큰 없음 | 401 |

### TestCoverDocumentAPI

| API | 시나리오 | 입력 | 예상 결과 |
|-----|----------|------|-----------|
| POST /work-rules/{id}/file | active 상태에서 생성 | active 상태 | 200, cover_document_url |
| POST /work-rules/{id}/file | draft 상태에서 시도 | draft 상태 | 400, "active 상태에서만 가능" |

---

## 경계 조건 / 에러 케이스

- 14개 법정 필수 섹션 중 일부가 누락된 content로 update 시도 -> 400 (검증 에러)
- content_html이 빈 문자열인 섹션 포함 시 -> 400 (min_length=1 위반)
- section_number 범위 외 값 (0, 15 이상) -> 400
- 동일 company에 active 취업규칙이 이미 있을 때 새로 생성 후 active 전환 -> 기존 active를 superseded로 자동 전환
- worker_consent_count가 total_worker_count의 과반수 미만일 때 active로 전환 시도 -> 경고 메시지 (차단은 아님, 의견 청취만 필요한 경우 있음)
- 매우 큰 content_html (100KB 이상) -> 400 또는 적절한 크기 제한
- effective_date가 과거 날짜 -> 허용 (소급 적용 가능)
- version이 순차적으로 증가하는지 검증 (동시 요청 시 race condition)
- 다른 사용자의 사업장 취업규칙 접근 시 -> 403 또는 404 (정보 노출 방지를 위해 404 권장)

---

## 테스트 헬퍼 함수

테스트 코드에서 재사용할 헬퍼:

```python
async def setup_authenticated_user(client) -> tuple[str, str]:
    """사용자 등록 + 로그인 + 사업장 생성 + 선택 후 (token, company_id) 반환"""

async def create_test_work_rule(client, token: str, industry_type: str = "it") -> dict:
    """테스트용 취업규칙 생성 후 응답 data 반환"""

async def activate_work_rule(client, token: str, work_rule_id: str) -> dict:
    """취업규칙을 active 상태로 전환 (under_review -> active)"""
```

---

## 테스트 실행 순서 권장

1. TestWorkRuleTemplatesAPI (의존성 없음)
2. TestCreateWorkRuleAPI (기본 CRUD)
3. TestListWorkRulesAPI (목록 조회)
4. TestGetWorkRuleAPI (상세 조회)
5. TestUpdateWorkRuleAPI (상태 전환 포함)
6. TestDeleteWorkRuleAPI (삭제)
7. TestGenerateAiDraftAPI (AI 연동, mock 사용)
8. TestReviseWorkRuleAPI (버전 관리)
9. TestDownloadWorkRuleAPI (파일 생성, mock 사용)
10. TestConsentChecklistAPI (체크리스트)
11. TestCoverDocumentAPI (커버 서류)

---

## AI Mock 전략

Claude API 호출이 필요한 테스트(`TestGenerateAiDraftAPI`)에서는 다음과 같이 mock 처리:

```python
@pytest.fixture
def mock_claude_api(monkeypatch):
    """Claude API 호출을 mock 응답으로 대체"""
    async def mock_generate(*args, **kwargs):
        return {
            "sections": [
                {
                    "section_number": i,
                    "title": f"섹션 {i}",
                    "content_html": f"<p>AI 생성 내용 {i}</p>",
                    "law_reference": f"근로기준법 제93조 제{i}호"
                }
                for i in range(1, 15)
            ]
        }
    monkeypatch.setattr(
        "app.services.work_rule_service.WorkRuleService._call_claude_api",
        mock_generate
    )
```

파일 생성(Word/PDF) 테스트에서도 S3 업로드를 mock하여 presigned URL 대신 로컬 경로를 반환.

---

## 변경 이력

| 날짜 | 변경 내용 | 이유 |
|------|-----------|------|
| 2026-03-12 | 초기 테스트 명세 작성 | M4 마일스톤 F-08 착수 |
