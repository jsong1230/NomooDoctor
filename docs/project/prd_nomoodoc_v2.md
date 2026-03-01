# PRD: 노무닥터 (NomooDoctor)
## AI 기반 노무/HR 자동화 SaaS — Product Requirements Document

**버전:** v2.0  
**작성일:** 2026-03-01  
**기술 스택:** Next.js 14 (App Router) + FastAPI (Python 3.12)  
**AI 파이프라인:** Claude Code 멀티에이전트 (기능별 에이전트 분리)  
**상태:** Development Ready

---

## 목차

1. [제품 개요](#1-제품-개요)
2. [목표 사용자](#2-목표-사용자)
3. [핵심 기능 명세](#3-핵심-기능-명세)
4. [DB 스키마](#4-db-스키마)
5. [API 엔드포인트 명세](#5-api-엔드포인트-명세)
6. [Claude 프롬프트 설계](#6-claude-프롬프트-설계)
7. [Claude Code 멀티에이전트 아키텍처](#7-claude-code-멀티에이전트-아키텍처)
8. [기술 스택 상세](#8-기술-스택-상세)
9. [수익 모델](#9-수익-모델)
10. [마케팅/GTM 전략](#10-마케팅gtm-전략)
11. [리스크 분석](#11-리스크-분석)
12. [성공 지표](#12-성공-지표)
13. [마일스톤](#13-마일스톤)

---

## 1. 제품 개요

### 1.1 제품 비전

> "대한민국 50인 미만 사업장 사장님이 노무사 없이도 노동법을 준수하고, HR 서류를 자동화할 수 있는 AI 노무 비서"

### 1.2 문제 정의

| 문제 | 규모 | 임팩트 |
|------|------|--------|
| 50인 미만 사업장이 전체의 99% | 약 280만 개 사업장 | 타깃 시장 |
| 노무사 선임 비용 부담 (월 30~150만원) | 대부분 미선임 | 예방 수요 미충족 |
| 노동법 무지로 인한 위반 반복 | 주휴수당, 연장수당, 근로계약서 | 신고 후 비용 2~5배 증가 |
| 기존 SaaS (더존 등) 는 중견기업 타깃 | SME에게 과도하게 복잡 | 진입 장벽 |

### 1.3 솔루션 요약

노무닥터는 AI를 활용해 다음 7개 핵심 기능을 제공한다:

1. **AI 노동법 Q&A 챗봇** — 자연어 질문 → 법령 기반 즉각 답변
2. **근로계약서 자동 생성** — 고용형태별 법적 유효 계약서 생성
3. **급여 자동 계산기** — 주휴수당, 연장수당, 4대보험, 소득세 완전 자동화
4. **취업규칙 자동화** — 업종별 초안 생성 + 고용노동부 신고 서류
5. **퇴직금/해고 계산기** — 정확한 퇴직금 계산 + 합법적 해고 절차 가이드
6. **노무사 마켓플레이스** — 복잡 케이스 파트너 노무사 연결
7. **컴플라이언스 대시보드** — 리스크 스코어 + 노무 이벤트 캘린더

### 1.4 포지셔닝

| 구분 | 기존 노무사 | 더존 Smart A | **노무닥터** |
|------|-----------|------------|------------|
| 월 비용 | 30~150만원 | 10~30만원 | **9,900~49,000원** |
| 타깃 | 30인 이상 | 중견기업 | **5~30인 SME** |
| 노동법 Q&A | 가능 | 불가 | **AI 기반 가능** |
| 서류 생성 | 수동 | 수동 | **자동화** |
| 진입 장벽 | 높음 | 높음 | **낮음 (Freemium)** |

---

## 2. 목표 사용자

### 2.1 Primary Persona: 5~30인 사업장 사장님

- **인구통계:** 40~60대 / 제조업·요식업·소매업·서비스업 / IT 친숙도 낮음~중간
- **Pain Points:**
  - "근로계약서 꼭 써야 해요?" (법적 의무임을 모름)
  - "주휴수당이 뭔지 잘 모르겠는데 안 줘도 되는 거 아닌가요?"
  - "직원이 갑자기 고용노동부에 신고했어요. 어떻게 해요?"
  - "퇴직금 계산을 어떻게 하는 건지 매번 헷갈려요."
- **행동 패턴:** 네이버 블로그·유튜브 검색, 지인 사장님에게 물어봄, 문제 발생 전까지 노무사 미선임

### 2.2 Secondary Persona: 스타트업 HR 겸직 담당자

- **인구통계:** 20~35대 / 재무·총무·운영 겸직으로 HR 담당 / IT 친숙도 높음
- **Pain Points:**
  - "노무사한테 물어보면 시간도 걸리고 비용도 아까워요."
  - "근로계약서 양식이 뭐가 맞는 건지 모르겠어요."
  - "외국인 직원 계약서는 어떻게 써야 해요?"

### 2.3 Tertiary Persona: 파트너 노무사

- **역할:** 복잡한 케이스를 수임받는 파트너
- **동기:** 노무닥터를 통해 신규 고객 확보, 단순 업무는 플랫폼이 처리하고 복잡 업무만 수임

---

## 3. 핵심 기능 명세

### Feature 1: AI 노동법 Q&A 챗봇

#### 개요
자연어로 노동법 질문을 입력하면 AI가 관련 법령 RAG 검색 후 답변 생성. 서비스의 진입점이자 리텐션 핵심.

#### Happy Path
1. 사용자가 채팅창에 질문 입력 (예: "주 15시간 미만 알바 주휴수당 줘야 하나요?")
2. 시스템이 업종·직원 수·고용형태 컨텍스트 확인 (없으면 기본값 사용)
3. RAG 검색으로 관련 법령 조항 검색
4. Claude API 호출 → 답변 생성
5. 면책 문구 자동 삽입
6. 관련 법령 조항 링크 첨부
7. 답변 화면 표시 + 후속 질문 추천

#### 기능 요구사항

| ID | 요구사항 | 우선순위 |
|----|---------|---------|
| FR-001 | 자연어 질문 → AI 노동법 기반 답변 생성 | P0 |
| FR-002 | 답변에 관련 법령 조항 인용 (근로기준법 제○○조) | P0 |
| FR-003 | 면책 문구 자동 삽입 (100% 삽입률 필수) | P0 |
| FR-004 | 멀티턴 대화 (질문 맥락 유지, 최대 20턴) | P1 |
| FR-005 | 업종·직원 수·고용형태 컨텍스트 입력 필드 | P1 |
| FR-006 | 자주 묻는 질문 카테고리 빠른 선택 UI | P2 |
| FR-007 | 질문 히스토리 저장 (로그인 사용자) | P2 |
| FR-008 | 위험도 분류 (낮음/중간/높음/긴급) 자동 태깅 | P1 |

#### 수락 기준

- AC-001: 주요 노동법 100개 시나리오 테스트 정답률 90% 이상
- AC-002: 답변 생성 시간 p95 기준 5초 이내
- AC-003: 관련 법령 조항 정확도 95% 이상
- AC-004: 면책 문구 삽입률 100%
- AC-005: 위험도 HIGH 케이스에서 노무사 연결 CTA 100% 표시

#### 에러 케이스

| 케이스 | 처리 방식 |
|--------|---------|
| AI 답변 불가 (법령 범위 외) | "이 케이스는 전문가 상담이 필요합니다" + 노무사 연결 CTA |
| 네트워크 타임아웃 (10초 초과) | 재시도 버튼 + 오프라인 FAQ 제공 |
| 위험도 HIGH 케이스 (해고·산재·임금체불) | 경고 배너 + 노무사 강력 권장 팝업 |
| Claude API rate limit | 큐 대기 메시지 표시, 30초 후 재시도 |
| 욕설·부적절 입력 | 입력 필터링, 안내 메시지 |

---

### Feature 2: 근로계약서 자동 생성

#### 개요
고용형태, 업종, 조건 입력 시 법적 유효 근로계약서 자동 생성 및 다운로드.

#### 지원 계약 유형
- 정규직 (무기계약직 포함)
- 계약직 (기간제)
- 단시간 근로자 (파트타임, 주 15시간 미만/이상 구분)
- 일용직
- 외국인 근로자 (한국어/영어/중국어/베트남어)
- 수습 직원 (수습기간 최저임금 80% 특례 포함)

#### Happy Path
1. 고용형태 선택
2. 근무 조건 입력: 직종, 임금, 근무시간, 근무지, 수습 여부
3. 선택 특약 사항 체크박스: 경업금지, 비밀유지, 전용계좌 지정 등
4. AI가 법령 준수 검토 후 계약서 초안 생성
5. 사용자 인라인 편집
6. Word(.docx) / PDF 다운로드
7. 전자서명 링크 생성 (Phase 2)

#### 기능 요구사항

| ID | 요구사항 | 우선순위 |
|----|---------|---------|
| FR-010 | 고용형태별 법정 필수 기재사항 자동 포함 (근로기준법 제17조) | P0 |
| FR-011 | 최저임금 기준 미달 시 실시간 경고 | P0 |
| FR-012 | 주휴수당 포함 여부 자동 계산·표시 | P0 |
| FR-013 | Word(.docx), PDF 다운로드 | P0 |
| FR-014 | 생성 계약서 저장 및 직원별 관리 | P1 |
| FR-015 | 계약 만료일 D-30, D-7 자동 알림 | P1 |
| FR-016 | 외국인 근로자 다국어 지원 (한/영/중/베트남) | P2 |
| FR-017 | 계약서 버전 관리 (개정 이력) | P2 |

#### 수락 기준

- AC-010: 법정 필수 기재사항 (근로기준법 제17조 8개 항목) 100% 포함
- AC-011: 최저임금 오류 탐지율 100%
- AC-012: 노무사 검토 통과율 95% 이상 (베타 검증)
- AC-013: 다운로드 완료 시간 5초 이내

#### 에러 케이스

| 케이스 | 처리 방식 |
|--------|---------|
| 최저임금 미달 입력 | 강제 경고 모달, "확인 후 저장" 2단계 확인 |
| 필수 항목 누락 | 인라인 빨간 테두리 + 에러 메시지 |
| 근무시간 주 52시간 초과 | 경고 배너 (저장은 허용, 위반 사실 명시) |
| 파일 생성 실패 | 재시도 버튼, 3회 실패 시 고객센터 안내 |

---

### Feature 3: 급여 자동 계산기

#### 개요
직원 정보와 근무 기록 입력 시 모든 수당·공제 자동 계산 후 법정 급여명세서 생성 및 발송.

#### 계산 항목 전체

```
[지급 항목]
- 기본급 (월급제: 기본급 ÷ 209시간 × 근무시간 / 시급제: 시급 × 시간)
- 주휴수당 = 1일 소정근로시간 × 시급 (주 15시간 이상, 개근 시)
- 연장수당 = 연장시간 × 시급 × 1.5
- 야간수당 = 야간시간(22:00~06:00) × 시급 × 0.5
- 휴일수당 = 휴일시간 × 시급 × 1.5 (8시간 이내)
            = 휴일시간 × 시급 × 2.0 (8시간 초과분)
- 연차수당 = (미사용 연차일수 × 1일 통상임금) [퇴직 시]
- 식대 (월 20만원 비과세 한도)
- 교통비 (월 20만원 비과세 한도)

[공제 항목]
- 국민연금 = 기준소득월액 × 4.5%
- 건강보험 = 보수월액 × 3.545%
- 장기요양보험 = 건강보험료 × 12.95%
- 고용보험 = 월보수 × 0.9%
- 소득세 = 간이세액표 기준 (가족수 반영)
- 지방소득세 = 소득세 × 10%
```

#### 기능 요구사항

| ID | 요구사항 | 우선순위 |
|----|---------|---------|
| FR-020 | 월급제/시급제/일급제 모두 지원 | P0 |
| FR-021 | 연도별 최저임금, 4대보험료율 자동 업데이트 (DB 관리) | P0 |
| FR-022 | 급여명세서 법정 기재사항 자동 포함 | P0 |
| FR-023 | 급여명세서 이메일/카카오 알림톡 발송 | P1 |
| FR-024 | PDF 다운로드 | P1 |
| FR-025 | 엑셀(xlsx, csv) 근무 기록 일괄 업로드 | P1 |
| FR-026 | 간이세액표 기반 소득세 자동 계산 | P0 |
| FR-027 | 직원별 급여 히스토리 (월별 이력) | P2 |
| FR-028 | 급여 지급일 자동 리마인더 | P2 |

#### 에러 케이스

| 케이스 | 처리 방식 |
|--------|---------|
| 최저임금 이하 계산 결과 | 경고 표시, 최저임금 기준 재계산 제안 |
| 카카오 알림톡 발송 실패 | 이메일로 자동 Fallback |
| 엑셀 파싱 오류 | 오류 행 번호 명시, 수정 후 재업로드 안내 |
| 4대보험료율 DB 미업데이트 상태 | 관리자 알림 + 사용자에게 "최신 요율 확인 중" 안내 |

---

### Feature 4: 취업규칙 자동화

#### 기능 요구사항

| ID | 요구사항 | 우선순위 |
|----|---------|---------|
| FR-030 | 업종별 표준 취업규칙 템플릿 (제조/서비스/IT/요식업) | P1 |
| FR-031 | 법정 필수 기재사항 자동 포함 (근로기준법 제93조 14개 항목) | P0 |
| FR-032 | 항목별 편집 기능 (리치텍스트) | P1 |
| FR-033 | 고용노동부 신고용 커버 서류 자동 생성 | P2 |
| FR-034 | 버전 관리 (개정 이력 추적) | P2 |
| FR-035 | 근로자 과반수 동의 절차 체크리스트 제공 | P2 |

---

### Feature 5: 퇴직금/해고 계산기

#### 퇴직금 계산 공식

```
퇴직금 = 평균임금 × 30일 × (총 재직일수 / 365)

평균임금 = 최근 3개월 임금 합계 / 최근 3개월 총 일수

[최근 3개월 임금에 포함]
- 기본급, 연장수당, 야간수당, 휴일수당
- 식대·교통비 (월정액인 경우)
- 상여금 (연간 총액의 3/12)

[제외]
- 실비 변상적 성격의 금품
- 결혼·조위 등 일시적 금품
```

#### 기능 요구사항

| ID | 요구사항 | 우선순위 |
|----|---------|---------|
| FR-040 | 입사일~퇴사일·임금 기반 퇴직금 자동 계산 | P0 |
| FR-041 | 계약 종료 유형별 절차 체크리스트 | P0 |
| FR-042 | 해고 유효 요건 자동 검토 | P1 |
| FR-043 | 해고 관련 서류 자동 생성 (해고예고통지서, 권고사직서) | P1 |
| FR-044 | 실업급여 수급 자격 가이드 | P2 |
| FR-045 | 연차 미사용 수당 자동 계산 (퇴직 시) | P0 |

---

### Feature 6: 노무사 마켓플레이스

#### 케이스 복잡도 분류 기준

```
LOW: AI 처리 가능
  - 표준 계약서 작성
  - 급여 계산
  - 일반적인 노동법 Q&A

MEDIUM: 노무사 추천
  - 계약 해지 관련
  - 연차 분쟁
  - 취업규칙 위반

HIGH: 노무사 강력 권장
  - 부당해고 관련
  - 직장 내 괴롭힘/성희롱
  - 산재 처리
  - 체불임금 신고 대응
  - 고용노동부 근로감독 대응

EMERGENCY: 즉각 연결
  - 고용노동부 출석 요구 받은 경우
  - 노동위원회 신청 접수된 경우
```

#### 기능 요구사항

| ID | 요구사항 | 우선순위 |
|----|---------|---------|
| FR-050 | 노무사 프로필 (전문분야, 지역, 상담료, 평점) | P2 |
| FR-051 | 케이스 자동 요약 생성 → 노무사에게 사전 전달 | P1 |
| FR-052 | 화상/유선 상담 예약 시스템 | P2 |
| FR-053 | 상담료 에스크로 결제 | P2 |
| FR-054 | 리뷰/평점 시스템 | P3 |
| FR-055 | 노무사 응답률/완료율 지표 | P3 |

---

### Feature 7: 컴플라이언스 대시보드

#### 리스크 스코어 계산 로직

```
리스크 스코어 (0~100점, 높을수록 위험)

감점 항목:
  - 근로계약서 미작성 직원 1인당: -10점
  - 취업규칙 미작성 (10인 이상): -20점
  - 급여명세서 미발송 직원 1인당: -5점
  - 연차 관리 부재: -10점
  - 주 52시간 초과 직원 존재: -15점

기본 100점에서 감점 누적
초록: 80~100 / 노랑: 60~79 / 빨강: 0~59
```

#### 기능 요구사항

| ID | 요구사항 | 우선순위 |
|----|---------|---------|
| FR-060 | 직원별 서류 완비 현황 표시 | P1 |
| FR-061 | 법 위반 리스크 스코어 자동 계산 | P1 |
| FR-062 | 연간 노무 이벤트 캘린더 | P2 |
| FR-063 | 위반 항목 클릭 시 해결 방법 안내 | P1 |
| FR-064 | 월별 리스크 스코어 변화 그래프 | P2 |

---

## 4. DB 스키마

### 4.1 ERD 개요

```
companies ←─── employees ←─── contracts
    │               │               │
    │               ├─── salaries   │
    │               ├─── payslips   │
    └─── work_rules └─── leaves     │
                                    │
users ──────────────────────────────┘
    │
    ├─── subscriptions
    └─── chat_sessions ──── chat_messages

labor_attorneys ←─── attorney_cases
    │
    └─── attorney_reviews
```

### 4.2 테이블 정의

#### users (사용자)

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),                    -- NULL: OAuth 전용
    name            VARCHAR(100) NOT NULL,
    phone           VARCHAR(20),
    kakao_id        VARCHAR(100) UNIQUE,
    role            VARCHAR(20) NOT NULL DEFAULT 'owner'
                    CHECK (role IN ('owner', 'manager', 'employee', 'admin')),
    plan            VARCHAR(20) NOT NULL DEFAULT 'free'
                    CHECK (plan IN ('free', 'basic', 'standard', 'premium', 'enterprise')),
    plan_expires_at TIMESTAMPTZ,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_kakao_id ON users(kakao_id);
```

#### companies (사업장)

```sql
CREATE TABLE companies (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id            UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    business_name       VARCHAR(200) NOT NULL,           -- 사업장명
    business_number     VARCHAR(20) UNIQUE NOT NULL,     -- 사업자등록번호 (xxx-xx-xxxxx)
    representative_name VARCHAR(100) NOT NULL,           -- 대표자명
    industry_type       VARCHAR(50) NOT NULL             -- 업종
                        CHECK (industry_type IN (
                            'manufacturing', 'food_service', 'retail',
                            'service', 'it', 'construction', 'healthcare', 'other'
                        )),
    employee_count      INTEGER NOT NULL DEFAULT 0,      -- 현재 직원 수
    address             TEXT,
    postal_code         VARCHAR(10),
    phone               VARCHAR(20),
    work_rule_required  BOOLEAN GENERATED ALWAYS AS    -- 취업규칙 의무 (10인 이상)
                        (employee_count >= 10) STORED,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_companies_owner_id ON companies(owner_id);
CREATE INDEX idx_companies_business_number ON companies(business_number);
```

#### employees (직원)

```sql
CREATE TABLE employees (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id             UUID REFERENCES users(id),       -- 앱 계정 연결 시
    name                VARCHAR(100) NOT NULL,
    id_number           VARCHAR(20),                     -- 주민등록번호 (암호화 저장)
    nationality         VARCHAR(50) DEFAULT 'korean'
                        CHECK (nationality IN (
                            'korean', 'chinese', 'vietnamese',
                            'american', 'other'
                        )),
    employment_type     VARCHAR(30) NOT NULL
                        CHECK (employment_type IN (
                            'regular', 'fixed_term', 'part_time',
                            'daily', 'dispatch', 'probation'
                        )),
    department          VARCHAR(100),
    position            VARCHAR(100),
    hire_date           DATE NOT NULL,
    resign_date         DATE,                            -- NULL: 재직 중
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    phone               VARCHAR(20),
    email               VARCHAR(255),
    bank_name           VARCHAR(50),
    bank_account        VARCHAR(50),                     -- 암호화 저장
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_employees_company_id ON employees(company_id);
CREATE INDEX idx_employees_hire_date ON employees(hire_date);
CREATE INDEX idx_employees_is_active ON employees(company_id, is_active);
```

#### contracts (근로계약서)

```sql
CREATE TABLE contracts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id         UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    company_id          UUID NOT NULL REFERENCES companies(id),
    contract_type       VARCHAR(30) NOT NULL
                        CHECK (contract_type IN (
                            'regular', 'fixed_term', 'part_time',
                            'daily', 'probation', 'foreign_worker'
                        )),
    -- 근무 조건
    start_date          DATE NOT NULL,
    end_date            DATE,                            -- NULL: 무기계약
    work_location       TEXT NOT NULL,
    work_hours_per_week NUMERIC(4,1) NOT NULL,           -- 소정 근로시간
    work_start_time     TIME NOT NULL,
    work_end_time       TIME NOT NULL,
    break_minutes       INTEGER NOT NULL DEFAULT 60,
    work_days           VARCHAR(20) NOT NULL,             -- "mon,tue,wed,thu,fri"
    -- 임금
    wage_type           VARCHAR(20) NOT NULL
                        CHECK (wage_type IN ('monthly', 'hourly', 'daily')),
    base_wage           NUMERIC(12,0) NOT NULL,          -- 기본급 (월급/시급/일급)
    meal_allowance      NUMERIC(10,0) DEFAULT 0,
    transport_allowance NUMERIC(10,0) DEFAULT 0,
    probation_months    INTEGER DEFAULT 0,
    probation_wage_rate NUMERIC(3,2) DEFAULT 1.0,        -- 수습 임금 비율 (0.80)
    -- 특약사항
    nda_included        BOOLEAN DEFAULT FALSE,            -- 비밀유지
    non_compete_included BOOLEAN DEFAULT FALSE,           -- 경업금지
    -- 상태
    status              VARCHAR(20) NOT NULL DEFAULT 'draft'
                        CHECK (status IN ('draft', 'sent', 'signed', 'expired', 'terminated')),
    -- 파일
    docx_url            TEXT,
    pdf_url             TEXT,
    -- AI 생성 메타
    ai_generated        BOOLEAN NOT NULL DEFAULT TRUE,
    ai_model            VARCHAR(50),                     -- claude-sonnet-4-6
    -- 전자서명
    signed_at           TIMESTAMPTZ,
    sign_service_ref    VARCHAR(200),                    -- 모두싸인 ref ID
    -- 알림
    expiry_notice_30_sent BOOLEAN DEFAULT FALSE,
    expiry_notice_7_sent  BOOLEAN DEFAULT FALSE,
    version             INTEGER NOT NULL DEFAULT 1,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_contracts_employee_id ON contracts(employee_id);
CREATE INDEX idx_contracts_company_id ON contracts(company_id);
CREATE INDEX idx_contracts_end_date ON contracts(end_date) WHERE end_date IS NOT NULL;
CREATE INDEX idx_contracts_status ON contracts(status);
```

#### salary_settings (급여 설정)

```sql
CREATE TABLE salary_settings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id     UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    effective_from  DATE NOT NULL,
    effective_to    DATE,                               -- NULL: 현재 적용 중
    wage_type       VARCHAR(20) NOT NULL
                    CHECK (wage_type IN ('monthly', 'hourly', 'daily')),
    base_wage       NUMERIC(12,0) NOT NULL,
    meal_allowance  NUMERIC(10,0) DEFAULT 0,
    transport_allowance NUMERIC(10,0) DEFAULT 0,
    income_tax_family_count INTEGER DEFAULT 1,         -- 부양가족 수 (소득세 계산용)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_salary_settings_employee ON salary_settings(employee_id, effective_from DESC);
```

#### work_records (근태 기록)

```sql
CREATE TABLE work_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id     UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    company_id      UUID NOT NULL REFERENCES companies(id),
    work_date       DATE NOT NULL,
    scheduled_start TIME NOT NULL,
    scheduled_end   TIME NOT NULL,
    actual_start    TIME,
    actual_end      TIME,
    break_minutes   INTEGER DEFAULT 60,
    overtime_minutes INTEGER DEFAULT 0,               -- 연장시간 (분)
    night_minutes   INTEGER DEFAULT 0,                -- 야간시간 (분, 22:00~06:00)
    holiday_minutes INTEGER DEFAULT 0,               -- 휴일근무 (분)
    is_holiday      BOOLEAN DEFAULT FALSE,
    memo            TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_work_records_employee_date ON work_records(employee_id, work_date);
CREATE INDEX idx_work_records_company_date ON work_records(company_id, work_date);
```

#### payslips (급여명세서)

```sql
CREATE TABLE payslips (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id             UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    company_id              UUID NOT NULL REFERENCES companies(id),
    pay_year                INTEGER NOT NULL,
    pay_month               INTEGER NOT NULL CHECK (pay_month BETWEEN 1 AND 12),
    -- 지급
    base_pay                NUMERIC(12,0) NOT NULL,
    holiday_pay             NUMERIC(12,0) DEFAULT 0,     -- 주휴수당
    overtime_pay            NUMERIC(12,0) DEFAULT 0,     -- 연장수당
    night_pay               NUMERIC(12,0) DEFAULT 0,     -- 야간수당
    holiday_work_pay        NUMERIC(12,0) DEFAULT 0,     -- 휴일수당
    meal_allowance          NUMERIC(10,0) DEFAULT 0,
    transport_allowance     NUMERIC(10,0) DEFAULT 0,
    other_allowance         NUMERIC(10,0) DEFAULT 0,
    gross_pay               NUMERIC(12,0) NOT NULL,      -- 지급 합계
    -- 공제
    national_pension        NUMERIC(10,0) DEFAULT 0,
    health_insurance        NUMERIC(10,0) DEFAULT 0,
    long_term_care          NUMERIC(10,0) DEFAULT 0,
    employment_insurance    NUMERIC(10,0) DEFAULT 0,
    income_tax              NUMERIC(10,0) DEFAULT 0,
    local_income_tax        NUMERIC(10,0) DEFAULT 0,
    total_deduction         NUMERIC(12,0) NOT NULL,      -- 공제 합계
    net_pay                 NUMERIC(12,0) NOT NULL,      -- 실수령액
    -- 발송
    sent_at                 TIMESTAMPTZ,
    sent_via                VARCHAR(20),                 -- 'kakao', 'email', 'both'
    send_status             VARCHAR(20) DEFAULT 'pending'
                            CHECK (send_status IN ('pending', 'sent', 'failed')),
    pdf_url                 TEXT,
    -- 메타
    calculation_detail      JSONB,                       -- 계산 상세 내역
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_payslips_unique ON payslips(employee_id, pay_year, pay_month);
CREATE INDEX idx_payslips_company_period ON payslips(company_id, pay_year, pay_month);
```

#### chat_sessions (AI 상담 세션)

```sql
CREATE TABLE chat_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_id      UUID REFERENCES companies(id),
    title           VARCHAR(200),                       -- 첫 메시지 기반 자동 생성
    risk_level      VARCHAR(20) DEFAULT 'low'
                    CHECK (risk_level IN ('low', 'medium', 'high', 'emergency')),
    attorney_referred BOOLEAN DEFAULT FALSE,             -- 노무사 연결 여부
    message_count   INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
```

#### chat_messages (AI 상담 메시지)

```sql
CREATE TABLE chat_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role            VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content         TEXT NOT NULL,
    law_references  JSONB,                              -- 인용 법령 조항 목록
    risk_level      VARCHAR(20),
    disclaimer_shown BOOLEAN DEFAULT FALSE,             -- 면책 문구 표시 여부
    tokens_used     INTEGER,
    model_used      VARCHAR(50),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id, created_at);
```

#### work_rules (취업규칙)

```sql
CREATE TABLE work_rules (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL DEFAULT 1,
    status          VARCHAR(20) NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft', 'under_review', 'active', 'superseded')),
    content         JSONB NOT NULL,                     -- 섹션별 내용
    docx_url        TEXT,
    pdf_url         TEXT,
    effective_date  DATE,
    approval_date   DATE,
    worker_consent_count INTEGER,                       -- 근로자 동의 수
    filed_at        TIMESTAMPTZ,                        -- 노동부 신고일
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### labor_attorneys (파트너 노무사)

```sql
CREATE TABLE labor_attorneys (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    license_number  VARCHAR(50) UNIQUE NOT NULL,        -- 노무사 자격번호
    name            VARCHAR(100) NOT NULL,
    firm_name       VARCHAR(200),
    specialties     TEXT[] NOT NULL,                    -- ARRAY['dismissal', 'wage', 'industrial_accident']
    regions         TEXT[] NOT NULL,                    -- ARRAY['seoul', 'gyeonggi', 'nationwide']
    consultation_fee NUMERIC(10,0) NOT NULL,            -- 기본 상담료
    is_available    BOOLEAN DEFAULT TRUE,
    rating          NUMERIC(3,2) DEFAULT 0.00,
    review_count    INTEGER DEFAULT 0,
    response_rate   NUMERIC(5,2) DEFAULT 0.00,          -- 응답률 (%)
    bio             TEXT,
    profile_image_url TEXT,
    verified        BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### attorney_cases (노무사 상담 케이스)

```sql
CREATE TABLE attorney_cases (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    attorney_id     UUID NOT NULL REFERENCES labor_attorneys(id),
    company_id      UUID REFERENCES companies(id),
    case_summary    TEXT NOT NULL,                      -- AI 자동 생성 케이스 요약
    case_type       VARCHAR(50) NOT NULL,               -- 'dismissal', 'wage', 'sexual_harassment' 등
    urgency         VARCHAR(20) NOT NULL
                    CHECK (urgency IN ('low', 'medium', 'high', 'emergency')),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'accepted', 'in_progress', 'completed', 'cancelled')),
    scheduled_at    TIMESTAMPTZ,
    consultation_type VARCHAR(20)
                    CHECK (consultation_type IN ('phone', 'video', 'visit')),
    fee_amount      NUMERIC(10,0),
    fee_paid        BOOLEAN DEFAULT FALSE,
    fee_paid_at     TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### subscriptions (구독)

```sql
CREATE TABLE subscriptions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan            VARCHAR(20) NOT NULL
                    CHECK (plan IN ('free', 'basic', 'standard', 'premium', 'enterprise')),
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'cancelled', 'expired', 'paused')),
    starts_at       TIMESTAMPTZ NOT NULL,
    expires_at      TIMESTAMPTZ,
    cancelled_at    TIMESTAMPTZ,
    toss_order_id   VARCHAR(100),                       -- 토스페이먼츠 주문 ID
    toss_billing_key VARCHAR(200),                      -- 자동결제 키
    monthly_amount  NUMERIC(10,0) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_expires ON subscriptions(expires_at) WHERE status = 'active';
```

#### labor_law_rates (노동법 요율 마스터)

```sql
CREATE TABLE labor_law_rates (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rate_type       VARCHAR(50) NOT NULL
                    CHECK (rate_type IN (
                        'minimum_wage',
                        'national_pension_employee',
                        'health_insurance_employee',
                        'long_term_care_rate',         -- 건강보험료 대비 비율
                        'employment_insurance_employee'
                    )),
    value           NUMERIC(10,4) NOT NULL,             -- 금액 또는 요율
    effective_year  INTEGER NOT NULL,
    effective_month INTEGER NOT NULL DEFAULT 1,
    source_url      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_rates_unique ON labor_law_rates(rate_type, effective_year, effective_month);

-- 초기 데이터 (2026년 기준)
INSERT INTO labor_law_rates (rate_type, value, effective_year) VALUES
    ('minimum_wage', 10030, 2026),                     -- 원/시간
    ('national_pension_employee', 0.045, 2026),
    ('health_insurance_employee', 0.03545, 2026),
    ('long_term_care_rate', 0.1295, 2026),
    ('employment_insurance_employee', 0.009, 2026);
```

---

## 5. API 엔드포인트 명세

### 5.1 공통 규칙

```
Base URL: https://api.nomoodoc.com/v1

인증: Bearer Token (JWT)
  Authorization: Bearer <access_token>

응답 포맷:
{
  "success": true,
  "data": { ... },
  "meta": { "page": 1, "per_page": 20, "total": 100 }  // 목록 시
}

에러 포맷:
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력값을 확인해주세요.",
    "details": [{ "field": "base_wage", "message": "최저임금 미달" }]
  }
}

에러 코드:
  400 VALIDATION_ERROR       - 입력값 오류
  401 UNAUTHORIZED           - 인증 필요
  403 FORBIDDEN              - 권한 없음
  403 PLAN_UPGRADE_REQUIRED  - 플랜 업그레이드 필요
  404 NOT_FOUND              - 리소스 없음
  429 RATE_LIMIT_EXCEEDED    - 요청 한도 초과
  500 INTERNAL_ERROR         - 서버 오류
```

---

### 5.2 인증 API

#### POST /auth/register
사용자 회원가입

**Request:**
```json
{
  "email": "owner@company.com",
  "password": "Password123!",
  "name": "홍길동",
  "phone": "010-1234-5678"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "email": "owner@company.com",
    "name": "홍길동",
    "plan": "free",
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

#### POST /auth/login
로그인

**Request:**
```json
{
  "email": "owner@company.com",
  "password": "Password123!"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",         // 만료: 1시간
    "refresh_token": "eyJ...",        // 만료: 30일
    "user": {
      "id": "uuid",
      "name": "홍길동",
      "plan": "standard",
      "company_id": "uuid"
    }
  }
}
```

#### POST /auth/kakao
카카오 OAuth 로그인

**Request:**
```json
{ "code": "kakao_auth_code" }
```

#### POST /auth/refresh
토큰 갱신

**Request:**
```json
{ "refresh_token": "eyJ..." }
```

---

### 5.3 회사 API

#### POST /companies
사업장 등록

**Request:**
```json
{
  "business_name": "행복한 식당",
  "business_number": "123-45-67890",
  "representative_name": "홍길동",
  "industry_type": "food_service",
  "employee_count": 8,
  "address": "서울시 강남구 테헤란로 123",
  "phone": "02-1234-5678"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "business_name": "행복한 식당",
    "work_rule_required": false,
    "compliance_score": 100,
    "created_at": "2026-03-01T00:00:00Z"
  }
}
```

#### GET /companies/{company_id}
사업장 조회

#### PATCH /companies/{company_id}
사업장 정보 수정

#### GET /companies/{company_id}/dashboard
컴플라이언스 대시보드 조회

**Response 200:**
```json
{
  "success": true,
  "data": {
    "compliance_score": 72,
    "risk_level": "yellow",
    "issues": [
      {
        "type": "missing_contract",
        "severity": "high",
        "message": "근로계약서 미작성 직원 2명",
        "affected_count": 2,
        "action_url": "/contracts/new"
      },
      {
        "type": "payslip_not_sent",
        "severity": "medium",
        "message": "이번 달 급여명세서 미발송 3명",
        "affected_count": 3,
        "action_url": "/payslips"
      }
    ],
    "upcoming_events": [
      {
        "type": "contract_expiry",
        "date": "2026-04-01",
        "description": "김철수 계약 만료 (D-31)",
        "employee_id": "uuid"
      }
    ],
    "stats": {
      "total_employees": 8,
      "active_contracts": 6,
      "monthly_payslips_sent": 5
    }
  }
}
```

---

### 5.4 직원 API

#### POST /companies/{company_id}/employees
직원 등록

**Request:**
```json
{
  "name": "김철수",
  "nationality": "korean",
  "employment_type": "regular",
  "department": "주방",
  "position": "조리사",
  "hire_date": "2024-01-15",
  "phone": "010-9876-5432",
  "email": "chulsoo@example.com"
}
```

#### GET /companies/{company_id}/employees
직원 목록 조회

**Query:** `?status=active&employment_type=regular&page=1&per_page=20`

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "김철수",
      "employment_type": "regular",
      "hire_date": "2024-01-15",
      "has_contract": true,
      "contract_status": "signed",
      "contract_end_date": null
    }
  ],
  "meta": { "page": 1, "per_page": 20, "total": 8 }
}
```

#### GET /companies/{company_id}/employees/{employee_id}
직원 상세 조회

#### PATCH /companies/{company_id}/employees/{employee_id}
직원 정보 수정

#### DELETE /companies/{company_id}/employees/{employee_id}
직원 퇴직 처리 (소프트 삭제, resign_date 설정)

---

### 5.5 근로계약서 API

#### POST /contracts/generate
근로계약서 AI 생성

**Request:**
```json
{
  "employee_id": "uuid",
  "company_id": "uuid",
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
  "meal_allowance": 200000,
  "transport_allowance": 100000,
  "probation_months": 3,
  "probation_wage_rate": 1.0,
  "nda_included": false,
  "non_compete_included": false
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "contract_id": "uuid",
    "status": "draft",
    "content": "...",
    "validations": {
      "minimum_wage_ok": true,
      "weekly_hours_ok": true,
      "mandatory_fields_ok": true
    },
    "warnings": [],
    "docx_url": "https://s3.amazonaws.com/...",
    "pdf_url": "https://s3.amazonaws.com/..."
  }
}
```

**에러 케이스:**
```json
{
  "success": false,
  "error": {
    "code": "MINIMUM_WAGE_VIOLATION",
    "message": "입력한 기본급이 2026년 최저임금 기준에 미달합니다.",
    "details": {
      "input_hourly": 9500,
      "minimum_wage_2026": 10030,
      "shortfall": 530
    }
  }
}
```

#### GET /contracts/{contract_id}
계약서 조회

#### PATCH /contracts/{contract_id}
계약서 수정

#### POST /contracts/{contract_id}/download
계약서 다운로드 URL 생성

**Request:**
```json
{ "format": "pdf" }    // "pdf" | "docx"
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "download_url": "https://s3.amazonaws.com/...",
    "expires_at": "2026-03-01T01:00:00Z"
  }
}
```

#### POST /contracts/{contract_id}/send-for-signature
전자서명 링크 발송 (Phase 2)

---

### 5.6 급여 계산 API

#### POST /payroll/calculate
급여 계산 (저장 없이 계산만)

**Request:**
```json
{
  "employee_id": "uuid",
  "year": 2026,
  "month": 3,
  "work_records": [
    {
      "work_date": "2026-03-04",
      "overtime_minutes": 60,
      "night_minutes": 0,
      "holiday_minutes": 0,
      "is_holiday": false
    }
  ]
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "gross_pay": 2800000,
    "breakdown": {
      "base_pay": 2500000,
      "holiday_pay": 0,
      "overtime_pay": 71770,
      "night_pay": 0,
      "holiday_work_pay": 0,
      "meal_allowance": 200000,
      "transport_allowance": 100000
    },
    "deductions": {
      "national_pension": 112500,
      "health_insurance": 99260,
      "long_term_care": 12854,
      "employment_insurance": 25200,
      "income_tax": 45000,
      "local_income_tax": 4500,
      "total": 299314
    },
    "net_pay": 2500686,
    "calculation_detail": { ... }
  }
}
```

#### POST /payroll/payslips
급여명세서 생성 및 저장

**Request:**
```json
{
  "employee_id": "uuid",
  "company_id": "uuid",
  "year": 2026,
  "month": 3,
  "work_records": [ ... ],
  "send_immediately": true,
  "send_via": "kakao"
}
```

#### GET /payroll/payslips
급여명세서 목록

**Query:** `?company_id=uuid&year=2026&month=3`

#### POST /payroll/payslips/{payslip_id}/send
급여명세서 발송

**Request:**
```json
{ "send_via": "kakao" }   // "kakao" | "email" | "both"
```

#### POST /payroll/upload-work-records
엑셀 근무 기록 일괄 업로드

**Request:** `multipart/form-data`
- `file`: xlsx/csv 파일
- `company_id`: UUID
- `year`: 2026
- `month`: 3

**Response 200:**
```json
{
  "success": true,
  "data": {
    "total_rows": 25,
    "success_count": 23,
    "error_rows": [
      { "row": 5, "employee_name": "박민수", "error": "직원 미등록" },
      { "row": 12, "employee_name": "이영희", "error": "날짜 형식 오류" }
    ]
  }
}
```

---

### 5.7 퇴직금 계산 API

#### POST /retirement/calculate
퇴직금 계산

**Request:**
```json
{
  "employee_id": "uuid",
  "resignation_date": "2026-03-31",
  "monthly_wages": [
    { "year": 2026, "month": 1, "gross_pay": 2800000 },
    { "year": 2025, "month": 12, "gross_pay": 2800000 },
    { "year": 2025, "month": 11, "gross_pay": 2800000 }
  ],
  "annual_bonus": 2400000,
  "unused_leave_days": 5
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "retirement_pay": 7123287,
    "unused_leave_pay": 458904,
    "total_payment": 7582191,
    "breakdown": {
      "average_daily_wage": 97579,
      "service_days": 730,
      "service_years": 2.0
    },
    "payment_deadline": "2026-04-14"     // 퇴직 후 14일 이내
  }
}
```

---

### 5.8 AI Q&A API

#### POST /chat/sessions
새 상담 세션 시작

**Request:**
```json
{
  "company_id": "uuid",
  "context": {
    "industry_type": "food_service",
    "employee_count": 8
  }
}
```

#### POST /chat/sessions/{session_id}/messages
메시지 전송 (Streaming SSE)

**Request:**
```json
{
  "content": "주 15시간 미만 알바생한테 주휴수당 줘야 하나요?"
}
```

**Response: Server-Sent Events (text/event-stream)**
```
data: {"type": "thinking", "content": ""}
data: {"type": "text", "content": "주"}
data: {"type": "text", "content": "휴수당"}
...
data: {"type": "law_reference", "law": "근로기준법 제55조", "url": "..."}
data: {"type": "risk_level", "level": "low"}
data: {"type": "disclaimer", "content": "※ 본 답변은 참고용..."}
data: {"type": "done", "session_id": "uuid", "message_id": "uuid"}
```

#### GET /chat/sessions/{session_id}/messages
상담 히스토리 조회

#### GET /chat/sessions
내 상담 세션 목록

---

### 5.9 구독/결제 API

#### GET /subscriptions/plans
플랜 목록 조회

#### POST /subscriptions
구독 시작 (토스페이먼츠 결제)

**Request:**
```json
{
  "plan": "standard",
  "billing_key": "toss_billing_key",
  "payment_method": "card"
}
```

#### GET /subscriptions/current
현재 구독 상태 조회

#### DELETE /subscriptions/current
구독 해지

---

### 5.10 노무사 마켓플레이스 API

#### GET /attorneys
노무사 목록

**Query:** `?specialty=dismissal&region=seoul&sort=rating`

#### GET /attorneys/{attorney_id}
노무사 프로필 조회

#### POST /attorney-cases
노무사 상담 신청

**Request:**
```json
{
  "attorney_id": "uuid",
  "company_id": "uuid",
  "case_type": "dismissal",
  "urgency": "high",
  "chat_session_id": "uuid",     // 기존 AI 상담 세션 → 케이스 요약 자동 생성
  "consultation_type": "video",
  "preferred_schedule": ["2026-03-05T14:00:00Z", "2026-03-06T10:00:00Z"]
}
```

---

## 6. Claude 프롬프트 설계

### 6.1 프롬프트 설계 원칙

```
1. 역할 명확화: 노무 전문 AI 어시스턴트 역할 고정
2. 컨텍스트 주입: 사업장 정보, 업종, 직원 수를 항상 포함
3. RAG 결과 통합: 관련 법령 조항을 context로 제공
4. 출력 형식 제어: 구조화된 JSON 또는 Markdown 형식 강제
5. 면책 문구: 시스템 레벨에서 자동 삽입 (프롬프트 의존 금지)
6. 토큰 최적화: 대화 히스토리 최대 10턴으로 제한
```

### 6.2 Feature 1: 노동법 Q&A 프롬프트

#### System Prompt

```
당신은 대한민국 노동법 전문 AI 어시스턴트입니다.
사용자의 노무·HR 질문에 정확하고 실용적인 답변을 제공합니다.

## 사업장 컨텍스트
- 업종: {industry_type_korean}
- 직원 수: {employee_count}명
- 사업장 규모: {scale}  (예: "소규모", "중소기업")

## 답변 원칙
1. 한국 노동법령에 근거하여 답변하십시오.
2. 법령 조항은 반드시 "(근로기준법 제○○조)" 형식으로 인용하십시오.
3. 불확실한 내용은 "확인이 필요합니다"라고 명시하십시오.
4. 위험도를 LOW/MEDIUM/HIGH/EMERGENCY 중 하나로 분류하십시오.
5. 사용자가 이해하기 쉬운 쉬운 말로 설명하십시오.
6. 복잡한 케이스는 전문가 상담을 권유하십시오.

## 참고 법령 컨텍스트
{rag_context}

## 출력 형식 (반드시 준수)
답변을 다음 JSON 형식으로 출력하십시오:
{
  "answer": "사용자에게 보여줄 답변 (Markdown 허용)",
  "risk_level": "low|medium|high|emergency",
  "law_references": [
    {"law": "근로기준법", "article": "제55조", "content": "조항 내용 요약"}
  ],
  "follow_up_questions": ["관련하여 궁금할 수 있는 질문 1", "질문 2"],
  "attorney_recommended": true/false,
  "attorney_reason": "노무사 추천 이유 (attorney_recommended가 true인 경우)"
}
```

#### User Prompt Template

```python
def build_qa_user_prompt(user_message: str, conversation_history: list) -> str:
    history_text = ""
    for msg in conversation_history[-10:]:  # 최대 10턴
        role = "사용자" if msg["role"] == "user" else "AI"
        history_text += f"{role}: {msg['content']}\n\n"
    
    return f"""이전 대화:
{history_text}

사용자 질문:
{user_message}"""
```

#### RAG 검색 전략

```python
# 1단계: 의도 분류
INTENT_CATEGORIES = {
    "wage": ["임금", "급여", "최저임금", "주휴수당", "연장수당", "야간수당", "퇴직금"],
    "contract": ["근로계약", "계약서", "수습", "계약직", "기간제"],
    "dismissal": ["해고", "권고사직", "계약해지", "부당해고", "해고예고"],
    "leave": ["연차", "휴가", "육아휴직", "출산휴가", "병가"],
    "safety": ["산재", "산업재해", "업무상 재해"],
    "discrimination": ["직장 내 괴롭힘", "성희롱", "차별"],
    "penalty": ["과태료", "신고", "고용노동부", "근로감독"]
}

# 2단계: 관련 법령 벡터 검색 (top-k=5)
# 3단계: 검색 결과를 system prompt의 {rag_context}에 주입
```

---

### 6.3 Feature 2: 근로계약서 생성 프롬프트

#### System Prompt

```
당신은 한국 노동법에 정통한 근로계약서 작성 전문가입니다.
입력된 근무 조건을 바탕으로 법적으로 유효한 근로계약서를 작성합니다.

## 필수 준수 사항
1. 근로기준법 제17조의 법정 필수 기재사항 8개를 반드시 포함하십시오:
   - 임금의 구성항목·계산방법·지급방법
   - 소정근로시간
   - 제55조에 따른 휴일
   - 제60조에 따른 연차 유급휴가
   - 취업의 장소와 종사해야 할 업무에 관한 사항
   - 근로기준법 제93조 각 호의 사항의 정함이 있는 경우 이에 관한 사항
   - 사업장의 부속 기숙사에 근로자를 기숙하게 하는 경우 기숙사 규칙
   - 근로계약기간 (기간 정함이 있는 경우)

2. 단시간 근로자의 경우 단시간근로자 보호법에 따른 추가 기재사항을 포함하십시오.
3. 외국인 근로자의 경우 외국인고용법을 준수하십시오.
4. 법적 분쟁 시 근로자에게 유리한 해석이 적용됨을 고려하여 명확하게 작성하십시오.

## 출력 형식
근로계약서 전문을 Markdown 형식으로 출력하십시오.
섹션 구분: ## 로 구분
서명란 포함
```

#### User Prompt Template

```python
def build_contract_prompt(contract_data: dict) -> str:
    return f"""다음 조건으로 근로계약서를 작성하십시오:

## 계약 당사자
- 사업장명: {contract_data['business_name']}
- 사업자등록번호: {contract_data['business_number']}
- 대표자: {contract_data['representative_name']}
- 근로자명: {contract_data['employee_name']}
- 생년월일: {contract_data.get('birth_date', '직접 기재')}

## 계약 기간
- 계약 유형: {contract_data['contract_type_korean']}
- 시작일: {contract_data['start_date']}
- 종료일: {contract_data.get('end_date', '정함 없음')}

## 근무 조건
- 근무 장소: {contract_data['work_location']}
- 업무 내용: {contract_data.get('job_description', '계약 당사자 합의에 따름')}
- 근무시간: {contract_data['work_start_time']} ~ {contract_data['work_end_time']}
- 휴게시간: {contract_data['break_minutes']}분
- 소정근로일: {contract_data['work_days_korean']}
- 주 소정근로시간: {contract_data['work_hours_per_week']}시간

## 임금 조건
- 임금 유형: {contract_data['wage_type_korean']}
- 기본급: {contract_data['base_wage']:,}원
- 식대: {contract_data.get('meal_allowance', 0):,}원
- 교통비: {contract_data.get('transport_allowance', 0):,}원
- 합계: {contract_data['total_wage']:,}원
- 지급일: 매월 {contract_data.get('pay_day', 25)}일
- 지급 방법: 근로자 본인 명의 계좌 입금

## 수습 조건
{f"- 수습기간: {contract_data['probation_months']}개월" if contract_data.get('probation_months') else "- 수습 없음"}
{f"- 수습기간 임금: 기본급의 {int(contract_data['probation_wage_rate'] * 100)}%" if contract_data.get('probation_months') else ""}

## 특약사항
{f"- 비밀유지 조항 포함" if contract_data.get('nda_included') else ""}
{f"- 경업금지 조항 포함 (퇴직 후 1년, 동종업계)" if contract_data.get('non_compete_included') else ""}
"""
```

---

### 6.4 Feature 3: 급여명세서 생성 프롬프트

#### System Prompt

```
당신은 급여명세서 작성 전문가입니다.
계산된 급여 데이터를 바탕으로 근로기준법 제48조에 따른 법정 급여명세서를 작성합니다.

## 급여명세서 법정 기재사항 (근로기준법 제48조제2항)
1. 임금의 구성항목별 금액
2. 출근일수·시간
3. 연장·야간·휴일근로 시간
4. 공제항목과 금액
5. 실지급액

출력을 보기 좋은 Markdown 표 형식으로 작성하십시오.
```

---

### 6.5 Feature 5: 퇴직금/해고 절차 프롬프트

#### System Prompt

```
당신은 한국 노동법 전문 AI입니다.
퇴직/해고 관련 질문에 법령에 근거한 절차와 계산 방법을 안내합니다.

## 해고 절차 안내 원칙
1. 해고의 정당한 이유 (근로기준법 제23조) 를 먼저 검토하십시오.
2. 해고예고 의무 (30일 전 예고 또는 30일분 통상임금 지급) 를 안내하십시오.
3. 서면 통보 의무 (근로기준법 제27조) 를 반드시 언급하십시오.
4. 해고가 부당할 가능성이 있으면 노무사 상담을 강력히 권유하십시오.
5. 해고 대신 권고사직, 계약 만료 등 대안을 먼저 제시하십시오.

## 위험 케이스 (반드시 HIGH 또는 EMERGENCY로 분류)
- 임신·육아휴직 중 직원 해고
- 노조 활동 관련 해고
- 공익신고자 해고
- 정당한 이유 없는 해고
```

---

### 6.6 Feature 6: 노무사 케이스 요약 프롬프트

#### System Prompt

```
당신은 노무 케이스 분석 전문가입니다.
AI 상담 대화 내역을 바탕으로 파트너 노무사가 즉시 파악할 수 있는 케이스 요약서를 작성합니다.

## 출력 형식 (JSON)
{
  "case_title": "케이스 제목 (예: 계약직 직원 부당해고 이의 신청 대응)",
  "case_type": "dismissal|wage|leave|industrial_accident|harassment|other",
  "urgency": "low|medium|high|emergency",
  "urgency_reason": "긴급도 판단 이유",
  "client_summary": {
    "industry": "업종",
    "employee_count": 8,
    "issue_date": "사건 발생 일시"
  },
  "issue_summary": "핵심 쟁점 3~5줄 요약",
  "key_facts": ["사실관계 항목 1", "항목 2"],
  "relevant_laws": ["근로기준법 제○○조"],
  "risk_assessment": "법적 위험도 및 예상 결과",
  "recommended_actions": ["즉시 해야 할 조치 1", "조치 2"],
  "documents_needed": ["필요 서류 1", "서류 2"]
}
```

---

### 6.7 컨텍스트 최적화 전략

```python
# 대화 히스토리 토큰 관리
MAX_HISTORY_TURNS = 10
MAX_TOKENS_PER_TURN = 500  # 각 메시지 최대 토큰

def trim_conversation_history(history: list) -> list:
    """
    최신 10턴 유지, 각 메시지 500토큰 이하로 트림
    시스템 메시지는 항상 유지
    """
    trimmed = []
    for msg in history[-MAX_HISTORY_TURNS:]:
        if len(msg["content"]) > MAX_TOKENS_PER_TURN * 4:  # 4 chars ≈ 1 token
            msg = {**msg, "content": msg["content"][:MAX_TOKENS_PER_TURN * 4] + "..."}
        trimmed.append(msg)
    return trimmed

# RAG 검색 결과 최대 3개 법령 조항으로 제한
MAX_RAG_RESULTS = 3
MAX_RAG_CHARS_PER_RESULT = 800
```

---

## 7. Claude Code 멀티에이전트 아키텍처

### 7.1 에이전트 분리 전략

```
전체 프로젝트를 8개 에이전트로 분리:

Agent-0: Orchestrator (조율)
Agent-1: Database & Models
Agent-2: Auth & User Management
Agent-3: Contract Generation
Agent-4: Payroll Calculation
Agent-5: AI Q&A & RAG
Agent-6: Frontend (Next.js)
Agent-7: DevOps & Integration
```

### 7.2 Agent-0: Orchestrator

**역할:** 전체 개발 순서 조율, 에이전트 간 의존성 관리

**실행 순서:**
```
1. Agent-1 (DB) → 완료 후
2. Agent-2 (Auth) 병렬 시작
3. Agent-3 (Contract) 병렬 시작
4. Agent-4 (Payroll) 병렬 시작
5. Agent-5 (AI Q&A) 병렬 시작
6. Agent-2,3,4,5 완료 후 → Agent-6 (Frontend) 시작
7. 전체 완료 후 → Agent-7 (DevOps)
```

**초기화 프롬프트:**
```
당신은 노무닥터 프로젝트의 오케스트레이터 에이전트입니다.

프로젝트 구조:
/nomoodoc
  /backend         # FastAPI 백엔드
    /app
      /api         # 라우터
      /core        # 설정, 보안
      /db          # SQLAlchemy 모델
      /services    # 비즈니스 로직
      /schemas     # Pydantic 스키마
      /ai          # Claude API 클라이언트
  /frontend        # Next.js 프론트엔드
    /app           # App Router
    /components    # 공통 컴포넌트
    /lib           # 유틸리티
  /docs            # 문서
  docker-compose.yml

기술 스택:
- Backend: Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic
- Database: PostgreSQL 16, Redis 7
- AI: Anthropic Claude API (claude-sonnet-4-6)
- Frontend: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- Auth: JWT (python-jose), bcrypt
- Storage: AWS S3 (boto3)
- Payment: 토스페이먼츠 API
- Deploy: Docker, AWS ECS

각 에이전트 작업을 순서에 맞게 시작하고, 각 에이전트가 작업 완료 시
다음 에이전트에게 컨텍스트를 전달하십시오.
```

---

### 7.3 Agent-1: Database & Models

**담당 파일:**
```
/backend/app/db/
  __init__.py
  base.py          # SQLAlchemy Base, engine, session
  models/
    user.py
    company.py
    employee.py
    contract.py
    salary.py       # salary_settings, work_records, payslips
    chat.py         # chat_sessions, chat_messages
    work_rule.py
    attorney.py     # labor_attorneys, attorney_cases
    subscription.py
    labor_law.py    # labor_law_rates
/backend/alembic/
  alembic.ini
  env.py
  versions/
    001_initial_schema.py
```

**초기화 프롬프트:**
```
당신은 노무닥터의 데이터베이스 에이전트입니다.

작업 목표:
1. PRD Section 4의 DB 스키마를 SQLAlchemy 2.0 ORM 모델로 구현하십시오.
2. Alembic 마이그레이션 스크립트를 생성하십시오.
3. 모든 외래키, 인덱스, 제약조건을 PRD 명세대로 구현하십시오.
4. 암호화가 필요한 필드 (id_number, bank_account)는 SQLAlchemy TypeDecorator로 처리하십시오.
5. Row-level security를 위해 company_id 기반 필터링 믹스인을 구현하십시오.

주요 구현 요구사항:
- UUID 기본키 (gen_random_uuid())
- TIMESTAMPTZ (타임존 포함)
- generated column: companies.work_rule_required
- JSONB 필드: chat_messages.law_references, payslips.calculation_detail
- TEXT[] 배열: labor_attorneys.specialties, regions

완료 후:
- models/__init__.py에 모든 모델 임포트
- docker-compose.yml의 postgres 서비스 확인
- alembic upgrade head 실행 가능한 상태로 제출
```

---

### 7.4 Agent-2: Auth & User Management

**담당 파일:**
```
/backend/app/
  core/
    config.py        # 환경변수 (pydantic-settings)
    security.py      # JWT, bcrypt, OAuth
    dependencies.py  # FastAPI 의존성 주입
  api/
    v1/
      auth.py        # 인증 라우터
      users.py       # 사용자 관리
      companies.py   # 회사 관리
  services/
    auth_service.py
    user_service.py
    company_service.py
  schemas/
    auth.py
    user.py
    company.py
```

**초기화 프롬프트:**
```
당신은 노무닥터의 인증/사용자 관리 에이전트입니다.

의존성: Agent-1 완료 후 시작 (DB 모델 사용)

작업 목표:
1. PRD Section 5.2, 5.3 API 명세를 FastAPI로 구현하십시오.
2. JWT 인증 (access: 1시간, refresh: 30일) 을 구현하십시오.
3. 카카오 OAuth 2.0 로그인을 구현하십시오.
4. 플랜별 접근 제어 미들웨어를 구현하십시오.
5. company_id 기반 데이터 격리를 의존성 주입으로 구현하십시오.

구현 세부사항:
- bcrypt 해싱 (rounds=12)
- JWT payload: {user_id, company_id, plan, role, exp}
- Refresh Token Rotation 구현
- Rate Limiting: 로그인 시도 5회/분 제한 (Redis)

플랜 권한 테이블:
  free: Q&A 10회/월, 계약서 2건/월
  basic: Q&A 무제한, 계약서 무제한
  standard: basic + 급여명세서 발송 100건/월
  premium: 전체 기능 무제한

완료 후: /docs에서 Swagger 문서 확인 가능하도록
```

---

### 7.5 Agent-3: Contract Generation

**담당 파일:**
```
/backend/app/
  api/v1/
    contracts.py
    employees.py
  services/
    contract_service.py
    employee_service.py
    document_service.py    # Word/PDF 생성
  ai/
    contract_prompt.py     # 계약서 생성 프롬프트
  schemas/
    contract.py
    employee.py
/backend/app/templates/
  contract_base.docx       # 기본 템플릿
```

**초기화 프롬프트:**
```
당신은 노무닥터의 근로계약서 생성 에이전트입니다.

의존성: Agent-1 (DB), Agent-2 (Auth) 완료 후 시작

작업 목표:
1. PRD Section 5.4, 5.5 API 명세를 구현하십시오.
2. PRD Section 6.3의 Claude 프롬프트를 사용하여 계약서를 생성하십시오.
3. python-docx로 Word(.docx) 파일을 생성하십시오.
4. WeasyPrint로 PDF를 생성하십시오.
5. 생성된 파일을 AWS S3에 업로드하고 presigned URL을 반환하십시오.
6. 최저임금 검증 로직을 구현하십시오.

최저임금 검증:
  시급 계산: 월급 ÷ 209시간 (월 소정근로시간)
  2026년 최저임금: labor_law_rates 테이블에서 조회
  미달 시: HTTP 422 + MINIMUM_WAGE_VIOLATION 에러코드 반환

계약서 생성 Flow:
  1. 입력 검증 (Pydantic)
  2. 최저임금 검증
  3. 주 근무시간 52시간 초과 체크
  4. Claude API 호출 (PRD 6.3 프롬프트)
  5. 응답 파싱 및 docx 생성
  6. PDF 변환
  7. S3 업로드
  8. DB 저장
  9. Presigned URL 반환 (24시간 유효)

완료 후: POST /contracts/generate 테스트 가능한 상태
```

---

### 7.6 Agent-4: Payroll Calculation

**담당 파일:**
```
/backend/app/
  api/v1/
    payroll.py
  services/
    payroll_service.py     # 급여 계산 엔진
    payslip_service.py     # 명세서 생성/발송
    notification_service.py # 카카오/이메일 발송
  schemas/
    payroll.py
  utils/
    wage_calculator.py     # 수당 계산 유틸
    tax_calculator.py      # 세금 계산 유틸
```

**초기화 프롬프트:**
```
당신은 노무닥터의 급여 계산 에이전트입니다.

의존성: Agent-1 (DB), Agent-2 (Auth) 완료 후 시작

작업 목표:
1. PRD Section 5.6의 API 명세를 구현하십시오.
2. PRD Feature 3의 계산 항목 전체를 수학적으로 정확하게 구현하십시오.
3. 간이세액표를 DB 또는 파일로 관리하고 소득세를 계산하십시오.
4. 카카오 알림톡 API로 급여명세서를 발송하십시오.
5. 엑셀 파일 파싱 (openpyxl) 을 구현하십시오.

급여 계산 정확성 요구사항:
  - 소수점 처리: 모든 중간 계산은 Decimal 타입 사용 (float 금지)
  - 원 단위 절사: 10원 미만 절사
  - 주휴수당: 주 소정근로시간 / 5 × 시급 (개근 조건 포함)

통상임금 계산:
  통상시급 = (기본급 + 고정수당) ÷ (주 소정근로시간 × 52 / 12 + 주휴수당 시간)

카카오 알림톡 Fallback:
  카카오 실패 → 이메일로 자동 재시도 (3회)
  이메일도 실패 → DB에 'failed' 기록, 관리자 알림

완료 후: 급여 계산 pytest 테스트 케이스 10개 포함 (다양한 고용형태)
```

---

### 7.7 Agent-5: AI Q&A & RAG

**담당 파일:**
```
/backend/app/
  api/v1/
    chat.py
    retirement.py      # 퇴직금 계산
  services/
    chat_service.py
    rag_service.py     # 벡터 검색
    retirement_service.py
  ai/
    claude_client.py   # Anthropic SDK 래퍼
    qa_prompt.py       # Q&A 프롬프트
    retirement_prompt.py
    attorney_case_prompt.py
  data/
    labor_laws/        # 법령 텍스트 데이터
      labor_standards_act.txt
      minimum_wage_act.txt
      employment_insurance_act.txt
      # ...
```

**초기화 프롬프트:**
```
당신은 노무닥터의 AI Q&A 및 RAG 에이전트입니다.

의존성: Agent-1 (DB), Agent-2 (Auth) 완료 후 시작

작업 목표:
1. PRD Section 5.8의 SSE 스트리밍 API를 구현하십시오.
2. PRD Section 6.2의 프롬프트를 사용한 Q&A 서비스를 구현하십시오.
3. pgvector 익스텐션을 사용한 RAG 검색을 구현하십시오.
4. PRD Section 5.7의 퇴직금 계산 API를 구현하십시오.
5. PRD Section 6.6의 노무사 케이스 요약 기능을 구현하십시오.

RAG 구현 세부사항:
  - Embedding 모델: text-embedding-3-small (OpenAI) 또는 Claude 자체 임베딩
  - Vector DB: pgvector (PostgreSQL 익스텐션)
  - 청크 크기: 500 토큰, 오버랩 100 토큰
  - 검색: cosine similarity, top-k=3

SSE 스트리밍 구현:
  FastAPI StreamingResponse + Server-Sent Events
  이벤트 타입: thinking, text, law_reference, risk_level, disclaimer, done

면책 문구 처리:
  - AI 답변 생성 완료 후 시스템 레벨에서 추가 (프롬프트 의존 금지)
  - 매 응답에 100% 삽입
  - DB의 disclaimer_shown 필드를 True로 업데이트

위험도 HIGH/EMERGENCY 자동 처리:
  - 채팅 세션의 risk_level 업데이트
  - 프론트엔드에 노무사 연결 CTA 표시 이벤트 전송

완료 후: 10개 Q&A 테스트 시나리오 포함 (다양한 위험도)
```

---

### 7.8 Agent-6: Frontend (Next.js)

**담당 파일:**
```
/frontend/
  app/
    (auth)/
      login/page.tsx
      register/page.tsx
    (dashboard)/
      layout.tsx
      page.tsx                  # 컴플라이언스 대시보드
      employees/
        page.tsx                # 직원 목록
        new/page.tsx            # 직원 등록
        [id]/page.tsx           # 직원 상세
      contracts/
        page.tsx                # 계약서 목록
        new/page.tsx            # 계약서 생성
        [id]/page.tsx           # 계약서 상세
      payroll/
        page.tsx                # 급여 계산
        payslips/page.tsx       # 급여명세서
      chat/
        page.tsx                # AI 상담
        [sessionId]/page.tsx    # 상담 상세
      settings/
        page.tsx                # 설정
    api/                        # Next.js API Routes (BFF)
  components/
    ui/                         # shadcn/ui
    layout/
      Sidebar.tsx
      Header.tsx
    chat/
      ChatWindow.tsx
      MessageBubble.tsx
      LawReference.tsx
    contracts/
      ContractForm.tsx
      ContractPreview.tsx
    payroll/
      PayrollCalculator.tsx
      PayslipCard.tsx
    dashboard/
      ComplianceScore.tsx
      RiskIssueCard.tsx
      EventCalendar.tsx
  lib/
    api.ts                      # API 클라이언트
    auth.ts                     # Auth 유틸
    hooks/
      useChat.ts
      usePayroll.ts
  types/
    api.ts                      # API 응답 타입
```

**초기화 프롬프트:**
```
당신은 노무닥터의 Next.js 프론트엔드 에이전트입니다.

의존성: Agent-2,3,4,5 완료 후 시작

작업 목표:
1. PRD의 모든 기능에 대한 UI를 Next.js 14 App Router로 구현하십시오.
2. 모바일 퍼스트 반응형 디자인으로 구현하십시오.
3. shadcn/ui 컴포넌트를 기반으로 일관된 디자인 시스템을 사용하십시오.

디자인 가이드라인:
  - Primary color: #1E3A5F (네이비)
  - Secondary: #2E75B6 (블루)
  - 폰트: Pretendard (한글) / Inter (영문)
  - 컴포넌트: shadcn/ui + Radix UI

핵심 UX 요구사항:
  1. AI Q&A: SSE 스트리밍으로 실시간 타이핑 효과
  2. 근로계약서: 실시간 최저임금 경고 (onChange)
  3. 급여 계산기: 항목 변경 시 즉시 재계산
  4. 대시보드: 리스크 스코어 시각화 (Gauge 차트)
  5. 면책 문구: 모든 AI 생성 컨텐츠에 항상 표시

인증 흐름:
  - Next.js middleware로 인증 보호
  - JWT 자동 갱신 (만료 5분 전)
  - 카카오 로그인 버튼

완료 후:
  - 모든 페이지 라우팅 작동
  - Storybook 컴포넌트 문서 (선택)
```

---

### 7.9 Agent-7: DevOps & Integration

**담당 파일:**
```
/
  docker-compose.yml
  docker-compose.prod.yml
  .env.example
  /backend
    Dockerfile
    requirements.txt
    pyproject.toml
  /frontend
    Dockerfile
    package.json
  /infrastructure
    nginx.conf
    /scripts
      setup_db.sh
      seed_data.py
      update_rates.py    # 연 1회 최저임금/보험료율 업데이트
```

**초기화 프롬프트:**
```
당신은 노무닥터의 DevOps 에이전트입니다.

의존성: 모든 에이전트 완료 후 시작

작업 목표:
1. Docker Compose로 로컬 개발 환경을 구성하십시오.
2. PostgreSQL + pgvector, Redis 컨테이너를 설정하십시오.
3. .env.example 파일을 모든 필요 환경변수와 함께 생성하십시오.
4. 최저임금/4대보험료율 연 1회 자동 업데이트 스크립트를 구현하십시오.
5. 기본 시드 데이터를 생성하십시오.

환경변수 목록:
  DATABASE_URL=postgresql+asyncpg://...
  REDIS_URL=redis://...
  SECRET_KEY=...
  ANTHROPIC_API_KEY=...
  KAKAO_CLIENT_ID=...
  KAKAO_REDIRECT_URI=...
  AWS_ACCESS_KEY_ID=...
  AWS_SECRET_ACCESS_KEY=...
  AWS_S3_BUCKET=...
  TOSS_CLIENT_KEY=...
  TOSS_SECRET_KEY=...

시드 데이터:
  - 관리자 계정 1개
  - 테스트 사업장 1개 (요식업, 8인)
  - 테스트 직원 3명 (정규직, 계약직, 파트타임)
  - 노동법 RAG 데이터 초기 임베딩

완료 후: docker-compose up 으로 전체 시스템 기동 가능
```

---

### 7.10 에이전트 간 인터페이스 계약

```python
# Agent-1이 완료 후 Agent-2,3,4,5에게 전달하는 컨텍스트
AGENT_1_OUTPUT = {
    "models_path": "/backend/app/db/models/",
    "session_factory": "AsyncSessionLocal",
    "base_class": "Base",
    "available_models": [
        "User", "Company", "Employee", "Contract",
        "SalarySetting", "WorkRecord", "Payslip",
        "ChatSession", "ChatMessage", "WorkRule",
        "LaborAttorney", "AttorneyCase", "Subscription",
        "LaborLawRate"
    ]
}

# Agent-5가 완료 후 Agent-6에게 전달하는 컨텍스트
AGENT_5_OUTPUT = {
    "sse_endpoint": "POST /api/v1/chat/sessions/{session_id}/messages",
    "sse_events": ["thinking", "text", "law_reference", "risk_level", "disclaimer", "done"],
    "risk_levels": ["low", "medium", "high", "emergency"]
}
```

---

## 8. 기술 스택 상세

### 8.1 Backend (FastAPI + Python 3.12)

```
# requirements.txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy[asyncio]==2.0.36
alembic==1.14.0
asyncpg==0.30.0           # PostgreSQL 비동기 드라이버
redis[asyncio]==5.2.0
pydantic==2.10.0
pydantic-settings==2.6.0
python-jose[cryptography]==3.3.0   # JWT
passlib[bcrypt]==1.7.4
anthropic==0.40.0          # Claude API
python-docx==1.1.2         # Word 생성
weasyprint==62.3           # PDF 생성
boto3==1.35.0              # AWS S3
openpyxl==3.1.5            # 엑셀 파싱
httpx==0.28.0              # HTTP 클라이언트 (카카오 API)
pgvector==0.3.6            # 벡터 검색
sentence-transformers==3.3.1  # 임베딩
pytest==8.3.0
pytest-asyncio==0.24.0
```

### 8.2 Frontend (Next.js 14 + TypeScript)

```json
// package.json 주요 의존성
{
  "dependencies": {
    "next": "14.2.0",
    "react": "18.3.0",
    "typescript": "5.6.0",
    "tailwindcss": "3.4.0",
    "@radix-ui/react-*": "latest",
    "shadcn-ui": "latest",
    "axios": "1.7.0",
    "zustand": "5.0.0",
    "react-hook-form": "7.54.0",
    "zod": "3.23.0",
    "recharts": "2.13.0",
    "@tanstack/react-query": "5.62.0",
    "react-markdown": "9.0.0",
    "eventsource-parser": "3.0.0"
  }
}
```

### 8.3 인프라

```yaml
# docker-compose.yml 서비스 구성
services:
  postgres:
    image: pgvector/pgvector:pg16
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [postgres, redis]

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on: [backend]
```

### 8.4 외부 API 연동

| 서비스 | API 문서 | 용도 | 우선순위 |
|--------|---------|------|---------|
| Anthropic Claude | docs.anthropic.com | AI Q&A, 계약서/요약 생성 | P0 |
| 카카오 알림톡 | developers.kakao.com | 급여명세서 발송 | P1 |
| 토스페이먼츠 | docs.tosspayments.com | 구독 결제, 에스크로 | P1 |
| AWS S3 | docs.aws.amazon.com | 계약서·명세서 파일 저장 | P0 |
| 모두싸인 | api.modusign.co.kr | 전자서명 (Phase 2) | P2 |

---

## 9. 수익 모델

### 9.1 구독 티어

| 플랜 | 월 요금 | 대상 | 포함 기능 |
|------|--------|------|---------|
| 스타터 | 무료 | 5인 이하 | Q&A 10회/월, 계약서 2건/월 |
| 베이직 | 9,900원 | ~10인 | Q&A 무제한, 계약서 무제한, 급여 계산 |
| 스탠다드 | 29,000원 | ~30인 | 전체 기능, 급여명세서 발송 100건/월 |
| 프리미엄 | 49,000원 | ~50인 | 전체 기능, 발송 무제한, 노무사 1회/월 무료 |
| 엔터프라이즈 | 별도 협의 | 50인+ | 커스텀 |

### 9.2 추가 수익원

| 항목 | 단가 |
|------|------|
| 노무사 연결 | 20,000원/건 |
| 전자서명 | 1,000원/건 |
| 발송 초과분 | 100원/건 |
| 마켓플레이스 수수료 | 상담료 15% |

### 9.3 수익 목표

| 기간 | 구독자 | MRR |
|------|-------|-----|
| 6개월 | 500명 | 1,000만원 |
| 12개월 | 2,000명 | 4,000만원 |
| 24개월 | 8,000명 | 1.6억원 |

---

## 10. 마케팅/GTM 전략

### 10.1 초기 채널 (0~6개월)

**네이버 SEO:** "주휴수당 계산", "근로계약서 양식", "퇴직금 계산기" 롱테일 키워드 → 무료 계산기 유입

**카카오 비즈니스:** 소상공인·자영업자 커뮤니티 타깃팅

**유튜브 콘텐츠:** "몰랐다가 노동청 신고당한 사장님 실제 사례" — Pain point 공감

**파트너십:** 소상공인시장진흥공단, 지역 상공회의소, 프랜차이즈 본사

### 10.2 바이럴 루프

```
사장님 사용 → 근로계약서 생성 → 직원에게 공유
  → "노무닥터로 생성됨" 워터마크 → 직원이 사장 됐을 때 재구매
```

---

## 11. 리스크 분석

### 11.1 법적 리스크

| 리스크 | 심각도 | 대응 방안 |
|--------|-------|---------|
| AI 오류로 인한 고객 피해 | 높음 | 면책 약관 + 100% 면책 문구 + 노무사 검토 |
| 법률 서비스 무단 제공 (변호사법) | 높음 | "정보 제공" 명확히 구분, 법률 자문 불제공 명시 |
| 직원 개인정보 유출 | 높음 | AES-256 암호화, 접근 최소화 원칙 |
| 법령 개정 미반영 | 중간 | 법령 모니터링 자동화, 24시간 내 반영 SLA |

### 11.2 사업 리스크

| 리스크 | 심각도 | 대응 방안 |
|--------|-------|---------|
| 대기업 진입 (삼쩜삼 등) | 중간 | 노무 전문화, 빠른 점유율 확보 |
| 노무사 협회 반발 | 중간 | 노무사와 공생 모델 구축 |
| SME 낮은 SaaS 결제 의향 | 높음 | Freemium으로 진입 장벽 최소화 |
| Claude API 비용 증가 | 중간 | 캐싱 전략, 응답 재사용, 토큰 최적화 |

---

## 12. 성공 지표

| 지표 | 목표값 | 측정 주기 |
|------|-------|---------|
| DAU/MAU 비율 | 30% 이상 | 월간 |
| Q&A 만족도 | 4.5/5.0 이상 | 실시간 |
| 근로계약서 완료율 | 85% 이상 | 주간 |
| 급여명세서 발송 성공률 | 99% 이상 | 월간 |
| 프리 → 유료 전환율 | 8% 이상 | 월간 |
| 월 이탈률 (Churn Rate) | 3% 이하 | 월간 |
| AI 답변 오류 건수 | 0건 | 실시간 |
| 면책 문구 삽입률 | 100% | 실시간 |
| API p95 응답시간 | 3초 이내 | 실시간 |

---

## 13. 마일스톤

| 기간 | 마일스톤 | 산출물 |
|------|---------|-------|
| Week 1 | 기술 셋업 + DB | Docker 환경, 전체 DB 스키마, Alembic 마이그레이션 |
| Week 2 | Auth + 직원 관리 | 로그인/회원가입, JWT, 직원 CRUD |
| Week 3 | 근로계약서 MVP | 계약서 생성 API, Word/PDF 다운로드 |
| Week 4 | 급여 계산 MVP | 급여 계산 엔진, 급여명세서 생성 |
| Month 2 | AI Q&A + RAG | 챗봇 API, SSE 스트리밍, 법령 RAG |
| Month 2 | 프론트엔드 MVP | 모든 페이지 1차 구현, 베타 출시 |
| Month 3 | 취업규칙 + 퇴직금 | 취업규칙 생성, 퇴직금 계산기 |
| Month 4 | 결제 + 유료 전환 | 토스페이먼츠 연동, 첫 100명 유료 구독자 |
| Month 5~6 | 노무사 마켓플레이스 | 노무사 프로필, 예약 시스템, 에스크로 |
| Month 12 | 스케일업 | 2,000명 구독자, MRR 4,000만원 |

---

*이 PRD는 Claude Code 멀티에이전트 파이프라인 직접 실행용 문서입니다.*  
*각 섹션은 해당 에이전트의 초기화 프롬프트에서 직접 참조됩니다.*  
*docs/project/prd.md 경로에 위치시키고 CLAUDE.md에서 이 파일을 참조하십시오.*
