# F-12 노무사 마켓플레이스 — 구현 계획서

## 참조
- 설계서: docs/specs/F-12-attorney-marketplace/design.md
- 테스트 스펙: docs/specs/F-12-attorney-marketplace/test-spec.md
- ERD: docs/system/erd.md (Section 3.8)
- PRD: docs/project/prd_nomoodoc_v2.md (Feature 6, Section 6.6)

## 태스크 목록

### Phase 1: 백엔드 구현
- [ ] [backend] DB 모델 + Alembic 마이그레이션
  - labor_attorneys, attorney_cases, attorney_reviews 테이블
  - 인덱스: specialty, region, rating, user_id
- [ ] [backend] Pydantic 스키마 (app/schemas/attorney.py)
- [ ] [backend] Repository 레이어
  - AttorneyRepository: 목록/상세/평점 업데이트
  - CaseRepository: CRUD + 필터
  - ReviewRepository: CRUD + 중복 체크
- [ ] [backend] Service 레이어
  - AttorneyService: 목록/상세
  - CaseService: 생성(AI 요약)/목록/상세/취소
  - ReviewService: 작성/목록/평점 업데이트
  - CaseSummaryService: Claude API 케이스 요약 생성
- [ ] [backend] API 라우터 (app/api/v1/attorneys.py)
- [ ] [backend] 예외 클래스 (E-8001 ~ E-8006)
- [ ] [backend] 시드 데이터 (테스트용 노무사 3명)
- [ ] [backend] 테스트 (단위 15 + 통합 12 = 27개)

### Phase 2: 프론트엔드 구현
- [ ] [frontend] 타입 + API 클라이언트 + 스토어
- [ ] [frontend] /attorneys 페이지 (검색/필터/카드 목록)
- [ ] [frontend] /attorneys/[id] 페이지 (프로필/리뷰/상담 신청)
- [ ] [frontend] 내 상담 케이스 섹션

### Phase 3: 검증
- [ ] 전체 회귀 테스트
- [ ] quality-gate 리뷰

## 태스크 의존성
Phase 1 → Phase 2 → Phase 3
