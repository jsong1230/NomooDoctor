# 노무닥터 (NomooDoctor)

AI 기반 노무/HR 자동화 SaaS — 50인 미만 사업장을 위한 AI 노무 비서

## 프로젝트 소개

노무닥터는 중소사업장(50인 미만)을 위한 올인원 노무 관리 솔루션입니다. 복잡한 노동법을 AI가 쉽게 풀어주고, 근로계약서 작성부터 급여 계산까지 자동화합니다.

## 핵심 기능

### M1 (1차 릴리즈)
- ✅ **F-01 사용자 인증**: 회원가입/로그인/JWT/카카오 OAuth
- ✅ **F-02 사업장 관리**: 사업장 등록/수정/조회/컨텍스트 설정
- ✅ **F-03 직원 관리**: 직원 CRUD/고용형태별 관리

### M2 (2차 릴리즈)
- ⏳ **F-04 근로계약서 자동 생성**: 고용형태별 법적 유효 계약서 생성/다운로드
- ⏳ **F-05 급여 자동 계산기**: 주휴수당/연장수당/4대보험/소득세 자동화
- ⏳ **F-07 급여명세서 생성 및 발송**: 법정 명세서 생성/이메일/카카오 알림톡

### M3 (3차 릴리즈)
- ⏳ **F-06 AI 노동법 Q&A 챗봇**: 자연어 질문 → 법령 기반 즉각 답변
- ⏳ **F-10 컴플라이언스 대시보드**: 리스크 스코어/노무 이벤트 캘린더

## 기술 스택

### Backend
- **Framework**: FastAPI (Python 3.12)
- **ORM**: SQLAlchemy 2.0 (Async)
- **Database**: PostgreSQL 16 + pgvector
- **Cache**: Redis 7
- **Auth**: JWT + Refresh Token Rotation

### Frontend
- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui

### Infrastructure
- **Container**: Docker + Docker Compose
- **DB Migration**: Alembic

## 시작하기

### 환경 요구사항
- Docker & Docker Compose
- Python 3.12+
- Node.js 20+

### 설치 및 실행

```bash
# 저장소 클론
git clone https://github.com/jsong1230/NomooDoctor.git
cd NomooDoctor

# 환경변수 설정
cp backend/.env.example backend/.env

# Docker 서비스 기동
docker compose up -d

# DB 마이그레이션
docker compose exec backend alembic upgrade head

# 접속 확인
# Backend: http://localhost:8000/docs
# Frontend: http://localhost:3000
```

### 로컬 개발

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## 프로젝트 구조

```
NomooDoctor/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API 라우터
│   │   ├── core/            # 핵심 설정/보안
│   │   ├── db/              # DB 모델/세션
│   │   ├── repositories/    # 데이터 접근 계층
│   │   ├── schemas/         # Pydantic 스키마
│   │   └── services/        # 비즈니스 로직
│   ├── alembic/             # DB 마이그레이션
│   └── tests/               # 테스트
├── frontend/
│   ├── app/                 # Next.js App Router
│   ├── components/          # React 컴포넌트
│   └── lib/                 # 유틸리티
└── docs/
    ├── project/             # 프로젝트 문서
    └── specs/               # 기능별 상세 명세
```

## API 문서

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 테스트

```bash
# Backend 테스트
cd backend
pytest

# Frontend 테스트
cd frontend
npm test
```

## 라이선스

Private Project - All Rights Reserved

## 기여

내부 프로젝트로 현재 외부 기여는 받지 않습니다.
