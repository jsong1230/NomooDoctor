# 노무닥터 — Design System

## 1. 디자인 철학

### 1.1 브랜드 키워드
- **신뢰 (Trust)** — 노동법 분야의 정확성과 안정성 전달
- **전문 (Professional)** — 노무사급 전문성을 간결한 UI로 표현
- **간편 (Simple)** — 복잡한 노무/HR을 쉽게 처리할 수 있는 직관성

### 1.2 무드 & 톤앤매너
- **레퍼런스 톤**: 은행/증권 앱 (안정성 + 전문성)
- **비주얼 스타일**: 클린, 미니멀, 기능적
- **인터랙션**: 부드러운 트랜지션, 명확한 피드백
- **마이크로카피**: 존댓말, 친절한 안내, 법률 용어 쉽게 풀어서 설명

### 1.3 UX 원칙

#### 접근성 기준
- WCAG 2.1 Level AA 준수
- 색상 대비비 4.5:1 이상 (일반 텍스트)
- 키보드 네비게이션 완전 지원
- 화면 리더기 호환

#### 인터랙션 패턴
- 단일 클릭로 주요 작업 완료
- 입력 필드에서 즉각적 유효성 피드백
- 로딩 상태 시 스켈레톤 UI + 프로그레스 바
- 에러 상태 시 복구 가능한 해결책 제시

#### 피드백 방식
- 성공: 토스트 알림 (녹색)
- 경고: 토스트 알림 (노란색)
- 에러: 토스트 알림 + 인라인 에러 메시지 (빨간색)
- 로딩: 스켈레톤 UI + 스피너

## 2. 색상 팔레트

### 2.1 색상 컨셉
- **Primary**: 전문적이고 신뢰감 있는 깊은 블루
- **Accent**: 생동감 있는 청록색 (CTA, 강조 포인트)
- **Neutral**: 오프화이트 배경 + 그레이 계열 텍스트
- **Semantic**: 기능적 색상 (success, warning, error, info)

### 2.2 색상 토큰

```css
/* Primary - 신뢰감 있는 블루 계열 */
--color-primary-50: #eff6ff;
--color-primary-100: #dbeafe;
--color-primary-200: #bfdbfe;
--color-primary-300: #93c5fd;
--color-primary-400: #60a5fa;
--color-primary-500: #3b82f6;
--color-primary-600: #2563eb;  /* 메인 브랜드 컬러 */
--color-primary-700: #1d4ed8;
--color-primary-800: #1e40af;
--color-primary-900: #1e3a8a;

/* Accent - 청록색 (CTA, 강조) */
--color-accent-50: #f0fdfa;
--color-accent-100: #ccfbf1;
--color-accent-200: #99f6e4;
--color-accent-300: #5eead4;
--color-accent-400: #2dd4bf;
--color-accent-500: #14b8a6;  /* 포인트 컬러 */
--color-accent-600: #0d9488;
--color-accent-700: #0f766e;
--color-accent-800: #115e59;
--color-accent-900: #134e4a;

/* Secondary - 중립적 보라 (보조) */
--color-secondary-50: #faf5ff;
--color-secondary-100: #f3e8ff;
--color-secondary-200: #e9d5ff;
--color-secondary-300: #d8b4fe;
--color-secondary-400: #c084fc;
--color-secondary-500: #a855f7;
--color-secondary-600: #9333ea;
--color-secondary-700: #7e22ce;
--color-secondary-800: #6b21a8;
--color-secondary-900: #581c87;

/* Neutral - 오프화이트 배경 + 그레이 텍스트 */
--color-slate-50: #f8fafc;  /* 배경 */
--color-slate-100: #f1f5f9;
--color-slate-200: #e2e8f0;
--color-slate-300: #cbd5e1;
--color-slate-400: #94a3b8;
--color-slate-500: #64748b;  /* 보조 텍스트 */
--color-slate-600: #475569;  /* 본문 텍스트 */
--color-slate-700: #334155;
--color-slate-800: #1e293b;  /* 제목 텍스트 */
--color-slate-900: #0f172a;

/* Semantic - 기능적 색상 */
--color-success-50: #f0fdf4;
--color-success-100: #dcfce7;
--color-success-500: #22c55e;  /* 성공 */
--color-success-600: #16a34a;
--color-success-700: #15803d;

--color-warning-50: #fffbeb;
--color-warning-100: #fef3c7;
--color-warning-500: #f59e0b;  /* 경고 */
--color-warning-600: #d97706;
--color-warning-700: #b45309;

--color-error-50: #fef2f2;
--color-error-100: #fee2e2;
--color-error-500: #ef4444;  /* 에러 */
--color-error-600: #dc2626;
--color-error-700: #b91c1c;

--color-info-50: #eff6ff;
--color-info-100: #dbeafe;
--color-info-500: #3b82f6;  /* 정보 */
--color-info-600: #2563eb;
--color-info-700: #1d4ed8;

/* Background & Surface */
--color-background: #ffffff;
--color-surface: #f8fafc;     /* 카드 배경 */
--color-surface-alt: #f1f5f9; /* 대체 배경 */
--color-border: #e2e8f0;     /* 테두리 */
--color-border-light: #f1f5f9;

/* Text Colors */
--color-text-primary: #1e293b;   /* 주요 텍스트 */
--color-text-secondary: #64748b; /* 보조 텍스트 */
--color-text-muted: #94a3b8;      /* 희미한 텍스트 */
--color-text-disabled: #cbd5e1;   /* 비활성 텍스트 */
--color-text-on-dark: #ffffff;    /* 어두운 배경 텍스트 */
```

### 2.3 Tailwind CSS 매핑

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        accent: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
        },
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
        },
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
        },
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
        },
      },
    },
  },
}
```

## 3. 타이포그래피

### 3.1 폰트 패밀리

한글 최적화를 위한 Google Fonts 조합:

```css
/* Display 폰트 - 제목용 (고급스러운 느낌) */
--font-display: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Body 폰트 - 본문용 (가독성) */
--font-body: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Monospace 폰트 - 코드/숫자용 */
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

**Google Fonts Import:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Pretendard:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### 3.2 폰트 사이즈 스케일

| 토큰 | 크기 | 용도 | line-height | 예시 |
|------|------|------|-------------|------|
| `text-xs` | 0.75rem (12px) | 캡션, 라벨 | 1.5 | 태그, 소라벨 |
| `text-sm` | 0.875rem (14px) | 작은 텍스트, 보조 | 1.5 | 헬퍼 텍스트 |
| `text-base` | 1rem (16px) | 본문 | 1.6 | 본문 텍스트 |
| `text-lg` | 1.125rem (18px) | 강조 텍스트 | 1.6 | 강조 문장 |
| `text-xl` | 1.25rem (20px) | 소제목 | 1.5 | 섹션 제목 |
| `text-2xl` | 1.5rem (24px) | 중간 제목 | 1.3 | 카드 제목 |
| `text-3xl` | 1.875rem (30px) | 큰 제목 | 1.2 | 페이지 제목 |
| `text-4xl` | 2.25rem (36px) | 히어로 제목 | 1.1 | 랜딩 페이지 |
| `text-5xl` | 3rem (48px) | 대형 히어로 | 1.1 | 브랜드 헤드라인 |

### 3.3 폰트 웨이트

| 토큰 | 웨이트 | 용도 |
|------|--------|------|
| `font-normal` | 400 | 본문, 일반 텍스트 |
| `font-medium` | 500 | 보조 텍스트, 강조 |
| `font-semibold` | 600 | 소제목, 버튼 텍스트 |
| `font-bold` | 700 | 제목, 강한 강조 |

### 3.4 라인 높이 & 레터 스페이싱

```css
/* Line Height */
--leading-tight: 1.1;  /* 제목 */
--leading-snug: 1.2;  /* 큰 제목 */
--leading-normal: 1.5; /* 소제목, 리스트 */
--leading-relaxed: 1.6; /* 본문 */

/* Letter Spacing */
--tracking-tight: -0.025em;  /* 제목 (고급스러움) */
--tracking-normal: 0;       /* 본문 */
--tracking-wide: 0.025em;    /* 라벨 */
```

### 3.5 Tailwind 매핑

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        display: ['Pretendard', 'sans-serif'],
        body: ['Pretendard', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1.5' }],
        sm: ['0.875rem', { lineHeight: '1.5' }],
        base: ['1rem', { lineHeight: '1.6' }],
        lg: ['1.125rem', { lineHeight: '1.6' }],
        xl: ['1.25rem', { lineHeight: '1.5' }],
        '2xl': ['1.5rem', { lineHeight: '1.3' }],
        '3xl': ['1.875rem', { lineHeight: '1.2' }],
        '4xl': ['2.25rem', { lineHeight: '1.1' }],
        '5xl': ['3rem', { lineHeight: '1.1' }],
      },
    },
  },
}
```

## 4. 스페이싱 시스템

### 4.1 4px 기반 그리드

| 토큰 | 값 | 용도 |
|------|-----|------|
| `space-0` | 0px | 기본 여백 제거 |
| `space-1` | 4px | 최소 단위, 아이콘 패딩 |
| `space-2` | 8px | 아이콘, 작은 요소 간격 |
| `space-3` | 12px | 작은 컴포넌트 내부 패딩 |
| `space-4` | 16px | 기본 패딩/마진 |
| `space-5` | 20px | 컴포넌트 간 간격 |
| `space-6` | 24px | 섹션 내부 여백 |
| `space-8` | 32px | 섹션 간 간격 |
| `space-10` | 40px | 큰 섹션 간격 |
| `space-12` | 48px | 섹션 간 큰 여백 |
| `space-16` | 64px | 페이지 레벨 여백 |
| `space-20` | 80px | 히어로 섹션 여백 |
| `space-24` | 96px | 대형 섹션 여백 |

### 4.2 여백 토큰 사용 가이드

```css
/* Component Padding */
--padding-xs: 0.5rem;    /* 8px - 아이콘 버튼 */
--padding-sm: 0.75rem;   /* 12px - 작은 버튼 */
--padding-md: 1rem;      /* 16px - 기본 버튼, 카드 패딩 */
--padding-lg: 1.5rem;    /* 24px - 카드 패딩 */
--padding-xl: 2rem;      /* 32px - 모달 패딩 */
--padding-2xl: 3rem;     /* 48px - 대형 모달 */

/* Gap */
--gap-xs: 0.5rem;        /* 8px - 아이콘 + 텍스트 */
--gap-sm: 0.75rem;       /* 12px - 작은 요소 간격 */
--gap-md: 1rem;          /* 16px - 기본 요소 간격 */
--gap-lg: 1.5rem;        /* 24px - 섹션 요소 간격 */
--gap-xl: 2rem;          /* 32px - 큰 섹션 간격 */

/* Margin */
--margin-sm: 0.5rem;     /* 8px */
--margin-md: 1rem;       /* 16px */
--margin-lg: 1.5rem;     /* 24px */
--margin-xl: 2rem;       /* 32px */
--margin-2xl: 3rem;      /* 48px */
```

## 5. 컴포넌트 스타일

### 5.1 버튼

#### Primary 버튼
```tsx
<button className="
  bg-primary-600 hover:bg-primary-700 active:bg-primary-800
  text-white font-medium
  px-4 py-2 rounded-lg
  transition-colors duration-200
  disabled:bg-slate-300 disabled:cursor-not-allowed
">
  확인
</button>
```

#### Secondary 버튼
```tsx
<button className="
  bg-slate-100 hover:bg-slate-200 active:bg-slate-300
  text-slate-700 font-medium
  px-4 py-2 rounded-lg
  transition-colors duration-200
  disabled:bg-slate-50 disabled:text-slate-400
">
  취소
</button>
```

#### Outline 버튼
```tsx
<button className="
  border-2 border-primary-600 hover:bg-primary-50 active:bg-primary-100
  text-primary-600 font-medium
  px-4 py-2 rounded-lg
  transition-colors duration-200
">
  자세히 보기
</button>
```

#### Ghost 버튼
```tsx
<button className="
  hover:bg-slate-100 active:bg-slate-200
  text-slate-700 font-medium
  px-3 py-2 rounded-md
  transition-colors duration-200
">
  편집
</button>
```

#### 버튼 사이즈
```tsx
// Small
<button className="px-3 py-1.5 text-sm rounded-md">작은 버튼</button>

// Medium (Default)
<button className="px-4 py-2 text-base rounded-lg">기본 버튼</button>

// Large
<button className="px-6 py-3 text-lg rounded-xl">큰 버튼</button>
```

#### 버튼 + 아이콘
```tsx
<button className="flex items-center gap-2">
  <Icon className="w-4 h-4" />
  <span>버튼 텍스트</span>
</button>
```

### 5.2 입력 필드

#### 기본 입력 필드
```tsx
<div className="flex flex-col gap-1">
  <label className="text-sm font-medium text-slate-700">
    이메일
  </label>
  <input
    type="email"
    placeholder="example@company.com"
    className="
      px-3 py-2
      border border-slate-300 rounded-lg
      text-slate-900 placeholder-slate-400
      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
      disabled:bg-slate-100 disabled:text-slate-500
      transition-shadow duration-200
    "
  />
</div>
```

#### 에러 상태
```tsx
<input
  className="
    px-3 py-2
    border-2 border-error-500 rounded-lg
    text-slate-900
    focus:outline-none focus:ring-2 focus:ring-error-500
  "
/>
<p className="text-sm text-error-600 mt-1">
  올바른 이메일 형식을 입력해주세요
</p>
```

#### 성공 상태
```tsx
<div className="relative">
  <input
    className="
      px-3 py-2 pr-10
      border-2 border-success-500 rounded-lg
      text-slate-900
      focus:outline-none focus:ring-2 focus:ring-success-500
    "
  />
  <CheckIcon className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-success-600" />
</div>
```

#### 라벨 + 헬퍼 텍스트
```tsx
<div className="flex flex-col gap-1">
  <label className="text-sm font-medium text-slate-700">
    비밀번호
  </label>
  <input
    type="password"
    className="px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
  />
  <p className="text-xs text-slate-500">
    8자 이상, 영문/숫자/특수문자 조합
  </p>
</div>
```

### 5.3 카드

#### 기본 카드
```tsx
<div className="
  bg-white
  border border-slate-200 rounded-xl
  p-6
  shadow-sm
">
  <h3 className="text-lg font-semibold text-slate-900 mb-2">
    카드 제목
  </h3>
  <p className="text-slate-600">
    카드 내용
  </p>
</div>
```

#### 호버 가능한 카드
```tsx
<div className="
  bg-white
  border border-slate-200 rounded-xl
  p-6
  shadow-sm
  hover:shadow-md hover:border-primary-300
  cursor-pointer
  transition-all duration-200
">
  {/* content */}
</div>
```

#### 강조 카드 (Primary)
```tsx
<div className="
  bg-gradient-to-br from-primary-50 to-white
  border-2 border-primary-200 rounded-xl
  p-6
">
  <div className="flex items-start gap-4">
    <div className="p-2 bg-primary-100 rounded-lg">
      <Icon className="w-6 h-6 text-primary-600" />
    </div>
    <div>
      <h3 className="text-lg font-semibold text-slate-900">
        카드 제목
      </h3>
      <p className="text-slate-600 mt-1">
        카드 내용
      </p>
    </div>
  </div>
</div>
```

#### 경고 카드
```tsx
<div className="
  bg-warning-50
  border border-warning-200 rounded-xl
  p-4
  flex items-start gap-3
">
  <AlertTriangle className="w-5 h-5 text-warning-600 flex-shrink-0 mt-0.5" />
  <div>
    <p className="text-sm font-medium text-warning-900">
      주의사항
    </p>
    <p className="text-sm text-warning-800 mt-1">
      경고 메시지 내용
    </p>
  </div>
</div>
```

### 5.4 모달

#### 기본 모달
```tsx
<div className="fixed inset-0 z-50 flex items-center justify-center">
  {/* Overlay */}
  <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />

  {/* Modal */}
  <div className="
    relative bg-white rounded-2xl shadow-xl
    max-w-md w-full mx-4
    animate-in fade-in slide-in-from-bottom-4
  ">
    {/* Header */}
    <div className="px-6 py-4 border-b border-slate-200">
      <h2 className="text-xl font-semibold text-slate-900">
        모달 제목
      </h2>
    </div>

    {/* Body */}
    <div className="px-6 py-4">
      <p className="text-slate-700">
        모달 내용
      </p>
    </div>

    {/* Footer */}
    <div className="px-6 py-4 border-t border-slate-200 flex justify-end gap-3">
      <button className="px-4 py-2 text-slate-700 hover:bg-slate-100 rounded-lg">
        취소
      </button>
      <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
        확인
      </button>
    </div>
  </div>
</div>
```

#### 다이얼로그 (간단한 확인)
```tsx
<div className="fixed inset-0 z-50 flex items-center justify-center">
  <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
  <div className="relative bg-white rounded-xl shadow-lg max-w-sm w-full mx-4 p-6">
    <div className="flex items-center gap-3 mb-4">
      <AlertCircle className="w-6 h-6 text-error-600" />
      <h3 className="text-lg font-semibold text-slate-900">
        정말 삭제하시겠습니까?
      </h3>
    </div>
    <p className="text-slate-600 mb-6">
      이 작업은 되돌릴 수 없습니다.
    </p>
    <div className="flex justify-end gap-3">
      <button className="px-4 py-2 text-slate-700 hover:bg-slate-100 rounded-lg">
        취소
      </button>
      <button className="px-4 py-2 bg-error-600 text-white rounded-lg hover:bg-error-700">
        삭제
      </button>
    </div>
  </div>
</div>
```

### 5.5 토스트/알림

#### 성공 토스트
```tsx
<div className="
  fixed bottom-4 right-4 z-50
  bg-white border border-success-200 rounded-lg shadow-lg
  flex items-center gap-3 p-4
  animate-in slide-in-from-right-4 fade-in
">
  <CheckCircle className="w-5 h-5 text-success-600" />
  <div>
    <p className="text-sm font-medium text-slate-900">
      저장 완료
    </p>
    <p className="text-xs text-slate-500">
      변경사항이 저장되었습니다
    </p>
  </div>
  <button className="ml-2 text-slate-400 hover:text-slate-600">
    <X className="w-4 h-4" />
  </button>
</div>
```

#### 에러 토스트
```tsx
<div className="
  fixed bottom-4 right-4 z-50
  bg-white border border-error-200 rounded-lg shadow-lg
  flex items-center gap-3 p-4
">
  <AlertCircle className="w-5 h-5 text-error-600" />
  <div>
    <p className="text-sm font-medium text-slate-900">
      오류 발생
    </p>
    <p className="text-xs text-slate-500">
      다시 시도해주세요
    </p>
  </div>
</div>
```

#### 경고 토스트
```tsx
<div className="
  fixed bottom-4 right-4 z-50
  bg-white border border-warning-200 rounded-lg shadow-lg
  flex items-center gap-3 p-4
">
  <AlertTriangle className="w-5 h-5 text-warning-600" />
  <div>
    <p className="text-sm font-medium text-slate-900">
      주의
    </p>
    <p class="text-xs text-slate-500">
      일부 정보가 누락되었습니다
    </p>
  </div>
</div>
```

## 6. 아이콘

### 6.1 아이콘 세트
**Lucide React** 사용 (shadcn/ui 기본)

```bash
npm install lucide-react
```

### 6.2 주요 아이콘 매핑

| 카테고리 | 아이콘 | 용도 |
|----------|--------|------|
| 네비게이션 | Home, Layout, Settings, User | 메인 메뉴 |
| 액션 | Plus, Pencil, Trash, Save | CRUD 작업 |
| 피드백 | CheckCircle, XCircle, AlertCircle, Info | 상태 표시 |
| 상태 | Clock, Calendar, FileText, Shield | 정보 표시 |
| 소통 | MessageSquare, Bell, Mail | 알림, 메시지 |
| 금융 | DollarSign, CreditCard, Receipt | 결제, 급여 |
| 문서 | Download, Upload, Copy, ExternalLink | 파일 작업 |

### 6.3 아이콘 사이즈

```tsx
// Extra Small
<Icon className="w-3 h-3" />  // 12px - 리스트 내

// Small
<Icon className="w-4 h-4" />  // 16px - 버튼 내, 라벨

// Medium (Default)
<Icon className="w-5 h-5" />  // 20px - 카드 내

// Large
<Icon className="w-6 h-6" />  // 24px - 섹션 헤더

// Extra Large
<Icon className="w-8 h-8" />  // 32px - 히어로, 빈 상태
```

## 7. 애니메이션

### 7.1 트랜지션 기본값

```css
/* Transition Timing */
--duration-fast: 150ms;
--duration-normal: 200ms;
--duration-slow: 300ms;

/* Easing */
--ease-out: cubic-bezier(0.215, 0.61, 0.355, 1);
--ease-in-out: cubic-bezier(0.645, 0.045, 0.355, 1);
```

### 7.2 공통 트랜지션

```tsx
// Hover 효과
className="transition-all duration-200 ease-out hover:scale-105"

// Fade 효과
className="transition-opacity duration-200 ease-out"

// Slide 효과
className="transform transition-transform duration-200 ease-out"

// Hover 상태
className="hover:bg-primary-50 hover:text-primary-700 transition-colors duration-200"
```

### 7.3 Tailwind Headless UI Animation

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      animation: {
        'fade-in': 'fadeIn 200ms ease-out',
        'fade-out': 'fadeOut 200ms ease-out',
        'slide-in-from-bottom': 'slideInFromBottom 200ms ease-out',
        'slide-out-to-bottom': 'slideOutToBottom 200ms ease-out',
        'slide-in-from-right': 'slideInFromRight 200ms ease-out',
        'slide-out-to-right': 'slideOutToRight 200ms ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        slideInFromBottom: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideOutToBottom: {
          '0%': { transform: 'translateY(0)', opacity: '1' },
          '100%': { transform: 'translateY(10px)', opacity: '0' },
        },
        slideInFromRight: {
          '0%': { transform: 'translateX(10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideOutToRight: {
          '0%': { transform: 'translateX(0)', opacity: '1' },
          '100%': { transform: 'translateX(10px)', opacity: '0' },
        },
      },
    },
  },
}
```

## 8. 레이아웃 그리드 시스템

### 8.1 그리드 구조

```css
/* Grid Columns */
--grid-cols: 12;

/* Container Max Width */
--container-sm: 640px;   /* 모바일 */
--container-md: 768px;   /* 태블릿 */
--container-lg: 1024px;  /* 랩탑 */
--container-xl: 1280px;  /* 데스크탑 */
--container-2xl: 1536px; /* 대형 스크린 */
```

### 8.2 그리드 사용 예시

```tsx
// 2열 레이아웃
<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
  <div className="col-span-1">왼쪽</div>
  <div className="col-span-1">오른쪽</div>
</div>

// 3열 레이아웃
<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
  <div className="col-span-1">1/3</div>
  <div className="col-span-2">2/3</div>
</div>

// 사이드바 + 메인
<div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
  <aside className="col-span-1">사이드바</aside>
  <main className="col-span-3">메인</main>
</div>
```

### 8.3 반응형 브레이크포인트

| 스크린 | 크기 | 용도 |
|--------|------|------|
| `sm` | 640px | 모바일 가로 |
| `md` | 768px | 태블릿 |
| `lg` | 1024px | 랩탑 |
| `xl` | 1280px | 데스크탑 |
| `2xl` | 1536px | 대형 스크린 |

## 9. 다크 모드

다크 모드는 지원하지 않습니다. 노무닥터는 전문성과 신뢰감을 중시하는 B2B SaaS로, 오프화이트 기반의 밝은 테마만 제공합니다.

## 10. 접근성 체크리스트

- [ ] 색상만으로 정보 전달 금지 (아이콘/텍스트 병행)
- [ ] 모든 이미지에 alt 텍스트 제공
- [ ] 키보드 네비게이션 지원 (Tab, Enter, Escape)
- [ ] 폼 라벨과 입력 필드 연결
- [ ] 에러 메시지에 해결책 제시
- [ ] 포커스 상태 시각적 표시
- [ ] 최소 터치 타깃: 44x44px
- [ ] 동영상/오디오 자동 재생 금지
- [ ] 플래시/깜빡임 사용 금지

## 11. shadcn/ui 기본 컴포넌트

### 11.1 설치된 컴포넌트
- Button
- Input
- Card
- Dialog
- Toast
- Dropdown Menu
- Tabs
- Badge
- Separator
- Avatar
- Select
- Checkbox
- Radio Group

### 11.2 컴포넌트 확장 가이드
기본 shadcn/ui 컴포넌트를 위 디자인 시스템의 토큰으로 커스터마이징합니다.

```tsx
// 예: Button 커스터마이징
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-lg font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800",
        secondary: "bg-slate-100 text-slate-700 hover:bg-slate-200",
        outline: "border-2 border-primary-600 text-primary-600 hover:bg-primary-50",
        ghost: "hover:bg-slate-100 text-slate-700",
      },
      size: {
        sm: "h-9 px-3 text-sm",
        default: "h-10 px-4",
        lg: "h-12 px-6 text-lg",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```

## 12. 사용 가이드

### 12.1 새로운 컴포넌트 작성 시
1. 위 색상/타이포그래피/스페이싱 토큰 사용
2. shadcn/ui 기반 컴포넌트 활용
3. 접근성 속성 (aria-label, role 등) 추가
4. 반응형 (모바일 우선) 고려
5. 로딩/에러 상태 처리

### 12.2 페이지 레이아웃 작성 시
1. 그리드 시스템 활용 (grid-cols-12 기반)
2. max-width: 1280px (container-xl) 제한
3. 반응형 (mobile-first) 브레이크포인트 활용
4. 세로 스크롤 방지 (내용이 길면 페이지 분리)

### 12.3 색상 사용 가이드
- Primary: 브랜드 표현, CTA 버튼
- Accent: 강조 포인트, 하이라이트
- Neutral: 배경, 테두리, 텍스트
- Success: 성공 메시지, 긍정 피드백
- Warning: 경고, 주의사항
- Error: 에러 메시지, 부정 피드백

---

**버전:** 1.0
**작성일:** 2026-03-01
**마지막 수정:** 2026-03-01
