# F-12 노무사 마켓플레이스 — 기술 설계서

## 1. 개요

파트너 노무사 프로필 조회, AI 기반 케이스 자동 요약, 상담 신청/관리 기능 구현.
프리미엄 플랜 사용자는 월 1회 무료 상담 포함.

## 2. 데이터 모델

ERD (docs/system/erd.md Section 3.8) 기준 3개 테이블:

### labor_attorneys (파트너 노무사)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | 노무사 ID |
| user_id | UUID FK | 사용자 ID (회원 연동) |
| license_number | VARCHAR(50) UK | 자격번호 |
| name | VARCHAR(100) | 성명 |
| firm_name | VARCHAR(200) | 사무소명 |
| specialties | TEXT[] | 전문분야 배열 |
| regions | TEXT[] | 활동지역 배열 |
| consultation_fee | INTEGER | 기본 상담료 (원) |
| experience_years | INTEGER | 경력 연수 |
| rating | NUMERIC(2,1) | 평균 평점 |
| review_count | INTEGER | 리뷰 수 |
| response_rate | NUMERIC(3,0) | 응답률 (%) |
| bio | TEXT | 소개 |
| profile_image_url | TEXT | 프로필 이미지 |
| verified | BOOLEAN | 인증 여부 |
| is_active | BOOLEAN | 활성 여부 |
| created_at | TIMESTAMPTZ | 생성일 |

### attorney_cases (상담 케이스)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | 케이스 ID |
| user_id | UUID FK | 의뢰인 ID |
| attorney_id | UUID FK | 노무사 ID |
| company_id | UUID FK | 관련 사업장 |
| chat_session_id | UUID FK | AI 상담 세션 (선택) |
| case_summary | TEXT | AI 자동 케이스 요약 |
| case_type | VARCHAR(50) | 유형 (dismissal/wage/leave/industrial_accident/harassment/other) |
| urgency | VARCHAR(20) | 긴급도 (low/medium/high/emergency) |
| status | VARCHAR(20) | 상태 (pending/accepted/in_progress/completed/cancelled) |
| consultation_type | VARCHAR(20) | 상담 방법 (video/phone/visit) |
| preferred_schedule | JSONB | 희망 일정 배열 |
| scheduled_at | TIMESTAMPTZ | 확정 일정 |
| consultation_fee | INTEGER | 실제 상담료 |
| fee_paid | BOOLEAN | 결제 여부 |
| fee_paid_at | TIMESTAMPTZ | 결제 일시 |
| completed_at | TIMESTAMPTZ | 완료 일시 |
| created_at | TIMESTAMPTZ | 생성일 |

### attorney_reviews (리뷰)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | 리뷰 ID |
| case_id | UUID FK | 케이스 ID |
| user_id | UUID FK | 작성자 ID |
| attorney_id | UUID FK | 노무사 ID |
| rating | INTEGER | 평점 (1-5) |
| comment | TEXT | 코멘트 |
| created_at | TIMESTAMPTZ | 생성일 |

## 3. API 설계

### 3.1 노무사 프로필 (공개)

```
GET /api/v1/attorneys
  Query: specialty, region, sort(rating/fee/experience), limit, cursor
  Response: { attorneys: [...], pagination: {...} }

GET /api/v1/attorneys/{id}
  Response: { attorney: {...}, recent_reviews: [...] }
```

### 3.2 상담 케이스 (인증 필요)

```
POST /api/v1/attorney-cases
  Body: { attorney_id, company_id?, chat_session_id?, case_type, urgency,
          consultation_type, preferred_schedule, description? }
  → AI 케이스 요약 자동 생성 (chat_session_id 제공 시)
  Response: 201 { case_id, case_summary, status, consultation_fee }

GET /api/v1/attorney-cases
  Query: status, limit, cursor
  Response: { cases: [...], pagination: {...} }

GET /api/v1/attorney-cases/{id}
  Response: { case: {...} }

PUT /api/v1/attorney-cases/{id}/cancel
  Response: { status: "cancelled" }
```

### 3.3 리뷰 (인증 필요)

```
POST /api/v1/attorney-cases/{id}/review
  Body: { rating: 1-5, comment? }
  Response: 201 { review_id }

GET /api/v1/attorneys/{id}/reviews
  Query: limit, cursor
  Response: { reviews: [...], pagination: {...} }
```

## 4. 서비스 레이어

### AttorneyService
- `list_attorneys(filters)` — 필터/정렬/페이지네이션
- `get_attorney(id)` — 상세 + 최근 리뷰

### CaseService
- `create_case(user, data)` — 케이스 생성 + AI 요약
- `list_my_cases(user, filters)` — 내 케이스 목록
- `get_case(user, id)` — 케이스 상세
- `cancel_case(user, id)` — 케이스 취소

### ReviewService
- `create_review(user, case_id, data)` — 리뷰 작성 + 평점 업데이트
- `list_reviews(attorney_id)` — 노무사 리뷰 목록

### CaseSummaryService
- `generate_summary(chat_session_id)` — Claude API로 케이스 요약 생성
  - PRD 6.6 프롬프트 사용
  - chat_session_id 없으면 사용자 입력 description 사용

## 5. 케이스 복잡도 분류

PRD 기준:
- **LOW**: AI 처리 가능 (계약서, 급여, 일반 Q&A)
- **MEDIUM**: 노무사 추천 (계약 해지, 연차 분쟁, 취업규칙 위반)
- **HIGH**: 노무사 강력 권장 (부당해고, 괴롭힘, 산재, 체불임금, 근로감독)
- **EMERGENCY**: 즉각 연결 (고용노동부 출석, 노동위원회 접수)

## 6. 프리미엄 플랜 무료 상담

- Premium 플랜: 월 1회 무료 노무사 상담
- PlanService.check_feature_access("attorney_consult") 연동
- 무료 사용 시 consultation_fee = 0, plan_usage.attorney_consult_count += 1

## 7. 프론트엔드

### 페이지
- `/attorneys` — 노무사 목록 (검색/필터)
- `/attorneys/[id]` — 노무사 상세 프로필 + 리뷰 + 상담 신청

### 컴포넌트
- AttorneyCard: 노무사 카드 (이름, 전문분야, 평점, 상담료)
- AttorneyProfile: 노무사 상세 프로필
- CaseRequestForm: 상담 신청 폼
- ReviewList: 리뷰 목록
- ReviewForm: 리뷰 작성 폼
- MyCaseList: 내 상담 케이스 목록

## 8. 에러 코드

| 코드 | HTTP | 설명 |
|------|------|------|
| E-8001 | 404 | 노무사 없음 |
| E-8002 | 404 | 케이스 없음 |
| E-8003 | 409 | 이미 리뷰 작성됨 |
| E-8004 | 400 | 잘못된 케이스 상태 (취소 불가) |
| E-8005 | 403 | 사용량 초과 (무료 상담 소진) |
| E-8006 | 400 | 평점 범위 오류 (1-5) |
