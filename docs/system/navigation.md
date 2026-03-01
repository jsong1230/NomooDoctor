# 노무닥터 — 네비게이션 구조

## 1. 전체 화면 목록

### 1.1 공개 화면 (인증 불필요)

| 화면명 | 경로 | 설명 | 관련 기능 |
|--------|------|------|----------|
| 랜딩 페이지 | `/` | 서비스 소개, CTA | - |
| 로그인 | `/login` | 이메일/카카오 로그인 | F-01 |
| 회원가입 | `/register` | 이메일 회원가입 | F-01 |
| 비밀번호 찾기 | `/forgot-password` | 비밀번호 재설정 요청 | F-01 |
| 카카오 콜백 | `/callback/kakao` | OAuth 리다이렉트 | F-01 |

### 1.2 대시보드 화면 (인증 필요)

| 화면명 | 경로 | 설명 | 관련 기능 |
|--------|------|------|----------|
| 컴플라이언스 대시보드 | `/dashboard` | 리스크 스코어, 이벤트 캘린더 | F-10 |
| 사업장 정보 | `/company` | 사업장 정보 조회/수정 | F-02 |
| 사업장 등록 | `/company/new` | 새 사업장 등록 | F-02 |

### 1.3 직원 관리 화면

| 화면명 | 경로 | 설명 | 관련 기능 |
|--------|------|------|----------|
| 직원 목록 | `/employees` | 직원 목록 (페이지네이션, 필터) | F-03 |
| 직원 상세 | `/employees/[id]` | 직원 상세 정보, 서류 연결 | F-03 |
| 직원 등록 | `/employees/new` | 새 직원 등록 | F-03 |

### 1.4 근로계약서 화면

| 화면명 | 경로 | 설명 | 관련 기능 |
|--------|------|------|----------|
| 계약서 목록 | `/contracts` | 전체 계약서 목록 | F-04 |
| 계약서 상세 | `/contracts/[id]` | 계약서 상세, 다운로드 | F-04 |
| 계약서 생성 | `/contracts/new` | 새 계약서 생성 | F-04 |

### 1.5 급여 관리 화면

| 화면명 | 경로 | 설명 | 관련 기능 |
|--------|------|------|----------|
| 급여 계산 | `/payroll` | 급여 자동 계산기 | F-05 |
| 급여명세서 목록 | `/payroll/payslips` | 급여명세서 발송 내역 | F-07 |
| 근태 관리 | `/payroll/attendance` | 근무 기록 입력/업로드 | F-13 |

### 1.6 AI 상담 화면

| 화면명 | 경로 | 설명 | 관련 기능 |
|--------|------|------|----------|
| AI 상담 | `/chat` | 새 상담 세션 | F-06 |
| 상담 세션 | `/chat/[sessionId]` | 기존 상담 세션 | F-06 |

### 1.7 노무사 마켓플레이스 화면

| 화면명 | 경로 | 설명 | 관련 기능 |
|--------|------|------|----------|
| 노무사 목록 | `/attorneys` | 노무사 검색, 필터 | F-12 |
| 노무사 상세 | `/attorneys/[id]` | 노무사 프로필, 상담 예약 | F-12 |

### 1.8 기타 화면

| 화면명 | 경로 | 설명 | 관련 기능 |
|--------|------|------|----------|
| 퇴직금 계산 | `/retirement` | 퇴직금/해고 절차 안내 | F-09 |
| 취업규칙 관리 | `/work-rules` | 취업규칙 작성, 관리 | F-08 |
| 계정 설정 | `/settings` | 계정 정보 수정 | F-01 |
| 구독 관리 | `/subscription` | 플랜 선택, 결제 | F-11 |

---

## 2. Next.js App Router 라우트 구조

```
app/
├── layout.tsx                          # 루트 레이아웃
├── page.tsx                            # 랜딩 페이지 (/)
├── globals.css
├── (auth)/                             # 인증 라우트 그룹
│   ├── layout.tsx                      # 인증 레이아웃 (사이드바 없음)
│   ├── login/
│   │   └── page.tsx                    # /login
│   ├── register/
│   │   └── page.tsx                    # /register
│   ├── forgot-password/
│   │   └── page.tsx                    # /forgot-password
│   └── callback/
│       └── kakao/
│           └── page.tsx                # /callback/kakao
└── (dashboard)/                        # 대시보드 라우트 그룹
    ├── layout.tsx                      # 대시보드 레이아웃 (사이드바 포함)
    ├── page.tsx                        # /dashboard
    ├── company/
    │   ├── page.tsx                    # /company
    │   └── new/
    │       └── page.tsx                # /company/new
    ├── employees/
    │   ├── page.tsx                    # /employees
    │   ├── new/
    │   │   └── page.tsx                # /employees/new
    │   └── [id]/
    │       └── page.tsx                # /employees/[id]
    ├── contracts/
    │   ├── page.tsx                    # /contracts
    │   ├── new/
    │   │   └── page.tsx                # /contracts/new
    │   └── [id]/
    │       └── page.tsx                # /contracts/[id]
    ├── payroll/
    │   ├── page.tsx                    # /payroll
    │   ├── payslips/
    │   │   └── page.tsx                # /payroll/payslips
    │   └── attendance/
    │       └── page.tsx                # /payroll/attendance
    ├── chat/
    │   ├── page.tsx                    # /chat
    │   └── [sessionId]/
    │       └── page.tsx                # /chat/[sessionId]
    ├── attorneys/
    │   ├── page.tsx                    # /attorneys
    │   └── [id]/
    │       └── page.tsx                # /attorneys/[id]
    ├── retirement/
    │   └── page.tsx                    # /retirement
    ├── work-rules/
    │   └── page.tsx                    # /work-rules
    ├── settings/
    │   └── page.tsx                    # /settings
    └── subscription/
        └── page.tsx                    # /subscription
```

---

## 3. 네비게이션 흐름도

### 3.1 전체 화면 흐름

```mermaid
flowchart TD
    Start([시작]) --> Landing[랜딩 페이지 /]
    Landing --> Login[로그인 /login]
    Landing --> Register[회원가입 /register]

    Login -->|성공| Dashboard[대시보드 /dashboard]
    Register -->|완료| CompanyNew[사업장 등록 /company/new]

    CompanyNew -->|등록 완료| Dashboard

    Dashboard -->|사업장 관리| Company[사업장 정보 /company]
    Dashboard -->|직원 관리| Employees[직원 목록 /employees]
    Dashboard -->|계약서 관리| Contracts[계약서 목록 /contracts]
    Dashboard -->|급여 관리| Payroll[급여 계산 /payroll]
    Dashboard -->|AI 상담| Chat[AI 상담 /chat]
    Dashboard -->|노무사 찾기| Attorneys[노무사 목록 /attorneys]
    Dashboard -->|설정| Settings[계정 설정 /settings]

    Employees -->|직원 상세| EmployeeDetail[직원 상세 /employees/[id]]
    Employees -->|직원 등록| EmployeeNew[직원 등록 /employees/new]
    EmployeeDetail -->|계약서 생성| ContractNew[계약서 생성 /contracts/new]

    Contracts -->|계약서 상세| ContractDetail[계약서 상세 /contracts/[id]]
    Contracts -->|계약서 생성| ContractNew

    Payroll -->|급여명세서| Payslips[급여명세서 목록 /payroll/payslips]
    Payroll -->|근태 관리| Attendance[근태 관리 /payroll/attendance]

    Chat -->|기존 세션| ChatSession[상담 세션 /chat/[sessionId]]

    Attorneys -->|노무사 상세| AttorneyDetail[노무사 상세 /attorneys/[id]]

    Settings -->|구독 관리| Subscription[구독 관리 /subscription]

    Dashboard -->|퇴직금 계산| Retirement[퇴직금 계산 /retirement]
    Dashboard -->|취업규칙| WorkRules[취업규칙 /work-rules]

    classDef public fill:#e0f2fe,stroke:#0284c7
    classDef protected fill:#fef3c7,stroke:#d97706
    classDef auth fill:#dcfce7,stroke:#16a34a

    class Landing,Login,Register public
    class Dashboard,Company,Employees,Contracts,Payroll,Chat,Attorneys,Settings,Retirement,WorkRules,Subscription protected
    class CompanyNew,EmployeeNew,ContractNew auth
```

### 3.2 인증 가드

```mermaid
flowchart TD
    Request[페이지 요청] --> CheckAuth{인증 상태?}
    CheckAuth -->|미인증| LoginCheck{로그인 페이지?}
    CheckAuth -->|인증됨| DashboardCheck{대시보드 페이지?}

    LoginCheck -->|예| Continue1[허용]
    LoginCheck -->|아니오| RedirectToLogin[/login로 리다이렉트]

    DashboardCheck -->|아니오| Continue2[허용]
    DashboardCheck -->|예| CompanyCheck{사업장 등록?}

    CompanyCheck -->|예| Continue3[허용]
    CompanyCheck -->|아니오| RedirectToCompany[/company/new로 리다이렉트]

    RedirectToLogin --> Request
    RedirectToCompany --> Request

    classDef success fill:#dcfce7,stroke:#16a34a
    classDef warning fill:#fef3c7,stroke:#d97706
    classDef error fill:#fee2e2,stroke:#dc2626

    class Continue1,Continue2,Continue3 success
    class CompanyCheck warning
    class RedirectToLogin,RedirectToCompany error
```

---

## 4. 사이드바/메뉴 구조

### 4.1 데스크톱 사이드바

```
┌─────────────────────────────┐
│  [로고] 노무닥터            │
├─────────────────────────────┤
│  [대시보드 아이콘] 대시보드 │
│                             │
│  직원 관리                  │
│    [사용자 아이콘] 직원 목록│
│    [플러스 아이콘] 직원 등록│
│                             │
│  근로계약서                 │
│    [문서 아이콘] 계약서 목록│
│    [플러스 아이콘] 계약 생성│
│                             │
│  급여 관리                  │
│    [계산기 아이콘] 급여 계산│
│    [명세서 아이콘] 급여명세서│
│    [시계 아이콘] 근태 관리  │
│                             │
│  [챗 아이콘] AI 상담        │
│  [변호사 아이콘] 노무사 찾기│
│                             │
│  ─────────────────────────  │
│  [설정 아이콘] 설정          │
│  [카드 아이콘] 구독 관리    │
│                             │
│  [사용자 프로필]             │
│    홍길동                    │
│    사업장: 스타트업 주식회사│
│    플랜: 베이직              │
└─────────────────────────────┘
```

### 4.2 모바일 하단 네비게이션

```
┌─────────────────────────────────┐
│  [헤더] 노무닥터   [메뉴 버튼]  │
├─────────────────────────────────┤
│                                 │
│          페이지 콘텐츠           │
│                                 │
│                                 │
├─────────────────────────────────┤
│ [홈]  [직원]  [AI]  [더보기]   │
└─────────────────────────────────┘
```

**하단 탭:**
- 홈: `/dashboard`
- 직원: `/employees`
- AI: `/chat`
- 더보기: 모달 메뉴 (나머지 항목)

### 4.3 메뉴 항목 정의

| 메뉴 항목 | 경로 | 아이콘 | 설명 |
|-----------|------|--------|------|
| 대시보드 | `/dashboard` | layout-4 | 컴플라이언스 요약 |
| 직원 목록 | `/employees` | users | 직원 리스트 |
| 직원 등록 | `/employees/new` | user-plus | 새 직원 추가 |
| 계약서 목록 | `/contracts` | file-text | 계약서 리스트 |
| 계약서 생성 | `/contracts/new` | plus-square | 새 계약서 |
| 급여 계산 | `/payroll` | calculator | 급여 계산기 |
| 급여명세서 | `/payroll/payslips` | receipt | 명세서 내역 |
| 근태 관리 | `/payroll/attendance` | clock-in-out | 근무 기록 |
| AI 상담 | `/chat` | message-circle | 노동법 Q&A |
| 노무사 찾기 | `/attorneys` | briefcase | 전문 상담 |
| 퇴직금 계산 | `/retirement` | piggy-bank | 퇴직금/해고 |
| 취업규칙 | `/work-rules` | book-open | 취업규칙 관리 |
| 설정 | `/settings` | settings | 계정 설정 |
| 구독 관리 | `/subscription` | credit-card | 플랜/결제 |

---

## 5. 접근 제어

### 5.1 인증 필요 페이지

`(dashboard)` 라우트 그룹 내 모든 페이지는 인증이 필요합니다:

| 경로 | 인증 필요 | 사업장 등록 필요 |
|------|----------|-----------------|
| `/dashboard` | O | O |
| `/company` | O | O |
| `/company/new` | O | - |
| `/employees/*` | O | O |
| `/contracts/*` | O | O |
| `/payroll/*` | O | O |
| `/chat/*` | O | O |
| `/attorneys/*` | O | O |
| `/retirement` | O | O |
| `/work-rules` | O | O |
| `/settings` | O | - |
| `/subscription` | O | - |

### 5.2 플랜별 접근 제한

| 기능 | 스타터 | 베이직 | 스탠다드 | 프리미엄 |
|------|--------|--------|----------|--------|
| AI 상담 | 10회/월 | 무제한 | 무제한 | 무제한 |
| 계약서 생성 | 2건/월 | 무제한 | 무제한 | 무제한 |
| 급여 계산 | - | O | O | O |
| 급여명세서 발송 | - | - | 100건/월 | 무제한 |
| 노무사 무료 상담 | - | - | - | 1회/월 |

### 5.3 미들웨어 로직

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // 공개 라우트
  const publicRoutes = ['/', '/login', '/register', '/forgot-password', '/callback/kakao']
  if (publicRoutes.some(route => pathname.startsWith(route))) {
    return NextResponse.next()
  }

  // 대시보드 라우트
  if (pathname.startsWith('/dashboard')) {
    // 인증 체크
    const token = request.cookies.get('access_token')
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url))
    }

    // 사업장 등록 체크 (제외 경로)
    const excludeRoutes = ['/company/new', '/settings', '/subscription']
    if (!excludeRoutes.some(route => pathname.startsWith(route))) {
      const hasCompany = request.cookies.get('has_company')
      if (!hasCompany) {
        return NextResponse.redirect(new URL('/company/new', request.url))
      }
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)']
}
```

---

## 6. 반응형 네비게이션

### 6.1 데스크톱 (≥1024px)
- 사이드바 (고정 왼쪽, 260px 너비)
- 메인 콘텐츠 (나머지 공간)

### 6.2 태블릿 (768px ~ 1023px)
- 접이식 사이드바 (햄버거 메뉴)

### 6.3 모바일 (<768px)
- 하단 네비게이션 (고정 하단)
- 상단 헤더 (로고, 메뉴 버튼)
- 사이드메뉴 (오픈 시 슬라이드인)

---

## 7. URL 파라미터 규칙

| 파라미터 | 타입 | 설명 | 예시 |
|----------|------|------|------|
| `id` | UUID | 직원/계약서/노무사 ID | `/employees/a1b2c3d4...` |
| `sessionId` | UUID | AI 상담 세션 ID | `/chat/a1b2c3d4...` |

---

## 8. 브레드크럼

```
홈 > [현재 페이지]

예시:
- 직원 목록: 홈 > 직원 관리
- 직원 상세: 홈 > 직원 관리 > 홍길동
- 계약서 생성: 홈 > 근로계약서 > 계약서 생성
- 급여명세서: 홈 > 급여 관리 > 급여명세서
```

---

## 9. 404 페이지

- `/not-found` 페이지 제공
- 잘못된 경로 접근 시 자동 리다이렉트

---

## 10. 리다이렉트 규칙

| 원인 | 리다이렉트 |
|------|-----------|
| 미인증 사용자 접근 | `/login` |
| 사업장 미등록 대시보드 접근 | `/company/new` |
| 로그인 상태에서 `/login` 접근 | `/dashboard` |
| `/` 접근 (인증됨) | `/dashboard` |
| `/` 접근 (미인증) | `/` (랜딩) |
