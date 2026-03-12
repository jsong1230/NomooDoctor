# F-11 구독 및 결제 — 기술 설계서

## 1. 참조
- 인수조건: docs/project/features.md #F-11
- 시스템 설계: docs/system/system-design.md
- ERD: docs/system/erd.md
- API 컨벤션: docs/system/api-conventions.md

---

## 2. 아키텍처 결정

### 결정 1: 정기 결제 방식
- **선택지**: A) 토스페이먼츠 Billing Key 방식 / B) 매월 결제 페이지 리다이렉트
- **결정**: A) Billing Key 방식
- **근거**: 사용자 경험 향상 (자동 결제), 이탈률 감소, PCI-DSS 준수 간소화

### 결정 2: 플랜 변경 시 프로레이션
- **선택지**: A) 즉시 변경 + 비례 계산 / B) 다음 결제일 적용
- **결정**: A) 즉시 변경 + 비례 계산
- **근거**: 사용자가 즉시 혜택을 받을 수 있어 만족도 향상, 업그레이드 유도 효과

### 결정 3: 빌링키 저장 방식
- **선택지**: A) DB 암호화 저장 / B) 토스페이먼츠에만 저장 (customerKey 매핑)
- **결정**: B) 토스페이먼츠에만 저장
- **근거**: 보안 책임 분산, PCI-DSS 범위 축소, 토스페이먼츠 권장 방식

### 결정 4: 플랜 상태 관리
- **선택지**: A) users 테이블 직접 관리 / B) subscriptions 테이블 이력 관리 + users 동기화
- **결정**: B) subscriptions 이력 관리 + users 동기화
- **근거**: 결제 이력 추적, 감사 로그, 환불 처리 용이

---

## 3. 데이터 모델

### 3.1 subscriptions 테이블 (기존 ERD 준수)

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 구독 고유 식별자 |
| user_id | UUID | FK(users.id), NOT NULL | 사용자 ID |
| plan | VARCHAR(20) | NOT NULL, CHECK | 플랜 유형 (free/basic/standard/premium) |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'active', CHECK | 상태 (active/cancelled/expired/paused) |
| starts_at | TIMESTAMPTZ | NOT NULL | 구독 시작일시 |
| expires_at | TIMESTAMPTZ | | 구독 만료일시 (NULL = 무제한) |
| cancelled_at | TIMESTAMPTZ | | 구독 취소일시 |
| toss_customer_key | VARCHAR(100) | | 토스페이먼츠 고객 식별자 |
| toss_billing_key | VARCHAR(200) | | 토스페이먼츠 빌링키 (참조용) |
| toss_order_id | VARCHAR(100) | | 최근 주문 ID |
| monthly_amount | NUMERIC(10,0) | NOT NULL | 월 결제 금액 (원) |
| created_at | TIMESTAMPTZ | NOT NULL | 생성일시 |
| updated_at | TIMESTAMPTZ | NOT NULL | 수정일시 |

**CHECK 제약조건**:
```sql
CHECK (plan IN ('free', 'basic', 'standard', 'premium'))
CHECK (status IN ('active', 'cancelled', 'expired', 'paused'))
```

### 3.2 payment_history 테이블 (신규 추가)

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 결제 이력 고유 식별자 |
| subscription_id | UUID | FK(subscriptions.id), NOT NULL | 구독 ID |
| user_id | UUID | FK(users.id), NOT NULL | 사용자 ID |
| toss_payment_id | VARCHAR(100) | UK | 토스페이먼츠 결제 ID |
| toss_order_id | VARCHAR(100) | NOT NULL | 주문 ID |
| amount | NUMERIC(10,0) | NOT NULL | 결제 금액 (원) |
| status | VARCHAR(20) | NOT NULL | 결제 상태 (pending/success/failed/refunded) |
| payment_method | VARCHAR(50) | | 결제 수단 (card/transfer) |
| paid_at | TIMESTAMPTZ | | 결제 완료일시 |
| failed_at | TIMESTAMPTZ | | 결제 실패일시 |
| failure_reason | TEXT | | 실패 사유 |
| refund_amount | NUMERIC(10,0) | | 환불 금액 |
| refunded_at | TIMESTAMPTZ | | 환불 일시 |
| metadata | JSONB | | 추가 메타데이터 |
| created_at | TIMESTAMPTZ | NOT NULL | 생성일시 |

### 3.3 plan_usage 테이블 (신규 추가 - 플랜별 사용량 추적)

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 사용량 ID |
| user_id | UUID | FK(users.id), NOT NULL | 사용자 ID |
| usage_month | DATE | NOT NULL | 사용 월 (YYYY-MM-01) |
| chat_count | INTEGER | NOT NULL, DEFAULT 0 | 채팅 횟수 |
| contract_count | INTEGER | NOT NULL, DEFAULT 0 | 계약서 생성 횟수 |
| payslip_send_count | INTEGER | NOT NULL, DEFAULT 0 | 급여명세서 발송 횟수 |
| attorney_consult_count | INTEGER | NOT NULL, DEFAULT 0 | 노무사 상담 횟수 |
| created_at | TIMESTAMPTZ | NOT NULL | 생성일시 |
| updated_at | TIMESTAMPTZ | NOT NULL | 수정일시 |

**인덱스**:
```sql
CREATE UNIQUE INDEX idx_plan_usage_user_month ON plan_usage(user_id, usage_month);
```

### 3.4 users 테이블 변경사항

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| plan | VARCHAR(20) | NOT NULL, DEFAULT 'free' | 현재 플랜 (subscriptions와 동기화) |
| plan_expires_at | TIMESTAMPTZ | | 플랜 만료일시 |

---

## 4. API 설계

### 4.1 GET /api/v1/subscriptions/plans
- **목적**: 플랜 목록 및 가격 정보 조회
- **인증**: 불필요
- **Response**:
```json
{
  "success": true,
  "data": {
    "plans": [
      {
        "id": "starter",
        "name": "스타터",
        "price": 0,
        "features": {
          "chat_limit": 10,
          "contract_limit": 2,
          "payroll": false,
          "payslip_send_limit": 0,
          "attorney_consult": false
        }
      },
      {
        "id": "basic",
        "name": "베이직",
        "price": 9900,
        "features": {
          "chat_limit": null,
          "contract_limit": null,
          "payroll": true,
          "payslip_send_limit": 10,
          "attorney_consult": false
        }
      },
      {
        "id": "standard",
        "name": "스탠다드",
        "price": 29000,
        "features": {
          "chat_limit": null,
          "contract_limit": null,
          "payroll": true,
          "payslip_send_limit": 100,
          "attorney_consult": false
        }
      },
      {
        "id": "premium",
        "name": "프리미엄",
        "price": 49000,
        "features": {
          "chat_limit": null,
          "contract_limit": null,
          "payroll": true,
          "payslip_send_limit": null,
          "attorney_consult": true,
          "attorney_consult_limit": 1
        }
      }
    ]
  }
}
```

### 4.2 GET /api/v1/subscriptions/me
- **목적**: 현재 사용자 구독 정보 조회
- **인증**: 필요
- **Response**:
```json
{
  "success": true,
  "data": {
    "subscription": {
      "id": "uuid",
      "plan": "standard",
      "status": "active",
      "starts_at": "2026-03-01T00:00:00Z",
      "expires_at": "2026-04-01T00:00:00Z",
      "monthly_amount": 29000,
      "has_billing_key": true,
      "cancelled_at": null
    },
    "usage": {
      "month": "2026-03",
      "chat_count": 5,
      "chat_limit": null,
      "contract_count": 3,
      "contract_limit": null,
      "payslip_send_count": 12,
      "payslip_send_limit": 100
    }
  }
}
```

### 4.3 POST /api/v1/subscriptions
- **목적**: 새 구독 시작 (플랜 선택 → 빌링키 등록 → 결제)
- **인증**: 필요
- **Request Body**:
```json
{
  "plan": "standard",
  "billing_key": "tb_xxx",  // 이미 발급받은 빌링키
  "success_url": "https://app.nomoodoc.com/subscription/success",
  "fail_url": "https://app.nomoodoc.com/subscription/fail"
}
```
- **Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "subscription_id": "uuid",
    "toss_order_id": "order_xxx",
    "status": "active",
    "starts_at": "2026-03-12T10:30:00Z",
    "expires_at": "2026-04-12T10:30:00Z"
  }
}
```
- **에러 케이스**:

| 코드 | 상황 | HTTP |
|------|------|------|
| E-7002 | 결제 실패 | 402 |
| E-7004 | 이미 활성 구독 존재 | 409 |
| E-7005 | 유효하지 않은 빌링키 | 400 |

### 4.4 PUT /api/v1/subscriptions
- **목적**: 플랜 변경 (업그레이드/다운그레이드)
- **인증**: 필요
- **Request Body**:
```json
{
  "plan": "premium"
}
```
- **Response**:
```json
{
  "success": true,
  "data": {
    "subscription_id": "uuid",
    "old_plan": "standard",
    "new_plan": "premium",
    "proration_amount": 20000,
    "proration_description": "잔여 20일에 대한 비례 계산",
    "next_billing_amount": 49000,
    "effective_at": "2026-03-12T10:30:00Z"
  }
}
```
- **에러 케이스**:

| 코드 | 상황 | HTTP |
|------|------|------|
| E-7003 | 활성 구독 없음 | 404 |
| E-7002 | 결제 실패 (업그레이드 시) | 402 |
| E-7006 | 다운그레이드는 다음 결제일 적용 | 400 |

### 4.5 DELETE /api/v1/subscriptions
- **목적**: 구독 해지 (만료일까지 유지)
- **인증**: 필요
- **Request Body**:
```json
{
  "reason": "사용 빈도 낮음",
  "feedback": "가격이 비싸요"
}
```
- **Response**:
```json
{
  "success": true,
  "data": {
    "subscription_id": "uuid",
    "status": "cancelled",
    "cancelled_at": "2026-03-12T10:30:00Z",
    "access_until": "2026-04-01T00:00:00Z",
    "message": "2026년 4월 1일까지 서비스를 이용하실 수 있습니다."
  }
}
```

### 4.6 POST /api/v1/subscriptions/billing-key
- **목적**: 빌링키 발급/등록
- **인증**: 필요
- **Request Body**:
```json
{
  "auth_key": "auth_xxx",  // 토스페이먼츠 인증 완료 후 받은 키
  "customer_key": "user_uuid"
}
```
- **Response**:
```json
{
  "success": true,
  "data": {
    "billing_key": "tb_xxx",
    "card_company": "신한카드",
    "card_number": "12345678****123*",
    "card_type": "신용",
    "registered_at": "2026-03-12T10:30:00Z"
  }
}
```
- **에러 케이스**:

| 코드 | 상황 | HTTP |
|------|------|------|
| E-7007 | 빌링키 발급 실패 | 400 |
| E-7008 | 이미 등록된 빌링키 존재 | 409 |

### 4.7 GET /api/v1/subscriptions/history
- **목적**: 결제 내역 조회
- **인증**: 필요
- **Query Parameters**:
  - `limit`: 페이지 크기 (기본 20, 최대 100)
  - `cursor`: 페이지네이션 커서
- **Response**:
```json
{
  "success": true,
  "data": {
    "payments": [
      {
        "id": "uuid",
        "toss_payment_id": "pay_xxx",
        "amount": 29000,
        "status": "success",
        "payment_method": "card",
        "paid_at": "2026-03-01T00:00:00Z"
      }
    ],
    "pagination": {
      "cursor": null,
      "has_next": false,
      "limit": 20,
      "total_count": 3
    }
  }
}
```

### 4.8 POST /api/v1/webhooks/toss
- **목적**: 토스페이먼츠 웹훅 수신
- **인증**: 서명 검증 (X-Toss-Signature 헤더)
- **Request Body**:
```json
{
  "eventType": "PAYMENT_STATUS_CHANGED",
  "data": {
    "paymentId": "pay_xxx",
    "orderId": "order_xxx",
    "status": "DONE",
    "method": "card",
    "totalAmount": 29000
  }
}
```
- **Response**: 200 OK (본문 없음)
- **처리 이벤트**:
  - `PAYMENT_STATUS_CHANGED`: 결제 상태 변경 (성공/실패)
  - `BILLING_KEY_STATUS_CHANGED`: 빌링키 상태 변경 (만료/정지)

---

## 5. 토스페이먼츠 연동

### 5.1 빌링키 발급 흐름

```
┌─────────┐      ┌────────────┐      ┌────────────┐      ┌─────────┐
│ Client  │      │   Toss     │      │  Backend   │      │   DB    │
└────┬────┘      └─────┬──────┘      └─────┬──────┘      └────┬────┘
     │                 │                   │                  │
     │ 1. 결제 위젯 렌더링                 │                  │
     │─────────────────────────────────────>                  │
     │                 │                   │                  │
     │ 2. 카드 정보 입력                   │                  │
     │─────────────────────────────────────>                  │
     │                 │                   │                  │
     │ 3. 인증 요청    │                   │                  │
     │────────────────>│                   │                  │
     │                 │                   │                  │
     │ 4. authKey 반환 │                   │                  │
     │<────────────────│                   │                  │
     │                 │                   │                  │
     │ 5. POST /subscriptions/billing-key  │                  │
     │────────────────────────────────────>│                  │
     │                 │                   │                  │
     │                 │ 6. 빌링키 발급 API │                  │
     │                 │<──────────────────│                  │
     │                 │                   │                  │
     │                 │ 7. billingKey 반환│                  │
     │                 │───────────────────>                  │
     │                 │                   │                  │
     │                 │                   │ 8. customerKey 저장
     │                 │                   │─────────────────>│
     │                 │                   │                  │
     │ 9. 등록 완료 응답                   │                  │
     │<────────────────────────────────────│                  │
```

### 5.2 정기 결제 흐름

```
┌────────────┐      ┌────────────┐      ┌─────────┐
│  Scheduler │      │   Toss     │      │   DB    │
└─────┬──────┘      └─────┬──────┘      └────┬────┘
      │                   │                  │
      │ 1. 매일 00:00 만료 예정 구독 조회    │
      │─────────────────────────────────────>│
      │                   │                  │
      │ 2. 만료 대상 목록 반환               │
      │<─────────────────────────────────────│
      │                   │                  │
      │ 3. 빌링키로 자동결제 요청            │
      │──────────────────>│                  │
      │                   │                  │
      │ 4. 결제 결과 반환 │                  │
      │<──────────────────│                  │
      │                   │                  │
      │ 5. 성공: 구독 연장 / 실패: 재시도 등록│
      │─────────────────────────────────────>│
```

### 5.3 웹훅 서명 검증

```python
import hmac
import hashlib

def verify_toss_webhook(payload: bytes, signature: str, secret: str) -> bool:
    """
    토스페이먼츠 웹훅 서명 검증

    Args:
        payload: 요청 본문 (bytes)
        signature: X-Toss-Signature 헤더 값
        secret: 토스페이먼츠 웹훅 시크릿

    Returns:
        검증 성공 여부
    """
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
```

---

## 6. 서비스 레이어 설계

### 6.1 SubscriptionService

```python
class SubscriptionService:
    """구독 관련 비즈니스 로직"""

    async def get_plans(self) -> list[PlanInfo]:
        """플랜 목록 조회"""

    async def get_my_subscription(self, user: User) -> SubscriptionResponse:
        """내 구독 정보 조회"""

    async def create_subscription(
        self,
        user: User,
        plan: str,
        billing_key: str
    ) -> Subscription:
        """구독 생성 (결제 처리 포함)"""

    async def change_plan(
        self,
        user: User,
        new_plan: str
    ) -> PlanChangeResult:
        """플랜 변경 (프로레이션 계산)"""

    async def cancel_subscription(
        self,
        user: User,
        reason: str | None,
        feedback: str | None
    ) -> Subscription:
        """구독 해지"""

    async def process_expiry(self) -> int:
        """만료 구독 처리 (배치)"""

    def calculate_proration(
        self,
        current_plan: str,
        new_plan: str,
        remaining_days: int
    ) -> int:
        """프로레이션 금액 계산"""
```

### 6.2 PaymentService

```python
class PaymentService:
    """결제 처리 관련 로직"""

    async def register_billing_key(
        self,
        user: User,
        auth_key: str,
        customer_key: str
    ) -> BillingKeyInfo:
        """빌링키 등록"""

    async def charge_with_billing_key(
        self,
        billing_key: str,
        amount: int,
        order_id: str,
        customer_key: str
    ) -> PaymentResult:
        """빌링키로 결제"""

    async def process_webhook(
        self,
        event_type: str,
        data: dict
    ) -> None:
        """웹훅 처리"""

    async def get_payment_history(
        self,
        user: User,
        limit: int,
        cursor: str | None
    ) -> PaginatedPayments:
        """결제 내역 조회"""

    async def handle_failed_payment(
        self,
        subscription: Subscription,
        error: str
    ) -> None:
        """결제 실패 처리 (재시도 스케줄링)"""
```

### 6.3 PlanService

```python
class PlanService:
    """플랜별 권한 및 사용량 관리"""

    PLAN_LIMITS = {
        "free": {
            "chat_limit": 10,
            "contract_limit": 2,
            "payroll": False,
            "payslip_send_limit": 0,
            "attorney_consult": False,
        },
        "basic": {
            "chat_limit": None,  # 무제한
            "contract_limit": None,
            "payroll": True,
            "payslip_send_limit": 10,
            "attorney_consult": False,
        },
        "standard": {
            "chat_limit": None,
            "contract_limit": None,
            "payroll": True,
            "payslip_send_limit": 100,
            "attorney_consult": False,
        },
        "premium": {
            "chat_limit": None,
            "contract_limit": None,
            "payroll": True,
            "payslip_send_limit": None,
            "attorney_consult": True,
            "attorney_consult_limit": 1,
        },
    }

    async def check_feature_access(
        self,
        user: User,
        feature: str
    ) -> bool:
        """기능 접근 권한 확인"""

    async def check_usage_limit(
        self,
        user: User,
        usage_type: str
    ) -> UsageLimitResult:
        """사용량 제한 확인"""

    async def increment_usage(
        self,
        user: User,
        usage_type: str
    ) -> None:
        """사용량 증가"""

    async def get_current_usage(
        self,
        user: User
    ) -> UsageInfo:
        """현재 월 사용량 조회"""

    def get_plan_features(self, plan: str) -> dict:
        """플랜별 기능 반환"""
```

---

## 7. 미들웨어 설계

### 7.1 PlanAccessMiddleware

```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class PlanAccessMiddleware(BaseHTTPMiddleware):
    """플랜별 접근 제어 미들웨어"""

    # 경로별 필요 기능 매핑
    FEATURE_MAP = {
        "/api/v1/chat/sessions/*/messages": "chat",
        "/api/v1/contracts": "contract",
        "/api/v1/payroll/calculate": "payroll",
        "/api/v1/payslips/*/send": "payslip_send",
        "/api/v1/attorney-cases": "attorney_consult",
    }

    async def dispatch(self, request: Request, call_next):
        # 인증된 사용자 확인
        user = getattr(request.state, "user", None)
        if not user:
            return await call_next(request)

        # 경로별 기능 확인
        required_feature = self._get_required_feature(request.url.path)
        if not required_feature:
            return await call_next(request)

        # 플랜 접근 권한 확인
        plan_service = PlanService(request.state.db)
        has_access = await plan_service.check_feature_access(user, required_feature)

        if not has_access:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "E-7001",
                    "message": "이 기능을 사용하려면 플랜을 업그레이드해야 합니다."
                }
            )

        # 사용량 제한 확인
        usage_result = await plan_service.check_usage_limit(user, required_feature)
        if not usage_result.allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "code": "E-2006",
                    "message": f"월 사용 한도({usage_result.limit}회)를 초과했습니다."
                }
            )

        response = await call_next(request)

        # 사용량 증가 (성공 시)
        if response.status_code < 400:
            await plan_service.increment_usage(user, required_feature)

        return response
```

### 7.2 Rate Limiting 확장

기존 Rate Limiting에 플랜별 차등 적용 추가:

```python
PLAN_RATE_LIMITS = {
    "free": {
        "chat_per_hour": 10,
        "contract_per_hour": 2,
        "payslip_send_per_day": 0,
    },
    "basic": {
        "chat_per_hour": None,  # 무제한
        "contract_per_hour": None,
        "payslip_send_per_day": 10,
    },
    "standard": {
        "chat_per_hour": None,
        "contract_per_hour": None,
        "payslip_send_per_day": 100,
    },
    "premium": {
        "chat_per_hour": None,
        "contract_per_hour": None,
        "payslip_send_per_day": None,
    },
}
```

---

## 8. 보안 설계

### 8.1 빌링키 보안

| 항목 | 방식 |
|------|------|
| 저장 | 토스페이먼츠 서버에만 저장 (customerKey로 매핑) |
| 전송 | HTTPS만 허용 |
| 로깅 | 빌링키 로깅 금지 (마스킹 필수) |
| 폐기 | 구독 해지 시 customerKey 무효화 |

### 8.2 웹훅 보안

| 항목 | 방식 |
|------|------|
| 서명 검증 | HMAC-SHA256 서명 필수 |
| IP 화이트리스트 | 토스페이먼츠 IP만 허용 |
| 재시도 방지 | 이벤트 ID 중복 체크 |
| 타임아웃 | 5초 이내 응답 |

### 8.3 결제 보안

| 항목 | 방식 |
|------|------|
| 금액 검증 | 클라이언트 금액 신뢰 금지, DB 플랜 가격 사용 |
| 중복 결제 방지 | order_id 멱등성 키 사용 |
| 결제 타임아웃 | 30초 |
| 실패 재시도 | 1일/3일/7일 간격 최대 3회 |

---

## 9. 시퀀스 흐름

### 9.1 구독 생성

```
사용자 → Frontend → Backend API → SubscriptionService → PaymentService → Toss API
    │         │           │              │                  │               │
    │ 플랜 선택│           │              │                  │               │
    │────────>│           │              │                  │               │
    │         │ POST /subscriptions      │                  │               │
    │         │──────────>│              │                  │               │
    │         │           │ create()     │                  │               │
    │         │           │─────────────>│                  │               │
    │         │           │              │ charge()         │               │
    │         │           │              │─────────────────>│               │
    │         │           │              │                  │ 결제 요청     │
    │         │           │              │                  │──────────────>│
    │         │           │              │                  │ 결제 결과     │
    │         │           │              │                  │<──────────────│
    │         │           │              │ 결과 반환        │               │
    │         │           │              │<─────────────────│               │
    │         │           │ DB 저장      │                  │               │
    │         │           │<─────────────│                  │               │
    │         │           │              │                  │               │
    │         │           │ user.plan 업데이트              │               │
    │         │           │─────────────────────────────────────────────────>│
    │         │ 응답      │              │                  │               │
    │         │<──────────│              │                  │               │
    │ 구독 완료│           │              │                  │               │
    │<────────│           │              │                  │               │
```

### 9.2 웹훅 처리

```
Toss → Backend API → PaymentService → SubscriptionService → DB
  │         │              │                  │              │
  │ 웹훅 전송│              │                  │              │
  │────────>│              │                  │              │
  │         │ 서명 검증    │                  │              │
  │         │──────────────────────────────────────────────>│
  │         │              │ process_webhook()│              │
  │         │─────────────>│                  │              │
  │         │              │ 상태 업데이트    │              │
  │         │              │─────────────────>│              │
  │         │              │                  │ DB 업데이트  │
  │         │              │                  │─────────────>│
  │ 200 OK  │              │                  │              │
  │<────────│              │                  │              │
```

---

## 10. 영향 범위

### 10.1 수정 필요 파일

| 파일 | 변경 내용 |
|------|----------|
| `backend/app/db/models/subscription.py` | toss_customer_key 컬럼 추가 |
| `backend/app/db/models/user.py` | plan_expires_at 동기화 로직 |
| `backend/app/core/config.py` | 토스페이먼츠 설정 추가 |
| `backend/app/core/exceptions.py` | 결제 관련 에러 추가 |
| `backend/app/core/rate_limit.py` | 플랜별 차등 적용 |
| `backend/app/api/v1/router.py` | subscriptions 라우터 추가 |
| `backend/app/core/dependencies.py` | PlanService 의존성 추가 |

### 10.2 신규 생성 파일

| 파일 | 설명 |
|------|------|
| `backend/app/db/models/payment_history.py` | 결제 이력 모델 |
| `backend/app/db/models/plan_usage.py` | 사용량 추적 모델 |
| `backend/app/repositories/subscription_repo.py` | 구독 Repository |
| `backend/app/repositories/payment_repo.py` | 결제 Repository |
| `backend/app/repositories/plan_usage_repo.py` | 사용량 Repository |
| `backend/app/services/subscription_service.py` | 구독 Service |
| `backend/app/services/payment_service.py` | 결제 Service |
| `backend/app/services/plan_service.py` | 플랜 Service |
| `backend/app/external/toss_client.py` | 토스페이먼츠 API 클라이언트 |
| `backend/app/api/v1/subscriptions.py` | 구독 API 라우터 |
| `backend/app/api/v1/webhooks.py` | 웹훅 API 라우터 |
| `backend/app/middleware/plan_access.py` | 플랜 접근 미들웨어 |
| `backend/app/schemas/subscription.py` | 구독 스키마 |
| `backend/app/schemas/payment.py` | 결제 스키마 |
| `backend/app/tasks/subscription_tasks.py` | 구독 배치 태스크 |

### 10.3 마이그레이션

```bash
# payment_history 테이블 생성
alembic revision -m "add_payment_history_table"

# plan_usage 테이블 생성
alembic revision -m "add_plan_usage_table"

# subscriptions 테이블 수정 (toss_customer_key 추가)
alembic revision -m "add_customer_key_to_subscriptions"
```

---

## 11. 성능 설계

### 11.1 인덱스 계획

```sql
-- subscriptions
CREATE INDEX idx_subscriptions_user_status ON subscriptions(user_id, status);
CREATE INDEX idx_subscriptions_expires_active ON subscriptions(expires_at) WHERE status = 'active';

-- payment_history
CREATE INDEX idx_payment_history_user ON payment_history(user_id, created_at DESC);
CREATE INDEX idx_payment_history_subscription ON payment_history(subscription_id);
CREATE INDEX idx_payment_history_toss_order ON payment_history(toss_order_id);

-- plan_usage
CREATE UNIQUE INDEX idx_plan_usage_user_month ON plan_usage(user_id, usage_month);
```

### 11.2 캐싱 전략

| 데이터 | 캐시 키 | TTL | 비고 |
|--------|---------|-----|------|
| 플랜 목록 | `plans:all` | 1시간 | 자주 변하지 않음 |
| 사용자 플랜 | `user:{id}:plan` | 5분 | JWT 갱신 시 캐시 무효화 |
| 사용량 | `usage:{user_id}:{month}` | 1분 | 사용 시마다 갱신 |

---

## 12. 변경 이력

| 날짜 | 변경 내용 | 이유 |
|------|----------|------|
| 2026-03-12 | 초기 작성 | F-11 구독 및 결제 기능 설계 |
