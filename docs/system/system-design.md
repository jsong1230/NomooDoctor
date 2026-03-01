# 시스템 설계서

## 1. 시스템 개요

### 1.1 아키텍처 패턴
- **패턴**: 모듈형 모놀리스 (Modular Monolith)
- **배포 전략**: Docker 컨테이너 + AWS ECS (초기) → 마이크로서비스 전환 가능 구조
- **이유**:
  - 초기 개발 속도와 운영 단순성 확보
  - 기능별 모듈 분리로 향후 마이크로서비스 분할 용이
  - 50인 미만 사업장 타겟으로 트래픽 예측 가능

### 1.2 전체 아키텍처 다이어그램

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Browser]
        Mobile[Mobile Web]
    end

    subgraph "CDN & Load Balancer"
        CDN[AWS CloudFront]
        ALB[Application Load Balancer]
    end

    subgraph "Frontend - Next.js 14"
        SSR[SSR Server]
        STATIC[Static Assets]
    end

    subgraph "Backend - FastAPI"
        API[API Gateway / v1 Routes]
        AUTH[Auth Module]
        EMP[Employee Module]
        CONTRACT[Contract Module]
        PAYROLL[Payroll Module]
        CHAT[AI Chat Module]
        ATTY[Attorney Module]
    end

    subgraph "AI Services"
        CLAUDE[Claude API]
        EMBED[OpenAI Embedding]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL 16<br/>+ pgvector)]
        REDIS[(Redis 7)]
        S3[(AWS S3)]
    end

    subgraph "External Services"
        TOSS[Toss Payments]
        KAKAO[Kakao Talk API]
        MODUSIGN[ModuSign]
        EMAIL[SES / SendGrid]
    end

    WEB --> CDN
    Mobile --> CDN
    CDN --> ALB
    ALB --> SSR
    SSR --> API

    API --> AUTH
    API --> EMP
    API --> CONTRACT
    API --> PAYROLL
    API --> CHAT
    API --> ATTY

    AUTH --> PG
    AUTH --> REDIS
    EMP --> PG
    CONTRACT --> PG
    CONTRACT --> S3
    CONTRACT --> CLAUDE
    PAYROLL --> PG
    PAYROLL --> KAKAO
    PAYROLL --> EMAIL
    CHAT --> PG
    CHAT --> CLAUDE
    CHAT --> EMBED
    ATTY --> PG
    ATTY --> MODUSIGN

    TOSS --> API
```

### 1.3 주요 컴포넌트 설명

| 컴포넌트 | 기술 스택 | 역할 |
|----------|-----------|------|
| Frontend | Next.js 14 App Router | SSR, 페이지 라우팅, UI 렌더링 |
| Backend API | FastAPI | REST API, 비즈니스 로직 |
| Database | PostgreSQL 16 + pgvector | 영속성 저장, 벡터 검색 |
| Cache | Redis 7 | 세션, Rate Limiting, 캐싱 |
| AI Engine | Claude API | 자연어 처리, 문서 생성 |
| Storage | AWS S3 | 파일 저장 (계약서, 명세서) |

---

## 2. 백엔드 아키텍처

### 2.1 디렉토리 구조

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 앱 진입점
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # 환경변수 (pydantic-settings)
│   │   ├── security.py            # JWT, 비밀번호 해싱
│   │   ├── exceptions.py          # 커스텀 예외
│   │   └── dependencies.py        # 공통 의존성
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py                # SQLAlchemy Base, engine
│   │   ├── session.py             # SessionLocal
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── user.py
│   │       ├── company.py
│   │       ├── employee.py
│   │       ├── contract.py
│   │       ├── salary.py          # salary_settings, work_records, payslips
│   │       ├── chat.py            # chat_sessions, chat_messages
│   │       ├── work_rule.py
│   │       ├── attorney.py        # labor_attorneys, attorney_cases
│   │       ├── subscription.py
│   │       └── labor_law.py       # labor_law_rates, law_vectors
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                # 인증, 권한 의존성
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # 전체 라우터 집합
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── companies.py
│   │       ├── employees.py
│   │       ├── contracts.py
│   │       ├── payroll.py
│   │       ├── chat.py
│   │       ├── retirement.py
│   │       ├── work_rules.py
│   │       ├── attorneys.py
│   │       └── subscriptions.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── company_service.py
│   │   ├── employee_service.py
│   │   ├── contract_service.py
│   │   ├── document_service.py    # Word/PDF 생성
│   │   ├── payroll_service.py
│   │   ├── payslip_service.py
│   │   ├── notification_service.py
│   │   ├── chat_service.py
│   │   ├── rag_service.py
│   │   ├── retirement_service.py
│   │   ├── attorney_service.py
│   │   └── subscription_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                # CRUD 베이스
│   │   ├── user_repo.py
│   │   ├── company_repo.py
│   │   ├── employee_repo.py
│   │   └── ...
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py              # 공통 스키마
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── employee.py
│   │   ├── contract.py
│   │   ├── payroll.py
│   │   ├── chat.py
│   │   └── ...
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── claude_client.py       # Anthropic SDK 래퍼
│   │   ├── prompts/
│   │   │   ├── __init__.py
│   │   │   ├── qa_prompt.py
│   │   │   ├── contract_prompt.py
│   │   │   ├── payslip_prompt.py
│   │   │   ├── retirement_prompt.py
│   │   │   └── attorney_case_prompt.py
│   │   └── embedding.py           # OpenAI Embedding 클라이언트
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── crypto.py              # AES-256 암호화
│   │   ├── wage_calculator.py
│   │   ├── tax_calculator.py
│   │   └── validators.py
│   └── data/
│       └── labor_laws/            # 법령 텍스트 데이터
│           ├── labor_standards_act.txt
│           ├── minimum_wage_act.txt
│           └── ...
├── alembic/
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│       └── 001_initial_schema.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── pyproject.toml
├── requirements.txt
└── Dockerfile
```

### 2.2 레이어 구성

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                   │
│  - 라우팅, 요청 검증 (Pydantic), 응답 직렬화            │
│  - 인증/인가 미들웨어                                   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Service Layer                          │
│  - 비즈니스 로직                                         │
│  - 트랜잭션 관리                                         │
│  - 외부 서비스 연동 (Claude, Toss, Kakao)               │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                 Repository Layer                         │
│  - 데이터 접근 추상화                                    │
│  - CRUD 오퍼레이션                                       │
│  - 쿼리 빌더                                             │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Model Layer (ORM)                      │
│  - SQLAlchemy 2.0 Models                                 │
│  - 데이터베이스 테이블 매핑                              │
└─────────────────────────────────────────────────────────┘
```

### 2.3 DB 스키마 설계

PRD Section 4 기반, 핵심 엔티티 관계도:

```mermaid
erDiagram
    users ||--o{ companies : owns
    users ||--o{ subscriptions : has
    users ||--o{ chat_sessions : creates
    users ||--o| labor_attorneys : is

    companies ||--o{ employees : employs
    companies ||--o| work_rules : has
    companies ||--o{ attorney_cases : involved

    employees ||--o{ contracts : signs
    employees ||--o{ salary_settings : has
    employees ||--o{ work_records : works
    employees ||--o{ payslips : receives

    chat_sessions ||--o{ chat_messages : contains
    labor_attorneys ||--o{ attorney_cases : handles

    users {
        uuid id PK
        string email UK
        string hashed_password
        string name
        string phone
        string kakao_id UK
        string role
        string plan
        timestamp plan_expires_at
        boolean is_active
    }

    companies {
        uuid id PK
        uuid owner_id FK
        string business_name
        string business_number UK
        string representative_name
        string industry_type
        int employee_count
        boolean work_rule_required
    }

    employees {
        uuid id PK
        uuid company_id FK
        uuid user_id FK
        string name
        string id_number_encrypted
        string nationality
        string employment_type
        date hire_date
        date resign_date
        boolean is_active
    }

    contracts {
        uuid id PK
        uuid employee_id FK
        uuid company_id FK
        string contract_type
        date start_date
        date end_date
        string work_location
        decimal base_wage
        string status
        text docx_url
        text pdf_url
    }

    payslips {
        uuid id PK
        uuid employee_id FK
        uuid company_id FK
        int pay_year
        int pay_month
        decimal gross_pay
        decimal total_deduction
        decimal net_pay
        jsonb calculation_detail
        string send_status
    }

    chat_sessions {
        uuid id PK
        uuid user_id FK
        uuid company_id FK
        string title
        string risk_level
        boolean attorney_referred
    }

    subscriptions {
        uuid id PK
        uuid user_id FK
        string plan
        string status
        timestamp expires_at
        string toss_billing_key
    }
```

### 2.4 Redis 활용 방안

| 용도 | Key 패턴 | TTL | 설명 |
|------|----------|-----|------|
| 세션/Refresh Token | `refresh:{user_id}` | 30일 | 리프레시 토큰 저장 |
| 블랙리스트 | `blacklist:{token_jti}` | 1시간 | 로그아웃 토큰 무효화 |
| Rate Limiting | `ratelimit:{ip}:{endpoint}` | 1분 | 요청 횟수 제한 |
| 캐싱 (법령 요율) | `cache:labor_rates:{year}` | 24시간 | 노동법 요율 캐시 |
| 캐싱 (RAG 결과) | `cache:rag:{query_hash}` | 1시간 | 유사 질문 답변 캐시 |
| 대기열 (AI) | `queue:chat:{session_id}` | 10분 | Claude API 대기열 |

---

## 3. 프론트엔드 아키텍처

### 3.1 디렉토리 구조

```
frontend/
├── app/
│   ├── layout.tsx                 # 루트 레이아웃
│   ├── page.tsx                   # 랜딩 페이지
│   ├── globals.css
│   ├── (auth)/
│   │   ├── layout.tsx
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   └── callback/
│   │       └── kakao/
│   │           └── page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx             # 사이드바 포함 레이아웃
│   │   ├── page.tsx               # 컴플라이언스 대시보드
│   │   ├── company/
│   │   │   ├── page.tsx           # 사업장 정보
│   │   │   └── new/
│   │   │       └── page.tsx
│   │   ├── employees/
│   │   │   ├── page.tsx           # 직원 목록
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx       # 직원 상세
│   │   │   └── new/
│   │   │       └── page.tsx
│   │   ├── contracts/
│   │   │   ├── page.tsx           # 계약서 목록
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx       # 계약서 상세
│   │   │   └── new/
│   │   │       └── page.tsx       # 계약서 생성
│   │   ├── payroll/
│   │   │   ├── page.tsx           # 급여 계산
│   │   │   └── payslips/
│   │   │       └── page.tsx       # 급여명세서 목록
│   │   ├── chat/
│   │   │   ├── page.tsx           # AI 상담 (새 세션)
│   │   │   └── [sessionId]/
│   │   │       └── page.tsx       # 상담 세션
│   │   ├── retirement/
│   │   │   └── page.tsx           # 퇴직금 계산
│   │   ├── work-rules/
│   │   │   └── page.tsx           # 취업규칙 관리
│   │   ├── attorneys/
│   │   │   ├── page.tsx           # 노무사 목록
│   │   │   └── [id]/
│   │   │       └── page.tsx       # 노무사 상세
│   │   ├── settings/
│   │   │   └── page.tsx           # 계정 설정
│   │   └── subscription/
│   │       └── page.tsx           # 구독 관리
│   └── api/
│       ├── auth/
│       │   └── route.ts           # NextAuth.js 설정
│       └── webhooks/
│           ├── toss/
│           │   └── route.ts
│           └── modusign/
│               └── route.ts
├── components/
│   ├── ui/                        # shadcn/ui 컴포넌트
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── form.tsx
│   │   ├── input.tsx
│   │   ├── select.tsx
│   │   ├── table.tsx
│   │   └── ...
│   ├── layout/
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   ├── mobile-nav.tsx
│   │   └── footer.tsx
│   ├── auth/
│   │   ├── login-form.tsx
│   │   ├── register-form.tsx
│   │   └── social-login-button.tsx
│   ├── dashboard/
│   │   ├── compliance-score-card.tsx
│   │   ├── risk-indicator.tsx
│   │   ├── event-calendar.tsx
│   │   └── issue-list.tsx
│   ├── employees/
│   │   ├── employee-list.tsx
│   │   ├── employee-form.tsx
│   │   └── employment-type-badge.tsx
│   ├── contracts/
│   │   ├── contract-form.tsx
│   │   ├── contract-preview.tsx
│   │   ├── minimum-wage-warning.tsx
│   │   └── contract-download-button.tsx
│   ├── payroll/
│   │   ├── payroll-calculator.tsx
│   │   ├── payslip-preview.tsx
│   │   ├── work-record-upload.tsx
│   │   └── deduction-breakdown.tsx
│   ├── chat/
│   │   ├── chat-window.tsx
│   │   ├── message-bubble.tsx
│   │   ├── message-input.tsx
│   │   ├── law-reference-card.tsx
│   │   ├── risk-badge.tsx
│   │   └── attorney-cta.tsx
│   └── subscription/
│       ├── plan-card.tsx
│       ├── payment-form.tsx
│       └── billing-history.tsx
├── lib/
│   ├── api/
│   │   ├── client.ts              # Axios 인스턴스
│   │   ├── auth.ts
│   │   ├── companies.ts
│   │   ├── employees.ts
│   │   ├── contracts.ts
│   │   ├── payroll.ts
│   │   ├── chat.ts
│   │   └── subscriptions.ts
│   ├── hooks/
│   │   ├── use-auth.ts
│   │   ├── use-company.ts
│   │   ├── use-employees.ts
│   │   ├── use-chat.ts
│   │   └── use-subscription.ts
│   ├── stores/
│   │   ├── auth-store.ts          # Zustand
│   │   └── ui-store.ts
│   ├── utils/
│   │   ├── format.ts              # 숫자, 날짜 포맷
│   │   ├── validation.ts
│   │   └── encryption.ts          # 민감정보 암호화
│   └── constants/
│       ├── plans.ts
│       ├── employment-types.ts
│       └── error-codes.ts
├── types/
│   ├── api.ts
│   ├── user.ts
│   ├── company.ts
│   ├── employee.ts
│   ├── contract.ts
│   ├── payroll.ts
│   └── chat.ts
├── public/
│   ├── icons/
│   └── images/
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── Dockerfile
```

### 3.2 상태 관리 전략

| 상태 유형 | 도구 | 사용처 |
|-----------|------|--------|
| 서버 상태 | TanStack Query (React Query) | API 데이터, 캐싱, 동기화 |
| 글로벌 클라이언트 상태 | Zustand | 인증, UI 상태, 테마 |
| 폼 상태 | React Hook Form + Zod | 입력 폼 검증 |
| 로컬 상태 | React useState | 컴포넌트 내부 상태 |

**상태 관리 구조:**

```typescript
// lib/stores/auth-store.ts (Zustand)
interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
}

// lib/hooks/use-employees.ts (TanStack Query)
export function useEmployees(companyId: string) {
  return useQuery({
    queryKey: ['employees', companyId],
    queryFn: () => employeeApi.list(companyId),
    staleTime: 5 * 60 * 1000, // 5분
  });
}
```

### 3.3 API 클라이언트 구조

```typescript
// lib/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터: 토큰 자동 주입
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 응답 인터셉터: 토큰 갱신, 에러 처리
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // 토큰 갱신 시도
      const refreshed = await refreshAccessToken();
      if (!refreshed) {
        useAuthStore.getState().logout();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 3.4 주요 페이지 구성

| 페이지 | 경로 | 주요 기능 |
|--------|------|-----------|
| 랜딩 | `/` | 서비스 소개, CTA |
| 로그인 | `/login` | 이메일/카카오 로그인 |
| 회원가입 | `/register` | 이메일 가입 |
| 대시보드 | `/dashboard` | 컴플라이언스 점수, 이슈, 캘린더 |
| 사업장 관리 | `/company` | 사업장 정보 CRUD |
| 직원 관리 | `/employees` | 직원 목록, 등록, 상세 |
| 근로계약서 | `/contracts` | 계약서 생성, 미리보기, 다운로드 |
| 급여 계산 | `/payroll` | 급여 계산, 명세서 생성 |
| AI 상담 | `/chat` | 노동법 Q&A 채팅 |
| 퇴직금 계산 | `/retirement` | 퇴직금/해고 절차 안내 |
| 취업규칙 | `/work-rules` | 취업규칙 작성, 관리 |
| 노무사 찾기 | `/attorneys` | 노무사 목록, 상담 예약 |
| 구독 관리 | `/subscription` | 플랜 선택, 결제 |

---

## 4. AI 파이프라인

### 4.1 Claude API 연동 구조

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Redis
    participant Claude
    participant pgvector

    User->>Frontend: 질문 입력
    Frontend->>Backend: POST /chat/sessions/{id}/messages

    Backend->>Redis: Rate Limit 체크
    Redis-->>Backend: OK

    Backend->>pgvector: 의도 분류 & 벡터 검색
    pgvector-->>Backend: 관련 법령 Top 3

    Backend->>Backend: 프롬프트 빌드 (컨텍스트 + RAG)

    loop SSE 스트리밍
        Backend->>Claude: Messages API (stream)
        Claude-->>Backend: chunk
        Backend-->>Frontend: SSE event
        Frontend-->>User: 타이핑 효과
    end

    Backend->>Backend: 면책 문구 추가
    Backend->>Backend: 위험도 분류
    Backend-->>Frontend: done event

    Backend->>pgvector: 대화 저장
```

### 4.2 RAG 구현 (pgvector)

**벡터 저장소 구조:**

```sql
-- 법령 벡터 테이블
CREATE TABLE law_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    law_name VARCHAR(100) NOT NULL,          -- 법령명
    article VARCHAR(50) NOT NULL,            -- 조항 (제55조)
    content TEXT NOT NULL,                   -- 조항 내용
    embedding vector(1536),                  -- OpenAI embedding
    keywords TEXT[],                         -- 키워드 배열
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_law_vectors_embedding ON law_vectors
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
```

**RAG 검색 파이프라인:**

```python
# services/rag_service.py
class RAGService:
    async def search_relevant_laws(
        self,
        query: str,
        top_k: int = 3
    ) -> list[LawReference]:
        # 1. 의도 분류 (임금/계약/해고/휴가/산재/차별/과태료)
        intent = self._classify_intent(query)

        # 2. 쿼리 임베딩
        query_embedding = await self.embedding_client.embed(query)

        # 3. 코사인 유사도 검색
        results = await self.db.execute(
            text("""
                SELECT law_name, article, content,
                       1 - (embedding <=> :embedding) as similarity
                FROM law_vectors
                WHERE :intent = ANY(keywords)
                ORDER BY embedding <=> :embedding
                LIMIT :top_k
            """),
            {"embedding": query_embedding, "intent": intent, "top_k": top_k}
        )

        return [LawReference(**row) for row in results]
```

### 4.3 프롬프트 관리 전략

```
backend/app/ai/prompts/
├── __init__.py
├── base.py               # 공통 템플릿
├── qa_prompt.py          # 노동법 Q&A
├── contract_prompt.py    # 근로계약서 생성
├── payslip_prompt.py     # 급여명세서 생성
├── retirement_prompt.py  # 퇴직금/해고 안내
└── attorney_case_prompt.py  # 노무사 케이스 요약
```

**프롬프트 버전 관리:**
- 각 프롬프트는 버전 번호 관리
- DB에 프롬프트 실행 로그 저장 (입력, 출력, 토큰 사용량)
- A/B 테스트를 통한 프롬프트 최적화

**토큰 최적화:**
```python
MAX_HISTORY_TURNS = 10
MAX_TOKENS_PER_TURN = 500
MAX_RAG_RESULTS = 3
MAX_RAG_CHARS_PER_RESULT = 800

def trim_context(history: list, rag_results: list) -> str:
    # 대화 히스토리 10턴, 각 500토큰 이하로 트림
    # RAG 결과 3개, 각 800자 이하로 트림
    pass
```

---

## 5. 외부 서비스 연동

### 5.1 토스페이먼츠

| 기능 | API | 설명 |
|------|-----|------|
| 결제 승인 | `POST /v1/payments/confirm` | 1회성 결제 |
| 빌링키 발급 | `POST /v1/billing/authorizations/issue` | 정기 결제용 |
| 자동 결제 | `POST /v1/billing/{billingKey}/pay` | 월 구독 결제 |
| 결제 취소 | `POST /v1/payments/{paymentKey}/cancel` | 환불 |

**구독 결제 흐름:**

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Toss

    User->>Frontend: 플랜 선택
    Frontend->>Toss: 결제 위젯 호출
    Toss-->>Frontend: billingKey 발급
    Frontend->>Backend: POST /subscriptions
    Backend->>Toss: 최초 결제 승인
    Toss-->>Backend: 결제 성공
    Backend->>Backend: 구독 생성 (DB)
    Backend-->>Frontend: 구독 완료

    Note over Backend,Toss: 매월 자동 결제
    Backend->>Toss: POST /billing/{key}/pay
    Toss-->>Backend: 결제 성공
    Backend->>Backend: 구독 연장
```

### 5.2 카카오 알림톡

| 기능 | Template | 사용처 |
|------|----------|--------|
| 급여명세서 발송 | `payslip_monthly` | 월 급여명세서 |
| 계약 만료 알림 | `contract_expiry` | D-30, D-7 알림 |
| 결제 알림 | `payment_success` | 구독 결제 완료 |

**Fallback 정책:**
```
카카오 알림톡 실패 → 이메일(SendGrid) 자동 발송 (3회 재시도)
이메일도 실패 → DB에 'failed' 기록, 관리자 Slack 알림
```

### 5.3 모두싸인 (전자서명)

| 기능 | API | 설명 |
|------|-----|------|
| 서명 요청 생성 | `POST /api/v1/documents` | 계약서 업로드 |
| 서명자 추가 | `POST /api/v1/documents/{id}/signers` | 사장님 + 직원 |
| 서명 상태 조회 | `GET /api/v1/documents/{id}` | 진행 상황 |
| 웹훅 수신 | `POST /webhooks/modusign` | 서명 완료 알림 |

**Phase 2 구현 (M6 마일스톤)**

---

## 6. 보안 설계

### 6.1 인증/인가 구조

**인증 흐름:**

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Redis

    User->>Frontend: 로그인
    Frontend->>Backend: POST /auth/login
    Backend->>Backend: 비밀번호 검증 (bcrypt)
    Backend->>Backend: JWT 생성 (access + refresh)
    Backend->>Redis: refresh token 저장 (30일 TTL)
    Backend-->>Frontend: tokens + user info
    Frontend->>Frontend: accessToken 저장 (Zustand)

    Note over User,Redis: API 요청
    Frontend->>Backend: API 요청 (Authorization: Bearer)
    Backend->>Backend: JWT 검증
    Backend->>Redis: 블랙리스트 확인
    Backend-->>Frontend: 응답

    Note over User,Redis: 토큰 갱신
    Frontend->>Backend: POST /auth/refresh
    Backend->>Redis: refresh token 검증
    Backend->>Redis: 기존 refresh 삭제 (Rotation)
    Backend->>Backend: 새 JWT 생성
    Backend-->>Frontend: 새 tokens
```

**JWT Payload:**
```json
{
  "sub": "user_uuid",
  "company_id": "company_uuid",
  "plan": "standard",
  "role": "owner",
  "exp": 1700000000,
  "jti": "unique_token_id"
}
```

### 6.2 데이터 암호화

| 데이터 | 암호화 방식 | 저장 위치 |
|--------|-------------|-----------|
| 비밀번호 | bcrypt (rounds=12) | users.hashed_password |
| 주민등록번호 | AES-256-GCM | employees.id_number (EncryptedString) |
| 계좌번호 | AES-256-GCM | employees.bank_account |
| 암호화 키 | AWS KMS | 환경변수 (ENCRYPTION_KEY) |

**SQLAlchemy TypeDecorator:**

```python
# utils/crypto.py
class EncryptedString(TypeDecorator):
    impl = String(256)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return encrypt_aes_gcm(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return decrypt_aes_gcm(value)
```

### 6.3 Rate Limiting

| 엔드포인트 | 제한 | 기준 |
|------------|------|------|
| `/auth/login` | 5회/분 | IP |
| `/auth/register` | 3회/시간 | IP |
| `/chat/sessions/{id}/messages` | 30회/시간 | User ID |
| `/contracts/generate` | 10회/시간 | User ID (플랜별 차등) |
| 일반 API | 100회/분 | User ID |

**구현 (Redis + FastAPI Middleware):**

```python
# core/rate_limit.py
async def rate_limit_check(key: str, limit: int, window: int) -> bool:
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, window)
    return current <= limit
```

### 6.4 기타 보안 조치

| 항목 | 조치 |
|------|------|
| HTTPS | 모든 통신 TLS 1.3 |
| CORS | 프론트엔드 도메인만 허용 |
| SQL Injection | SQLAlchemy ORM 사용 (Raw Query 지양) |
| XSS | React 기본 escape, DOMPurify 추가 |
| CSRF | SameSite 쿠키, CSRF 토큰 |
| 로깅 | 민감정보 마스킹 (주민번호, 계좌번호) |

---

## 7. 인프라 구성

### 7.1 Docker 구성

```yaml
# docker-compose.yml (개발환경)
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: nomoodoc
      POSTGRES_USER: nomoodoc
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    command: >
      postgres
      -c shared_preload_libraries='vector'

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://nomoodoc:${DB_PASSWORD}@postgres:5432/nomoodoc
      REDIS_URL: redis://redis:6379/0
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api/v1
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app

volumes:
  postgres_data:
  redis_data:
```

### 7.2 배포 아키텍처 (AWS)

```mermaid
graph TB
    subgraph "AWS Cloud"
        CF[CloudFront CDN]

        subgraph "VPC"
            ALB[Application Load Balancer]

            subgraph "ECS Cluster"
                FE1[Next.js Task 1]
                FE2[Next.js Task 2]
                BE1[FastAPI Task 1]
                BE2[FastAPI Task 2]
            end

            subgraph "Managed Services"
                RDS[(RDS PostgreSQL<br/>+ pgvector)]
                EC[(ElastiCache Redis)]
            end
        end

        S3[(S3 Bucket<br/>계약서/명세서)]
        KMS[AWS KMS<br/>암호화 키]
        CW[CloudWatch<br/>Logs & Metrics]
        SE[Sentry<br/>Error Tracking]
    end

    USER[Users] --> CF
    CF --> ALB
    ALB --> FE1
    ALB --> FE2
    ALB --> BE1
    ALB --> BE2
    BE1 --> RDS
    BE1 --> EC
    BE1 --> S3
    BE1 --> KMS
    BE1 --> CW
    BE1 --> SE
```

### 7.3 CI/CD 파이프라인

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Backend Tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest --cov=app
      - name: Run Frontend Tests
        run: |
          cd frontend
          npm ci
          npm run test
          npm run lint

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build & Push Docker Images
        run: |
          docker build -t nomoodoc-backend ./backend
          docker build -t nomoodoc-frontend ./frontend
          # ECR push...

      - name: Deploy to ECS
        run: |
          # ECS service update...
```

---

## 8. 개발 규칙

### 8.1 코딩 컨벤션

**Backend (Python):**
- 포맷터: Black (line-length=88)
- Import 정리: isort
- Linter: Ruff
- 타입 힌트: 필수 (mypy 검증)

```python
# 예시
async def create_contract(
    self,
    employee_id: UUID,
    contract_data: ContractCreate,
    current_user: User = Depends(get_current_user),
) -> ContractResponse:
    ...
```

**Frontend (TypeScript):**
- 포맷터: Prettier
- Linter: ESLint (Next.js 권장 설정)
- 타입: 엄격 모드 (strict: true)

```typescript
// 예시
interface ContractCreate {
  employeeId: string;
  contractType: ContractType;
  startDate: string;
  baseWage: number;
}
```

### 8.2 Git 브랜치 전략

```
main
  │
  ├── develop
  │     │
  │     ├── feature/F-01-auth
  │     │     └── commit...
  │     │
  │     ├── feature/F-04-contract
  │     │     └── commit...
  │     │
  │     └── bugfix/issue-123
  │
  └── hotfix/critical-bug
```

| 브랜치 | 용도 | 머지 대상 |
|--------|------|-----------|
| `main` | 운영 배포 | - |
| `develop` | 개발 통합 | main |
| `feature/{기능명}` | 기능 개발 | develop |
| `bugfix/{이슈명}` | 버그 수정 | develop |
| `hotfix/{이슈명}` | 긴급 수정 | main, develop |

**커밋 컨벤션:**
```
feat(F-04): 근로계약서 생성 API 구현
fix(F-05): 급여 계산 소수점 처리 수정
docs: API 문서 업데이트
test: 급여 계산 테스트 케이스 추가
```

### 8.3 테스트 전략

| 테스트 유형 | 도구 | 커버리지 목표 |
|-------------|------|---------------|
| 단위 테스트 | pytest (BE), Vitest (FE) | 80% |
| 통합 테스트 | pytest + TestClient | 주요 API 100% |
| E2E 테스트 | Playwright | Happy Path 100% |
| 부하 테스트 | Locust | 월간 트래픽 2배 |

**테스트 구조:**

```
backend/tests/
├── conftest.py                 # Fixtures
├── unit/
│   ├── test_wage_calculator.py
│   ├── test_tax_calculator.py
│   └── test_crypto.py
├── integration/
│   ├── test_auth_api.py
│   ├── test_contract_api.py
│   └── test_payroll_api.py
└── e2e/
    └── test_subscription_flow.py

frontend/tests/
├── unit/
│   └── utils/format.test.ts
├── integration/
│   └── components/ContractForm.test.tsx
└── e2e/
    └── contract-creation.spec.ts
```

### 8.4 문서화 규칙

- API 문서: Swagger (FastAPI 자동 생성)
- ERD: docs/system/erd.md (별도 작성)
- 컴포넌트 문서: Storybook (선택)
- 변경 로그: CHANGELOG.md

---

## 9. 참조 문서

- PRD: docs/project/prd_nomoodoc_v2.md
- 기능 명세: docs/project/features.md
- 로드맵: docs/project/roadmap.md
- doc-rules: .claude/skills/doc-rules
