# 노무닥터 (NomooDoctor)

## 프로젝트
AI 기반 노무/HR 자동화 SaaS — 50인 미만 사업장을 위한 AI 노무 비서

## 기술 스택
- Backend: FastAPI (Python 3.12) + SQLAlchemy 2.0
- Frontend: Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui
- DB: PostgreSQL 16 (pgvector) + Redis 7

## 디렉토리
- `backend/` — FastAPI 백엔드 소스 코드
- `frontend/` — Next.js 프론트엔드 소스 코드
- `docs/` — 프로젝트 문서

## 실행

### 환경 설정
1. `.env.example` 복사하여 `.env` 생성: `cp .env.example .env`
2. `.env` 파일에서 필요한 API 키 설정 (개발용으로 기본값 제공)

### Docker 개발 서버 기동
```bash
# 전체 서비스 기동 (PostgreSQL + Redis + Backend + Frontend)
docker compose up

# 백그라운드 실행
docker compose up -d

# 로그 확인
docker compose logs -f

# 서비스 중지
docker compose down

# 볼륨 포함 전체 삭제
docker compose down -v
```

### 로컬 개발 (Docker 외)
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

### DB 마이그레이션
```bash
# Docker 컨테이너 내에서 실행
docker compose exec backend alembic upgrade head

# 로컬에서 실행
cd backend
alembic upgrade head
```

### 테스트
- Backend: `cd backend && pytest`
- Frontend: `cd frontend && npm test`

### 빌드
- Docker 이미지 빌드: `docker compose build`

## 프로젝트 관리
- 방식: file
