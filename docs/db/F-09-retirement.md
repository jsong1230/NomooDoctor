# F-09 퇴직금/해고 계산기 DB 스키마

**최종 확정본** | 2026-03-12

---

## 1. 신규 테이블

### 1.1 severance_records (퇴직금 기록)

퇴직금 산출 결과를 저장하는 테이블. 법적 증빙 용도로 모든 계산 정보를 기록합니다.

| 컬럼 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | UUID | PK | 고유 ID |
| employee_id | UUID | FK, NOT NULL, INDEX | 직원 ID |
| company_id | UUID | FK, NOT NULL, INDEX | 사업장 ID |
| hire_date | DATE | NOT NULL | 입사일 (스냅샷) |
| resign_date | DATE | NOT NULL, UNIQUE(with emp_id) | 퇴사일 |
| total_service_days | INTEGER | NOT NULL | 총 재직일수 |
| last_3m_total_wage | NUMERIC(14,0) | NOT NULL | 최근 3개월 임금 합계 |
| last_3m_total_days | INTEGER | NOT NULL | 최근 3개월 일수 합계 |
| bonus_3m_share | NUMERIC(12,0) | DEFAULT 0 | 상여금 3/12분 |
| average_daily_wage | NUMERIC(12,0) | NOT NULL | 평균임금(일) |
| severance_pay | NUMERIC(14,0) | NOT NULL | 퇴직금액 |
| unused_leave_days | INTEGER | DEFAULT 0 | 미사용 연차일수 |
| unused_leave_pay | NUMERIC(12,0) | DEFAULT 0 | 연차 미사용 수당 |
| total_payment | NUMERIC(14,0) | NOT NULL | 총 지급액 |
| payment_deadline | DATE | NOT NULL | 지급 기한 |
| status | VARCHAR(20) | DEFAULT 'calculated', CHECK | 상태 |
| paid_at | TIMESTAMP | NULL | 지급 일시 |
| calculation_detail | JSONB | NULL | 계산 상세 내역 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성일시 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 수정일시 |

**제약조건**:
```sql
CHECK (status IN ('calculated', 'paid', 'overdue'))
UNIQUE (employee_id, resign_date)
```

**인덱스**:
```sql
CREATE INDEX idx_severance_employee ON severance_records(employee_id);
CREATE INDEX idx_severance_company ON severance_records(company_id);
CREATE UNIQUE INDEX idx_severance_unique ON severance_records(employee_id, resign_date);
CREATE INDEX idx_severance_status ON severance_records(status)
  WHERE status != 'paid';
```

**샘플 데이터**:
```sql
INSERT INTO severance_records (
  id, employee_id, company_id, hire_date, resign_date,
  total_service_days, last_3m_total_wage, last_3m_total_days,
  bonus_3m_share, average_daily_wage, severance_pay,
  unused_leave_days, unused_leave_pay, total_payment,
  payment_deadline, status, calculation_detail,
  created_at, updated_at
) VALUES (
  'a0000000-0000-0000-0000-000000000001',
  'b0000000-0000-0000-0000-000000000001',
  'c0000000-0000-0000-0000-000000000001',
  '2024-01-15', '2026-03-31', 806,
  9000000, 90, 0, 100000, 2633150,
  0, 0, 2633150, '2026-04-14',
  'calculated',
  '{"last_3_months_total_wage": 9000000, ...}',
  NOW(), NOW()
);
```

---

### 1.2 termination_documents (해고/퇴직 서류)

해고 또는 퇴직 관련 생성된 서류를 저장합니다. 앞서 생성한 해고예고통지서, 권고사직서 등의 URL과 메타데이터를 기록합니다.

| 컬럼 | 타입 | 제약 | 설명 |
|------|------|------|------|
| id | UUID | PK | 고유 ID |
| employee_id | UUID | FK, NOT NULL, INDEX | 직원 ID |
| company_id | UUID | FK, NOT NULL, INDEX | 사업장 ID |
| document_type | VARCHAR(30) | NOT NULL, CHECK | 서류 유형 |
| termination_date | DATE | NOT NULL | 해고/퇴직일 |
| reason | TEXT | NULL | 사유 |
| pdf_url | TEXT | NULL | PDF 다운로드 URL (S3) |
| docx_url | TEXT | NULL | Word 다운로드 URL (S3) |
| ai_generated | BOOLEAN | DEFAULT true | AI 생성 여부 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성일시 |

**제약조건**:
```sql
CHECK (document_type IN ('dismissal_notice', 'resignation_agreement'))
```

**인덱스**:
```sql
CREATE INDEX idx_termination_docs_employee ON termination_documents(employee_id);
CREATE INDEX idx_termination_docs_company ON termination_documents(company_id);
```

---

## 2. 기존 테이블 변경

### 2.1 Employee 테이블 (외래키 추가)

`employees` 테이블에 관계 설정 (CASCADE):

```sql
ALTER TABLE severance_records
  ADD CONSTRAINT fk_severance_employee
  FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE;

ALTER TABLE termination_documents
  ADD CONSTRAINT fk_termination_employee
  FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE;
```

SQLAlchemy ORM에서 역 관계 정의:
```python
# Employee 모델
severance_records: Mapped[list["SeveranceRecord"]] = relationship(
    "SeveranceRecord", back_populates="employee", cascade="all, delete-orphan"
)
termination_documents: Mapped[list["TerminationDocument"]] = relationship(
    "TerminationDocument", back_populates="employee", cascade="all, delete-orphan"
)
```

---

## 3. 마이그레이션 정보

### Revision: 006
- **Revises**: 005
- **Date**: 2026-03-12
- **Description**: Add severance_records and termination_documents tables

### 마이그레이션 파일
경로: `backend/alembic/versions/006_add_severance_and_termination.py`

### 실행 명령
```bash
cd backend
alembic upgrade head
```

---

## 4. 데이터 관계도

```
employees (1) ──── (N) severance_records
  ├─ id (FK)
  ├─ company_id
  └─ ... 직원 정보

companies (1) ──── (N) severance_records
  ├─ id (FK)
  └─ ... 사업장 정보

employees (1) ──── (N) termination_documents
  ├─ id (FK)
  └─ ... 직원 정보
```

---

## 5. 성능 최적화

### 인덱스 전략

1. **조회 성능**:
   - `idx_severance_employee`: 직원별 퇴직금 빠른 조회
   - `idx_severance_company`: 사업장별 목록 조회
   - `idx_severance_unique`: 중복 체크 (제약조건 인덱스)

2. **필터링 성능**:
   - `idx_severance_status` (부분 인덱스): 미지급(`status != 'paid'`) 건 빠른 조회

3. **외래키 조인**:
   - `idx_termination_docs_employee`, `idx_termination_docs_company`: 조인 성능

### 쿼리 예시

```sql
-- 특정 직원의 퇴직금 조회 (빠름: 유니크 인덱스)
SELECT * FROM severance_records
WHERE employee_id = $1 AND resign_date = $2;

-- 회사의 미지급 퇴직금 목록 (빠름: 부분 인덱스)
SELECT * FROM severance_records
WHERE company_id = $1 AND status != 'paid';

-- 직원의 해고 서류 모두 조회 (빠름)
SELECT * FROM termination_documents
WHERE employee_id = $1
ORDER BY created_at DESC;
```

---

## 6. 캐싱 전략

### 캐시 불필요
- 퇴직금 계산은 상태가 없으므로 캐싱 불필요 (매번 실시간)
- 각 직원마다 재직기간, 급여 등이 계속 변하므로 캐싱 불가

### 정적 데이터
- 근로기준법 상수 (퇴직금 30일, 지급기한 14일) → 코드 레벨 상수
- 해고 체크리스트 → 코드 레벨 상수

---

## 7. 백업 및 복구

### 중요 데이터
- **severance_records**: 법적 증빙이므로 **주기적 백업 필수**
- **termination_documents**: S3 링크 저장이므로 **메타데이터만 백업**

### 권장 전략
```sql
-- 주간 백업 (CSV)
COPY severance_records TO STDOUT
  WITH CSV HEADER
  WHERE created_at > NOW() - INTERVAL '7 days';
```

---

## 8. 확장 계획

### 향후 추가 컬럼
- `severance_records.adjustment_reason`: 퇴직금 조정 사유 (협의 해고 등)
- `severance_records.paid_amount`: 실제 지급액 (협상 결과)
- `termination_documents.signed_at`: 서명 일시
- `termination_documents.signatory_id`: 서명자 (직원 ID)

### 향후 통합
- F-13 (근태관리) 통합: 실제 근무 일수 기반 정확 계산
- 실업급여 시스템 연계: 해고 시 자동 신청

---

## 9. 샘플 쿼리

### 사업장별 퇴직금 지급액 합계
```sql
SELECT
  company_id,
  COUNT(*) as count,
  SUM(total_payment) as total_amount,
  AVG(total_payment) as avg_amount
FROM severance_records
WHERE status = 'paid'
GROUP BY company_id;
```

### 최근 30일 계산 건수
```sql
SELECT
  DATE(created_at) as date,
  COUNT(*) as count,
  SUM(total_payment) as amount
FROM severance_records
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### 미지급 퇴직금 (기한 경과)
```sql
SELECT *
FROM severance_records
WHERE status IN ('calculated', 'overdue')
  AND payment_deadline < NOW()::DATE
ORDER BY payment_deadline ASC;
```

---

## 변경 이력

| 날짜 | 변경 | 이유 |
|------|------|------|
| 2026-03-12 | DB 스키마 확정 | F-09 구현 완료 |
