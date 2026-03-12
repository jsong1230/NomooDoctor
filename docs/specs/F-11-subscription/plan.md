# 구독 및 결제 — 구현 계획서

## 참조
- 설계서: docs/specs/F-11-subscription/design.md
- 테스트 스펙: docs/specs/F-11-subscription/test-spec.md
- 인수조건: docs/project/features.md #F-11
- ERD: docs/system/erd.md
- API 컨벤션: docs/system/api-conventions.md

## 태스크 목록

### Phase 1: 백엔드 구현 (✅ 완료)
- [x] [backend] DB 스키마 + 마이그레이션
  - subscriptions, payment_history, plan_usage 테이블 생성
  - 복합 인덱스 (user_status, expires_active, payment_user, usage_user_month)
  - Alembic 마이그레이션: `20260312_1922_4ddb6934627a`
- [x] [backend] 토스페이먼츠 SDK 연동
  - TossClient: 빌링키 발급, 정기 결제, 빌링키 검증
  - Mock 모드 (API 키 미설정 시 자동)
  - 웹훅 엔드포인트 (POST /api/v1/webhooks/toss)
- [x] [backend] 서비스 로직 구현
  - SubscriptionService: 구독 생성, 플랜 변경(비례배분), 해지
  - PaymentService: 결제 처리, 빌링키 관리, 웹훅 처리, 실패 재시도
  - PlanService: 플랜별 권한 확인, 사용량 제한 체크
- [x] [backend] API 라우트 구현
  - GET /subscriptions/plans — 플랜 목록 (비인증)
  - GET /subscriptions/me — 내 구독 + 사용량
  - POST /subscriptions — 구독 시작
  - PUT /subscriptions — 플랜 변경
  - DELETE /subscriptions — 구독 해지
  - GET /subscriptions/history — 결제 내역 (커서 페이지네이션)
- [x] [backend] 테스트 (41/41 PASSED)
  - 단위 테스트 22개 (SubscriptionService 12, PlanService 10)
  - 통합 테스트 19개 (Plans 1, MySubscription 2, Create 5, ChangePlan 4, Cancel 3, History 2, Webhook 2)

### Phase 2: 프론트엔드 구현 (✅ 완료)
- [x] [frontend] 타입 정의 + API 클라이언트
  - types/subscription.ts: 전체 타입 정의
  - lib/api/subscription.ts: API 클라이언트 (6개 함수)
  - lib/stores/subscription-store.ts: Zustand 스토어
- [x] [frontend] UI 컴포넌트 구현
  - PlanCard: 플랜 카드 (가격, 기능 비교, 추천 뱃지)
  - SubscriptionInfo: 구독 상태 + 사용량 프로그레스 바
  - PaymentHistory: 결제 내역 테이블 (커서 페이지네이션)
  - PlanChangeDialog: 플랜 변경 확인 모달
  - CancelDialog: 구독 해지 사유/피드백 모달
- [x] [frontend] 페이지 통합
  - /subscription 페이지 (3탭: 구독 현황, 플랜 비교, 결제 내역)
  - Tabs 컴포넌트 controlled mode 확장

### Phase 3: 검증 (✅ 완료)
- [x] 전체 회귀 테스트: 205 passed, 20 failed (기존 M1 이슈)
- [x] F-11 신규 실패: 0건

## 태스크 의존성
Phase 1 ──▶ Phase 2 ──▶ Phase 3

## 기술적 고려사항

### 토스페이먼츠 연동
- **Billing Key 발급**: authKey → TossClient.issue_billing_key() → billingKey 반환
- **정기 결제**: TossClient.charge(billing_key, amount, order_id, customer_key)
- **Mock 모드**: TOSS_SECRET_KEY/TOSS_CLIENT_KEY 미설정 시 자동 mock 응답
- **플랜 변경**: 일할 비례배분 (proration) 계산

### 플랜별 기능 제한
| 기능 | Starter | Basic | Standard | Premium |
|------|---------|-------|----------|---------|
| AI 상담 | 10회/월 | 무제한 | 무제한 | 무제한 |
| 계약서 생성 | 2건/월 | 무제한 | 무제한 | 무제한 |
| 급여 관리 | X | O | O | O |
| 급여명세서 발송 | X | 10건/월 | 100건/월 | 무제한 |
| 노무사 상담 | X | X | X | 1회/월 |

### 에러 코드
- E-7001: 결제 필요 (구독 만료)
- E-7002: 결제 실패
- E-7003: 구독 없음 (404)
- E-7004: 이미 활성 구독 존재 / 동일 플랜 변경 시도 (409)
- E-7005: 유효하지 않은 빌링키 (400)
- E-7006: 다운그레이드 오류 (400)
- E-7007: 빌링키 등록 실패 (400)
- E-7008: 빌링키 이미 존재 (409)

## 인수조건 체크리스트
- [x] 스타터(무료): AI 상담 10회/월, 계약서 2건/월
- [x] 베이직(9,900원): AI 상담 무제한, 계약서 무제한, 급여 계산
- [x] 스탠다드(29,000원): 전체 기능, 급여명세서 100건/월
- [x] 프리미엄(49,000원): 전체 기능, 명세서 무제한, 노무사 1회/월
- [x] 토스페이먼츠 결제 연동 (mock 모드 지원)
- [x] 정기 결제 (빌링키 기반)
- [x] 플랜 업그레이드/다운그레이드 (비례배분)
- [x] 구독 해지 (사유/피드백 수집)
- [x] 플랜별 접근 제어 (PlanService)
- [ ] 구독 만료 전 알림 (Celery 등 배경 작업 — 추후 구현)
