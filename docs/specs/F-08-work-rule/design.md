# F-08 취업규칙 자동화 -- 기술 설계서

## 1. 참조
- 인수조건: docs/project/features.md #F-08
- 시스템 설계: docs/system/system-design.md
- ERD: docs/system/erd.md (work_rules 테이블)
- API 컨벤션: docs/system/api-conventions.md

---

## 2. 아키텍처 결정

### 결정 1: 취업규칙 섹션 저장 방식
- **선택지**: A) 별도 테이블(work_rule_sections)로 정규화 / B) 기존 work_rules.content JSONB 활용
- **결정**: B) JSONB 활용
- **근거**: 기존 work_rules 테이블에 content JSONB 컬럼이 이미 존재. 섹션 14개는 고정 구조이므로 JSONB가 적합하며 조회 시 JOIN 불필요. 섹션별 편집은 JSONB 내 키 단위 업데이트로 처리.

### 결정 2: 업종별 템플릿 관리 방식
- **선택지**: A) DB 테이블(work_rule_templates) / B) Python 상수 (dict/dataclass) / C) JSON 파일
- **결정**: B) Python 상수
- **근거**: 템플릿은 4개 업종뿐이고 변경 주기가 길다. 배포 시 코드와 함께 버전 관리되는 것이 안전하며, DB 마이그레이션이나 파일 I/O 불필요. 향후 관리자 UI가 생기면 DB로 전환 가능.

### 결정 3: AI 초안 생성 방식
- **선택지**: A) 전체 취업규칙을 한 번에 생성 / B) 섹션별로 나누어 생성
- **결정**: A) 전체 한 번에 생성
- **근거**: 섹션 간 정합성(예: 근로시간-휴게시간-수당 간 일관성)이 중요. 템플릿 + 회사 컨텍스트를 한 번에 주입하고 Claude가 전체를 생성하면 품질이 높다. 토큰 사용량이 커지지만 취업규칙 생성은 빈도가 낮아 비용 허용 범위 내.

### 결정 4: 버전 관리 전략
- **선택지**: A) 같은 레코드를 업데이트하고 별도 이력 테이블 / B) 새 레코드 생성 (version 증가)
- **결정**: B) 새 레코드 생성
- **근거**: 기존 work_rules 모델에 version 컬럼과 status(draft/under_review/active/superseded) 상태가 이미 설계되어 있다. 새 버전 생성 시 이전 버전을 superseded로 변경하고 새 레코드를 생성하면 이력이 자연스럽게 보존된다.

### 결정 5: Word/PDF 생성
- **선택지**: A) python-docx + WeasyPrint / B) Jinja2 HTML 템플릿 + WeasyPrint
- **결정**: A) python-docx + WeasyPrint
- **근거**: F-04 근로계약서에서 동일한 패턴이 이미 사용되고 있음. python-docx로 Word 생성 후 PDF 변환 파이프라인 재사용.

---

## 3. API 설계

모든 엔드포인트는 JWT 인증 필요. company_id는 JWT payload에서 추출.

### GET /api/v1/work-rules/templates
- **목적**: 업종별 표준 취업규칙 템플릿 목록 조회
- **인증**: 필요
- **Query Params**: `industry_type` (선택, 업종 필터)
- **Response 200**:
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
          "title": "총칙",
          "description": "목적, 적용범위, 용어 정의"
        }
      ]
    }
  ]
}
```

### POST /api/v1/work-rules
- **목적**: 취업규칙 초안 생성 (템플릿 기반 수동 생성)
- **인증**: 필요
- **Request Body**:
```json
{
  "industry_type": "manufacturing",
  "effective_date": "2026-04-01"
}
```
- **Response 201**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "company_id": "uuid",
    "version": 1,
    "status": "draft",
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
    "created_at": "2026-03-12T10:00:00Z"
  },
  "meta": { "message": "취업규칙 초안이 생성되었습니다." }
}
```
- **에러 케이스**:

| 코드 | HTTP | 상황 |
|------|------|------|
| E-2001 | 401 | 인증 없음 |
| E-2005 | 403 | 사업장 미선택 |
| E-1001 | 400 | 잘못된 industry_type |
| E-4001 | 404 | 사업장 없음 |

### GET /api/v1/work-rules
- **목적**: 취업규칙 목록 조회 (버전 이력 포함)
- **인증**: 필요
- **Query Params**: `status` (선택), `page` (기본 1), `per_page` (기본 20)
- **Response 200**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "version": 2,
      "status": "active",
      "effective_date": "2026-04-01",
      "approval_date": "2026-03-25",
      "worker_consent_count": 8,
      "filed_at": "2026-03-26T09:00:00Z",
      "created_at": "2026-03-12T10:00:00Z",
      "updated_at": "2026-03-25T14:00:00Z"
    }
  ]
}
```

### GET /api/v1/work-rules/{id}
- **목적**: 취업규칙 상세 조회 (전체 content 포함)
- **인증**: 필요
- **Response 200**: 전체 work_rule 데이터 (content JSONB 포함)
- **에러 케이스**:

| 코드 | HTTP | 상황 |
|------|------|------|
| E-4001 | 404 | 취업규칙 없음 |

### PUT /api/v1/work-rules/{id}
- **목적**: 취업규칙 내용 수정 (섹션별 편집)
- **인증**: 필요
- **조건**: status가 draft 또는 under_review일 때만 수정 가능
- **Request Body**:
```json
{
  "content": {
    "sections": [
      {
        "section_number": 1,
        "title": "총칙",
        "content_html": "<p>수정된 내용...</p>"
      }
    ]
  },
  "effective_date": "2026-04-01",
  "status": "under_review"
}
```
- **Response 200**: 수정된 work_rule 전체 데이터
- **에러 케이스**:

| 코드 | HTTP | 상황 |
|------|------|------|
| E-1001 | 400 | active/superseded 상태에서 수정 시도 |

### DELETE /api/v1/work-rules/{id}
- **목적**: 취업규칙 삭제
- **인증**: 필요
- **조건**: draft 상태에서만 삭제 가능. active는 삭제 불가 (superseded로 전환만 가능).
- **Response 204**: No Content
- **에러 케이스**:

| 코드 | HTTP | 상황 |
|------|------|------|
| E-1001 | 400 | draft 외 상태에서 삭제 시도 |

### POST /api/v1/work-rules/{id}/generate
- **목적**: Claude API로 AI 초안 생성 (기존 content를 AI가 개선/재생성)
- **인증**: 필요
- **조건**: draft 상태에서만 호출 가능
- **Request Body**:
```json
{
  "industry_type": "manufacturing",
  "additional_context": "직원 15명, 교대근무 운영, 기숙사 제공"
}
```
- **Response 200**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "content": { "sections": [...] },
    "ai_generated": true,
    "ai_model": "claude-sonnet-4-20250514"
  },
  "meta": { "message": "AI 초안이 생성되었습니다." }
}
```
- **에러 케이스**:

| 코드 | HTTP | 상황 |
|------|------|------|
| E-6002 | 502 | Claude API 오류 |
| E-1001 | 400 | draft 외 상태에서 생성 시도 |

### GET /api/v1/work-rules/{id}/download/{type}
- **목적**: Word(.docx) 또는 PDF 다운로드
- **인증**: 필요
- **Path Params**: `type` = "docx" | "pdf"
- **Response 200**:
```json
{
  "success": true,
  "data": {
    "download_url": "https://s3.../work-rules/xxx.docx?...",
    "expires_at": "2026-03-13T10:00:00Z",
    "filename": "취업규칙_테스트사업장_v2.docx"
  }
}
```

### POST /api/v1/work-rules/{id}/revise
- **목적**: 새 버전 생성 (개정)
- **인증**: 필요
- **조건**: 기존 active 버전이 있을 때 호출. 기존 active를 superseded로 변경하고 새 draft 생성.
- **Request Body**:
```json
{
  "revision_reason": "근로시간 변경에 따른 개정",
  "effective_date": "2026-07-01"
}
```
- **Response 201**: 새로 생성된 work_rule (version + 1, status=draft)

### GET /api/v1/work-rules/consent-checklist
- **목적**: 근로자 과반수 동의 절차 체크리스트 조회
- **인증**: 필요
- **Response 200**:
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

### POST /api/v1/work-rules/{id}/file
- **목적**: 고용노동부 신고용 커버 서류 자동 생성 (별도 문서)
- **인증**: 필요
- **조건**: status가 active일 때만 생성 가능
- **Response 200**:
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

---

## 4. DB 설계

### 기존 테이블: work_rules (변경 없음)

기존 work_rules 테이블이 F-08 요구사항을 이미 충분히 지원한다. 추가 컬럼이 필요한 부분만 마이그레이션 004에서 처리한다.

### 마이그레이션 004: work_rules 테이블 확장

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| industry_type | VARCHAR(50) | NOT NULL, DEFAULT 'other' | 작성 시 사용한 업종 템플릿 |
| ai_generated | BOOLEAN | NOT NULL, DEFAULT FALSE | AI 생성 여부 |
| ai_model | VARCHAR(50) | NULL | 사용된 AI 모델명 |
| revision_reason | TEXT | NULL | 개정 사유 (v2부터) |
| total_worker_count | INTEGER | NULL | 전체 근로자 수 (동의 비율 계산용) |
| cover_docx_url | TEXT | NULL | 고용노동부 신고용 커버 서류 URL |

**마이그레이션 SQL (004_add_work_rule_columns.py)**:

```python
"""Add work rule columns for F-08

Revision ID: 004
Revises: 003
"""

def upgrade() -> None:
    op.add_column('work_rules', sa.Column('industry_type', sa.String(50), nullable=False, server_default='other'))
    op.add_column('work_rules', sa.Column('ai_generated', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('work_rules', sa.Column('ai_model', sa.String(50), nullable=True))
    op.add_column('work_rules', sa.Column('revision_reason', sa.Text(), nullable=True))
    op.add_column('work_rules', sa.Column('total_worker_count', sa.Integer(), nullable=True))
    op.add_column('work_rules', sa.Column('cover_docx_url', sa.Text(), nullable=True))

    # 인덱스
    op.create_index('idx_work_rules_company_version', 'work_rules', ['company_id', 'version'])
    op.create_index('idx_work_rules_company_status', 'work_rules', ['company_id', 'status'])

def downgrade() -> None:
    op.drop_index('idx_work_rules_company_status')
    op.drop_index('idx_work_rules_company_version')
    op.drop_column('work_rules', 'cover_docx_url')
    op.drop_column('work_rules', 'total_worker_count')
    op.drop_column('work_rules', 'revision_reason')
    op.drop_column('work_rules', 'ai_model')
    op.drop_column('work_rules', 'ai_generated')
    op.drop_column('work_rules', 'industry_type')
```

### JSONB content 구조 (work_rules.content)

```json
{
  "sections": [
    {
      "section_number": 1,
      "title": "총칙",
      "content_html": "<p>제1조(목적) 이 규칙은 ...</p>",
      "is_required": true,
      "law_reference": "근로기준법 제93조 제1호"
    },
    {
      "section_number": 2,
      "title": "채용 및 근로계약",
      "content_html": "<p>제2조(채용 절차) ...</p>",
      "is_required": true,
      "law_reference": "근로기준법 제93조 제1호"
    }
  ]
}
```

### 근로기준법 제93조 법정 필수 기재사항 14개 항목 매핑

| section_number | title | law_reference |
|---|---|---|
| 1 | 업무의 시작과 종료 시각, 휴게시간, 휴일, 휴가 및 교대근로에 관한 사항 | 제93조 제1호 |
| 2 | 임금의 결정, 계산, 지급 방법, 임금의 산정기간, 지급시기 및 승급에 관한 사항 | 제93조 제2호 |
| 3 | 가족수당의 계산, 지급 방법에 관한 사항 | 제93조 제3호 |
| 4 | 퇴직에 관한 사항 | 제93조 제4호 |
| 5 | 퇴직급여, 상여 및 최저임금에 관한 사항 | 제93조 제5호 |
| 6 | 근로자의 식비, 작업용품 등의 부담에 관한 사항 | 제93조 제6호 |
| 7 | 근로자를 위한 교육시설에 관한 사항 | 제93조 제7호 |
| 8 | 출산전후휴가, 육아휴직 등 근로자의 모성 보호 및 일-가정 양립 지원에 관한 사항 | 제93조 제8호 |
| 9 | 안전과 보건에 관한 사항 | 제93조 제9호 |
| 10 | 근로자의 성별, 연령 또는 신체적 조건 등의 특성에 따른 사업장 환경의 개선에 관한 사항 | 제93조 제10호 |
| 11 | 업무상과 업무 외의 재해부조에 관한 사항 | 제93조 제11호 |
| 12 | 직장 내 괴롭힘의 예방 및 발생 시 조치 등에 관한 사항 | 제93조 제11의2호 |
| 13 | 표창과 제재에 관한 사항 | 제93조 제12호 |
| 14 | 기타 해당 사업 또는 사업장의 근로자 전체에 적용될 사항 | 제93조 제13호 |

---

## 5. 시퀀스 흐름

### 시나리오 1: 취업규칙 초안 생성 (템플릿 기반)

```
사용자 → Frontend(POST /work-rules)
  → API Layer (인증/company_id 검증)
  → WorkRuleService.create_work_rule()
    → CompanyRepository.get_by_id() (사업장 확인)
    → 업종별 템플릿 로드 (WORK_RULE_TEMPLATES[industry_type])
    → 14개 법정 섹션 초기화
    → WorkRuleRepository.create()
  → DB 저장 (status=draft, version=1)
  → 응답 반환
```

### 시나리오 2: AI 초안 생성

```
사용자 → Frontend(POST /work-rules/{id}/generate)
  → API Layer (인증/company_id 검증)
  → WorkRuleService.generate_ai_draft()
    → WorkRuleRepository.get_by_id_and_company() (존재 확인)
    → 상태 검증 (draft만 허용)
    → CompanyRepository.get_by_id() (회사 컨텍스트)
    → Claude API 호출 (시스템 프롬프트 + 업종 + 회사 정보 + 추가 컨텍스트)
    → 응답 파싱 → JSONB 섹션 구조화
    → WorkRuleRepository.update() (content, ai_generated=True)
  → DB 저장
  → 응답 반환
```

### 시나리오 3: 버전 개정

```
사용자 → Frontend(POST /work-rules/{id}/revise)
  → API Layer (인증/company_id 검증)
  → WorkRuleService.revise_work_rule()
    → WorkRuleRepository.get_by_id_and_company() (기존 active 버전 확인)
    → 기존 active 버전 → superseded로 변경
    → 새 WorkRule 생성 (version + 1, status=draft, content 복사)
    → WorkRuleRepository.create()
  → DB 저장
  → 응답 반환
```

### 시나리오 4: 10인 이상 사업장 자동 감지

```
사업장 관리 → 직원 수 변경 또는 직원 등록/퇴직
  → CompanyService에서 employee_count 업데이트
  → work_rule_required = (employee_count >= 10) (DB CHECK 제약조건)
  → 프론트엔드: 사업장 정보 조회 시 work_rule_required=true이면
    → 취업규칙 미작성 시 배너/알림 표시
```

(이 부분은 F-02에서 이미 구현된 CHECK 제약조건과 프론트엔드 알림 로직을 활용. F-08에서는 취업규칙 관리 페이지 진입 시 상태 표시만 추가.)

---

## 6. 영향 범위

### 수정 필요 파일
| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/db/models/work_rule.py` | 신규 컬럼 6개 추가 (industry_type, ai_generated, ai_model, revision_reason, total_worker_count, cover_docx_url) |
| `backend/app/db/models/__init__.py` | WorkRule import 확인 (이미 존재) |
| `backend/app/api/v1/router.py` | work_rules 라우터 include_router 추가 |

### 신규 생성 파일
| 파일 | 설명 |
|------|------|
| `backend/alembic/versions/004_add_work_rule_columns.py` | 마이그레이션 |
| `backend/app/api/v1/work_rules.py` | API 라우터 |
| `backend/app/schemas/work_rule.py` | Pydantic 스키마 |
| `backend/app/services/work_rule_service.py` | 비즈니스 로직 |
| `backend/app/repositories/work_rule_repo.py` | 데이터 접근 |
| `backend/app/services/work_rule_templates.py` | 업종별 템플릿 데이터 |
| `backend/app/ai/prompts/work_rule_prompt.py` | AI 프롬프트 |
| `backend/tests/api/test_work_rules_api.py` | API 통합 테스트 |
| `frontend/app/(main)/work-rules/page.tsx` | 취업규칙 관리 페이지 |
| `frontend/app/(main)/work-rules/[id]/page.tsx` | 취업규칙 상세/편집 페이지 |
| `frontend/components/work-rule/work-rule-list.tsx` | 목록 컴포넌트 |
| `frontend/components/work-rule/work-rule-editor.tsx` | 섹션별 편집기 |
| `frontend/components/work-rule/consent-checklist.tsx` | 동의 절차 체크리스트 |
| `frontend/components/work-rule/template-selector.tsx` | 업종 템플릿 선택기 |
| `frontend/lib/api/work-rule.ts` | API 클라이언트 |
| `frontend/lib/stores/work-rule-store.ts` | Zustand 스토어 |
| `frontend/types/work-rule.ts` | TypeScript 타입 |

---

## 7. 레이어별 상세 설계

### 7.1 Repository (work_rule_repo.py)

```python
class WorkRuleRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, work_rule_id: UUID) -> Optional[WorkRule]
    async def get_by_id_and_company(self, work_rule_id: UUID, company_id: UUID) -> Optional[WorkRule]
    async def list_by_company(self, company_id: UUID, status: str | None, skip: int, limit: int) -> list[WorkRule]
    async def count_by_company(self, company_id: UUID, status: str | None) -> int
    async def get_active_by_company(self, company_id: UUID) -> Optional[WorkRule]
    async def get_latest_version(self, company_id: UUID) -> int
    async def create(self, **kwargs) -> WorkRule
    async def update(self, work_rule: WorkRule, **kwargs) -> WorkRule
    async def delete(self, work_rule: WorkRule) -> None
```

### 7.2 Service (work_rule_service.py)

```python
class WorkRuleService:
    def __init__(self, db: AsyncSession, redis: aioredis.Redis) -> None:
        self.db = db
        self.repo = WorkRuleRepository(db)
        self.redis = redis

    async def create_work_rule(
        self, company_id: UUID, user_id: UUID,
        industry_type: str, effective_date: date | None
    ) -> dict
    # 업종 템플릿 기반 14개 섹션 초기화, version=1, status=draft

    async def get_work_rules(
        self, company_id: UUID, user_id: UUID,
        status: str | None, limit: int, skip: int
    ) -> list[dict]

    async def get_work_rule(
        self, work_rule_id: UUID, company_id: UUID, user_id: UUID
    ) -> dict

    async def update_work_rule(
        self, work_rule_id: UUID, company_id: UUID, user_id: UUID,
        content: dict | None, effective_date: date | None, status: str | None,
        worker_consent_count: int | None, total_worker_count: int | None,
        approval_date: date | None
    ) -> dict
    # draft/under_review 상태에서만 수정 가능

    async def delete_work_rule(
        self, work_rule_id: UUID, company_id: UUID, user_id: UUID
    ) -> None
    # draft 상태에서만 삭제 가능

    async def generate_ai_draft(
        self, work_rule_id: UUID, company_id: UUID, user_id: UUID,
        industry_type: str, additional_context: str | None
    ) -> dict
    # Claude API 호출 -> content 업데이트

    async def revise_work_rule(
        self, work_rule_id: UUID, company_id: UUID, user_id: UUID,
        revision_reason: str, effective_date: date | None
    ) -> dict
    # 기존 active -> superseded, 새 버전 생성

    async def generate_download(
        self, work_rule_id: UUID, company_id: UUID, user_id: UUID,
        file_type: str  # "docx" | "pdf"
    ) -> dict
    # Word/PDF 생성 -> S3 업로드 -> presigned URL 반환

    async def generate_cover_document(
        self, work_rule_id: UUID, company_id: UUID, user_id: UUID
    ) -> dict
    # 고용노동부 신고용 커버 서류 생성

    def get_consent_checklist(self, employee_count: int) -> dict
    # 동의 절차 체크리스트 반환 (동기 메서드)

    def get_templates(self, industry_type: str | None) -> list[dict]
    # 업종별 템플릿 반환 (동기 메서드)
```

### 7.3 Schema (work_rule.py)

```python
class WorkRuleSectionSchema(BaseModel):
    section_number: int = Field(..., ge=1, le=14)
    title: str = Field(..., min_length=1, max_length=200)
    content_html: str = Field(..., min_length=1)
    is_required: bool = True
    law_reference: str | None = None

class WorkRuleContentSchema(BaseModel):
    sections: list[WorkRuleSectionSchema]

class WorkRuleCreate(BaseModel):
    industry_type: Literal["manufacturing", "food_service", "service", "it"]
    effective_date: date | None = None

class WorkRuleUpdate(BaseModel):
    content: WorkRuleContentSchema | None = None
    effective_date: date | None = None
    status: Literal["draft", "under_review", "active"] | None = None
    worker_consent_count: int | None = Field(None, ge=0)
    total_worker_count: int | None = Field(None, ge=0)
    approval_date: date | None = None

class WorkRuleGenerateRequest(BaseModel):
    industry_type: Literal["manufacturing", "food_service", "service", "it"] | None = None
    additional_context: str | None = Field(None, max_length=1000)

class WorkRuleReviseRequest(BaseModel):
    revision_reason: str = Field(..., min_length=1, max_length=500)
    effective_date: date | None = None

class WorkRuleResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    version: int
    status: str
    industry_type: str
    content: dict
    effective_date: date | None
    approval_date: date | None
    worker_consent_count: int | None
    total_worker_count: int | None
    revision_reason: str | None
    ai_generated: bool
    ai_model: str | None
    docx_url: str | None
    pdf_url: str | None
    filed_at: str | None
    created_at: str
    updated_at: str

class WorkRuleListItem(BaseModel):
    id: uuid.UUID
    version: int
    status: str
    industry_type: str
    effective_date: date | None
    approval_date: date | None
    worker_consent_count: int | None
    ai_generated: bool
    filed_at: str | None
    created_at: str
    updated_at: str

class DownloadResponse(BaseModel):
    download_url: str
    filename: str
    expires_at: str

class ConsentChecklistStep(BaseModel):
    step: int
    title: str
    description: str
    law_reference: str
    is_required: bool

class ConsentChecklistResponse(BaseModel):
    checklist: list[ConsentChecklistStep]
    employee_count: int
    consent_threshold: int
    consent_type: str  # "majority" | "opinion"

class TemplateSection(BaseModel):
    section_number: int
    title: str
    description: str

class TemplateResponse(BaseModel):
    industry_type: str
    industry_name: str
    description: str
    sections: list[TemplateSection]
```

### 7.4 AI Prompt (work_rule_prompt.py)

```python
WORK_RULE_SYSTEM_PROMPT = """당신은 대한민국 노동법 전문가로서, 사업장의 취업규칙 초안을 작성합니다.

## 규칙
1. 근로기준법 제93조의 법정 필수 기재사항 14개 항목을 모두 포함하세요.
2. 업종 특성에 맞는 구체적인 내용을 작성하세요.
3. 각 섹션은 HTML 형식으로 작성하세요 (<p>, <ol>, <li> 등 사용).
4. 법령 인용 시 정확한 조항을 명시하세요.
5. 50인 미만 사업장에 적합한 내용으로 작성하세요.
6. 2026년 현행법 기준으로 작성하세요.

## 출력 형식
JSON 형식으로 각 섹션을 반환하세요:
{
  "sections": [
    {
      "section_number": 1,
      "title": "...",
      "content_html": "...",
      "law_reference": "근로기준법 제93조 제X호"
    }
  ]
}
"""

def build_work_rule_prompt(
    industry_type: str,
    company_name: str,
    employee_count: int,
    additional_context: str | None = None
) -> str:
    # 사용자 프롬프트 빌드
    ...
```

---

## 8. 성능 설계

### 인덱스 계획
- `idx_work_rules_company_version`: (company_id, version) -- 버전 이력 조회
- `idx_work_rules_company_status`: (company_id, status) -- 상태별 필터링, active 버전 조회

### 캐싱 전략
- 템플릿 데이터: Python 상수이므로 캐싱 불필요 (메모리 상주)
- 동의 절차 체크리스트: Python 상수이므로 캐싱 불필요
- AI 생성 결과: 캐싱하지 않음 (매번 고유한 결과)
- 취업규칙 조회: Redis 캐싱 선택 사항 (빈도 낮아 초기에는 불필요)

### Rate Limiting
| 엔드포인트 | 제한 | 근거 |
|---|---|---|
| POST /work-rules/{id}/generate | 5회/시간 | Claude API 비용 제어 |
| GET /work-rules/{id}/download/{type} | 20회/시간 | 문서 생성 비용 |
| 기타 CRUD | 100회/분 | 일반 API 기준 |

---

## 9. Frontend 설계

### 페이지 구조

| 경로 | 페이지 | 설명 |
|------|--------|------|
| `/work-rules` | 취업규칙 관리 | 목록, 새로 작성 버튼, 10인 미만 시 안내 |
| `/work-rules/[id]` | 취업규칙 상세/편집 | 섹션별 리치텍스트 편집기, 다운로드, 상태 변경 |

### 주요 컴포넌트

| 컴포넌트 | 설명 |
|----------|------|
| `template-selector.tsx` | 업종별 템플릿 선택 모달 (제조/서비스/IT/요식업) |
| `work-rule-list.tsx` | 취업규칙 목록 (버전, 상태 배지, 날짜) |
| `work-rule-editor.tsx` | 14개 섹션 아코디언 + 리치텍스트 편집기 |
| `consent-checklist.tsx` | 동의 절차 체크리스트 (진행 상태 트래커) |
| `work-rule-status-badge.tsx` | 상태 배지 (draft/under_review/active/superseded) |
| `work-rule-toolbar.tsx` | 액션 바 (AI 생성, 다운로드, 개정, 신고서류) |

### 리치텍스트 편집기 선택
- **TipTap** (ProseMirror 기반): headless, React 친화적, 커스터마이징 용이
- HTML 입출력 지원으로 content_html과 직접 호환

### Zustand 스토어

```typescript
interface WorkRuleStore {
  workRules: WorkRule[];
  currentWorkRule: WorkRule | null;
  isLoading: boolean;
  fetchWorkRules: () => Promise<void>;
  fetchWorkRule: (id: string) => Promise<void>;
  createWorkRule: (data: WorkRuleCreate) => Promise<WorkRule>;
  updateWorkRule: (id: string, data: WorkRuleUpdate) => Promise<void>;
  generateAiDraft: (id: string, data: GenerateRequest) => Promise<void>;
  reviseWorkRule: (id: string, data: ReviseRequest) => Promise<WorkRule>;
}
```

---

## 변경 이력

| 날짜 | 변경 내용 | 이유 |
|------|-----------|------|
| 2026-03-12 | 초기 설계 작성 | M4 마일스톤 F-08 착수 |
