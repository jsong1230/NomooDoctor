# F-09 퇴직금/해고 계산기 -- 기술 설계서

## 1. 참조

- 인수조건: docs/project/features.md #F-09
- 시스템 설계: docs/system/system-design.md
- ERD: docs/system/erd.md
- API 컨벤션: docs/system/api-conventions.md
- 의존 기능: F-03 (직원 관리), F-05 (급여 자동 계산기)

---

## 2. 아키텍처 결정

### 결정 1: 퇴직금 계산 결과 저장 전략

- **선택지**: A) 매번 실시간 계산만 제공 / B) 계산 결과를 DB에 저장하여 이력 관리
- **결정**: B) DB 저장 + 실시간 계산(미리보기)
- **근거**: 퇴직금 산출 내역은 법적 증빙이므로 확정 후 DB에 보관 필요. 미리보기(시뮬레이션)는 저장하지 않고, 확정 시에만 저장.

### 결정 2: 해고 절차 가이드 생성 방식

- **선택지**: A) 정적 템플릿 기반 / B) Claude API 동적 생성
- **결정**: B) Claude API 동적 생성 + 정적 체크리스트 병행
- **근거**: 위험 케이스(임신/육아휴직/노조활동) 감지 등 컨텍스트 반영 필요. 체크리스트는 정적으로 제공하되, 상세 가이드는 Claude API 활용.

### 결정 3: 평균임금 산출을 위한 급여 데이터 소스

- **선택지**: A) payslips 테이블에서 최근 3개월 조회 / B) 사용자가 직접 입력
- **결정**: A) payslips 우선 조회 + B) 수동 입력 fallback
- **근거**: payslips 데이터가 있으면 자동으로 채우고, 없으면 사용자가 수동 입력하도록 하여 유연성 확보.

### 결정 4: 위험 케이스 감지 방식

- **선택지**: A) 사용자 입력 기반 / B) 직원 데이터 자동 분석
- **결정**: A) 사용자 입력 기반 (체크리스트)
- **근거**: 임신/육아휴직/노조활동 상태를 DB에 저장하지 않으므로, 해고 절차 시 사용자가 해당 사항을 체크하는 방식. 향후 F-13(근태) 연동 후 자동화 가능.

---

## 3. API 설계

### 3.1 POST /api/v1/retirement/calculate

- **목적**: 퇴직금 시뮬레이션 (미리보기, DB 저장 안 함)
- **인증**: 필요
- **Request Body**:

```json
{
  "employee_id": "uuid",
  "resign_date": "2026-03-31",
  "annual_bonus": 0,
  "unused_annual_leave_days": 0,
  "monthly_wages": [
    {
      "year": 2026,
      "month": 1,
      "total_wage": 3000000,
      "days_in_month": 31
    },
    {
      "year": 2026,
      "month": 2,
      "total_wage": 3000000,
      "days_in_month": 28
    },
    {
      "year": 2026,
      "month": 3,
      "total_wage": 3000000,
      "days_in_month": 31
    }
  ]
}
```

필드 설명:
- `employee_id`: 직원 UUID (hire_date, salary_settings 자동 참조)
- `resign_date`: 퇴사 예정일
- `annual_bonus`: 연간 상여금 총액 (기본값 0)
- `unused_annual_leave_days`: 미사용 연차 일수 (기본값 0)
- `monthly_wages`: 최근 3개월 급여 정보 (선택). 미제공 시 payslips에서 자동 조회

- **Response 200**:

```json
{
  "success": true,
  "data": {
    "employee_id": "uuid",
    "employee_name": "홍길동",
    "hire_date": "2023-01-02",
    "resign_date": "2026-03-31",
    "total_service_days": 1184,
    "average_daily_wage": 101111,
    "severance_pay": 3268028,
    "unused_leave_pay": 303333,
    "bonus_included": 250000,
    "total_payment": 3821361,
    "payment_deadline": "2026-04-14",
    "eligible": true,
    "calculation_detail": {
      "last_3_months_total_wage": 9000000,
      "last_3_months_total_days": 90,
      "bonus_3_months_share": 750000,
      "average_daily_wage": 108333,
      "severance_formula": "108333 * 30 * (1184 / 365)",
      "unused_leave_formula": "108333 * 3"
    }
  }
}
```

- **에러 케이스**:

| HTTP | 코드 | 상황 |
|------|------|------|
| 404 | E-4004 | 직원을 찾을 수 없음 |
| 422 | E-5010 | 재직기간 1년 미만 (퇴직금 미해당) |
| 422 | E-5011 | 퇴사일이 입사일 이전 |
| 422 | E-5012 | 최근 3개월 급여 데이터 부족 (payslips 없고 monthly_wages 미제공) |
| 400 | E-1001 | 입력값 검증 실패 |

### 3.2 POST /api/v1/retirement/severance

- **목적**: 퇴직금 산출 결과 확정 및 DB 저장
- **인증**: 필요
- **Request Body**: calculate와 동일한 구조
- **Response 201**:

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "employee_id": "uuid",
    "employee_name": "홍길동",
    "hire_date": "2023-01-02",
    "resign_date": "2026-03-31",
    "total_service_days": 1184,
    "average_daily_wage": 108333,
    "severance_pay": 3268028,
    "unused_leave_pay": 303333,
    "bonus_included": 750000,
    "total_payment": 4321361,
    "payment_deadline": "2026-04-14",
    "status": "calculated",
    "calculation_detail": { ... },
    "created_at": "2026-03-12T10:00:00Z"
  }
}
```

- **에러 케이스**: calculate와 동일 + 409 (이미 해당 직원의 퇴직금이 존재)

### 3.3 GET /api/v1/retirement/severance/{id}

- **목적**: 저장된 퇴직금 상세 조회
- **인증**: 필요
- **Response 200**: `ApiResponse[SeveranceResponse]`
- **에러 케이스**: 404 E-5013 (퇴직금 기록 없음)

### 3.4 GET /api/v1/retirement/severance

- **목적**: 사업장 퇴직금 기록 목록 조회
- **인증**: 필요
- **Query Params**: `employee_id` (선택), `status` (선택), `limit`, `offset`
- **Response 200**: `ApiResponse[list[SeveranceSummary]]`

### 3.5 POST /api/v1/retirement/termination-guide

- **목적**: 해고/퇴직 절차 가이드 생성 (Claude API 활용)
- **인증**: 필요
- **Request Body**:

```json
{
  "employee_id": "uuid",
  "termination_type": "dismissal",
  "reason": "경영상 사유로 인한 해고",
  "risk_factors": {
    "is_pregnant": false,
    "is_on_parental_leave": false,
    "is_union_member": false,
    "is_workplace_injury": false,
    "is_whistleblower": false
  }
}
```

`termination_type` enum: `resignation` (자발적 퇴사), `mutual_agreement` (권고사직), `dismissal` (해고), `contract_expiry` (계약만료), `retirement` (정년퇴직)

- **Response 200**:

```json
{
  "success": true,
  "data": {
    "termination_type": "dismissal",
    "risk_level": "HIGH",
    "checklist": [
      {
        "step": 1,
        "title": "해고 사유 정당성 확인",
        "description": "근로기준법 제23조에 따라 ...",
        "required": true,
        "completed": false
      }
    ],
    "advance_notice": {
      "required": true,
      "notice_days": 30,
      "notice_pay_amount": 3000000,
      "description": "30일 전 서면 예고 또는 30일분 통상임금 지급"
    },
    "risk_warnings": [
      {
        "type": "pregnancy",
        "severity": "EMERGENCY",
        "message": "임산부 해고는 근로기준법 제65조에 의해 금지됩니다.",
        "recommendation": "노무사 상담을 강력히 권장합니다."
      }
    ],
    "documents": [
      {
        "type": "dismissal_notice",
        "name": "해고예고통지서",
        "available": true
      },
      {
        "type": "resignation_agreement",
        "name": "권고사직서",
        "available": true
      }
    ],
    "unemployment_benefit_guide": {
      "eligible": true,
      "conditions": "비자발적 이직(해고) 시 ...",
      "required_documents": ["이직확인서", "구직신청서"]
    },
    "ai_guide": "근로기준법 제23조에 따르면...(Claude 생성 상세 가이드)",
    "law_references": [
      {
        "law_name": "근로기준법",
        "article": "제23조",
        "content": "정당한 이유 없이 해고..."
      }
    ],
    "disclaimer": "본 가이드는 참고용이며, 법적 효력이 없습니다. 구체적 사안에 대해서는 전문 노무사와 상담하시기 바랍니다."
  }
}
```

- **에러 케이스**:

| HTTP | 코드 | 상황 |
|------|------|------|
| 404 | E-4004 | 직원 없음 |
| 502 | E-6002 | Claude API 오류 |
| 422 | E-5014 | 이미 퇴직 처리된 직원 |

### 3.6 POST /api/v1/retirement/documents/generate

- **목적**: 해고 관련 서류 생성 (해고예고통지서, 권고사직서)
- **인증**: 필요
- **Request Body**:

```json
{
  "employee_id": "uuid",
  "document_type": "dismissal_notice",
  "termination_date": "2026-04-30",
  "reason": "경영상 사유",
  "format": "pdf"
}
```

`document_type` enum: `dismissal_notice` (해고예고통지서), `resignation_agreement` (권고사직서)

- **Response 200**:

```json
{
  "success": true,
  "data": {
    "download_url": "https://s3.amazonaws.com/...",
    "expires_at": "2026-03-13T10:00:00Z",
    "filename": "해고예고통지서_홍길동_20260312.pdf",
    "document_type": "dismissal_notice"
  }
}
```

---

## 4. DB 설계

### 4.1 새 테이블: severance_records

퇴직금 산출 기록을 저장하는 테이블.

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 퇴직금 기록 고유 식별자 |
| employee_id | UUID | FK(employees.id), NOT NULL | 직원 ID |
| company_id | UUID | FK(companies.id), NOT NULL | 사업장 ID |
| hire_date | DATE | NOT NULL | 입사일 (산출 시점 스냅샷) |
| resign_date | DATE | NOT NULL | 퇴사일 |
| total_service_days | INTEGER | NOT NULL | 총 재직일수 |
| last_3m_total_wage | NUMERIC(14,0) | NOT NULL | 최근 3개월 임금 합계 |
| last_3m_total_days | INTEGER | NOT NULL | 최근 3개월 총 일수 |
| bonus_3m_share | NUMERIC(12,0) | DEFAULT 0 | 상여금 3/12 |
| average_daily_wage | NUMERIC(12,0) | NOT NULL | 평균임금 (일) |
| severance_pay | NUMERIC(14,0) | NOT NULL | 퇴직금 |
| unused_leave_days | INTEGER | DEFAULT 0 | 미사용 연차 일수 |
| unused_leave_pay | NUMERIC(12,0) | DEFAULT 0 | 연차 미사용 수당 |
| total_payment | NUMERIC(14,0) | NOT NULL | 총 지급액 |
| payment_deadline | DATE | NOT NULL | 지급 기한 (퇴직일 + 14일) |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'calculated' | 상태 (calculated/paid/overdue) |
| paid_at | TIMESTAMPTZ | | 지급 일시 |
| calculation_detail | JSONB | | 계산 상세 내역 |
| created_at | TIMESTAMPTZ | NOT NULL | 생성일시 |
| updated_at | TIMESTAMPTZ | NOT NULL | 수정일시 |

**제약조건:**
```sql
CHECK (status IN ('calculated', 'paid', 'overdue'))
UNIQUE (employee_id, resign_date)  -- 동일 직원+퇴사일 중복 방지
```

**인덱스:**
```sql
CREATE INDEX idx_severance_employee ON severance_records(employee_id);
CREATE INDEX idx_severance_company ON severance_records(company_id);
CREATE UNIQUE INDEX idx_severance_unique ON severance_records(employee_id, resign_date);
CREATE INDEX idx_severance_status ON severance_records(status) WHERE status != 'paid';
```

### 4.2 새 테이블: termination_documents

해고/퇴직 관련 생성된 서류를 저장.

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 서류 고유 식별자 |
| employee_id | UUID | FK(employees.id), NOT NULL | 직원 ID |
| company_id | UUID | FK(companies.id), NOT NULL | 사업장 ID |
| document_type | VARCHAR(30) | NOT NULL | 서류 유형 (dismissal_notice/resignation_agreement) |
| termination_date | DATE | NOT NULL | 해고/퇴직일 |
| reason | TEXT | | 사유 |
| pdf_url | TEXT | | PDF 파일 URL (S3) |
| docx_url | TEXT | | Word 파일 URL (S3) |
| ai_generated | BOOLEAN | DEFAULT TRUE | AI 생성 여부 |
| created_at | TIMESTAMPTZ | NOT NULL | 생성일시 |

**인덱스:**
```sql
CREATE INDEX idx_termination_docs_employee ON termination_documents(employee_id);
CREATE INDEX idx_termination_docs_company ON termination_documents(company_id);
```

### 4.3 마이그레이션 (004_add_severance_and_termination.py)

```python
# alembic/versions/004_add_severance_and_termination.py
"""add severance_records and termination_documents tables"""

def upgrade():
    # severance_records 테이블 생성
    op.create_table('severance_records', ...)
    # termination_documents 테이블 생성
    op.create_table('termination_documents', ...)

def downgrade():
    op.drop_table('termination_documents')
    op.drop_table('severance_records')
```

### 4.4 ERD 관계 추가

```
employees ||--o{ severance_records : "퇴직금"
employees ||--o{ termination_documents : "해고서류"
```

---

## 5. 시퀀스 흐름

### 5.1 퇴직금 계산 (시뮬레이션)

```
사용자 → Frontend(retirement 페이지)
    → POST /api/v1/retirement/calculate
    → SeveranceService.calculate_severance()
        → EmployeeRepo.get_by_id_and_company() -- 직원 정보 확인
        → PayslipRepo.list_by_employee() -- 최근 3개월 급여 조회 (자동)
        → SeveranceService._compute_average_daily_wage() -- 평균임금 산출
        → SeveranceService._compute_severance_pay() -- 퇴직금 산출
        → SeveranceService._compute_unused_leave_pay() -- 연차미사용수당
    → ApiResponse(data=계산 결과)
```

### 5.2 퇴직금 확정 저장

```
사용자 → POST /api/v1/retirement/severance
    → SeveranceService.create_severance()
        → (5.1과 동일한 계산)
        → SeveranceRepo.create() -- DB 저장
    → ApiResponse(data=저장된 결과, status=201)
```

### 5.3 해고 절차 가이드

```
사용자 → POST /api/v1/retirement/termination-guide
    → SeveranceService.generate_termination_guide()
        → EmployeeRepo.get_by_id_and_company()
        → SeveranceService._detect_risk_level() -- 위험도 판정
        → SeveranceService._build_checklist() -- 정적 체크리스트
        → SeveranceService._calculate_advance_notice_pay() -- 해고예고수당
        → ClaudeClient.generate() -- AI 상세 가이드 (retirement_prompt)
        → (면책 문구 자동 추가)
    → ApiResponse(data=가이드)
```

### 5.4 해고 서류 생성

```
사용자 → POST /api/v1/retirement/documents/generate
    → SeveranceService.generate_document()
        → EmployeeRepo / CompanyRepo -- 직원/사업장 정보
        → ClaudeClient.generate() -- 서류 본문 생성
        → PdfService.generate() -- PDF 변환
        → S3 업로드 → presigned URL 반환
        → TerminationDocRepo.create() -- DB 저장
    → ApiResponse(data=download_url)
```

---

## 6. Service 레이어 상세 설계

### 6.1 SeveranceService (backend/app/services/severance_service.py)

```python
class SeveranceService:
    """퇴직금/해고 계산 서비스"""

    @staticmethod
    def compute_average_daily_wage(
        monthly_wages: list[MonthlyWage],
        annual_bonus: Decimal,
    ) -> tuple[Decimal, dict]:
        """평균임금 계산

        평균임금 = (최근 3개월 임금 합계 + 상여금 3/12) / 최근 3개월 총 일수

        Args:
            monthly_wages: 최근 3개월 급여 [{total_wage, days_in_month}]
            annual_bonus: 연간 상여금 총액

        Returns:
            (평균임금(일), 계산 상세 dict)
        """

    @staticmethod
    def compute_severance_pay(
        average_daily_wage: Decimal,
        total_service_days: int,
    ) -> int:
        """퇴직금 계산

        퇴직금 = 평균임금 x 30일 x (총 재직일수 / 365)
        10원 미만 절사
        """

    @staticmethod
    def compute_unused_leave_pay(
        average_daily_wage: Decimal,
        unused_days: int,
    ) -> int:
        """연차 미사용 수당 계산

        미사용 수당 = 평균임금 x 미사용 연차일수
        10원 미만 절사
        """

    @staticmethod
    def compute_total_service_days(
        hire_date: date,
        resign_date: date,
    ) -> int:
        """총 재직일수 계산"""

    @staticmethod
    def compute_payment_deadline(resign_date: date) -> date:
        """지급 기한 계산 (퇴직일 + 14일)"""

    async def calculate_severance(
        self,
        db: AsyncSession,
        company_id: str,
        request: SeveranceCalculateRequest,
    ) -> SeveranceCalculateResponse:
        """퇴직금 시뮬레이션 (DB 저장 없음)

        1. 직원 정보 조회 + 접근 권한 확인
        2. monthly_wages 미제공 시 payslips에서 자동 조회
        3. 재직기간 1년 미만 검증
        4. 평균임금 → 퇴직금 → 연차미사용수당 순서로 계산
        5. 계산 결과 반환
        """

    async def create_severance(
        self,
        db: AsyncSession,
        company_id: str,
        request: SeveranceCalculateRequest,
    ) -> SeveranceResponse:
        """퇴직금 확정 저장

        1. calculate_severance() 호출
        2. 중복 체크 (동일 employee_id + resign_date)
        3. severance_records에 저장
        4. 저장 결과 반환
        """

    async def generate_termination_guide(
        self,
        db: AsyncSession,
        company_id: str,
        request: TerminationGuideRequest,
    ) -> TerminationGuideResponse:
        """해고/퇴직 절차 가이드 생성

        1. 직원 정보 조회
        2. 위험 요소 감지 → risk_level 판정
        3. termination_type별 정적 체크리스트 구성
        4. 해고예고수당 계산 (dismissal인 경우)
        5. Claude API로 상세 가이드 생성
        6. 면책 문구 자동 추가
        7. 가이드 반환
        """

    def _detect_risk_level(
        self,
        risk_factors: RiskFactors,
    ) -> str:
        """위험도 판정

        - EMERGENCY: 임신, 육아휴직, 산재 중
        - HIGH: 노조활동, 내부고발자
        - MEDIUM: 해고 유형
        - LOW: 자발적 퇴사, 계약만료
        """

    def _build_checklist(
        self,
        termination_type: str,
        risk_level: str,
    ) -> list[ChecklistItem]:
        """종료 유형별 정적 체크리스트 구성"""

    async def _get_recent_payslips(
        self,
        db: AsyncSession,
        employee_id: str,
        resign_date: date,
        months: int = 3,
    ) -> list[MonthlyWage]:
        """최근 N개월 급여 데이터 조회 (payslips 테이블)"""
```

### 6.2 위험도 판정 로직

```python
RISK_LEVEL_MAP = {
    "is_pregnant": "EMERGENCY",
    "is_on_parental_leave": "EMERGENCY",
    "is_workplace_injury": "EMERGENCY",
    "is_union_member": "HIGH",
    "is_whistleblower": "HIGH",
}

def _detect_risk_level(self, risk_factors: RiskFactors) -> str:
    max_level = "LOW"
    priority = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "EMERGENCY": 3}

    # 해고 유형에 따른 기본 위험도
    if termination_type in ("dismissal",):
        max_level = "MEDIUM"

    # 위험 요소별 위험도 상향
    for factor, level in RISK_LEVEL_MAP.items():
        if getattr(risk_factors, factor, False):
            if priority[level] > priority[max_level]:
                max_level = level

    return max_level
```

### 6.3 퇴직금 계산 상수

```python
# 근로기준법 기반 상수
SEVERANCE_DAYS = Decimal("30")       # 퇴직금 기본 30일
SEVERANCE_YEAR_DAYS = Decimal("365") # 연간 일수
BONUS_MONTHS_RATIO = Decimal("3") / Decimal("12")  # 상여금 3/12 반영
PAYMENT_DEADLINE_DAYS = 14           # 퇴직 후 14일 이내 지급
MIN_SERVICE_DAYS = 365               # 최소 재직일수 (1년)
```

---

## 7. Repository 설계

### 7.1 SeveranceRepository (backend/app/repositories/severance_repo.py)

```python
class SeveranceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> SeveranceRecord: ...
    async def get_by_id(self, id: UUID) -> SeveranceRecord | None: ...
    async def get_by_id_and_company(self, id: UUID, company_id: UUID) -> SeveranceRecord | None: ...
    async def get_by_employee_and_date(self, employee_id: UUID, resign_date: date) -> SeveranceRecord | None: ...
    async def list_by_company(self, company_id: UUID, employee_id: UUID | None, status: str | None, limit, offset) -> list[SeveranceRecord]: ...
    async def update_status(self, id: UUID, status: str, paid_at: datetime | None) -> SeveranceRecord | None: ...
```

### 7.2 TerminationDocRepository (backend/app/repositories/termination_doc_repo.py)

```python
class TerminationDocRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> TerminationDocument: ...
    async def get_by_id_and_company(self, id: UUID, company_id: UUID) -> TerminationDocument | None: ...
    async def list_by_employee(self, employee_id: UUID) -> list[TerminationDocument]: ...
```

---

## 8. Schema (Pydantic) 설계

### 8.1 backend/app/schemas/severance.py

```python
class MonthlyWageInput(BaseModel):
    """월별 급여 입력"""
    year: int = Field(..., ge=2020, le=2099)
    month: int = Field(..., ge=1, le=12)
    total_wage: Decimal = Field(..., gt=0, description="해당 월 총 급여")
    days_in_month: int = Field(..., ge=28, le=31, description="해당 월 총 일수")

class SeveranceCalculateRequest(BaseModel):
    """퇴직금 계산 요청"""
    employee_id: str = Field(...)
    resign_date: date = Field(...)
    annual_bonus: Decimal = Field(default=Decimal("0"), ge=0, description="연간 상여금 총액")
    unused_annual_leave_days: int = Field(default=0, ge=0, le=40, description="미사용 연차 일수")
    monthly_wages: list[MonthlyWageInput] | None = Field(
        default=None,
        min_length=3, max_length=3,
        description="최근 3개월 급여 (미입력시 payslips에서 자동 조회)"
    )

class SeveranceCalculateResponse(BaseModel):
    """퇴직금 계산 결과"""
    employee_id: str
    employee_name: str
    hire_date: date
    resign_date: date
    total_service_days: int
    average_daily_wage: int
    severance_pay: int
    unused_leave_pay: int
    bonus_included: int
    total_payment: int
    payment_deadline: date
    eligible: bool
    calculation_detail: dict

class SeveranceResponse(SeveranceCalculateResponse):
    """퇴직금 저장 결과"""
    id: str
    status: str
    created_at: datetime

class SeveranceSummary(BaseModel):
    """퇴직금 목록 요약"""
    id: str
    employee_id: str
    employee_name: str
    resign_date: date
    total_payment: int
    status: str
    payment_deadline: date
    created_at: datetime

class RiskFactors(BaseModel):
    """위험 요소 체크리스트"""
    is_pregnant: bool = False
    is_on_parental_leave: bool = False
    is_union_member: bool = False
    is_workplace_injury: bool = False
    is_whistleblower: bool = False

class TerminationGuideRequest(BaseModel):
    """해고 절차 가이드 요청"""
    employee_id: str = Field(...)
    termination_type: str = Field(
        ...,
        pattern="^(resignation|mutual_agreement|dismissal|contract_expiry|retirement)$"
    )
    reason: str = Field(..., max_length=500)
    risk_factors: RiskFactors = Field(default_factory=RiskFactors)

class ChecklistItem(BaseModel):
    step: int
    title: str
    description: str
    required: bool
    completed: bool = False

class AdvanceNotice(BaseModel):
    required: bool
    notice_days: int
    notice_pay_amount: int
    description: str

class RiskWarning(BaseModel):
    type: str
    severity: str
    message: str
    recommendation: str

class DocumentInfo(BaseModel):
    type: str
    name: str
    available: bool

class UnemploymentGuide(BaseModel):
    eligible: bool
    conditions: str
    required_documents: list[str]

class LawReference(BaseModel):
    law_name: str
    article: str
    content: str

class TerminationGuideResponse(BaseModel):
    termination_type: str
    risk_level: str
    checklist: list[ChecklistItem]
    advance_notice: AdvanceNotice
    risk_warnings: list[RiskWarning]
    documents: list[DocumentInfo]
    unemployment_benefit_guide: UnemploymentGuide
    ai_guide: str
    law_references: list[LawReference]
    disclaimer: str

class DocumentGenerateRequest(BaseModel):
    employee_id: str = Field(...)
    document_type: str = Field(
        ..., pattern="^(dismissal_notice|resignation_agreement)$"
    )
    termination_date: date = Field(...)
    reason: str = Field(..., max_length=500)
    format: str = Field(default="pdf", pattern="^(pdf|docx)$")

class DocumentGenerateResponse(BaseModel):
    download_url: str
    expires_at: datetime
    filename: str
    document_type: str
```

---

## 9. DB Model 설계

### 9.1 backend/app/db/models/severance.py

```python
class SeveranceRecord(Base):
    __tablename__ = "severance_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    resign_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_service_days: Mapped[int] = mapped_column(Integer, nullable=False)
    last_3m_total_wage: Mapped[float] = mapped_column(Numeric(14, 0), nullable=False)
    last_3m_total_days: Mapped[int] = mapped_column(Integer, nullable=False)
    bonus_3m_share: Mapped[float] = mapped_column(Numeric(12, 0), default=0)
    average_daily_wage: Mapped[float] = mapped_column(Numeric(12, 0), nullable=False)
    severance_pay: Mapped[float] = mapped_column(Numeric(14, 0), nullable=False)
    unused_leave_days: Mapped[int] = mapped_column(Integer, default=0)
    unused_leave_pay: Mapped[float] = mapped_column(Numeric(12, 0), default=0)
    total_payment: Mapped[float] = mapped_column(Numeric(14, 0), nullable=False)
    payment_deadline: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="calculated")
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    calculation_detail: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Constraints & Indexes
    __table_args__ = (
        CheckConstraint("status IN ('calculated', 'paid', 'overdue')", name="ck_severance_status"),
        Index("idx_severance_employee", "employee_id"),
        Index("idx_severance_company", "company_id"),
        Index("idx_severance_unique", "employee_id", "resign_date", unique=True),
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="severance_records")


class TerminationDocument(Base):
    __tablename__ = "termination_documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    document_type: Mapped[str] = mapped_column(String(30), nullable=False)
    termination_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    docx_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "document_type IN ('dismissal_notice', 'resignation_agreement')",
            name="ck_termination_doc_type"
        ),
        Index("idx_termination_docs_employee", "employee_id"),
        Index("idx_termination_docs_company", "company_id"),
    )

    employee: Mapped["Employee"] = relationship("Employee", back_populates="termination_documents")
```

### 9.2 Employee 모델 변경

Employee 모델에 relationship 추가:

```python
# backend/app/db/models/employee.py에 추가
severance_records: Mapped[list["SeveranceRecord"]] = relationship(
    "SeveranceRecord", back_populates="employee", cascade="all, delete-orphan"
)
termination_documents: Mapped[list["TerminationDocument"]] = relationship(
    "TerminationDocument", back_populates="employee", cascade="all, delete-orphan"
)
```

### 9.3 models/__init__.py 변경

```python
from .severance import SeveranceRecord, TerminationDocument
# __all__에 추가
```

---

## 10. API 라우터 설계

### 10.1 backend/app/api/v1/retirement.py

```python
router = APIRouter()

@router.post("/calculate", response_model=ApiResponse[dict])
async def calculate_severance(request, user_id, company_id, db): ...

@router.post("/severance", response_model=ApiResponse[dict], status_code=201)
async def create_severance(request, user_id, company_id, db): ...

@router.get("/severance", response_model=ApiResponse[list])
async def list_severances(employee_id, status, limit, offset, user_id, company_id, db): ...

@router.get("/severance/{severance_id}", response_model=ApiResponse[dict])
async def get_severance(severance_id, user_id, company_id, db): ...

@router.post("/termination-guide", response_model=ApiResponse[dict])
async def generate_termination_guide(request, user_id, company_id, db): ...

@router.post("/documents/generate", response_model=ApiResponse[dict])
async def generate_document(request, user_id, company_id, db): ...
```

### 10.2 router.py 변경

```python
from app.api.v1 import retirement
api_router.include_router(retirement.router, prefix="/retirement", tags=["퇴직금/해고"])
```

---

## 11. AI 프롬프트 설계

### 11.1 backend/app/ai/prompts/retirement_prompt.py

해고 절차 가이드 프롬프트:

```python
TERMINATION_GUIDE_SYSTEM = """
당신은 한국 노동법 전문가입니다.
사용자의 상황에 맞는 해고/퇴직 절차를 안내합니다.

다음 법률을 참조합니다:
- 근로기준법 제23조 (해고 등의 제한)
- 근로기준법 제26조 (해고의 예고)
- 근로기준법 제27조 (해고사유 등의 서면통지)
- 근로기준법 제65조 (임산부 보호)
- 고용보험법 (실업급여 관련)

반드시 구체적인 법 조항을 인용하세요.
위험 요소가 있으면 반드시 경고하세요.
"""

TERMINATION_GUIDE_USER = """
해고/퇴직 유형: {termination_type}
사유: {reason}
직원 정보: {employee_info}
위험 요소: {risk_factors}
사업장 정보: 직원수 {employee_count}명, 업종 {industry}

위 상황에 대한 상세 절차 가이드를 제공해주세요.
"""
```

해고 서류 생성 프롬프트:

```python
DOCUMENT_SYSTEM = """
당신은 한국 노동법 전문가이며, 법적 서류 작성 전문가입니다.
정식 법률 서류 형식에 맞게 작성합니다.
"""

DISMISSAL_NOTICE_USER = """
다음 정보로 해고예고통지서를 작성해주세요:
- 사업장: {company_name} (대표: {representative})
- 직원: {employee_name}
- 해고일: {termination_date}
- 해고사유: {reason}
- 통지일: {today}

근로기준법 제27조에 따른 법정 양식을 준수하세요.
"""
```

---

## 12. Frontend 설계

### 12.1 페이지 구조

```
frontend/app/(main)/retirement/
    page.tsx           -- 퇴직금 계산 메인 페이지 (Server Component 래퍼)
    termination/
        page.tsx       -- 해고 절차 가이드 페이지
```

### 12.2 컴포넌트 구조

```
frontend/components/retirement/
    severance-calculator.tsx    -- 퇴직금 계산 폼 + 결과 표시
    severance-result-card.tsx   -- 계산 결과 카드 (금액 breakdown)
    monthly-wage-input.tsx      -- 최근 3개월 급여 입력 폼
    termination-guide-form.tsx  -- 해고 절차 요청 폼
    termination-checklist.tsx   -- 절차 체크리스트 UI
    risk-warning-banner.tsx     -- 위험 경고 배너 (EMERGENCY/HIGH)
    document-download.tsx       -- 서류 다운로드 버튼
    payment-deadline-badge.tsx  -- 지급 기한 표시
```

### 12.3 API 클라이언트

```
frontend/lib/api/retirement.ts
    calculateSeverance(request) -> SeveranceResult
    createSeverance(request) -> SeveranceRecord
    getSeverance(id) -> SeveranceRecord
    listSeverances(params) -> SeveranceRecord[]
    generateTerminationGuide(request) -> TerminationGuide
    generateDocument(request) -> DocumentResult
```

### 12.4 타입

```
frontend/types/retirement.ts
    SeveranceCalculateRequest
    SeveranceResult
    TerminationGuideRequest
    TerminationGuide
    RiskFactors
    ChecklistItem
    ...
```

### 12.5 Zustand 스토어

```
frontend/lib/stores/retirement-store.ts
    - calculationResult: SeveranceResult | null
    - terminationGuide: TerminationGuide | null
    - isCalculating: boolean
    - actions: calculate, save, reset
```

---

## 13. 영향 범위

### 수정 필요 파일

| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/api/v1/router.py` | retirement 라우터 등록 |
| `backend/app/db/models/__init__.py` | SeveranceRecord, TerminationDocument import 추가 |
| `backend/app/db/models/employee.py` | severance_records, termination_documents relationship 추가 |

### 신규 생성 파일

| 파일 | 설명 |
|------|------|
| `backend/alembic/versions/004_add_severance_and_termination.py` | 마이그레이션 |
| `backend/app/db/models/severance.py` | SeveranceRecord, TerminationDocument 모델 |
| `backend/app/schemas/severance.py` | Pydantic 스키마 |
| `backend/app/services/severance_service.py` | 퇴직금/해고 서비스 |
| `backend/app/repositories/severance_repo.py` | SeveranceRepository |
| `backend/app/repositories/termination_doc_repo.py` | TerminationDocRepository |
| `backend/app/api/v1/retirement.py` | API 라우터 |
| `backend/app/ai/prompts/retirement_prompt.py` | AI 프롬프트 |
| `frontend/app/(main)/retirement/page.tsx` | 퇴직금 계산 페이지 |
| `frontend/app/(main)/retirement/termination/page.tsx` | 해고 절차 페이지 |
| `frontend/components/retirement/*.tsx` | 퇴직금/해고 컴포넌트 |
| `frontend/lib/api/retirement.ts` | API 클라이언트 |
| `frontend/types/retirement.ts` | TypeScript 타입 |
| `frontend/lib/stores/retirement-store.ts` | Zustand 스토어 |

---

## 14. 성능 설계

### 14.1 인덱스 계획

- `idx_severance_unique (employee_id, resign_date)`: 중복 방지 + 조회
- `idx_severance_company (company_id)`: 사업장별 목록 조회
- `idx_severance_status (status) WHERE status != 'paid'`: 미지급 건 조회

### 14.2 캐싱 전략

- 퇴직금 계산은 상태가 없으므로 캐싱 불필요 (매번 실시간 계산)
- 해고 절차 가이드의 정적 체크리스트는 코드 레벨 상수로 관리
- Claude API 응답은 캐싱하지 않음 (매번 컨텍스트가 다름)

### 14.3 Rate Limiting

| 엔드포인트 | 제한 |
|------------|------|
| `POST /retirement/calculate` | 30회/시간 (User) |
| `POST /retirement/termination-guide` | 10회/시간 (Claude API 비용) |
| `POST /retirement/documents/generate` | 10회/시간 (Claude API 비용) |

---

## 15. 에러 코드 추가

| 코드 | HTTP | 메시지 | 설명 |
|------|------|--------|------|
| E-5010 | 422 | 재직기간이 1년 미만입니다. | 퇴직금 수급 자격 미달 |
| E-5011 | 422 | 퇴사일이 입사일보다 이전입니다. | 날짜 검증 실패 |
| E-5012 | 422 | 최근 3개월 급여 데이터가 부족합니다. | payslips 없고 manual 미입력 |
| E-5013 | 404 | 퇴직금 기록을 찾을 수 없습니다. | 기록 없음 |
| E-5014 | 422 | 이미 퇴직 처리된 직원입니다. | is_active=false 상태 |
| E-5015 | 409 | 이미 해당 직원의 퇴직금 기록이 존재합니다. | 중복 |

---

## 변경 이력

| 날짜 | 변경 내용 | 이유 |
|------|-----------|------|
| 2026-03-12 | 초기 설계 작성 | F-09 퇴직금/해고 계산기 기능 구현 준비 |
