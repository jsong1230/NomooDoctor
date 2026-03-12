# 모두싸인 API 클라이언트
import httpx
import uuid
from typing import Optional
from datetime import datetime, timezone
from app.core.config import settings
from app.core.exceptions import AppError


class ModusignClient:
    """모두싸인 전자서명 API 클라이언트"""

    def __init__(self):
        self.base_url = "https://api.modusign.co.kr/documents"
        self.api_key = settings.MODUSIGN_API_KEY
        self._http_client: Optional[httpx.AsyncClient] = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient()
        return self._http_client

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._http_client:
            await self._http_client.aclose()

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @property
    def is_mock(self) -> bool:
        return not self.api_key

    async def create_signing_request(
        self,
        document_title: str,
        pdf_url: str,
        signer_name: str,
        signer_email: str,
        signer_phone: Optional[str] = None,
    ) -> dict:
        """
        전자서명 요청 생성

        Returns:
            {"document_id": str, "signing_url": str, "status": str}
        """
        if self.is_mock:
            doc_id = f"mds_mock_{uuid.uuid4().hex[:12]}"
            return {
                "document_id": doc_id,
                "signing_url": f"https://mock.modusign.co.kr/sign/{doc_id}",
                "status": "sent",
            }

        try:
            payload = {
                "title": document_title,
                "file_url": pdf_url,
                "signers": [
                    {
                        "name": signer_name,
                        "email": signer_email,
                        "phone": signer_phone,
                        "role": "signer",
                    }
                ],
            }

            response = await self.http_client.post(
                self.base_url,
                headers=self._get_headers(),
                json=payload,
                timeout=30.0,
            )

            if response.status_code == 401:
                raise AppError("E-9003", "모두싸인 인증에 실패했습니다.")
            if response.status_code >= 400:
                raise AppError("E-9003", "모두싸인 API 요청에 실패했습니다.")

            data = response.json()
            return {
                "document_id": data["id"],
                "signing_url": data.get("signing_url", ""),
                "status": "sent",
            }

        except httpx.TimeoutException:
            raise AppError("E-9003", "모두싸인 API 연결 시간초과")
        except AppError:
            raise
        except Exception as e:
            raise AppError("E-9003", f"전자서명 요청 실패: {str(e)}")

    async def get_document_status(self, document_id: str) -> dict:
        """
        문서 서명 상태 조회

        Returns:
            {"document_id": str, "status": str, "completed_at": str | None}
        """
        if self.is_mock:
            return {
                "document_id": document_id,
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }

        try:
            response = await self.http_client.get(
                f"{self.base_url}/{document_id}",
                headers=self._get_headers(),
                timeout=30.0,
            )

            if response.status_code == 404:
                raise AppError("E-9001", "서명 문서를 찾을 수 없습니다.")
            if response.status_code >= 400:
                raise AppError("E-9003", "모두싸인 API 요청에 실패했습니다.")

            data = response.json()
            return {
                "document_id": data["id"],
                "status": data.get("status", "pending"),
                "completed_at": data.get("completed_at"),
            }

        except httpx.TimeoutException:
            raise AppError("E-9003", "모두싸인 API 연결 시간초과")
        except AppError:
            raise
        except Exception as e:
            raise AppError("E-9003", f"서명 상태 조회 실패: {str(e)}")

    async def download_signed_pdf(self, document_id: str) -> bytes:
        """
        서명 완료된 PDF 다운로드

        Returns:
            PDF 바이트 데이터
        """
        if self.is_mock:
            return b"%PDF-1.4 mock signed document"

        try:
            response = await self.http_client.get(
                f"{self.base_url}/{document_id}/download",
                headers=self._get_headers(),
                timeout=60.0,
            )

            if response.status_code == 404:
                raise AppError("E-9001", "서명 문서를 찾을 수 없습니다.")
            if response.status_code >= 400:
                raise AppError("E-9003", "PDF 다운로드에 실패했습니다.")

            return response.content

        except httpx.TimeoutException:
            raise AppError("E-9003", "PDF 다운로드 시간초과")
        except AppError:
            raise
        except Exception as e:
            raise AppError("E-9003", f"PDF 다운로드 실패: {str(e)}")
