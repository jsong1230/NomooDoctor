# F-08 취업규칙 자동화 - DB 스키마 확정본

## 개요
F-08 취업규칙 자동화 기능에서 사용하는 데이터베이스 스키마입니다. 기존 work_rules 테이블을 확장하여 구현합니다.

---

## 테이블 스키마

### work_rules (기존 테이블 확장)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|---------|------|
| id | UUID | PK | 취업규칙 ID |
| company_id | UUID | FK, NOT NULL | 사업장 ID (companies 테이블 참조) |
| version | INTEGER | NOT NULL, DEFAULT 1 | 버전 번호 (1부터 시작) |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'draft', CHECK | 상태: draft / under_review / active / superseded |
| content | JSONB | NOT NULL | 14개 법정 섹션 내용 (sections 배열) |
| **industry_type** | **VARCHAR(50)** | **NOT NULL, DEFAULT 'other'** | **새 컬럼: 작성 시 사용한 업종 템플릿** |
| **ai_generated** | **BOOLEAN** | **NOT NULL, DEFAULT FALSE** | **새 컬럼: AI 생성 여부** |
| **ai_model** | **VARCHAR(50)** | **NULL** | **새 컬럼: 사용된 AI 모델명** |
| **revision_reason** | **TEXT** | **NULL** | **새 컬럼: 개정 사유** |
| **total_worker_count** | **INTEGER** | **NULL** | **새 컬럼: 전체 근로자 수** |
| **cover_docx_url** | **TEXT** | **NULL** | **새 컬럼: 고용노동부 신고용 커버 서류 URL** |
| docx_url | VARCHAR | NULL | 생성된 Word 파일 URL |
| pdf_url | VARCHAR | NULL | 생성된 PDF 파일 URL |
| effective_date | DATE | NULL | 효력 발생일 |
| approval_date | DATE | NULL | 승인일 |
| worker_consent_count | INTEGER | NULL | 동의한 근로자 수 |
| filed_at | TIMESTAMP WITH TIME ZONE | NULL | 고용노동부 신고 일시 |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | 생성 일시 |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | 수정 일시 |

**주요 제약조건**:
- CHECK: `status IN ('draft', 'under_review', 'active', 'superseded')`
- FK: company_id → companies(id) ON DELETE CASCADE
- 한 사업장당 하나의 active 버전만 유지

---

## 인덱스

| 인덱스명 | 컬럼 | 타입 | 목적 |
|---------|------|------|------|
| pk_work_rules | id | PRIMARY | 기본 키 |
| fk_work_rules_company | company_id | FOREIGN KEY | 사업장 참조 |
| **idx_work_rules_company_version** | **(company_id, version)** | **새 추가** | **버전 이력 조회 (version 내림차순 정렬)** |
| **idx_work_rules_company_status** | **(company_id, status)** | **새 추가** | **상태별 필터링, active 버전 조회** |

---

## JSONB content 구조

```json
{
  "sections": [
    {
      "section_number": 1,
      "title": "업무의 시작과 종료 시각, 휴게시간, 휴일, 휴가 및 교대근로에 관한 사항",
      "content_html": "<h2>제1조 (근로시간)</h2><p>근로자의 근로시간은 월~금 09:00~18:00(점심시간 12:00~13:00)으로 합니다.</p>",
      "is_required": true,
      "law_reference": "근로기준법 제93조 제1호"
    },
    {
      "section_number": 2,
      "title": "임금의 결정, 계산, 지급 방법, 임금의 산정기간, 지급시기 및 승급에 관한 사항",
      "content_html": "<h2>제1조 (임금의 구성)</h2><p>임금은 기본급 및 각종 수당으로 구성합니다.</p>",
      "is_required": true,
      "law_reference": "근로기준법 제93조 제2호"
    },
    ...
    {
      "section_number": 14,
      "title": "기타 해당 사업 또는 사업장의 근로자 전체에 적용될 사항",
      "content_html": "<h2>제1조 (기타)</h2><p>본 규칙에 명시되지 않은 사항은 법령을 따릅니다.</p>",
      "is_required": true,
      "law_reference": "근로기준법 제93조 제13호"
    }
  ]
}
```

**필드 설명**:
- `section_number`: 1~14 (근로기준법 제93조 법정 필수 기재사항)
- `title`: 섹션 제목
- `content_html`: HTML 형식의 섹션 본문 (리치텍스트 에디터 호환)
- `is_required`: 항상 true (법정 필수 항목)
- `law_reference`: 관련 법령 인용

---

## 마이그레이션 (004번)

### 업그레이드 SQL
```sql
-- 컬럼 추가
ALTER TABLE work_rules
ADD COLUMN industry_type VARCHAR(50) NOT NULL DEFAULT 'other',
ADD COLUMN ai_generated BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN ai_model VARCHAR(50),
ADD COLUMN revision_reason TEXT,
ADD COLUMN total_worker_count INTEGER,
ADD COLUMN cover_docx_url TEXT;

-- 인덱스 생성
CREATE INDEX idx_work_rules_company_version
ON work_rules (company_id, version);

CREATE INDEX idx_work_rules_company_status
ON work_rules (company_id, status);
```

### 다운그레이드 SQL
```sql
-- 인덱스 삭제
DROP INDEX IF EXISTS idx_work_rules_company_status;
DROP INDEX IF EXISTS idx_work_rules_company_version;

-- 컬럼 삭제
ALTER TABLE work_rules
DROP COLUMN cover_docx_url,
DROP COLUMN total_worker_count,
DROP COLUMN revision_reason,
DROP COLUMN ai_model,
DROP COLUMN ai_generated,
DROP COLUMN industry_type;
```

---

## 데이터 관계도

```
users (1) ──────┐
                 │
                 ├──────→ (N) companies
                 │           ↓ (1)
                 │           ├─ (N) work_rules
                 │           │
                 │           ├─ (N) employees
                 │           │
                 │           └─ (N) contracts
                 │
            └────┘
```

---

## 주요 쿼리 패턴

### 패턴 1: 사업장의 active 취업규칙 조회
```python
stmt = select(WorkRule).where(
    (WorkRule.company_id == company_id) &
    (WorkRule.status == "active")
).order_by(WorkRule.version.desc()).limit(1)
```
**인덱스**: idx_work_rules_company_status

### 패턴 2: 사업장의 모든 버전 조회
```python
stmt = select(WorkRule).where(
    WorkRule.company_id == company_id
).order_by(WorkRule.created_at.desc())
```
**인덱스**: idx_work_rules_company_version

### 패턴 3: 최신 버전 번호 조회
```python
stmt = select(func.max(WorkRule.version)).where(
    WorkRule.company_id == company_id
)
```
**인덱스**: idx_work_rules_company_version (compound index의 첫 번째 컬럼)

---

## 성능 고려사항

### N+1 쿼리 방지
- 사업장 정보가 필요한 경우: `include(WorkRule.company)` 사용
- 예시:
  ```python
  stmt = select(WorkRule).options(
      joinedload(WorkRule.company)
  ).where(WorkRule.company_id == company_id)
  ```

### 대용량 조회
- 페이지네이션 필수: LIMIT와 OFFSET 사용
- content JSONB 검색이 필요한 경우 GIN 인덱스 고려 (향후)

### 캐싱 전략
- 템플릿 데이터: Python 상수 (메모리 상주)
- 동의 절차 체크리스트: Python 상수
- 취업규칙 조회: Redis 캐싱 선택 (현재 구현 없음, 필요시 추가)

---

## 업종별 템플릿 데이터

기존 테이블에는 저장하지 않으며, Python 상수(`app/services/work_rule_templates.py`)로 관리:

```python
WORK_RULE_TEMPLATES = {
    "manufacturing": {
        "industry_name": "제조업",
        "sections": [...]
    },
    "food_service": {
        "industry_name": "요식업",
        "sections": [...]
    },
    "service": {
        "industry_name": "서비스업",
        "sections": [...]
    },
    "it": {
        "industry_name": "IT업",
        "sections": [...]
    }
}
```

**장점**:
- 마이그레이션 불필요
- 배포 시 버전 관리
- 빠른 조회

---

## 상태 전환 규칙

```
draft ──→ under_review ──→ active ──→ superseded
  ↓           ↓                ↓
  └───── 삭제 (DELETE) 가능
```

**상태 설명**:
- **draft**: 작성 중 (수정, 삭제 가능)
- **under_review**: 검토 중 (수정 가능, 삭제 불가)
- **active**: 활성화됨 (수정 불가, 개정만 가능)
- **superseded**: 폐지됨 (읽기만 가능)

---

## 변경 이력

| 날짜 | 마이그레이션 | 변경 내용 | 상태 |
|------|-----------|-----------|------|
| 2026-03-12 | 004 | work_rules 테이블 확장 (6개 컬럼, 2개 인덱스) | 적용됨 |
