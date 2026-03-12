# F-12 노무사 마켓플레이스 — 테스트 스펙

## 단위 테스트 (backend/tests/unit/test_attorney_service.py)

### AttorneyService (5개)
1. test_노무사_목록_조회_기본 — 전체 목록 반환
2. test_노무사_목록_필터_전문분야 — specialty 필터
3. test_노무사_목록_필터_지역 — region 필터
4. test_노무사_목록_정렬_평점순 — sort=rating
5. test_노무사_상세_조회 — ID로 조회 + 리뷰 포함

### CaseService (6개)
6. test_케이스_생성_성공 — 기본 케이스 생성
7. test_케이스_생성_AI_요약_포함 — chat_session_id 기반 요약
8. test_케이스_목록_조회 — 내 케이스 필터
9. test_케이스_상세_조회 — 단건 조회
10. test_케이스_취소_성공 — pending 상태 취소
11. test_케이스_취소_불가_진행중 — in_progress 취소 실패

### ReviewService (4개)
12. test_리뷰_작성_성공 — 평점 + 코멘트
13. test_리뷰_중복_작성_실패 — 같은 케이스 중복 리뷰
14. test_리뷰_작성_후_평점_업데이트 — 노무사 평균 평점 재계산
15. test_리뷰_평점_범위_오류 — 0 또는 6 입력 시 실패

## 통합 테스트 (backend/tests/api/test_attorney_api.py)

### 노무사 목록 API (3개)
1. test_노무사_목록_조회_성공 — GET /attorneys
2. test_노무사_목록_필터_조회_성공 — specialty + region 필터
3. test_노무사_상세_조회_성공 — GET /attorneys/{id}

### 상담 케이스 API (6개)
4. test_상담_신청_성공 — POST /attorney-cases (201)
5. test_상담_신청_미인증_실패 — 401
6. test_내_케이스_목록_조회_성공 — GET /attorney-cases
7. test_케이스_상세_조회_성공 — GET /attorney-cases/{id}
8. test_케이스_취소_성공 — PUT /attorney-cases/{id}/cancel
9. test_존재하지_않는_케이스_실패 — 404

### 리뷰 API (3개)
10. test_리뷰_작성_성공 — POST /attorney-cases/{id}/review (201)
11. test_리뷰_중복_작성_실패 — 409
12. test_노무사_리뷰_목록_조회 — GET /attorneys/{id}/reviews

총 테스트: 단위 15개 + 통합 12개 = **27개**
