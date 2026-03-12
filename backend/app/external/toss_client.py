# TossPayments API 클라이언트
import httpx
from typing import Optional
from datetime import datetime, timezone
from app.core.config import settings
from app.core.exceptions import AppError


class TossClient:
    """토스페이먼츠 API 클라이언트"""

    def __init__(self):
        self.base_url = "https://api.tosspayments.com/v1"
        self.secret_key = settings.TOSS_SECRET_KEY
        self.client_key = settings.TOSS_CLIENT_KEY
        self._http_client: Optional[httpx.AsyncClient] = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """HTTP 클라이언트 (lazy initialization)"""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient()
        return self._http_client

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._http_client:
            await self._http_client.aclose()

    def _get_headers(self) -> dict:
        """요청 헤더 생성"""
        return {
            "Authorization": f"SECRET_KEY {self.secret_key}",
            "Content-Type": "application/json",
        }

    async def issue_billing_key(
        self,
        auth_key: str,
        customer_key: str
    ) -> dict:
        """
        빌링키 발급

        Args:
            auth_key: 토스페이먼츠 인증 완료 후 받은 authKey
            customer_key: 고객 식별자 (사용자 UUID)

        Returns:
            빌링키 정보
        """
        if not self.secret_key or not self.client_key:
            # Mock 모드: 테스트용 빌링키 반환
            return {
                "billingKey": f"tb_test_{customer_key[:8]}",
                "cardType": "신용",
                "cardCompany": "신한카드",
                "cardNumber": "12345678****1234"
            }

        try:
            response = await self.http_client.post(
                f"{self.base_url}/billing-keys/resolve",
                headers=self._get_headers(),
                json={
                    "authKey": auth_key,
                    "customerKey": customer_key
                },
                timeout=30.0
            )

            if response.status_code == 401:
                raise AppError("E-7007", "인증에 실패했습니다.")
            elif response.status_code == 404:
                raise AppError("E-7007", "인증에 실패했습니다.")

            data = response.json()

            return {
                "billingKey": data["billingKey"],
                "cardType": data.get("cardType", ""),
                "cardCompany": data.get("cardCompany", ""),
                "cardNumber": self._mask_card_number(data.get("cardNumber", ""))
            }

        except httpx.TimeoutException:
            raise AppError("E-8001", "토스페이먼츠 API 연결 시간초과")
        except httpx.HTTPStatusError as e:
            error_data = e.response.json() if e.response.text else {}
            raise AppError("E-7007", error_data.get("message", "빌링키 발급에 실패했습니다."))
        except Exception as e:
            raise AppError("E-8001", f"빌링키 발급 실패: {str(e)}")

    async def charge(
        self,
        billing_key: str,
        amount: int,
        order_id: str,
        customer_key: str
    ) -> dict:
        """
        빌링키로 결제 요청

        Args:
            billing_key: 빌링키
            amount: 결제 금액
            order_id: 주문 ID
            customer_key: 고객 식별자

        Returns:
            결제 결과
        """
        if not self.secret_key or not self.client_key:
            # Mock 모드: 결제 성공 반환
            return {
                "paymentId": f"pay_{order_id}",
                "status": "DONE",
                "totalAmount": amount,
                "paidAt": datetime.now(timezone.utc).isoformat()
            }

        try:
            response = await self.http_client.post(
                f"{self.base_url}/payments/billing",
                headers=self._get_headers(),
                json={
                    "billingKey": billing_key,
                    "amount": amount,
                    "orderId": order_id,
                    "orderName": "구독 결제",
                    "customerKey": customer_key,
                    "successUrl": "https://app.nomoodoc.com/subscription/success",
                    "failUrl": "https://app.nomoodoc.com/subscription/fail"
                },
                timeout=30.0
            )

            data = response.json()

            if response.status_code == 401:
                raise AppError("E-7002", "결제에 실패했습니다.")
            elif response.status_code == 400:
                error_data = response.json()
                if "INSUFFICIENT_FUNDS" in error_data.get("message", ""):
                    raise AppError("E-7002", "잔액이 부족합니다.", details=[
                        {"field": "amount", "message": error_data.get("message", "잔액 부족")}
                    ])
                raise AppError("E-7002", error_data.get("message", "결제에 실패했습니다."))
            elif response.status_code == 402:
                error_data = response.json()
                raise AppError("E-7002", error_data.get("message", "결제에 실패했습니다."))

            return {
                "paymentId": data["paymentId"],
                "status": "DONE" if data.get("status") == "DONE" else "FAILED",
                "totalAmount": data.get("totalAmount", amount),
                "paidAt": data.get("paidAt", datetime.now(timezone.utc).isoformat()),
                "failure": data.get("failure")
            }

        except httpx.TimeoutException:
            raise AppError("E-8001", "토스페이먼츠 API 연결 시간초과")
        except httpx.HTTPStatusError as e:
            error_data = e.response.json() if e.response.text else {}
            raise AppError("E-7002", error_data.get("message", "결제에 실패했습니다."))
        except Exception as e:
            raise AppError("E-8001", f"결제에 실패했습니다: {str(e)}")

    async def get_payment(self, payment_id: str) -> dict:
        """
        결제 정보 조회

        Args:
            payment_id: 결제 ID

        Returns:
            결제 상세 정보
        """
        if not self.secret_key or not self.client_key:
            # Mock 모드: 결제 상세 반환
            return {
                "paymentId": payment_id,
                "status": "DONE",
                "totalAmount": 9900,
                "method": "card",
                "paidAt": datetime.now(timezone.utc).isoformat()
            }

        try:
            response = await self.http_client.get(
                f"{self.base_url}/payments/{payment_id}",
                headers=self._get_headers(),
                timeout=30.0
            )

            if response.status_code == 404:
                raise AppError("E-3002", "결제 정보를 찾을 수 없습니다.")

            data = response.json()

            return {
                "paymentId": data["paymentId"],
                "status": data.get("status"),
                "totalAmount": data.get("totalAmount"),
                "method": data.get("method"),
                "paidAt": data.get("paidAt"),
                "failure": data.get("failure")
            }

        except httpx.TimeoutException:
            raise AppError("E-8001", "토스페이먼츠 API 연결 시간초과")
        except httpx.HTTPStatusError as e:
            error_data = e.response.json() if e.response.text else {}
            raise AppError("E-3002", error_data.get("message", "결제 정보 조회 실패"))
        except Exception as e:
            raise AppError("E-8001", f"결제 정보 조회 실패: {str(e)}")

    def _mask_card_number(self, card_number: str) -> str:
        """카드 번호 마스킹"""
        if not card_number or len(card_number) < 16:
            return "****"
        return f"{card_number[:4]}****{card_number[-4:]}"
