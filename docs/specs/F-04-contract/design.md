# F-04 근로계약서 자동 생성 — 기술 설계서

## 1. 참조
- 인수조건: docs/project/features.md #F-04
- 시스템 설계: docs/system/system-design.md
- ERD: docs/system/erd.md
- API 컨벤션: docs/system/api-conventions.md

---

## 2. 아키텍처 결정

### 결정 1: 문서 생성 파이프라인
- **선택지**:
  - A) 동기 생성 (요청 → 생성 → 응답)
  - B) 비동기 생성 (요청 → 큐 → 작업 → 알림)
- **결정**: A) 동기 생성 (초기) + B) 비동기 (확장 시)
- **근거**:
  - 초기에는 계약서 1건 생성이 5초 이내로 완료되어 동기 처리 가능
  - 사용자 경험상 즉시 미리보기 선호
  - 향후 대량 생성 요구 시 Redis Queue 기반 비동기 확장

### 결정 2: 다국어 지원 방식
- **선택지**:
  - A) Claude API에 다국어 번역 요청
  - B) 템플릿 기반 다국어 (한국어 템플릿 → 번역 파일)
  - C) 혼합 (법적 필수 문구는 템플릿, 나머지는 Claude 번역)
- **결정**: C) 혼합 방식
- **근거**:
  - 법적 필수 기재사항은 정확한 번역 필수 → 템플릿 사용
  - 특약 사항 등 가변 부분은 Claude 번역으로 유연성 확보
  - 번역 품질 검증 용이

### 결정 3: 파일 저장소
- **선택지**:
  - A) 로컬 파일 시스템
  - B) AWS S3
  - C) DB BLOB
- **결정**: B) AWS S3
- **근거**:
  - 확장성 (다중 서버 환경 대응)
  - Presigned URL로 보안 다운로드
  - 비용 효율성 (S3 Standard-IA로 자동 전환)

### 결정 4: 알림 스케줄러
- **선택지**:
  - A) APScheduler (In-process)
  - B) Celery Beat + Redis
  - C) 별도 스케줄러 서비스 (AWS EventBridge)
- **결정**: A) APScheduler (초기) → B) Celery Beat (확장 시)
- **근거**:
  - 초기에는 단순한 스케줄링으로 충분
  - M2 마일스톤에서는 APScheduler로 빠르게 구현
  - 향후 트래픽 증가 시 Celery로 전환

---

## 3. API 설계

### 3.1 POST /api/v1/contracts
- **목적**: 근로계약서 생성 (초안 저장)
- **인증**: 필요 (JWT)
- **Rate Limit**: 10회/시간 (플랜별 차등)
- **Request Body**:
```json
{
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "contract_type": "regular",
  "start_date": "2026-03-01",
  "end_date": null,
  "work_location": "서울시 강남구 테헤란로 123",
  "work_hours_per_week": 40,
  "work_start_time": "09:00",
  "work_end_time": "18:00",
  "break_minutes": 60,
  "work_days": "mon,tue,wed,thu,fri",
  "wage_type": "monthly",
  "base_wage": 2500000,
  "meal_allowance": 100000,
  "transport_allowance": 50000,
  "probation_months": 3,
  "probation_wage_rate": 1.0,
  "nda_included": true,
  "non_compete_included": false,
  "language": "ko"
}
```
- **Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "employee_name": "홍길동",
    "contract_type": "regular",
    "status": "draft",
    "start_date": "2026-03-01",
    "end_date": null,
    "work_hours_per_week": 40,
    "base_wage": 2500000,
    "warnings": [],
    "created_at": "2026-03-02T10:00:00Z"
  },
  "message": "근로계약서 초안이 생성되었습니다."
}
```
- **에러 케이스**:
| 코드 | HTTP | 상황 |
|------|------|------|
| E-4004 | 404 | 직원을 찾을 수 없음 |
| E-5001 | 422 | 최저임금 기준 미달 |
| E-5002 | 422 | 주 52시간 초과 |
| E-2005 | 403 | 다른 사업장 직원 접근 |

### 3.2 POST /api/v1/contracts/{id}/generate
- **목적**: Claude API로 계약서 본문 생성
- **인증**: 필요
- **Rate Limit**: 10회/시간
- **Request Body**:
```json
{
  "additional_terms": "재택근무 협의 가능"
}
```
- **Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "generated_content": {
      "sections": [
        {
          "title": "제1조 (목적)",
          "content": "이 계약서는..."
        },
        {
          "title": "제2조 (근로계약기간)",
          "content": "본 계약의 기간은..."
        }
      ],
      "mandatory_items": {
        "included": true,
        "items_count": 8
      }
    },
    "ai_model": "claude-sonnet-4-6",
    "generated_at": "2026-03-02T10:01:00Z"
  }
}
```

### 3.3 POST /api/v1/contracts/{id}/generate-docx
- **목적**: Word(.docx) 파일 생성 및 S3 업로드
- **인증**: 필요
- **Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "download_url": "https://s3.amazonaws.com/bucket/contracts/xxx.docx?X-Amz-Signature=...",
    "expires_at": "2026-03-03T10:00:00Z",
    "filename": "근로계약서_홍길동_20260302.docx"
  }
}
```

### 3.4 POST /api/v1/contracts/{id}/generate-pdf
- **목적**: PDF 파일 생성 및 S3 업로드
- **인증**: 필요
- **Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "download_url": "https://s3.amazonaws.com/bucket/contracts/xxx.pdf?X-Amz-Signature=...",
    "expires_at": "2026-03-03T10:00:00Z",
    "filename": "근로계약서_홍길동_20260302.pdf"
  }
}
```

### 3.5 GET /api/v1/contracts
- **목적**: 계약서 목록 조회
- **인증**: 필요
- **Query Parameters**:
  - `employee_id` (선택): 직원별 필터
  - `status` (선택): draft/sent/signed/expired/terminated
  - `expiring_within_days` (선택): N일 내 만료 예정
- **Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "660e8400-...",
      "employee_name": "홍길동",
      "contract_type": "regular",
      "start_date": "2026-03-01",
      "end_date": null,
      "status": "draft",
      "days_until_expiry": null
    }
  ],
  "pagination": {
    "cursor": null,
    "has_next": false,
    "limit": 20
  }
}
```

### 3.6 GET /api/v1/contracts/{id}
- **목적**: 계약서 상세 조회
- **인증**: 필요
- **Response** (200 OK): 전체 계약서 정보 + 생성된 본문

### 3.7 PATCH /api/v1/contracts/{id}
- **목적**: 계약서 수정 (draft 상태만 가능)
- **인증**: 필요
- **Request Body**: POST와 동일 (부분 수정 가능)

### 3.8 POST /api/v1/contracts/{id}/send-for-signature
- **목적**: 전자서명 요청 (F-14 연동, Phase 2)
- **인증**: 필요
- **상태**: 구현 예정 (M6)

### 3.9 GET /api/v1/contracts/templates
- **목적**: 고용형태별 템플릿 목록
- **인증**: 필요
- **Response**:
```json
{
  "success": true,
  "data": [
    {
      "contract_type": "regular",
      "name": "정규직 근로계약서",
      "description": "무기계약 정규직 근로계약서",
      "mandatory_fields": ["work_location", "work_hours_per_week", ...]
    },
    {
      "contract_type": "part_time",
      "name": "시간제 근로계약서",
      "description": "주 15시간 미만 단시간 근로자",
      "mandatory_fields": [...]
    }
  ]
}
```

---

## 4. DB 설계

### 4.1 contracts 테이블 (기존 ERD 활용)

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 계약서 고유 ID |
| employee_id | UUID | FK, NOT NULL | 직원 ID |
| company_id | UUID | FK, NOT NULL | 사업장 ID |
| contract_type | VARCHAR(30) | NOT NULL | regular/fixed_term/part_time/daily/probation/foreign_worker |
| start_date | DATE | NOT NULL | 계약 시작일 |
| end_date | DATE | NULL | 계약 종료일 (NULL=무기계약) |
| work_location | TEXT | NOT NULL | 근무지 |
| work_hours_per_week | NUMERIC(4,1) | NOT NULL | 주 소정근로시간 |
| work_start_time | TIME | NOT NULL | 근무 시작시간 |
| work_end_time | TIME | NOT NULL | 근무 종료시간 |
| break_minutes | INTEGER | NOT NULL, DEFAULT 60 | 휴게시간 (분) |
| work_days | VARCHAR(20) | NOT NULL | 근무요일 (콤마 구분) |
| wage_type | VARCHAR(20) | NOT NULL | monthly/hourly/daily |
| base_wage | NUMERIC(12,0) | NOT NULL | 기본급 |
| meal_allowance | NUMERIC(10,0) | DEFAULT 0 | 식대 |
| transport_allowance | NUMERIC(10,0) | DEFAULT 0 | 교통비 |
| probation_months | INTEGER | DEFAULT 0 | 수습기간 (개월) |
| probation_wage_rate | NUMERIC(3,2) | DEFAULT 1.0 | 수습 임금 비율 |
| nda_included | BOOLEAN | DEFAULT FALSE | 비밀유지 조항 포함 |
| non_compete_included | BOOLEAN | DEFAULT FALSE | 경업금지 조항 포함 |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'draft' | draft/sent/signed/expired/terminated |
| generated_content | JSONB | NULL | Claude 생성 본문 (추가 필요) |
| docx_url | TEXT | NULL | Word 파일 S3 URL |
| pdf_url | TEXT | NULL | PDF 파일 S3 URL |
| ai_generated | BOOLEAN | NOT NULL, DEFAULT TRUE | AI 생성 여부 |
| ai_model | VARCHAR(50) | NULL | 사용된 AI 모델 |
| language | VARCHAR(10) | DEFAULT 'ko' | 언어 (ko/en/zh/vi) |
| signed_at | TIMESTAMPTZ | NULL | 서명일시 |
| sign_service_ref | VARCHAR(200) | NULL | 전자서명 서비스 참조 |
| expiry_notice_30_sent | BOOLEAN | DEFAULT FALSE | D-30 알림 발송 여부 |
| expiry_notice_7_sent | BOOLEAN | DEFAULT FALSE | D-7 알림 발송 여부 |
| version | INTEGER | NOT NULL, DEFAULT 1 | 버전 |
| created_at | TIMESTAMPTZ | NOT NULL | 생성일시 |
| updated_at | TIMESTAMPTZ | NOT NULL | 수정일시 |

### 4.2 새 컬럼 추가 (마이그레이션 필요)

```sql
-- generated_content 컬럼 추가
ALTER TABLE contracts ADD COLUMN generated_content JSONB;

-- language 컬럼 추가
ALTER TABLE contracts ADD COLUMN language VARCHAR(10) DEFAULT 'ko';

-- 인덱스 추가
CREATE INDEX idx_contracts_expiry ON contracts(end_date)
  WHERE end_date IS NOT NULL AND status IN ('draft', 'signed');
```

---

## 5. 시퀀스 흐름

### 5.1 계약서 생성 플로우

```
┌─────────┐     ┌────────────┐     ┌─────────┐     ┌──────────┐     ┌──────┐
│ Frontend│     │ Backend API│     │ Contract│     │ Claude   │     │  S3  │
│         │     │            │     │ Service │     │ API      │     │      │
└────┬────┘     └─────┬──────┘     └────┬────┘     └────┬─────┘     └──┬───┘
     │                │                 │               │              │
     │ POST /contracts│                 │               │              │
     │ {employee_id,  │                 │               │              │
     │  work_info...} │                 │               │              │
     │───────────────>│                 │               │              │
     │                │                 │               │              │
     │                │ validate_input()│               │              │
     │                │────────────────>│               │              │
     │                │                 │               │              │
     │                │                 │ check_minimum_wage()         │
     │                │                 │─────────────────────────────>│
     │                │                 │ (labor_law_rates)            │
     │                │                 │               │              │
     │                │                 │ check_52hours()│              │
     │                │                 │───────────────│              │
     │                │                 │               │              │
     │                │                 │ create_draft()│              │
     │                │                 │──────────────>│              │
     │                │                 │               │              │
     │ 201 Created    │                 │               │              │
     │ {id, status:   │                 │               │              │
     │  "draft"}      │                 │               │              │
     │<───────────────│                 │               │              │
     │                │                 │               │              │
     │ POST /contracts/{id}/generate   │               │              │
     │───────────────>│                 │               │              │
     │                │                 │               │              │
     │                │ generate_content()              │              │
     │                │────────────────>│               │              │
     │                │                 │               │              │
     │                │                 │ build_prompt()│              │
     │                │                 │──────────────>│              │
     │                │                 │               │              │
     │                │                 │ messages API  │              │
     │                │                 │──────────────>│              │
     │                │                 │               │              │
     │                │                 │ generated_text│              │
     │                │                 │<──────────────│              │
     │                │                 │               │              │
     │                │                 │ parse_sections()              │
     │                │                 │───────────────│              │
     │                │                 │               │              │
     │                │                 │ save_content()│              │
     │                │                 │──────────────>│              │
     │                │                 │               │              │
     │ 200 OK         │                 │               │              │
     │ {sections...}  │                 │               │              │
     │<───────────────│                 │               │              │
     │                │                 │               │              │
     │ POST /contracts/{id}/generate-docx               │              │
     │───────────────>│                 │               │              │
     │                │                 │               │              │
     │                │                 │ create_docx() │              │
     │                │                 │ (python-docx) │              │
     │                │                 │               │              │
     │                │                 │ upload_to_s3()│              │
     │                │                 │──────────────────────────────>│
     │                │                 │               │              │
     │                │                 │ generate_presigned_url()      │
     │                │                 │──────────────────────────────>│
     │                │                 │               │              │
     │ 200 OK         │                 │               │              │
     │ {download_url} │                 │               │              │
     │<───────────────│                 │               │              │
```

### 5.2 만료 알림 스케줄러

```
┌────────────────┐     ┌──────────────┐     ┌─────────┐     ┌────────┐
│ APScheduler    │     │ Notification │     │  Redis  │     │ Kakao/ │
│ (매일 09:00)   │     │   Service    │     │         │     │ Email  │
└───────┬────────┘     └──────┬───────┘     └────┬────┘     └───┬────┘
        │                     │                  │              │
        │ check_expiring_contracts()             │              │
        │────────────────────>│                  │              │
        │                     │                  │              │
        │                     │ find D-30, D-7   │              │
        │                     │ contracts        │              │
        │                     │─────────────────>│              │
        │                     │                  │              │
        │                     │ contracts list   │              │
        │                     │<─────────────────│              │
        │                     │                  │              │
        │                     │ for each contract:              │
        │                     │ send_notification()             │
        │                     │─────────────────────────────────>│
        │                     │                  │              │
        │                     │ mark notice_sent│              │
        │                     │─────────────────>│              │
        │                     │                  │              │
```

---

## 6. 영향 범위

### 6.1 수정 필요 파일
| 파일 | 변경 내용 |
|------|----------|
| backend/app/db/models/contract.py | generated_content, language 컬럼 추가 |
| backend/app/api/v1/router.py | contracts 라우터 등록 |
| backend/app/core/exceptions.py | MinimumWageError, WorkHoursExceededError 추가 |

### 6.2 신규 생성 파일
| 파일 | 설명 |
|------|------|
| backend/app/api/v1/contracts.py | 계약서 API 라우터 |
| backend/app/services/contract_service.py | 계약서 비즈니스 로직 |
| backend/app/services/document_service.py | Word/PDF 생성 로직 |
| backend/app/services/notification_service.py | 알림 발송 로직 |
| backend/app/repositories/contract_repo.py | 계약서 레포지토리 |
| backend/app/schemas/contract.py | 계약서 스키마 |
| backend/app/ai/prompts/contract_prompt.py | Claude 프롬프트 템플릿 |
| backend/app/utils/wage_validator.py | 최저임금/52시간 검증 |
| backend/app/workers/contract_expiry_worker.py | 만료 알림 워커 |
| alembic/versions/xxx_add_contract_fields.py | 마이그레이션 |

---

## 7. 성능 설계

### 7.1 인덱스 계획

```sql
-- 기존 인덱스 (ERD 참조)
CREATE INDEX idx_contracts_employee_id ON contracts(employee_id);
CREATE INDEX idx_contracts_company_id ON contracts(company_id);
CREATE INDEX idx_contracts_end_date ON contracts(end_date);
CREATE INDEX idx_contracts_status ON contracts(status);

-- 추가 인덱스
CREATE INDEX idx_contracts_expiry_check ON contracts(end_date, status)
  WHERE end_date IS NOT NULL AND status IN ('draft', 'signed');

-- 만료 알림 체크용 부분 인덱스
CREATE INDEX idx_contracts_expiry_30 ON contracts(end_date, expiry_notice_30_sent)
  WHERE end_date IS NOT NULL AND expiry_notice_30_sent = FALSE;

CREATE INDEX idx_contracts_expiry_7 ON contracts(end_date, expiry_notice_7_sent)
  WHERE end_date IS NOT NULL AND expiry_notice_7_sent = FALSE;
```

### 7.2 캐싱 전략

| 데이터 | 캐시 위치 | TTL | 설명 |
|--------|----------|-----|------|
| 최저임금 요율 | Redis | 24시간 | labor_law_rates 캐시 |
| 계약서 템플릿 | Redis | 1시간 | 고용형태별 템플릿 |
| Claude 생성 결과 | DB (JSONB) | 영구 | 재사용 가능 |
| Presigned URL | - | 24시간 | S3 설정 |

### 7.3 Claude API 호출 최적화

```python
# 토큰 최적화 설정
MAX_PROMPT_TOKENS = 4000
MAX_OUTPUT_TOKENS = 4000
TEMPERATURE = 0.3  # 일관성 높은 출력

# 프롬프트 구조
SYSTEM_PROMPT = "근로기준법 전문가로서..."
CONTEXT = f"""
사업장 정보: {company_info}
직원 정보: {employee_info}
계약 조건: {contract_conditions}
법정 필수 기재사항 8개: {mandatory_items}
"""

USER_PROMPT = f"""
위 정보를 바탕으로 {contract_type} 근로계약서를 작성해주세요.
언어: {language}
특약 사항: {additional_terms}
"""
```

---

## 8. 보안 설계

### 8.1 권한 체크
```python
# 모든 계약서 API에서 검증
async def verify_contract_access(
    contract_id: UUID,
    user_id: UUID,
    company_id: UUID
) -> Contract:
    contract = await repo.get_with_company(contract_id)
    if contract.company_id != company_id:
        raise ForbiddenError("접근 권한이 없습니다.")
    return contract
```

### 8.2 파일 다운로드 보안
- S3 Presigned URL 사용 (24시간 유효)
- URL에 서명 포함 (위변조 방지)
- 다운로드 로그 기록

### 8.3 민감정보 처리
- 주민등록번호는 계약서에 마스킹하여 표시 (******-1******)
- 급여 정보는 암호화하여 전송

---

## 9. 다국어 지원

### 9.1 지원 언어
| 코드 | 언어 | 비고 |
|------|------|------|
| ko | 한국어 | 기본 |
| en | 영어 | 외국인 근로자 |
| zh | 중국어 | 중국인 근로자 |
| vi | 베트남어 | 베트남인 근로자 |

### 9.2 번역 방식
```python
LANGUAGE_TEMPLATES = {
    "ko": {
        "contract_title": "표준근로계약서",
        "article_1": "제1조 (목적)",
        # ...
    },
    "en": {
        "contract_title": "Standard Employment Contract",
        "article_1": "Article 1 (Purpose)",
        # ...
    },
    # zh, vi ...
}

# Claude API 호출 시 언어 지정
prompt = f"Write the contract in {LANGUAGE_NAMES[language]}."
```

---

## 10. 법정 필수 기재사항 (근로기준법 제17조)

| 번호 | 항목 | 계약서 필드 | 검증 |
|------|------|------------|------|
| 1 | 근로계약기간 | start_date, end_date | 필수 |
| 2 | 근로장소 | work_location | 필수 |
| 3 | 업무 내용 | - | 직원 직급/부서 참조 |
| 4 | 근로시간 | work_start_time, work_end_time, break_minutes | 필수 |
| 5 | 휴일 | work_days | 필수 |
| 6 | 임금 | base_wage, wage_type | 필수 + 최저임금 검증 |
| 7 | 임금 지급일 | - | 사업장 기본 설정 (매월 25일 등) |
| 8 | 연차유급휴가 | - | 법정 연차 안내 문구 자동 추가 |

---

## 11. 검증 로직

### 11.1 최저임금 검증
```python
async def validate_minimum_wage(
    base_wage: Decimal,
    wage_type: str,
    work_hours_per_week: Decimal,
    year: int
) -> bool:
    # labor_law_rates에서 최저임금 조회
    minimum_wage = await get_minimum_wage(year)  # 시간당 원화

    if wage_type == "hourly":
        hourly_wage = base_wage
    elif wage_type == "monthly":
        # 월급 → 시급 변환
        # 시급 = 월급 / (주소정근로시간 × 52/12 + 주휴시간)
        hourly_wage = base_wage / (work_hours_per_week * 52/12 * (1 + 1/5))
    elif wage_type == "daily":
        hourly_wage = base_wage / 8  # 1일 8시간 가정

    if hourly_wage < minimum_wage:
        raise MinimumWageError(
            current_wage=hourly_wage,
            minimum_wage=minimum_wage,
            year=year
        )

    return True
```

### 11.2 주 52시간 검증
```python
def validate_work_hours(work_hours_per_week: Decimal) -> tuple[bool, str]:
    if work_hours_per_week > 52:
        return False, "주 52시간을 초과합니다. 연장근로 협의가 필요합니다."
    elif work_hours_per_week > 40:
        return True, "warning"  # 경고만 표시
    return True, "ok"
```

---

## 12. 알림 스케줄러 설계

### 12.1 APScheduler 설정
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# 매일 09:00 실행
@scheduler.scheduled_job('cron', hour=9, minute=0)
async def check_contract_expiry():
    today = date.today()

    # D-30 알림
    d30 = today + timedelta(days=30)
    contracts_30 = await contract_repo.find_expiring(
        expiry_date=d30,
        notice_type="30"
    )

    for contract in contracts_30:
        await notification_service.send_expiry_notice(
            contract=contract,
            days_remaining=30
        )
        await contract_repo.mark_notice_sent(contract.id, "30")

    # D-7 알림 (동일 로직)
```

### 12.2 알림 내용
```json
{
  "template": "contract_expiry",
  "data": {
    "employee_name": "홍길동",
    "contract_end_date": "2026-04-01",
    "days_remaining": 30,
    "action_url": "/contracts/{contract_id}"
  }
}
```

---

## 변경 이력

| 날짜 | 변경 내용 | 이유 |
|------|----------|------|
| 2026-03-02 | 초기 작성 | F-04 기능 설계 |
