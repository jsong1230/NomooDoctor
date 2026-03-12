# F-11 구독 및 결제 — 테스트 명세

## 참조
- 설계서: docs/specs/F-11-subscription/design.md
- 인수조건: docs/project/features.md #F-11

---

## 1. 단위 테스트

### 1.1 SubscriptionService

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| get_plans | 플랜 목록 조회 | - | 4개 플랜 반환 (starter, basic, standard, premium) |
| get_plans | 플랜 가격 확인 | - | starter=0, basic=9900, standard=29000, premium=49000 |
| get_my_subscription | 활성 구독 조회 | user with active subscription | subscription + usage 반환 |
| get_my_subscription | 구독 없음 | user without subscription | subscription=null, usage=0 |
| create_subscription | 구독 생성 성공 | user, plan=basic, billing_key=valid | subscription 생성, status=active |
| create_subscription | 이미 활성 구독 존재 | user with active subscription | E-7004 에러 |
| create_subscription | 유효하지 않은 빌링키 | user, plan=basic, billing_key=invalid | E-7005 에러 |
| create_subscription | 결제 실패 | user, plan=basic, billing_key=fail | E-7002 에러 |
| change_plan | 업그레이드 성공 | current=basic, new=standard | proration 계산, 즉시 변경 |
| change_plan | 다운그레이드 요청 | current=premium, new=basic | 다음 결제일 적용 안내 |
| change_plan | 동일 플랜 변경 | current=basic, new=basic | E-7004 에러 (이미 구독 중) |
| change_plan | 활성 구독 없음 | user without subscription | E-7003 에러 |
| cancel_subscription | 구독 해지 | user with active subscription | status=cancelled, access_until 반환 |
| cancel_subscription | 이미 해지된 구독 | user with cancelled subscription | E-7003 에러 |
| calculate_proration | 비례 계산 | basic(9900), standard(29000), remaining_days=15 | (29000-9900) * 15/30 = 9550 |
| calculate_proration | 월 초 변경 | basic(9900), standard(29000), remaining_days=30 | (29000-9900) = 19100 |

### 1.2 PaymentService

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| register_billing_key | 빌링키 등록 성공 | user, auth_key=valid, customer_key=uuid | billing_key 반환, 카드 정보 포함 |
| register_billing_key | 이미 등록된 빌링키 | user with existing billing_key | E-7008 에러 |
| register_billing_key | 인증 실패 | user, auth_key=invalid | E-7007 에러 |
| charge_with_billing_key | 결제 성공 | billing_key=valid, amount=29000 | payment_id 반환, status=success |
| charge_with_billing_key | 결제 실패 - 잔액 부족 | billing_key=insufficient_funds | status=failed, failure_reason |
| charge_with_billing_key | 결제 실패 - 카드 정지 | billing_key=blocked_card | status=failed, failure_reason |
| process_webhook | 결제 성공 웹훅 | eventType=PAYMENT_STATUS_CHANGED, status=DONE | subscription 연장 |
| process_webhook | 결제 실패 웹훅 | eventType=PAYMENT_STATUS_CHANGED, status=FAILED | 재시도 스케줄링 |
| process_webhook | 빌링키 만료 웹훅 | eventType=BILLING_KEY_STATUS_CHANGED | 사용자 알림 발송 |
| process_webhook | 중복 웹훅 | 이미 처리된 payment_id | 무시 (멱등성) |
| get_payment_history | 결제 내역 조회 | user with 5 payments, limit=3 | 3개 반환, has_next=true |
| get_payment_history | 페이지네이션 | cursor=valid | 다음 페이지 반환 |
| handle_failed_payment | 실패 처리 | subscription, error=insufficient_funds | retry_at 설정 (1일 후) |
| handle_failed_payment | 최대 재시도 초과 | subscription, retry_count=3 | subscription.status=paused |

### 1.3 PlanService

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| check_feature_access | 스타터 채팅 접근 | user.plan=free, feature=chat | True |
| check_feature_access | 스타터 급여계산 접근 | user.plan=free, feature=payroll | False |
| check_feature_access | 베이직 급여계산 접근 | user.plan=basic, feature=payroll | True |
| check_feature_access | 만료된 플랜 접근 | user.plan=basic, plan_expires_at=past | False |
| check_usage_limit | 스타터 채팅 5회 사용 | user.plan=free, usage=5, limit=10 | allowed=true, remaining=5 |
| check_usage_limit | 스타터 채팅 10회 사용 | user.plan=free, usage=10, limit=10 | allowed=false, remaining=0 |
| check_usage_limit | 프리미엄 채팅 사용 | user.plan=premium, usage=100, limit=None | allowed=true, remaining=null |
| check_usage_limit | 스탠다드 명세서 50회 사용 | user.plan=standard, usage=50, limit=100 | allowed=true, remaining=50 |
| check_usage_limit | 스탠다드 명세서 100회 사용 | user.plan=standard, usage=100, limit=100 | allowed=false, remaining=0 |
| increment_usage | 사용량 증가 | user, usage_type=chat | chat_count + 1 |
| increment_usage | 새 월 첫 사용 | user, usage_month=new_month | 새 레코드 생성 |
| get_current_usage | 현재 사용량 조회 | user with usage | chat=5, contract=2, payslip=10 |
| get_current_usage | 사용량 없음 | user without usage | 모든 값 0 |
| get_plan_features | 스타터 기능 조회 | plan=free | chat_limit=10, payroll=false |
| get_plan_features | 프리미엄 기능 조회 | plan=premium | 모든 limit=null, attorney=true |

### 1.4 TossClient (외부 API)

| 대상 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| issue_billing_key | 빌링키 발급 성공 | auth_key=valid, customer_key=uuid | billing_key, card_info 반환 |
| issue_billing_key | 인증 키 만료 | auth_key=expired | TossAPIError |
| charge | 결제 성공 | billing_key, amount, order_id | payment_id, status=DONE |
| charge | 결제 실패 | billing_key=invalid | payment_id, status=FAILED |
| charge | 중복 order_id | order_id=duplicate | 에러 (멱등성 위반) |
| get_payment | 결제 조회 | payment_id=valid | 결제 상세 정보 |
| cancel_payment | 결제 취소 | payment_id=valid, reason=reason | status=CANCELED |

---

## 2. 통합 테스트

### 2.1 POST /api/v1/subscriptions/plans

| 시나리오 | 입력 | 예상 결과 |
|----------|------|-----------|
| 플랜 목록 조회 (비인증) | GET /subscriptions/plans | 200, 4개 플랜 반환 |
| 플랜 기능 검증 | - | starter.chat_limit=10, premium.attorney=true |

### 2.2 GET /api/v1/subscriptions/me

| 시나리오 | 입력 | 예상 결과 |
|----------|------|-----------|
| 활성 구독 조회 | Authorization: Bearer valid_token | 200, subscription + usage |
| 구독 없음 | Authorization: Bearer token_no_subscription | 200, subscription=null |
| 미인증 요청 | Authorization: 없음 | 401, E-2001 |

### 2.3 POST /api/v1/subscriptions

| 시나리오 | 입력 | 예상 결과 |
|----------|------|-----------|
| 구독 생성 성공 (정기 결제) | plan=basic, billing_key=valid | 201, subscription 생성 |
| 구독 생성 - 결제 실패 | plan=basic, billing_key=fail | 402, E-7002 |
| 이미 활성 구독 존재 | plan=basic (이미 구독 중) | 409, E-7004 |
| 유효하지 않은 플랜 | plan=invalid | 400, E-1001 |
| 빌링키 없음 | plan=basic, billing_key=null | 400, E-1003 |
| 미인증 요청 | Authorization: 없음 | 401, E-2001 |

### 2.4 PUT /api/v1/subscriptions

| 시나리오 | 입력 | 예상 결과 |
|----------|------|-----------|
| 업그레이드 성공 (basic → standard) | plan=standard | 200, proration_amount 반환 |
| 업그레이드 - 결제 실패 | plan=premium (잔액 부족) | 402, E-7002 |
| 다운그레이드 요청 (premium → basic) | plan=basic | 200, 다음 결제일 적용 안내 |
| 동일 플랜 변경 | plan=basic (현재 basic) | 400, E-7004 |
| 활성 구독 없음 | plan=standard (구독 없음) | 404, E-7003 |
| 미인증 요청 | Authorization: 없음 | 401, E-2001 |

### 2.5 DELETE /api/v1/subscriptions

| 시나리오 | 입력 | 예상 결과 |
|----------|------|-----------|
| 구독 해지 성공 | reason="사용 빈도 낮음" | 200, status=cancelled, access_until |
| 이미 해지된 구독 | - | 404, E-7003 |
| 무료 플랜 해지 | - | 200, 즉시 만료 |
| 미인증 요청 | Authorization: 없음 | 401, E-2001 |

### 2.6 POST /api/v1/subscriptions/billing-key

| 시나리오 | 입력 | 예상 결과 |
|----------|------|-----------|
| 빌링키 등록 성공 | auth_key=valid, customer_key=uuid | 200, billing_key + 카드 정보 |
| 이미 등록된 빌링키 존재 | auth_key=valid | 409, E-7008 |
| 인증 키 무효 | auth_key=invalid | 400, E-7007 |
| 미인증 요청 | Authorization: 없음 | 401, E-2001 |

### 2.7 GET /api/v1/subscriptions/history

| 시나리오 | 입력 | 예상 결과 |
|----------|------|-----------|
| 결제 내역 조회 | Authorization: Bearer valid_token | 200, payments 목록 |
| 페이지네이션 | limit=5, cursor=valid | 200, 5개 + next_cursor |
| 결제 내역 없음 | - | 200, payments=[] |
| 미인증 요청 | Authorization: 없음 | 401, E-2001 |

### 2.8 POST /api/v1/webhooks/toss

| 시나리오 | 입력 | 예상 결과 |
|----------|------|-----------|
| 결제 성공 웹훅 | eventType=PAYMENT_STATUS_CHANGED, status=DONE | 200, subscription 연장 |
| 결제 실패 웹훅 | eventType=PAYMENT_STATUS_CHANGED, status=FAILED | 200, 재시도 스케줄링 |
| 서명 검증 실패 | X-Toss-Signature: invalid | 401 |
| 중복 웹훅 | 이미 처리된 payment_id | 200, 무시 |
| 잘못된 이벤트 타입 | eventType=UNKNOWN | 200, 무시 |

---

## 3. 플랜별 권한 테스트

### 3.1 채팅 기능 (Q&A)

| 플랜 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| Starter | 10회 미만 사용 | usage=5, limit=10 | 200, 응답 반환 |
| Starter | 10회 도달 | usage=10, limit=10 | 429, E-2006 (업그레이드 유도) |
| Basic | 무제한 사용 | usage=100, limit=null | 200, 응답 반환 |
| Standard | 무제한 사용 | usage=1000, limit=null | 200, 응답 반환 |
| Premium | 무제한 사용 | usage=10000, limit=null | 200, 응답 반환 |
| 만료된 플랜 | 만료 후 접근 | plan_expires_at < now | 403, E-7001 |

### 3.2 계약서 생성

| 플랜 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| Starter | 2회 미만 생성 | usage=1, limit=2 | 200, 계약서 생성 |
| Starter | 2회 도달 | usage=2, limit=2 | 429, E-2006 |
| Basic | 무제한 생성 | usage=100, limit=null | 200, 계약서 생성 |
| Standard | 무제한 생성 | usage=100, limit=null | 200, 계약서 생성 |
| Premium | 무제한 생성 | usage=100, limit=null | 200, 계약서 생성 |

### 3.3 급여 계산

| 플랜 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| Starter | 급여 계산 접근 | feature=payroll | 403, E-7001 |
| Basic | 급여 계산 접근 | feature=payroll | 200, 계산 결과 |
| Standard | 급여 계산 접근 | feature=payroll | 200, 계산 결과 |
| Premium | 급여 계산 접근 | feature=payroll | 200, 계산 결과 |

### 3.4 급여명세서 발송

| 플랜 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| Starter | 발송 시도 | feature=payslip_send | 403, E-7001 |
| Basic | 10회 미만 발송 | usage=5, limit=10 | 200, 발송 성공 |
| Basic | 10회 도달 | usage=10, limit=10 | 429, E-2006 |
| Standard | 100회 미만 발송 | usage=50, limit=100 | 200, 발송 성공 |
| Standard | 100회 도달 | usage=100, limit=100 | 429, E-2006 |
| Premium | 무제한 발송 | usage=500, limit=null | 200, 발송 성공 |

### 3.5 노무사 상담

| 플랜 | 시나리오 | 입력 | 예상 결과 |
|------|----------|------|-----------|
| Starter | 노무사 상담 접근 | feature=attorney_consult | 403, E-7001 |
| Basic | 노무사 상담 접근 | feature=attorney_consult | 403, E-7001 |
| Standard | 노무사 상담 접근 | feature=attorney_consult | 403, E-7001 |
| Premium | 1회 무료 상담 | usage=0, limit=1 | 200, 상담 예약 |
| Premium | 1회 사용 후 | usage=1, limit=1 | 402, 유료 안내 |

---

## 4. 경계 조건 / 에러 케이스

### 4.1 결제 관련

| 케이스 | 시나리오 | 예상 결과 |
|--------|----------|-----------|
| 잔액 부족 | 카드 잔액 부족으로 결제 실패 | E-7002, 재시도 안내 |
| 카드 정지 | 카드 분실/정지로 결제 실패 | E-7002, 카드사 문의 안내 |
| 한도 초과 | 카드 사용 한도 초과 | E-7002, 한도 확인 안내 |
| 통신 오류 | 토스페이먼츠 API 타임아웃 | E-8001, 잠시 후 재시도 안내 |
| 중복 결제 | 동일 order_id 재요청 | 멱등성 유지, 기존 결과 반환 |

### 4.2 구독 상태 관련

| 케이스 | 시나리오 | 예상 결과 |
|--------|----------|-----------|
| 구독 만료 | expires_at 도달 | status=expired, 서비스 접근 차단 |
| 결제 실패 3회 연속 | retry_count >= 3 | status=paused, 알림 발송 |
| 빌링키 만료 | 토스페이먼츠에서 빌링키 무효화 | 알림 발송, 재등록 유도 |
| 동시 구독 시도 | 여러 디바이스에서 동시 구독 | 하나만 성공, 나머지 E-7004 |

### 4.3 웹훅 관련

| 케이스 | 시나리오 | 예상 결과 |
|--------|----------|-----------|
| 웹훅 지연 | 결제 후 웹훅 5분 지연 수신 | 정상 처리 (멱등성) |
| 웹훅 순서 뒤바뀜 | 실패 후 성공 웹훅 수신 | 최종 상태(success)로 업데이트 |
| 웹훅 본문 손상 | JSON 파싱 실패 | 400, 로깅 후 무시 |
| 재전송 웹훅 | 토스페이먼츠 재전송 | 멱등성으로 중복 처리 방지 |

### 4.4 프로레이션 관련

| 케이스 | 시나리오 | 예상 결과 |
|--------|----------|-----------|
| 월 말 업그레이드 | remaining_days=1 | proration_amount 최소화 |
| 월 초 업그레이드 | remaining_days=30 | proration_amount 최대화 |
| 플랜 가격 동일 | basic → basic (동일 가격) | proration_amount=0 |
| 다운그레이드 즉시 취소 | premium → basic 요청 후 취소 | 원상 복구 |

---

## 5. 보안 테스트

### 5.1 빌링키 보안

| 케이스 | 시나리오 | 예상 결과 |
|--------|----------|-----------|
| 빌링키 로그 확인 | 로그에 billing_key 노출 여부 | 마스킹 처리 (tb_***) |
| 빌링키 API 응답 | 응답에 전체 billing_key 포함 여부 | 마스킹 처리 |
| 타인 빌링키 사용 | 다른 사용자의 billing_key로 결제 시도 | 403, 권한 없음 |

### 5.2 웹훅 보안

| 케이스 | 시나리오 | 예상 결과 |
|--------|----------|-----------|
| 서명 없는 웹훅 | X-Toss-Signature 헤더 없음 | 401, 거부 |
| 잘못된 서명 | 서명 불일치 | 401, 거부 |
| 리플레이 공격 | 과거 웹훅 재전송 | 멱등성으로 무시 |
| 비화이트리스트 IP | 허용되지 않은 IP에서 웹훅 | 403, 거부 |

### 5.3 결제 보안

| 케이스 | 시나리오 | 예상 결과 |
|--------|----------|-----------|
| 금액 변조 | 클라이언트에서 amount 변조 | DB 플랜 가격 사용, 무시 |
| order_id 예측 | 순차적 order_id 추측 공격 | UUID 사용으로 불가능 |
| 타인 구독 조회 | 다른 사용자 구독 정보 조회 | 403, 권한 없음 |

---

## 6. 성능 테스트

### 6.1 응답 시간 기준

| API | 목표 응답 시간 |
|-----|----------------|
| GET /subscriptions/plans | < 100ms |
| GET /subscriptions/me | < 200ms |
| POST /subscriptions | < 3000ms (결제 포함) |
| PUT /subscriptions | < 3000ms (결제 포함) |
| DELETE /subscriptions | < 500ms |
| POST /subscriptions/billing-key | < 2000ms |
| GET /subscriptions/history | < 500ms |
| POST /webhooks/toss | < 1000ms |

### 6.2 부하 테스트

| 시나리오 | 조건 | 목표 |
|----------|------|------|
| 동시 구독 생성 | 100 RPS | 에러율 < 1% |
| 웹훅 집중 수신 | 1000개/분 | 모두 5초 내 처리 |
| 플랜 확인 캐시 적중 | 1000 RPS | 캐시 적중률 > 95% |

---

## 7. E2E 시나리오

### 7.1 정상 구독 플로우

```
1. 사용자 로그인
2. GET /subscriptions/plans (플랜 목록 확인)
3. POST /subscriptions/billing-key (빌링키 등록)
4. POST /subscriptions (basic 플랜 구독)
5. GET /subscriptions/me (구독 정보 확인)
6. 채팅 5회 사용
7. GET /subscriptions/me (사용량 확인)
8. PUT /subscriptions (standard로 업그레이드)
9. 급여명세서 50회 발송
10. DELETE /subscriptions (구독 해지)
11. GET /subscriptions/me (만료일까지 접근 가능 확인)
```

### 7.2 결제 실패 복구 플로우

```
1. 사용자 로그인
2. POST /subscriptions (잔액 부족으로 결제 실패)
3. E-7002 에러 응답
4. 사용자 카드 충전
5. POST /subscriptions (재시도 - 성공)
6. 구독 활성화 확인
```

### 7.3 플랜 제한 초과 플로우

```
1. Starter 플랜 사용자 로그인
2. 채팅 10회 사용
3. 11회째 채팅 시도
4. E-2006 에러 (사용 한도 초과)
5. 업그레이드 CTA 표시
6. Basic 플랜으로 업그레이드
7. 채팅 정상 사용 가능
```

---

## 8. 테스트 환경

### 8.1 토스페이먼츠 Sandbox

| 항목 | 값 |
|------|-----|
| 환경 | Sandbox |
| 테스트 카드 | 4000-0000-0000-0001 (성공) |
| 테스트 카드 (실패) | 4000-0000-0000-0002 (잔액부족) |
| 웹훅 URL | https://api-staging.nomoodoc.com/api/v1/webhooks/toss |

### 8.2 목업 모드 (TOSS_API_KEY 미설정 시)

- 모든 결제: 자동 성공
- 빌링키: fake_billing_key 반환
- 웹훅: 수동 트리거 불가 (실제 연동 테스트는 sandbox 사용)

---

## 9. 테스트 체크리스트

### 9.1 기능 테스트

- [ ] 플랜 목록 조회
- [ ] 내 구독 정보 조회
- [ ] 구독 생성 (정기 결제 성공)
- [ ] 구독 생성 (결제 실패)
- [ ] 플랜 업그레이드
- [ ] 플랜 다운그레이드
- [ ] 구독 해지
- [ ] 빌링키 등록
- [ ] 결제 내역 조회
- [ ] 웹훅 처리 (성공)
- [ ] 웹훅 처리 (실패)

### 9.2 플랜 권한 테스트

- [ ] Starter: 채팅 10회 제한
- [ ] Starter: 계약서 2건 제한
- [ ] Starter: 급여 계산 불가
- [ ] Starter: 명세서 발송 불가
- [ ] Basic: 채팅 무제한
- [ ] Basic: 계약서 무제한
- [ ] Basic: 급여 계산 가능
- [ ] Basic: 명세서 발송 10건 제한
- [ ] Standard: 명세서 발송 100건 제한
- [ ] Premium: 모든 기능 무제한
- [ ] Premium: 노무사 상담 1회 무료

### 9.3 보안 테스트

- [ ] 웹훅 서명 검증
- [ ] 빌링키 마스킹
- [ ] 타인 구독 접근 차단
- [ ] 금액 변조 방지

### 9.4 성능 테스트

- [ ] API 응답 시간 기준 충족
- [ ] 동시 요청 처리
- [ ] 캐시 적중률

---

## 10. 변경 이력

| 날짜 | 변경 내용 | 이유 |
|------|----------|------|
| 2026-03-12 | 초기 작성 | F-11 구독 및 결제 테스트 명세 |
