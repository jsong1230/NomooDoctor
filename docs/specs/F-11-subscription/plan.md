# 구독 및 결제 — 구현 계획서

## 참조
- 설계서: docs/specs/F-11-subscription/design.md (미작성 - 추후 /feat에서 작성)
- 인수조건: docs/project/features.md #F-11
- UI 설계서: docs/specs/F-11-subscription/ui-spec.md (미작성 - 추후 /feat에서 작성)
- ERD: docs/system/erd.md
- API 컨벤션: docs/system/api-conventions.md

## 태스크 목록

### Phase 1: 백엔드 구현
- [ ] [backend] DB 스키마 + 마이그레이션 (subscriptions 테이블)
  - subscriptions 테이블 생성 (users와 1:N 관계)
  - plan, status, starts_at, expires_at, toss_order_id, toss_billing_key, monthly_amount 컬럼
  - 인덱스 생성 (user_id, expires_at)
- [ ] [backend] 토스페이먼츠 SDK 연동
  - 토스페이먼츠 API 클라이언트 구현 (billing_key 발급, 정기 결제)
  - 웹훅 엔드포인트 구현 (/api/v1/webhooks/toss)
  - 서명 검증 미들웨어
- [ ] [backend] 서비스 로직 구현
  - SubscriptionService: 구독 생성, 플랜 변경, 해지, 만료 확인
  - PaymentService: 결제 처리, 빌링키 관리, 웹훅 처리
  - PlanService: 플랜별 권한 확인 (Q&A 횟수, 계약서 횟수, 급여명세서 발송)
- [ ] [backend] API 라우트 구현
  - GET /api/v1/subscriptions/plans - 플랜 목록
  - GET /api/v1/subscriptions/me - 내 구독 정보
  - POST /api/v1/subscriptions - 구독 시작
  - PUT /api/v1/subscriptions - 플랜 변경
  - DELETE /api/v1/subscriptions - 구독 해지
  - POST /api/v1/subscriptions/billing-key - 빌링키 등록
  - GET /api/v1/subscriptions/history - 결제 내역
- [ ] [backend] 플랜별 접근 제어 미들웨어
  - PlanMiddleware: 요청별 플랜 권한 확인
  - Q&A 횟수 제한 (starter: 10회/월)
  - 계약서 생성 제한 (starter: 2건/월)
  - 급여명세서 발송 제한 (standard: 100건/월, premium: 무제한)
  - JWT payload에 plan 정보 포함 (토큰 갱신 시 동기화)
- [ ] [backend] 구독 만료 알림 기능
  - Celery/Background Task로 만료 7일 전/만료일 알림
  - users.plan, users.plan_expires_at 업데이트
- [ ] [backend] API 스펙 문서 작성 (docs/api/F-11-subscription.md)

### Phase 2: 프론트엔드 구현
- [ ] [frontend] 타입 정의 + API 클라이언트
  - Subscription 타입 정의 (plan, status, starts_at, expires_at, monthly_amount)
  - SubscriptionPlan 타입 정의 (starter, basic, standard, premium)
  - Subscription API 클라이언트 (getPlans, getMySubscription, createSubscription, updatePlan, cancelSubscription, registerBillingKey, getPaymentHistory)
- [ ] [frontend] UI 컴포넌트 구현
  - PlanCard: 플랜 카드 (가격, 기능 비교)
  - PlanComparison: 플랜 비교 표
  - SubscriptionStatus: 현재 구독 상태 표시
  - BillingKeyForm: 빌링키 등록 폼
  - PaymentHistory: 결제 내역 리스트
- [ ] [frontend] 페이지 통합
  - /pricing 페이지: 플랜 선택 및 업그레이드
  - /subscription 페이지: 구독 관리 (플랜 변경, 해지, 빌링키 관리)
  - 대시보드에 현재 플랜 표시
  - Q&A, 계약서, 급여명세서 발송 시 플랜 제한 UI (limit 초과 시 업그레이드 CTA)
- [ ] [frontend] 플랜별 Rate Limiting UI
  - 스타터 플랜: Q&A 10회/월 표시 (현재/한도)
  - 스타터 플랜: 계약서 2건/월 표시
  - 스탠다드 플랜: 급여명세서 100건/월 표시

### Phase 3: 검증
- [ ] [shared] 통합 테스트 실행
  - 구독 생성 테스트 (정기 결제 성공)
  - 플랜 변경 테스트 (프로레이션 계산)
  - 구독 해지 테스트 (만료일 설정)
  - 웹훅 처리 테스트 (결제 성공/실패)
  - 플랜별 권한 테스트 (starter 제한, premium 무제한)
- [ ] [shared] quality-gate 검증
  - 보안: 빌링키 암호화 저장, 웹훅 서명 검증
  - 성능: 플랜 확인 쿼리 최적화 (Redis 캐싱)
  - 코드 리뷰: 결제 로직의 원자성 보장
- [ ] [shared] 토스페이먼츠 테스트 결제 (sandbox 환경)

## 태스크 의존성
Phase 1 ──▶ Phase 2 ──▶ Phase 3

## 병렬 실행 판단
- Agent Team 권장: Yes
- 근거:
  - 백엔드(토스페이먼츠 연동)과 프론트엔드(UI)는 독립적
  - API 스펙이 확정되면 병렬 개발 가능
  - 토스페이먼츠 sandbox 환경에서 병렬 테스트 가능

## 기술적 고려사항

### 토스페이먼츠 연동
- **Billing Key 발급**: 카드 정보 등록 → 빌링키 반환 → DB 저장
- **정기 결제**: 매월 1일 00:00 자동 결제 (또는 구독 시작일 기준)
- **플랜 변경**: 프로레이션 계산 (잔여일 기준 차감/추가)
- **구독 해지**: 만료일까지 서비스 유지 → 만료일에 status = 'cancelled'
- **웹훅**: 결제 성공/실패 시 subscription.status 업데이트

### 플랜별 Rate Limiting
| 기능 | Starter | Basic | Standard | Premium |
|------|---------|-------|----------|---------|
| Q&A | 10회/월 | 무제한 | 무제한 | 무제한 |
| 계약서 생성 | 2건/월 | 무제한 | 무제한 | 무제한 |
| 급여 계산 | X | O | O | O |
| 급여명세서 발송 | X | X | 100건/월 | 무제한 |
| 노무사 상담 | X | X | X | 1회/월 무료 |

### JWT Payload 확장
```json
{
  "sub": "user_id",
  "company_id": "company_id",
  "plan": "standard",  // 추가
  "plan_expires_at": "2026-04-12T00:00:00Z",  // 추가
  "role": "owner",
  "exp": 1700000000,
  "iat": 1699996400,
  "jti": "token_id"
}
```

### 보안
- 빌링키는 AES-256-GCM 암호화 저장 (또는 토스페이먼츠가 직접 관리하는 방식 고려)
- 웹훅 요청 시 서명 검증 필수
- 결제 실패 시 재시도 로직 구현 (최대 3회)

### 데이터 모델
- subscriptions 테이블: users와 1:N 관계
- status: active, cancelled, expired, paused
- plan: starter, basic, standard, premium
- toss_billing_key: 토스페이먼츠에서 발급받은 빌링키

### 에러 처리
- 결제 실패: E-7002 (결제 실패), 재시도 안내
- 플랜 제한 초과: E-6001 (요청 횟수 초과), 업그레이드 CTA
- 구독 만료: E-7001 (결제 필요), 갱신 안내

## 인수조건 체크리스트
- [ ] 스타터(무료): Q&A 10회/월, 계약서 2건/월
- [ ] 베이직(9,900원): Q&A 무제한, 계약서 무제한, 급여 계산
- [ ] 스탠다드(29,000원): 전체 기능, 급여명세서 발송 100건/월
- [ ] 프리미엄(49,000원): 전체 기능, 발송 무제한, 노무사 1회/월 무료
- [ ] 토스페이먼츠 결제 연동
- [ ] 정기 결제 (자동결제)
- [ ] 플랜 업그레이드/다운그레이드
- [ ] 구독 해지
- [ ] 플랜별 접근 제어 미들웨어
- [ ] 구독 만료 전 알림
